from uuid import UUID
from sqlmodel import Session, select
from shared_utils.sql_models import IngestionJob

def insert_ingestion_job(session: Session, ingestion_job: IngestionJob) -> None:
    """
    Inserts a new ingestion job into the database.

    Args:
        session (Session): The session to use for the insert operation.
        ingestion_job (IngestionJob): The ingestion job object to insert.

    Returns:
        None
    """
    session.add(ingestion_job)
    session.commit()

def get_ingestion_job(session: Session, job_id: UUID) -> IngestionJob:
    """
    Retrieves an ingestion job by its ID.

    Args:
        session (Session): The session to use for the query.
        job_id (UUID): The ID of the ingestion job to retrieve.

    Returns:
        IngestionJob: The ingestion job if found, otherwise None.
    """
    statement = select(IngestionJob).where(IngestionJob.job_id == job_id)
    result = session.exec(statement).first()
    return result if result else None

def update_ingestion_job_status(session: Session, job_id: UUID, status: str) -> None:
    """
    Updates the status of an ingestion job.

    Args:
        session (Session): The session to use for the update operation.
        job_id (UUID): The ID of the ingestion job to update.
        status (str): The new status to set for the ingestion job.

    Returns:
        None
    """
    statement = select(IngestionJob).where(IngestionJob.job_id == job_id)
    ingestion_job = session.exec(statement).first()
    
    if ingestion_job:
        ingestion_job.status = status
        session.commit()
    else:
        raise ValueError(f"Ingestion job with ID {job_id} not found.")
    
def update_ingestion_job_content(session: Session, job_id: UUID, content: dict) -> None:
    """
    Updates the content of an ingestion job.

    Args:
        session (Session): The session to use for the update operation.
        job_id (UUID): The ID of the ingestion job to update.
        content (dict): The new content to set for the ingestion job.

    Returns:
        None
    """
    statement = select(IngestionJob).where(IngestionJob.job_id == job_id)
    ingestion_job = session.exec(statement).first()
    
    if ingestion_job:
        ingestion_job.content = content
        session.commit()
    else:
        raise ValueError(f"Ingestion job with ID {job_id} not found.")