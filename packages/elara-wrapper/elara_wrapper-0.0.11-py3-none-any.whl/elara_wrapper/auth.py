from fastapi import APIRouter

from elara_wrapper.interfaces import AuthMessageRequest, AuthMessageResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


def auth_message(address: str) -> str:
    return f"Sign with your wallet {address.lower()} to access the Elara agent."


@router.post("/message")
async def get_auth_message(request: AuthMessageRequest) -> AuthMessageResponse:
    """Get the static message for wallet signature authentication."""

    return AuthMessageResponse(message=auth_message(request.address))
