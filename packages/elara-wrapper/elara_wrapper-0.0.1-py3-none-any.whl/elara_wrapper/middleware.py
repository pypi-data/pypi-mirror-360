"""
Elara FastAPI Middleware for request validation
"""

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class ElaraMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware that validates requests based on a validation string
    """

    def __init__(self, app, validation_string: str):
        """
        Initialize the middleware

        Args:
            app: FastAPI application
            validation_string: String parameter used for request validation
        """
        super().__init__(app)
        self.validation_string = validation_string

    async def dispatch(self, request: Request, call_next):
        """
        Process the request through the middleware

        Args:
            request: The incoming request
            call_next: The next middleware or endpoint

        Returns:
            Response or error
        """
        try:
            # Perform validation
            if not self._validate_request(request):
                return JSONResponse(
                    status_code=403,
                    content={
                        "error": "Request validation failed",
                        "message": "Access denied",
                    },
                )

            # Continue to next middleware/endpoint
            response = await call_next(request)
            return response

        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"error": "Middleware error", "message": str(e)},
            )

    def _validate_request(self, request: Request) -> bool:
        """
        Validate the request based on the validation string

        Args:
            request: The incoming request

        Returns:
            True if request is valid, False otherwise
        """
        return self.validation_string == "True"


def add_elara_middleware(app: FastAPI, validation_string: str) -> ElaraMiddleware:
    """
    Add Elara middleware to a FastAPI application

    Args:
        app: FastAPI application instance
        validation_string: String parameter for validation

    Returns:
        ElaraMiddleware instance for further configuration
    """
    middleware = ElaraMiddleware(app, validation_string)
    app.add_middleware(ElaraMiddleware, validation_string=validation_string)
    return middleware
