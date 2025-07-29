# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True

from libc.string cimport memcpy
from cpython.bytes cimport PyBytes_FromStringAndSize

import orjson as json
import uuid_utils as uuid
from collections.abc import MutableSequence
from inspect import isasyncgenfunction
from typing import Dict, List, Optional, Tuple, Union
from urllib.parse import parse_qsl, quote_plus

from shuttleasgi.settings.json import json_settings


from .exceptions cimport MessageAborted


cdef class Content:

    def __init__(
        self,
        bytes content_type,
        bytes data
    ):
        self.type = content_type
        self.body = data
        self.length = len(data)

    async def read(self):
        return self.body


cdef class StreamedContent(Content):

    def __init__(
        self,
        bytes content_type,
        object data_provider,
        long long data_length = -1
    ):
        self.type = content_type
        self.body = None
        self.length = data_length
        self.generator = data_provider

        if not isasyncgenfunction(data_provider):
            raise ValueError("Data provider must be an async generator")

    async def read(self):
        value = bytearray()

        async for chunk in self.generator():
            value.extend(chunk)

        self.body = bytes(value)
        self.length = len(self.body)
        return self.body

    async def stream(self):
        async for chunk in self.generator():
            yield chunk

    async def get_parts(self):
        async for chunk in self.generator():
            yield chunk


cdef class ASGIContent(Content):

    def __init__(self, object receive):
        self.type = None
        self.body = None
        self.length = -1
        self.receive = receive

    cpdef void dispose(self):
        self.receive = None
        self.body = None

    async def stream(self):
        while True:
            message = await self.receive()

            if message.get('type') == 'http.disconnect':
                raise MessageAborted()

            yield message.get('body', b'')

            if not message.get('more_body'):
                break

        yield b''

    async def read(self):
        if self.body is not None:
            return self.body
        value = bytearray()

        while True:
            message = await self.receive()

            if message.get('type') == 'http.disconnect':
                raise MessageAborted()

            value.extend(message.get('body', b''))

            if not message.get('more_body'):
                break

        self.body = bytes(value)
        self.length = len(self.body)
        return self.body


cdef class TextContent(Content):

    def __init__(self, str text):
        super().__init__(b'text/plain; charset=utf-8', text.encode('utf8'))


cdef class HTMLContent(Content):

    def __init__(self, str html):
        super().__init__(b'text/html; charset=utf-8', html.encode('utf8'))


cdef class JSONContent(Content):

    def __init__(self, object data, dumps=json_settings.dumps):
        super().__init__(b'application/json', dumps(data))


cdef dict parse_www_form_urlencoded(str content):
    # application/x-www-form-urlencoded
    cdef str key, value
    cdef dict data = {}
    for key, value in parse_qsl(content):
        if key in data:
            if isinstance(data[key], str):
                data[key] = [data[key], value]
            else:
                data[key].append(value)
        else:
            data[key] = value
    return data


cpdef dict parse_www_form(str content):
    return parse_www_form_urlencoded(content)


cdef object try_decode(bytes value, str encoding):
    try:
        return value.decode(encoding or 'utf8')
    except:
        return value


cdef dict multiparts_to_dictionary(list parts):
    cdef str key
    cdef str charset
    cdef data = {}
    cdef FormPart part

    for part in parts:
        key = part.name.decode('utf8')
        if part.charset:
            charset = part.charset.encode()
        else:
            charset = None

        # NB: we cannot assume that the value of a multipart form part can be decoded as UTF8;
        # here we try to decode it, just to be more consistent with values read from www-urlencoded form data
        if part.file_name:
            # Files need special handling, must be kept as-is
            if key in data:
                data[key].append(part)
            else:
                data[key] = [part]
        else:
            if key in data:
                if isinstance(data[key], list):
                    data[key].append(try_decode(part.data, charset))
                else:
                    data[key] = [data[key], try_decode(part.data, charset)]
            else:
                data[key] = try_decode(part.data, charset)

    return data


cpdef void write_multipart_part(FormPart part, bytearray destination):
    # https://tools.ietf.org/html/rfc7578#page-4
    destination.extend(b'Content-Disposition: form-data; name="')
    destination.extend(part.name)
    destination.extend(b'"')
    if part.file_name:
        destination.extend(b'; filename="')
        destination.extend(part.file_name)
        destination.extend(b'"\r\n')
    if part.content_type:
        destination.extend(b'Content-Type: ')
        destination.extend(part.content_type)
    destination.extend(b'\r\n\r\n')
    destination.extend(part.data)
    destination.extend(b'\r\n')


