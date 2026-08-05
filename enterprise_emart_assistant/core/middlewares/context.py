from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from core.context import Context, context


class ContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        uid = request.headers.get("x-uid")
        authorization = request.headers.get("authorization")
        ctx = context.set(Context(uid=uid, token=authorization))
        try:
            return await call_next(request)
        finally:
            context.reset(ctx)
