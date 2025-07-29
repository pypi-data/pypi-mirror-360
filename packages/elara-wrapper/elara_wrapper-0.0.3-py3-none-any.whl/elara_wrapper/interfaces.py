from pydantic import BaseModel


class GeneratePostRequestBody(BaseModel):
    """
    Request body for a generation request
    """

    prompt: str
