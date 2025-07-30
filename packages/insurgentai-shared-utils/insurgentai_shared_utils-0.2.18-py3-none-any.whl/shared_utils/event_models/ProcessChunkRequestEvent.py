from uuid import UUID
from pydantic import BaseModel, Field

class ProcessChunkRequestEvent(BaseModel):
    """
    Event triggered when a document chunk needs to be processed.
    """
    job_id: UUID = Field(..., description="Unique identifier for the job associated with the document ingestion")
    chunk_id: str = Field(..., description="Unique identifier for the chunk.")
    document_id: str = Field(..., description="The id of the document associated with the chunk.")
    text: str = Field(..., description="The text content of the chunk.")