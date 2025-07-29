from libertai_agents.interfaces.messages import Message
from pydantic import BaseModel, field_validator
from web3 import Web3


class GeneratePostRequestBody(BaseModel):
    """
    Request body for a generation request
    """

    messages: list[Message]
    address: str
    signature: str

    @field_validator("address")
    def validate_eth_address(cls, value):
        return Web3.to_checksum_address(value)


class AuthMessageRequest(BaseModel):
    address: str

    @field_validator("address")
    def validate_eth_address(cls, value):
        return Web3.to_checksum_address(value)


class AuthMessageResponse(BaseModel):
    message: str
