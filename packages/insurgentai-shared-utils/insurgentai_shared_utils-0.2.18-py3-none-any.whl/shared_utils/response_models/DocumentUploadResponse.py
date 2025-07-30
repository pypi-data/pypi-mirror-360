from pydantic import BaseModel, Field

class DocumentUploadResponse(BaseModel):
    """
    Response model for the document upload operation.
    """
    document_id: str = Field(..., description="The id of the document.")