cpdef bytes write_www_form_urlencoded(data: Union[dict, list]):
    # application/x-www-form-urlencoded
    if isinstance(data, list):
        values = data
    else:
        values = data.items()

    cdef list contents = []

    for key, value in values:
        if isinstance(value, MutableSequence):
            for item in value:
                contents.append(quote_plus(key) + '=' + quote_plus(str(item)))
        else:
            contents.append(quote_plus(key) + '=' + quote_plus(str(value)))
    return ('&'.join(contents)).encode('utf8')


cdef class FormContent(Content):

    def __init__(self, data: Union[Dict[str, str], List[Tuple[str, str]]]):
        super().__init__(b'application/x-www-form-urlencoded', write_www_form_urlencoded(data))


cdef class FormPart:

    def __init__(self,
                 bytes name,
                 bytes data,
                 bytes content_type: Optional[bytes]=None,
                 bytes file_name: Optional[bytes]=None,
                 bytes charset: Optional[bytes] = None):
        self.name = name
        self.data = data
        self.file_name = file_name
        self.content_type = content_type
        self.charset = charset

    def __eq__(self, other):
        if isinstance(other, FormPart):
            return other.name == self.name and other.file_name == self.file_name and other.content_type == self.content_type and other.charset == self.charset and other.data == self.data
        if other is None:
            return False
        return NotImplemented

    def __repr__(self):
        return f'<FormPart {self.name} - at {id(self)}>'


cdef class MultiPartFormData(Content):

    def __init__(self, list parts):
        self.parts = parts
        self.boundary = b'------' + str(uuid.uuid4()).replace('-', '').encode()
        super().__init__(b'multipart/form-data; boundary=' + self.boundary, write_multipart_form_data(self))


cpdef bytes write_multipart_form_data(MultiPartFormData data):
    cdef bytearray contents = bytearray()
    cdef FormPart part
    for part in data.parts:
        contents.extend(b'--')
        contents.extend(data.boundary)
        contents.extend(b'\r\n')
        write_multipart_part(part, contents)
    contents.extend(b'--')
    contents.extend(data.boundary)
    contents.extend(b'--\r\n')
    return bytes(contents)


cdef class ServerSentEvent:
    """
    Represents a single event of a Server-sent event communication, to be used
    in a asynchronous generator.

    Attributes:
        data: An object that will be transmitted to the client, in JSON format.
    """

    def __init__(
        self,
        object data,
    ):
        """
        Creates an instance of ServerSentEvent
        """
        self.data = data

    cpdef bytes write_data(self):
        return json_settings.dumps(self.data)

    def __repr__(self):
        return f"ServerSentEvent({self.data})"


cdef bytes _DONE_BYTES = b'[DONE]'


cdef class DONEServerSentEvent(ServerSentEvent):
    """
    Represents a special event that indicates the end of a Server-sent event stream.
    This is used to signal that no more events will be sent.

    Attributes:
        data: A constant string '[DONE]' to indicate the end of the stream.
    """

    def __init__(self):
        ServerSentEvent.__init__(self, _DONE_BYTES)

    cpdef bytes write_data(self):
        return _DONE_BYTES


cdef class TextServerSentEvent(ServerSentEvent):
    """
    Represents a single event of a Server-sent event communication, to be used
    in a asynchronous generator.

    Attributes:
        data: A string that will be transmitted to the client as is.
    """

    def __init__(
        self,
        str data,
    ):
        super().__init__(data)

    cpdef bytes write_data(self):
        cdef:
            str data_str = self.data
            bytes utf8_data = data_str.encode('utf-8')
            char* src = <char*>utf8_data
            Py_ssize_t length = len(utf8_data)
            Py_ssize_t i, j, newline_count = 0
            bytes result
            char* dst

        for i in range(length):
            if src[i] == b'\n':
                newline_count += 1
        
        if newline_count == 0:
            return utf8_data

        result = PyBytes_FromStringAndSize(NULL, length + newline_count)
        dst = <char*>result
        j = 0

        for i in range(length):
            if src[i] == b'\n':
                dst[j] = b'\\'
                dst[j + 1] = b'n'
                j += 2
            else:
                dst[j] = src[i]
                j += 1
                
        return result