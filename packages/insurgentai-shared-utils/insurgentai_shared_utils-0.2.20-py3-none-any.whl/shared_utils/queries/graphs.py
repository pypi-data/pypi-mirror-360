from typing import Optional
from uuid import UUID
from sqlmodel import Session, select
from shared_utils.sql_models import Graph

def insert_graph(session: Session, graph: Graph) -> None:
    """
    Inserts a new graph into the database.

    Args:
        session (Session): The session to use for the insert operation.
        graph (Graph): The graph object to insert.

    Returns:
        None
    """
    session.add(graph)
    session.commit()

def get_graph(session: Session, graph_id: UUID) -> Optional[Graph]:
    """
    Retrieves a graph by its ID.

    Args:
        session (Session): The session to use for the query.
        graph_id (UUID): The ID of the graph to retrieve.

    Returns:
        Optional[Graph]: The graph data if found, otherwise None.
    """
    statement = select(Graph).where(Graph.graph_id == graph_id)
    result = session.exec(statement).first()
    return result if result else None