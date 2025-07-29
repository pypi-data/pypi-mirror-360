"""
Elara FastAPI Middleware for request validation
"""

from http import HTTPStatus

from eth_account.messages import encode_defunct
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from hexbytes import HexBytes
from starlette.middleware.base import BaseHTTPMiddleware
from web3 import Web3

from elara_wrapper.auth import auth_message
from elara_wrapper.interfaces import GeneratePostRequestBody

# ENS contract address on Base
ENS_CONTRACT_ADDRESS = "0xc3a4eB979e9035486b54Fe8b57D36aEF9519eAc6"

# ENS contract ABI (only the text function we need)
ENS_CONTRACT_ABI = [
    {
        "inputs": [
            {"internalType": "bytes32", "name": "node", "type": "bytes32"},
            {"internalType": "string", "name": "key", "type": "string"},
        ],
        "name": "text",
        "outputs": [{"internalType": "string", "name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function",
    }
]


def is_eth_signature_valid(message: str, signature: str, address: str) -> bool:
    """Check if a message signature with an Ethereum wallet is valid"""
    w3 = Web3(Web3.HTTPProvider(""))
    encoded_message = encode_defunct(text=message)
    recovered_address = w3.eth.account.recover_message(
        encoded_message,
        signature=HexBytes(signature),
    )
    return address.lower() == recovered_address.lower()


def namehash(name: str) -> bytes:
    """Calculate the namehash for an ENS name"""
    if not name:
        return b"\x00" * 32

    node = b"\x00" * 32
    labels = name.split(".")
    for label in reversed(labels):
        label_hash = Web3.keccak(text=label)
        node = Web3.keccak(node + label_hash)

    return node


def get_ens_text_record(validation_string: str, key: str = "allowed_callers") -> str:
    """
    Fetch the ENS text record for a given validation string

    Args:
        validation_string: The validation string (e.g., "test" for "test.elara-app.eth")
        key: The text record key to fetch (default: "allowed_callers")

    Returns:
        The text record value, or empty string if not found
    """
    try:
        # Connect to Base network
        w3 = Web3(Web3.HTTPProvider("https://mainnet.base.org"))

        # Construct the full ENS name
        ens_name = f"{validation_string}.elara-app.eth"

        # Calculate namehash
        node = namehash(ens_name)

        # Create contract instance
        contract = w3.eth.contract(
            address=Web3.to_checksum_address(ENS_CONTRACT_ADDRESS), abi=ENS_CONTRACT_ABI
        )

        # Call the text function
        text_value = contract.functions.text(node, key).call()

        return text_value

    except Exception:
        # Return empty string if any error occurs
        return ""


class ElaraMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware that validates requests based on a validation string
    """

    def __init__(self, app, ens_name: str):
        """
        Initialize the middleware

        Args:
            app: FastAPI application
            ens_name: ENS subdomain to use for validation (e.g., "test" for "test.elara-app.eth")
        """
        super().__init__(app)
        self.ens_name = ens_name

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
            validation_result = await self._validate_request(request)
            if validation_result is not True:
                return validation_result

            # Continue to next middleware/endpoint
            response = await call_next(request)
            return response

        except HTTPException as e:
            # Return proper HTTP response for HTTPExceptions
            return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
        except Exception as e:
            # Return proper HTTP response for other exceptions
            return JSONResponse(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                content={"detail": f"Internal Elara middleware error: {str(e)}"},
            )

    async def _validate_request(self, request: Request):
        """
        Validate the request based on the validation string

        Args:
            request: The incoming request

        Returns:
            True if request is valid, JSONResponse with error if invalid
        """
        # Only validate /generate route
        if request.url.path != "/generate":
            return True

        body = await request.body()

        try:
            body_data = body.decode()
            request_body = GeneratePostRequestBody.model_validate_json(body_data)

            # First check if the signature is valid
            if not is_eth_signature_valid(
                auth_message(request_body.address),
                request_body.signature,
                request_body.address,
            ):
                return JSONResponse(
                    status_code=HTTPStatus.FORBIDDEN,
                    content={"detail": "Signature doesn't match the given address"},
                )

            # Then check if the address is in the allowed_callers ENS record
            allowed_callers = get_ens_text_record(self.ens_name, "allowed_callers")

            # If ENS record is not set or empty, deny access
            if not allowed_callers:
                return JSONResponse(
                    status_code=HTTPStatus.FORBIDDEN,
                    content={"detail": "ENS allowed_callers record not found or empty"},
                )

            # Check if the request address is in the allowed callers list
            # The allowed_callers field should contain comma-separated addresses
            allowed_addresses = [
                addr.strip().lower() for addr in allowed_callers.split(",")
            ]

            if request_body.address.lower() not in allowed_addresses:
                return JSONResponse(
                    status_code=HTTPStatus.FORBIDDEN,
                    content={"detail": "Address not in allowed_callers list"},
                )

        except Exception:
            return JSONResponse(
                status_code=HTTPStatus.BAD_REQUEST,
                content={"detail": "Invalid request body format"},
            )

        return True


def add_elara_middleware(app: FastAPI, ens_name: str) -> ElaraMiddleware:
    """
    Add Elara middleware to a FastAPI application

    Args:
        app: FastAPI application instance
        ens_name: ENS subdomain to use for validation (e.g., "test" for "test.elara-app.eth")

    Returns:
        ElaraMiddleware instance for further configuration
    """
    middleware = ElaraMiddleware(app, ens_name)
    app.add_middleware(ElaraMiddleware, ens_name=ens_name)
    return middleware
