cdef class JSONSettings:
    cpdef bytes dumps(self, object obj)

cdef JSONSettings json_settings