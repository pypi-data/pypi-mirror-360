
from uuid import UUID
from sqlmodel import Session
from sqlalchemy import select
from shared_utils.sql_models import Layout

def get_layout(session: Session, graph_id: UUID, layout_name: str) -> Layout:
    """
    Retrieves a specific layout by graph ID and layout name.

    Args:
        session (Session): The session to use for the query.
        graph_id (UUID): The ID of the graph to retrieve the layout for.
        layout_name (str): The name of the layout to retrieve.

    Returns:
        Layout: The layout object if found, otherwise None.
    """
    statement = select(Layout).where(
        Layout.graph_id == graph_id,
        Layout.layout_name == layout_name
    )
    result = session.exec(statement).first()
    return result if result else None

def get_layouts(session: Session, graph_id: UUID) -> list[Layout]:
    """
    Retrieves all layouts for a specific graph.

    Args:
        session (Session): The session to use for the query.
        graph_id (UUID): The ID of the graph to retrieve layouts for.

    Returns:
        list[Layout]: A list of layouts for the specified graph.
    """
    statement = select(Layout).where(Layout.graph_id == graph_id)
    results = session.exec(statement).all()
    return results if results else []

def insert_layout(session: Session, layout: Layout) -> None:
    """
    Inserts a new layout into the database.

    Args:
        session (Session): The session to use for the insert operation.
        layout (Layout): The layout object to insert.

    Returns:
        None
    """
    session.add(layout)
    session.commit()
