"""
Elara FastAPI Middleware for request validation
"""

from http import HTTPStatus

from eth_account.messages import encode_defunct
from fastapi import FastAPI, Request, HTTPException
from hexbytes import HexBytes
from starlette.middleware.base import BaseHTTPMiddleware
from web3 import Web3

from elara_wrapper.auth import auth_message
from elara_wrapper.interfaces import GeneratePostRequestBody


def is_eth_signature_valid(message: str, signature: str, address: str) -> bool:
    """Check if a message signature with an Ethereum wallet is valid"""
    w3 = Web3(Web3.HTTPProvider(""))
    encoded_message = encode_defunct(text=message)
    recovered_address = w3.eth.account.recover_message(
        encoded_message,
        signature=HexBytes(signature),
    )
    return address.lower() == recovered_address.lower()


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
            if not await self._validate_request(request):
                return HTTPException(
                    status_code=HTTPStatus.FORBIDDEN,
                    detail="Elara validation failed, access denied",
                )

            # Continue to next middleware/endpoint
            response = await call_next(request)
            return response

        except Exception as e:
            return HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail=f"Internal Elara middleware error: {e}",
            )

    async def _validate_request(self, request: Request) -> bool:
        """
        Validate the request based on the validation string

        Args:
            request: The incoming request

        Returns:
            True if request is valid, False otherwise
        """
        # Only validate /generate route
        if request.url.path != "/generate":
            return True

        body = await request.body()

        try:
            body_data = body.decode()
            request_body = GeneratePostRequestBody.model_validate_json(body_data)

            if not is_eth_signature_valid(
                auth_message(request_body.address),
                request_body.signature,
                request_body.address,
            ):
                raise HTTPException(
                    status_code=HTTPStatus.FORBIDDEN,
                    detail="Signature doesn't match the given address",
                )
        except Exception:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Invalid request body format",
            )

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
