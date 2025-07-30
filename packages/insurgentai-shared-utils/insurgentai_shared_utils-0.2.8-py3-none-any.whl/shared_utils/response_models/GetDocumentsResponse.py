from uuid import UUID
from pydantic import BaseModel, Field

class GetDocumentsResponse(BaseModel):
    """
    Response model for getting all documents operation.
    """
    document_ids: list[UUID] = Field(..., description="List of document IDs retrieved from the database.")