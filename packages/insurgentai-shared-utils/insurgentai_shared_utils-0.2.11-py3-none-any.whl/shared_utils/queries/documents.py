from typing import Optional
from uuid import UUID
from sqlmodel import Session, select
from shared_utils.sql_models import DocumentMetadata

def insert_document(session: Session, document_metadata: DocumentMetadata) -> None:
    """
    Inserts a new document metadata entry into the database.

    Args:
        session (Session): The session to use for the insert operation.
        document_metadata (DocumentMetadata): The document metadata object to insert.

    Returns:
        None
    """
    session.add(document_metadata)
    session.commit()

def get_document(session: Session, document_id: str) -> Optional[dict]:
    """
    Retrieves a document by its ID.

    Args:
        session (Session): The session to use for the query.
        document_id (str): The ID of the document to retrieve.

    Returns:
        Optional[dict]: The document metadata if found, otherwise None.
    """
    statement = select(DocumentMetadata).where(DocumentMetadata.document_id == UUID(document_id))
    result = session.exec(statement).first()
    return result if result else None

def update_document_status(session: Session, document_id: str, status: str) -> None:
    """
    Updates the status of a document.

    Args:
        session (Session): The session to use for the update operation.
        document_id (str): The ID of the document to update.
        status (str): The new status to set for the document.

    Returns:
        None
    """
    statement = select(DocumentMetadata).where(DocumentMetadata.document_id == UUID(document_id))
    document = session.exec(statement).first()
    
    if document:
        document.status = status
        session.commit()
    else:
        raise ValueError(f"Document with ID {document_id} not found.")