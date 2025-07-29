# cython: language_level=3, boundscheck=False, wraparound=False, cdivision=True, initializedcheck=False

from cpython.bytes cimport PyBytes_FromStringAndSize, PyBytes_AS_STRING
from cpython.bytearray cimport PyByteArray_FromStringAndSize, PyByteArray_AS_STRING
from libc.string cimport memcpy
from libc.stdio cimport sprintf
from libc.stdint cimport int64_t, uint64_t
from cpython.mem cimport PyMem_Malloc, PyMem_Free
from cpython.object cimport PyObject_HasAttr

from shuttleasgi.server import responses
import time
import uuid_utils as uuid
from shuttleasgi.messages import Request, Response
from shuttleasgi.context import RequestContext, _request_context

cdef:
    object _REQ_ID_HEADER = b"x-request-id"
    object _PROCESSING_TIME_HEADER = b"shuttle-processing-ms"
    object _VERSION_HEADER = b"shuttle-version"
    object _SHUTTLE_VERSION_BYTES = b"2025-07-01"

    str _REQ_ID_CONTEXT_KEY = "request_id"
    str _PROCESSING_TIME_CONTEXT_KEY = "processing_time"

    object _SHUTTLE_HEADERS_ATTR = "_shuttle_headers_enabled"

    # Pre-allocated buffers per thread (thread-safe via GIL)
    char[512] _req_id_buffer
    char[64] _time_buffer
    bytearray _req_id_bytearray = bytearray(36)  # Pre-allocated for request ID
    char* _req_id_ba_data = PyByteArray_AS_STRING(_req_id_bytearray)

    char[512] _HEX_TABLE
    bint _hex_table_initialized = False

    # Cache for handler attribute checks
    dict _handler_cache = {}

cdef void _init_hex_table() noexcept nogil:
    cdef:
        int i
        unsigned char byte
    for i in range(256):
        byte = <unsigned char>i
        _HEX_TABLE[i * 2] = 48 + (byte >> 4) if (byte >> 4) < 10 else 87 + (byte >> 4)
        _HEX_TABLE[i * 2 + 1] = 48 + (byte & 15) if (byte & 15) < 10 else 87 + (byte & 15)

cdef inline bytes _build_request_id():
    """Optimized UUID to hex conversion with bytearray"""
    cdef:
        object uuid_obj = uuid.uuid7()
        bytes uuid_bytes = uuid_obj.bytes
        unsigned char* raw_bytes = <unsigned char*>PyBytes_AS_STRING(uuid_bytes)
        char* buf = _req_id_ba_data
        unsigned char b

    # Manual prefix copy
    buf[0] = 114  # 'r'
    buf[1] = 101  # 'e'
    buf[2] = 113  # 'q'
    buf[3] = 95   # '_'

    # Unrolled hex conversion
    with nogil:
        b = raw_bytes[0]; buf[4] = _HEX_TABLE[b*2]; buf[5] = _HEX_TABLE[b*2+1]
        b = raw_bytes[1]; buf[6] = _HEX_TABLE[b*2]; buf[7] = _HEX_TABLE[b*2+1]
        b = raw_bytes[2]; buf[8] = _HEX_TABLE[b*2]; buf[9] = _HEX_TABLE[b*2+1]
        b = raw_bytes[3]; buf[10] = _HEX_TABLE[b*2]; buf[11] = _HEX_TABLE[b*2+1]
        b = raw_bytes[4]; buf[12] = _HEX_TABLE[b*2]; buf[13] = _HEX_TABLE[b*2+1]
        b = raw_bytes[5]; buf[14] = _HEX_TABLE[b*2]; buf[15] = _HEX_TABLE[b*2+1]
        b = raw_bytes[6]; buf[16] = _HEX_TABLE[b*2]; buf[17] = _HEX_TABLE[b*2+1]
        b = raw_bytes[7]; buf[18] = _HEX_TABLE[b*2]; buf[19] = _HEX_TABLE[b*2+1]
        b = raw_bytes[8]; buf[20] = _HEX_TABLE[b*2]; buf[21] = _HEX_TABLE[b*2+1]
        b = raw_bytes[9]; buf[22] = _HEX_TABLE[b*2]; buf[23] = _HEX_TABLE[b*2+1]
        b = raw_bytes[10]; buf[24] = _HEX_TABLE[b*2]; buf[25] = _HEX_TABLE[b*2+1]
        b = raw_bytes[11]; buf[26] = _HEX_TABLE[b*2]; buf[27] = _HEX_TABLE[b*2+1]
        b = raw_bytes[12]; buf[28] = _HEX_TABLE[b*2]; buf[29] = _HEX_TABLE[b*2+1]
        b = raw_bytes[13]; buf[30] = _HEX_TABLE[b*2]; buf[31] = _HEX_TABLE[b*2+1]
        b = raw_bytes[14]; buf[32] = _HEX_TABLE[b*2]; buf[33] = _HEX_TABLE[b*2+1]
        b = raw_bytes[15]; buf[34] = _HEX_TABLE[b*2]; buf[35] = _HEX_TABLE[b*2+1]

    return bytes(_req_id_bytearray)

