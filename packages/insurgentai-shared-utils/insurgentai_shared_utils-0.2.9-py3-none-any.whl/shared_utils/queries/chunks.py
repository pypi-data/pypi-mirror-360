from typing import Optional
from uuid import UUID
from sqlmodel import Session, select
from shared_utils.sql_models.Chunk import Chunk

def get_chunk(session: Session, chunk_id: UUID) -> Optional[Chunk]:
    """
    Retrieves a chunk by its ID.
    
    Args:
        session (Session): The session to use for the query.
        chunk_id (UUID): The ID of the chunk to retrieve.

    Returns:
        Optional[Chunk]: The chunk data if found, otherwise None.
    """
    statement = select(Chunk).where(Chunk.chunk_id == chunk_id)
    result = session.exec(statement).first()
    return result
