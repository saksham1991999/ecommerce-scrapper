from fastapi import HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_403_FORBIDDEN


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware for authenticating API requests using an API key.

    This middleware checks for the presence of a valid API key in the request headers
    for all requests that start with "/api/". If the API key is missing or invalid,
    a 403 Forbidden response is returned.

    Attributes:
        api_key (str): The valid API key to authenticate requests.
    """

    def __init__(self, app: str, api_key: str) -> None:
        """
        Initializes the AuthMiddleware with the given API key.

        Args:
            app (str): The FastAPI application instance.
            api_key (str): The valid API key for authentication.
        """
        super().__init__(app)
        self.api_key = api_key

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Processes the request and checks for a valid API key.

        If the request path starts with "/api/", it checks the "X-API-Key" header
        against the stored API key. If the key is invalid, a 403 Forbidden error is raised.

        Args:
            request (Request): The incoming request.
            call_next: A function to call the next middleware or endpoint.

        Returns:
            Response: The response from the next middleware or endpoint.
        """
        if request.url.path.startswith("/api/"):
            api_key = request.headers.get("X-API-Key")
            if api_key != self.api_key:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN,
                    detail="Could not validate credentials"
                )
        response = await call_next(request)
        return response
