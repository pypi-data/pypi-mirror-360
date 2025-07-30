"""Middleware package for qakeapi"""

import time
from typing import Any, Callable, Dict, List, Optional, Type

from ..requests import Request
from ..responses import JSONResponse, Response
from .cors import CORSMiddleware


class BaseMiddleware:
    """Base class for all middleware in QakeAPI."""
    
    async def process_request(self, request: Request) -> Optional[Response]:
        """Process the request before it reaches the view.
        
        Args:
            request: The incoming request object
            
        Returns:
            Optional[Response]: If a response is returned, the request processing
            will be short-circuited and the response will be returned to the client.
            If None is returned, the request will continue to be processed.
        """
        return None
        
    async def process_response(self, response: Response) -> Response:
        """Process the response after it leaves the view.
        
        Args:
            response: The outgoing response object
            
        Returns:
            Response: The processed response object
        """
        return response


class Middleware:
    async def __call__(
        self, request: Request, call_next: Callable[[Request], Response]
    ) -> Response:
        return await call_next(request)


class RequestLoggingMiddleware(Middleware):
    async def __call__(
        self, request: Request, call_next: Callable[[Request], Response]
    ) -> Response:
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time

        print(
            f"{request.method} {request.path} "
            f"- {response.status_code} "
            f"- {duration:.3f}s"
        )

        return response


class ErrorHandlingMiddleware(Middleware):
    async def __call__(
        self, request: Request, call_next: Callable[[Request], Response]
    ) -> Response:
        try:
            return await call_next(request)
        except Exception as exc:
            return JSONResponse(
                {"detail": str(exc), "type": exc.__class__.__name__}, status_code=500
            )


class AuthenticationMiddleware(Middleware):
    def __init__(
        self,
        auth_header: str = "Authorization",
        auth_scheme: str = "Bearer",
        exempt_paths: List[str] = [],
    ):
        self.auth_header = auth_header
        self.auth_scheme = auth_scheme
        self.exempt_paths = exempt_paths

    async def __call__(
        self, request: Request, call_next: Callable[[Request], Response]
    ) -> Response:
        if request.path in self.exempt_paths:
            return await call_next(request)

        auth_header = request.headers.get(
            self.auth_header.lower().encode(), b""
        ).decode()

        if not auth_header:
            return JSONResponse({"detail": "Not authenticated"}, status_code=401)

        try:
            scheme, token = auth_header.split(" ", 1)
        except ValueError:
            return JSONResponse({"detail": "Invalid authorization header format"}, status_code=401)

        if scheme.lower() != self.auth_scheme.lower():
            return JSONResponse(
                {
                    "detail": f"Invalid authentication scheme. Expected {self.auth_scheme}"
                },
                status_code=401,
            )

        request.auth_token = token
        return await call_next(request)


class RateLimitMiddleware(Middleware):
    def __init__(self, requests_per_minute: int = 60, window_size: int = 60):
        self.requests_per_minute = requests_per_minute
        self.window_size = window_size
        self.requests: Dict[str, List[float]] = {}

    def _clean_old_requests(self, client: str):
        """Remove requests older than window_size"""
        current_time = time.time()
        self.requests[client] = [
            req_time
            for req_time in self.requests[client]
            if current_time - req_time < self.window_size
        ]

    async def __call__(
        self, request: Request, call_next: Callable[[Request], Response]
    ) -> Response:
        client = request.client[0] if request.client else "unknown"

        if client not in self.requests:
            self.requests[client] = []

        self._clean_old_requests(client)

        if len(self.requests[client]) >= self.requests_per_minute:
            return JSONResponse({"detail": "Too many requests"}, status_code=429)

        self.requests[client].append(time.time())
        return await call_next(request)


__all__ = [
    "Middleware",
    "CORSMiddleware",
    "RequestLoggingMiddleware",
    "ErrorHandlingMiddleware",
    "AuthenticationMiddleware",
    "RateLimitMiddleware",
]
