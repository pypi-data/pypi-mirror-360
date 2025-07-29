# cython: language_level=3, embedsignature=True

from .exceptions cimport HTTPException
from .messages cimport Request, Response

cdef class BaseApplication:
    cdef public bint show_error_details
    cdef readonly object router
    cdef readonly object logger
    cdef public dict exceptions_handlers
    cdef object _default_404
    cdef object _default_405
    cpdef object get_http_exception_handler(self, HTTPException http_exception)
    cdef object get_exception_handler(self, Exception exception, type stop_at)
    cdef bint is_handled_exception(self, Exception exception)