# shuttleasgi/context.py
from contextvars import ContextVar

_request_context: ContextVar[dict] = ContextVar("request_context")

class RequestContext:
    @staticmethod
    def get(key: str, default=None):
        return _request_context.get().get(key, default)
    
    @staticmethod
    def set(key: str, value):
        _request_context.get()[key] = value