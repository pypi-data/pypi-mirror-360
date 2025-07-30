from sqlmodel import Session, select
from shared_utils.sql_models import IngestionJob

def get_ingestion_job(session: Session, job_id: str) -> IngestionJob:
    """
    Retrieves an ingestion job by its ID.

    Args:
        session (Session): The session to use for the query.
        job_id (str): The ID of the ingestion job to retrieve.

    Returns:
        IngestionJob: The ingestion job if found, otherwise None.
    """
    statement = select(IngestionJob).where(IngestionJob.job_id == job_id)
    result = session.exec(statement).first()
    return result if result else None

def update_ingestion_job(session: Session, job_id: str, status: str, content: dict = None) -> IngestionJob:
    """
    Updates the status and content of an ingestion job.

    Args:
        session (Session): The session to use for the query.
        job_id (str): The ID of the ingestion job to update.
        status (str): The new status of the ingestion job.
        content (dict, optional): The content of the job if it is completed successfully. Defaults to None.

    Returns:
        IngestionJob: The updated ingestion job.
    """
    job = get_ingestion_job(session, job_id)
    if not job:
        raise ValueError(f"Ingestion job with ID {job_id} not found.")
    
    job.status = status
    job.content = content
    session.add(job)
    session.commit()
    session.refresh(job)
    
    return job