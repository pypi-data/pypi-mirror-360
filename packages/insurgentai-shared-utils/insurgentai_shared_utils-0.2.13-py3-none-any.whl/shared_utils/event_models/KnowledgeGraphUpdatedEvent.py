from uuid import UUID
from pydantic import BaseModel, Field

class KnowledgeGraphUpdatedEvent(BaseModel):
    """
    Event triggered when the knowledge graph is updated.
    """
    job_id: UUID = Field(..., description="Unique identifier for the job associated with the document ingestion")
