from pydantic import BaseModel, Field

class IngestionRequestResponse(BaseModel):
    """
    Response model for the ingestion request operation.
    """
    job_id: str = Field(..., description="The id of the ingestion job.")