#cython: language_level=3

from collections.abc import Mapping, MutableSequence
from typing import Dict, List, Tuple, Union

cdef class Header:
    def __init__(self, bytes name, bytes value):
        self.name = name
        self.value = value
    def __repr__(self):
        return f'<Header {self.name}: {self.value}>'
    def __iter__(self):
        yield self.name
        yield self.value
    def __eq__(self, other):
        if isinstance(other, Header):
            return other.name.lower() == self.name.lower() and other.value == self.value
        return NotImplemented

cdef class Headers:
    def __init__(self, list values=None):
        cdef list values_to_add
        cdef bytes name, value, lower_name
        self._values = []
        self._lookup = {}
        if values:
            values_to_add = list(values)
            self._values.extend(values_to_add)
            for name, value in values_to_add:
                lower_name = name.lower()
                if lower_name in self._lookup:
                    self._lookup[lower_name].append(value)
                else:
                    self._lookup[lower_name] = [value]

    cpdef tuple get(self, bytes name):
        cdef list results = self._lookup.get(name.lower())
        if results:
            return tuple(results)
        return ()

    cpdef list get_tuples(self, bytes name):
        cdef list results = []
        cdef tuple header
        cdef bytes header_name
        name = name.lower()
        for header in self._values:
            header_name, _ = header
            if header_name.lower() == name:
                results.append(header)
        return results

    cpdef bytes get_first(self, bytes key):
        cdef list values = self._lookup.get(key.lower())
        if values:
            return values[0]

    cpdef bytes get_single(self, bytes key):
        cdef list results = self._lookup.get(key.lower())
        if not results:
            raise ValueError('Headers does not contain one header with the given key')
        if len(results) > 1:
            raise ValueError('Headers contains more than one header with the given key')
        return results[0]

    cpdef void merge(self, list values):
        cdef tuple header
        for header in values:
            if header is None:
                continue
            self.add(header[0], header[1])

    def update(self, dict values: Dict[bytes, bytes]):
        for key, value in values.items():
            self[key] = value

    def items(self):
        yield from self._values

    cpdef Headers clone(self):
        return Headers(self._values)

    def add_many(self, values: Union[Dict[bytes, bytes], List[Tuple[bytes, bytes]]]):
        if isinstance(values, MutableSequence):
            for item in values:
                self.add(*item)
        elif isinstance(values, Mapping):
            for key, value in values.items():
                self.add(key, value)
        else:
            raise ValueError('values must be Dict[bytes, bytes] or List[Header]')

    @staticmethod
    def _add_to_instance(instance, other):
        if isinstance(other, Headers):
            for name, value in other._values:
                instance.add(name, value)
            return instance
        if isinstance(other, Header):
            instance.add(other.name, other.value)
            return instance
        if isinstance(other, tuple):
            if len(other) != 2:
                raise ValueError(f'Cannot add, an invalid tuple {str(other)}.')
            instance.add(*other)
            return instance
        if isinstance(other, MutableSequence):
            for value in other:
                if isinstance(value, tuple) and len(value) == 2:
                    instance.add(*value)
                else:
                    raise ValueError(f'The sequence contains invalid elements: '
                                     f'cannot add {str(value)} to {instance.__class__.__name__}')
            return instance
        return NotImplemented

    def __add__(self, other):
        return self._add_to_instance(self.clone(), other)

    def __radd__(self, other):
        return self._add_to_instance(self.clone(), other)

    def __iadd__(self, other):
        return self._add_to_instance(self, other)

    def __iter__(self):
        yield from self._values

    def __setitem__(self, bytes key, bytes value):
        self.set(key, value)

    def __getitem__(self, bytes item):
        return self.get(item)

    cpdef tuple keys(self):
        cdef set seen = set()
        cdef list results = []
        cdef bytes name, value, lower_name
        for name, value in self._values:
            lower_name = name.lower()
            if lower_name not in seen:
                results.append(name)
                seen.add(lower_name)
        return tuple(results)

    cpdef void add(self, bytes name, bytes value):
        cdef bytes lower_name = name.lower()
        self._values.append((name, value))
        if lower_name in self._lookup:
            self._lookup[lower_name].append(value)
        else:
            self._lookup[lower_name] = [value]

    cpdef void set(self, bytes name, bytes value):
        self.remove(name)
        self.add(name, value)

    cpdef void remove(self, bytes key):
        cdef bytes lower_key = key.lower()
        if lower_key not in self._lookup:
            return
        del self._lookup[lower_key]
        self._values = [item for item in self._values if item[0].lower() != lower_key]

    cpdef bint contains(self, bytes key):
        return key.lower() in self._lookup

    def __delitem__(self, bytes key):
        self.remove(key)

    def __contains__(self, bytes key):
        return self.contains(key)

    def __repr__(self):
        return f'<Headers {self._values}>'

    def __len__(self):
        return len(self._values)