from uuid import UUID
from sqlmodel import SQLModel, Field
from sqlalchemy.dialects.postgresql import JSONB

class Layout(SQLModel, table=True):
    """Represents a layout for a graph, storing the positions of nodes in a 2D space."""
    __tablename__ = "layouts"
    graph_id: UUID = Field(primary_key=True, foreign_key="chunk_graphs.graph_id", index=True, description="The unique identifier for the graph this layout belongs to.")
    layout_name: str = Field(primary_key=True)
    positions: dict[int, tuple[float, float]] = Field(sa_type=JSONB)