from pydantic import BaseModel, Field

class IngestionJobStatusResponse(BaseModel):
    """
    Response model for the status of an ingestion job.
    """
    status: str = Field(..., description="The current status of the ingestion job (e.g., 'pending', 'in_progress', 'completed', 'failed').")
    # optional content in case job is completed:
    content: dict = Field(default=None, description="The content of the document if the job is completed successfully. This field is optional and may not be present if the job is still in progress or has failed.")