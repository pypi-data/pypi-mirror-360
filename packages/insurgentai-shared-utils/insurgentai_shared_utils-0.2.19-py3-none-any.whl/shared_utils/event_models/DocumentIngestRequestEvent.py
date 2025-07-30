from uuid import UUID
from pydantic import BaseModel, Field

class DocumentIngestRequestEvent(BaseModel):
    """
    Event contract for requesting the ingestion of a document.
    This event is used to initiate the process of ingesting a document into the system.
    """
    job_id: UUID = Field(..., description="Unique identifier for the job associated with the document ingestion")
    document_id: str = Field(..., description="Unique identifier for the document to be ingested")