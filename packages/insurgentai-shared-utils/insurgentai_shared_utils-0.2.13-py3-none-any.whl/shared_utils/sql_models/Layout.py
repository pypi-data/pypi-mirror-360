from sqlmodel import SQLModel, Field
from sqlalchemy import Column, JSON

class Layout(SQLModel, table=True):
    """Represents a layout for a graph, storing the positions of nodes in a 2D space."""
    
    graph_id: str = Field(primary_key=True)
    layout_name: str = Field(primary_key=True)
    positions: dict[int, tuple[float, float]] = Field(sa_type=Column(JSON))