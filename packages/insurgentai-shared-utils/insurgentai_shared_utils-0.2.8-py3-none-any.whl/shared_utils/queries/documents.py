from typing import Optional
from uuid import UUID
from sqlmodel import Session, select
from shared_utils.sql_models import DocumentMetadata

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