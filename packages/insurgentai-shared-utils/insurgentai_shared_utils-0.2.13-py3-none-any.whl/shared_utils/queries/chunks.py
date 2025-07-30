from typing import Optional
from uuid import UUID
from sqlmodel import Session, select
from shared_utils.sql_models.Chunk import Chunk

def insert_chunk(session:Session, chunk: Chunk) -> None:
    """
    Inserts a new chunk into the database.
    
    Args:
        session (Session): The session to use for the insert operation.
        chunk (Chunk): The chunk object to insert.

    Returns:
        None
    """
    session.add(chunk)
    session.commit()

def insert_chunks(session: Session, chunks: list[Chunk]) -> None:
    """
    Inserts multiple chunks into the database.
    
    Args:
        session (Session): The session to use for the insert operation.
        chunks (list[Chunk]): A list of chunk objects to insert.

    Returns:
        None
    """
    session.add_all(chunks)
    session.commit()

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

def update_chunk_graph_id(session: Session, chunk_id: UUID, graph_id: UUID) -> None:
    """
    Updates the graph ID of a chunk.
    
    Args:
        session (Session): The session to use for the update operation.
        chunk_id (UUID): The ID of the chunk to update.
        graph_id (UUID): The new graph ID to set.

    Returns:
        None
    """
    statement = select(Chunk).where(Chunk.chunk_id == chunk_id)
    chunk = session.exec(statement).first()
    if chunk:
        chunk.graph_id = graph_id
        session.add(chunk)
        session.commit()