cdef inline bytes _format_time(double elapsed_s):
    """Fast time formatting"""
    cdef:
        int elapsed_ms = <int>(elapsed_s * 1000.0)
        char* buf = _time_buffer
        int temp
    
    if elapsed_ms < 10:
        buf[0] = 48 + elapsed_ms
        return PyBytes_FromStringAndSize(buf, 1)
    elif elapsed_ms < 100:
        buf[0] = 48 + elapsed_ms // 10
        buf[1] = 48 + elapsed_ms % 10
        return PyBytes_FromStringAndSize(buf, 2)
    elif elapsed_ms < 1000:
        temp = elapsed_ms
        buf[2] = 48 + temp % 10; temp //= 10
        buf[1] = 48 + temp % 10; temp //= 10
        buf[0] = 48 + temp
        return PyBytes_FromStringAndSize(buf, 3)
    else:
        # Simplified fallback to sprintf
        return str(elapsed_ms).encode()

cdef inline bint _has_shuttle_headers(object handler):
    """Cached attribute check"""
    cdef:
        unsigned long long handler_id = id(handler)  # Use 64-bit type
        object cached_result
    cached_result = _handler_cache.get(handler_id)
    if cached_result is not None:
        return cached_result
    try:
        result = PyObject_HasAttr(handler, _SHUTTLE_HEADERS_ATTR) and getattr(handler, _SHUTTLE_HEADERS_ATTR, False)
        _handler_cache[handler_id] = result
        return result
    except:
        _handler_cache[handler_id] = False
        return False

cdef inline object _ensure_response(object response):
    """Fast response normalization"""
    if response is None:
        return Response(204)
    if type(response) is Response:
        return response
    if type(response) is str:
        return responses.text(response)
    if not isinstance(response, Response):
        return responses.json(response)
    return response

if not _hex_table_initialized:
    with nogil:
        _init_hex_table()
    _hex_table_initialized = True

class ShuttleHeadersDecoratorMiddleware:
    async def __call__(self, request: Request, handler):
        cdef:
            double start_time, end_time, elapsed
            bytes request_id, time_bytes
            object response
            dict ctx

        if not _has_shuttle_headers(handler):
            return await handler(request)

        # Create dict once, store in local variable AND contextvar
        ctx = {}
        _request_context.set(ctx)

        start_time = time.perf_counter()
        request_id = _build_request_id()

        ctx[_REQ_ID_CONTEXT_KEY] = request_id

        response = await handler(request)
        response = _ensure_response(response)

        end_time = time.perf_counter()
        elapsed = end_time - start_time
        time_bytes = _format_time(elapsed)

        ctx[_PROCESSING_TIME_CONTEXT_KEY] = time_bytes

        response.add_header(_REQ_ID_HEADER, request_id)
        response.add_header(_PROCESSING_TIME_HEADER, time_bytes)
        response.add_header(_VERSION_HEADER, _SHUTTLE_VERSION_BYTES)

        return response


def shuttle_headers():
    """Decorator with minimal overhead"""
    def decorator(handler):
        async def wrapped(*args, **kwargs):
            return await handler(*args, **kwargs)

        wrapped._shuttle_headers_enabled = True
        wrapped.__module__ = getattr(handler, '__module__', None)
        wrapped.__name__ = getattr(handler, '__name__', 'wrapped')
        wrapped.__qualname__ = getattr(handler, '__qualname__', 'wrapped')
        wrapped.__doc__ = getattr(handler, '__doc__', None)
        wrapped.__annotations__ = getattr(handler, '__annotations__', {})
        wrapped.__wrapped__ = handler
        
        return wrapped
    return decorator