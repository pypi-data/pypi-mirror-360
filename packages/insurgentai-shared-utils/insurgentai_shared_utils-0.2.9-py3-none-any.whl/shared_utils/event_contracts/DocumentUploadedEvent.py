from pydantic import BaseModel, Field

class DocumentUploadedEvent(BaseModel):
    """
    Event triggered when a document is uploaded.
    """
    document_id: str = Field(..., description="The id of the uploaded document.")