from pydantic import BaseModel, Field

class UserPromptResponse(BaseModel):
    """
    Response model for user prompt operations.
    """
    response: str = Field(..., description="The response generated based on the user's prompt.")
    #TODO: statements
    #TODO: references