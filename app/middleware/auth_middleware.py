from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_403_FORBIDDEN

class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, api_key: str):
        super().__init__(app)
        self.api_key = api_key

    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/api/"):
            api_key = request.headers.get("X-API-Key")
            if api_key != self.api_key:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN, 
                    detail="Could not validate credentials"
                )
        response = await call_next(request)
        return response