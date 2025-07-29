from shuttleasgi.messages import Request
from typing import Callable, Awaitable, Any

class ShuttleHeadersDecoratorMiddleware:
    async def __call__(self, request: Request, handler: Callable[..., Awaitable[Any]]) -> Any: ...

def shuttle_headers() -> Callable[[Callable[..., Awaitable[Any]]], Callable[..., Awaitable[Any]]]: ...