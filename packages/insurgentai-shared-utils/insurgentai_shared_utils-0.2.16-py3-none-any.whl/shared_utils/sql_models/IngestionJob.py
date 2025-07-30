from uuid import UUID
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy.dialects.postgresql import JSONB

class IngestionJob(SQLModel, table=True):
    """
    Represents an ingestion job in the system.
    """
    __tablename__ = "ingestion_jobs"
    job_id: UUID = Field(primary_key=True, description="The unique identifier for the ingestion job.")
    status: str = Field(..., description="The processing status of the ingestion job, e.g., 'uploading', 'processing', 'failed', etc.")
    content: Optional[dict] = Field(default=None, sa_type=JSONB, description="The content of the job if the job is completed successfully. This field is optional and may not be present if the job is still in progress or has failed.")
