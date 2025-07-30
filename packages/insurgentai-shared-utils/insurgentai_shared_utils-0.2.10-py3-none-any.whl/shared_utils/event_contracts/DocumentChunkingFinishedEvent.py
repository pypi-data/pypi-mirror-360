from pydantic import BaseModel, Field

class DocumentChunkingFinishedEvent(BaseModel):
    """
    Event triggered when the chunking of a document is finished.
    """
    document_id: str = Field(..., description="The id of the document associated with the chunking process.")