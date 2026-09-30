from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings

class InstanceIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Instance-ID"] = settings.INSTANCE_ID
        return response