from pydantic import BaseModel, Field

class DocumentUploadResponse(BaseModel):
    """
    Response model for the document upload operation.
    """
    s3_key: str = Field(..., description="The S3 key where the document is stored.")
