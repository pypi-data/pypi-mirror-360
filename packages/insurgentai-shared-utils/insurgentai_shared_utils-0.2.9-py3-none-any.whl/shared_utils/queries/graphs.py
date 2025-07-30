from typing import Optional
from sqlmodel import Session, select
from shared_utils.sql_models import Graph


def get_graph(session: Session, graph_id: str) -> Optional[dict]:
    """
    Retrieves a graph by its ID.

    Args:
        session (Session): The session to use for the query.
        graph_id (str): The ID of the graph to retrieve.

    Returns:
        Optional[dict]: The graph data if found, otherwise None.
    """
    statement = select(Graph).where(Graph.graph_id == graph_id)
    result = session.exec(statement).first()
    return result if result else None