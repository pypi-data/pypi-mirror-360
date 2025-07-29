# cython: language_level=3, embedsignature=True
# Copyright (C) 2018-present Roberto Prevato
#
# This module is part of ShuttleASGI and is released under
# the MIT License https://opensource.org/licenses/MIT


cdef class Header:
    cdef readonly bytes name
    cdef readonly bytes value

cdef class Headers:
    cdef readonly list values
    cdef list _values
    cdef dict _lookup

    cpdef tuple get(self, bytes name)
    cpdef list get_tuples(self, bytes name)
    cpdef bytes get_first(self, bytes key)
    cpdef bytes get_single(self, bytes key)
    cpdef void merge(self, list values)
    cpdef Headers clone(self)
    cpdef tuple keys(self)
    cpdef void add(self, bytes name, bytes value)
    cpdef void set(self, bytes name, bytes value)
    cpdef void remove(self, bytes key)
    cpdef bint contains(self, bytes key)