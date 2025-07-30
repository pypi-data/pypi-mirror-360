from pydantic import BaseModel, Field

class DocumentIngestionFinalizedEvent(BaseModel):
    """
    Event triggered when the ingestion of a document is finalized.
    This event indicates that all processing related to the document has been completed.
    """
    document_id: str = Field(..., description="The id of the document that has been ingested.")