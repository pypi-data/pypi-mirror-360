# cython: language_level=3
# cython: boundscheck=False, wraparound=False, nonecheck=False
# cython: initializedcheck=False, cdivision=True

import http
import logging
import time

from .contents cimport Content, TextContent, JSONContent
from .exceptions cimport BadRequest, HTTPException, InternalServerError, NotFound, WrongMethod
from .messages cimport Request, Response
from .context import RequestContext, _request_context

from .utils import get_class_instance_hierarchy

# Better support for Pydantic
try:
    from pydantic import ValidationError
except ImportError:
    ValidationError = None


async def handle_wrong_method(app, Request request, HTTPException http_exception):
    cdef str method = request.method
    cdef str path = request.url.path.decode()

    return Response(
        405,
        content=JSONContent({
            "error": {
                "type": "invalid_request_error",
                "code": "method_not_allowed",
                "message": f"Not allowed to {method} on {path}.",
                "param": None
            }
        })
    )


async def handle_not_found(app, Request request, HTTPException http_exception):
    """Default Not Found handler, returns a simple 404 response."""
    cdef method = request.method
    cdef path = request.url.path.decode()

    return Response(
        404,
        content=JSONContent({
            "error": {
                "type": "invalid_request_error",
                "code": "unknown_url",
                "message": f"Invalid URL ({method} {path}).",
                "param": None
            }
        })
    )


async def handle_internal_server_error(app, Request request, Exception exception):
    """Default Internal Server Error handler, returns a simple 500 response."""
    # Intentionally without details!
    return Response(500, content=TextContent("Internal Server Error"))


async def handle_bad_request(app, Request request, HTTPException http_exception):
    # supports for pydantic ValidationError with json() method
    if http_exception.__context__ is not None and callable(getattr(http_exception.__context__, "json", None)):
        return Response(http_exception.status, content=Content(b"application/json", http_exception.__context__.json().encode("utf8")))

    return Response(400, content=TextContent(f'Bad Request: {str(http_exception)}'))


async def _default_pydantic_validation_error_handler(app, Request request, Exception error):
    return Response(400, content=Content(b"application/json", error.json(indent=4).encode("utf-8")))


async def common_http_exception_handler(app, Request request, HTTPException http_exception):
    return Response(http_exception.status, content=TextContent(http.HTTPStatus(http_exception.status).phrase))


def get_logger():
    logger = logging.getLogger("shuttleasgi.server")
    logger.setLevel(logging.INFO)
    return logger


cdef class BaseApplication:

    def __init__(self, bint show_error_details, object router):
        self.router = router
        self.exceptions_handlers = self.init_exceptions_handlers()
        self._default_404 = self.exceptions_handlers.get(404, handle_not_found)
        self._default_405 = self.exceptions_handlers.get(405, handle_wrong_method)
        self.show_error_details = show_error_details
        self.logger = get_logger()

    def init_exceptions_handlers(self):
        default_handlers = {
            405: handle_wrong_method,
            404: handle_not_found,
            400: handle_bad_request
        }
        if ValidationError is not None:
            default_handlers[ValidationError] = _default_pydantic_validation_error_handler
        return default_handlers

    async def log_unhandled_exc(self, request, exc):
        self.logger.error(
            "Unhandled exception - \"%s %s\"",
            request.method,
            request.url.value.decode(),
            exc_info=exc
        )

    async def log_handled_exc(self, request, exc):
        if isinstance(exc, HTTPException):
            self.logger.info(
                "HTTP %s - \"%s %s\". %s",
                exc.status,
                request.method,
                request.url.value.decode(),
                str(exc)
            )
        else:
            self.logger.info(
                "Handled error: \"%s %s\". %s",
                request.method,
                request.url.value.decode(),
                str(exc)
            )

    async def handle(self, Request request):
        cdef object route
        cdef Response response
        cdef set allowed_methods
        cdef bytes path_bytes = request._path

        route = self.router.get_match(request)
        if route is not None:
            request.route_values = route.values
            try:
                response = await route.handler(request)
            except Exception as exc:
                response = await self.handle_request_handler_exception(request, exc)

        else:  # no route matched
            allowed_methods = self.router.get_methods_for_path(path_bytes)

            if allowed_methods and request.method.encode() not in allowed_methods:
                # 405 – wrong HTTP method
                response = await self._default_405(self, request, WrongMethod())
                if response is not None:
                    response.add_header(b"Allow", b", ".join(allowed_methods))
            else:
                # 404 – path not found
                response = await self._default_404(self, request, NotFound())

            if response is None:
                response = Response(404)

        return response or Response(204)

    async def handle_request_handler_exception(self, request, exc):
        if isinstance(exc, HTTPException):
            await self.log_handled_exc(request, exc)
            return await self.handle_http_exception(request, exc)

        if self.is_handled_exception(exc):
            await self.log_handled_exc(request, exc)
        else:
            await self.log_unhandled_exc(request, exc)

        return await self.handle_exception(request, exc)

    cpdef object get_http_exception_handler(self, HTTPException http_exception):
        # Try getting HTTP exception handler by type first, supporting
        # base classes up to a certain point (HTTPException)
        handler = self.get_exception_handler(http_exception, stop_at=HTTPException)
        if handler:
            return handler
        # Try getting HTTP exception handler by HTTP error status code
        return self.exceptions_handlers.get(
            http_exception.status, common_http_exception_handler
        )

    cdef bint is_handled_exception(self, Exception exception):
        for class_type in get_class_instance_hierarchy(exception):
            if class_type in self.exceptions_handlers:
                return True
        return False

    cdef object get_exception_handler(self, Exception exception, type stop_at):
        for class_type in get_class_instance_hierarchy(exception):
            if stop_at is not None and stop_at is class_type:
                return None
            if class_type in self.exceptions_handlers:
                return self.exceptions_handlers[class_type]

        return None

    async def handle_internal_server_error(self, Request request, Exception exc):
        """
        Handle an unhandled exception. If an exception handler is defined for
        InternalServerError or status 500, it is used.
        """
        if self.show_error_details:
            return self.server_error_details_handler.produce_response(request, exc)

        # We want to hide exception details, and possibly use a user-defined
        # handler for this.
        error = InternalServerError(exc)
        internal_server_error_handler = self.get_http_exception_handler(error)

        try:
            return await internal_server_error_handler(self, request, error)
        except Exception:
            self.logger.exception(
                "An exception occurred while trying to apply the configured "
                "Internal Server Error handler!"
            )
        return Response(500, content=TextContent("Internal Server Error"))

    async def _apply_exception_handler(self, Request request, Exception exc, object exception_handler):
        try:
            return await exception_handler(self, request, exc)
        except Exception as server_ex:
            return await self.handle_exception(request, server_ex)

    async def handle_http_exception(self, Request request, HTTPException http_exception):
        exception_handler = self.get_http_exception_handler(http_exception)
        if exception_handler:
            return await self._apply_exception_handler(request, http_exception, exception_handler)

        return await self.handle_exception(request, http_exception)

    async def handle_exception(self, request, exc):
        exception_handler = self.get_exception_handler(exc, None)
        if exception_handler:
            return await self._apply_exception_handler(request, exc, exception_handler)

        return await self.handle_internal_server_error(request, exc)
