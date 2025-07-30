from uuid import UUID
from sqlmodel import SQLModel, Field

class DocumentMetadata(SQLModel, table=True):
    """
    Represents a document in the system.
    """
    __tablename__ = "documentmetadata"
    document_id: UUID = Field(primary_key=True, description="The unique identifier for the document.")
    s3_key : str = Field(..., description="The S3 key where the document is stored.")
    status : str = Field(..., description="The processing status of the document, e.g., 'pending', 'processed', 'failed'.")