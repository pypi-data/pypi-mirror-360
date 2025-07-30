from sqlmodel import SQLModel, Field
from sqlalchemy import Column, JSON
from uuid import UUID

class Graph(SQLModel, table=True):
    """
    Represents a graph in the system for a chunk (1:1)
    """
    graph_id: UUID = Field(primary_key=True, description="The unique identifier for the graph.")
    chunk_id: UUID = Field(foreign_key="chunk.chunk_id", index=True, description="The unique identifier for the chunk associated with the graph.")
    
    entities: list[str] = Field(default_factory=list, sa_column=Column(JSON), description="List of entities in the graph.")
    edges: list[str] = Field(default_factory=list, sa_column=Column(JSON), description="List of edges in the graph.")
    relations: list[tuple[str, str, str]] = Field(default_factory=list, sa_column=Column(JSON), description="List of relations in the graph, represented as tuples of (source_entity, relation_type, target_entity).")
