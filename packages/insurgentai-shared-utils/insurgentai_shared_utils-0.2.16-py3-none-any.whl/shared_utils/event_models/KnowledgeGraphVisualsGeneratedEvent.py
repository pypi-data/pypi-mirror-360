from uuid import UUID
from pydantic import BaseModel, Field

class KnowledgeGraphVisualsGeneratedEvent(BaseModel):
    """
    Event triggered when the knowledge graph visuals are generated.
    This event is used to notify that the visuals for the knowledge graph have been successfully created.
    """
    job_id: UUID = Field(..., description="Unique identifier for the job associated with the document ingestion")