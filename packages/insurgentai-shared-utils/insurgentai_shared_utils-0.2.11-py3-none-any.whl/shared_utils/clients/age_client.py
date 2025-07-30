import os
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
import psycopg
from psycopg.rows import dict_row
from psycopg import Connection
from .db_client import DBClientBase

class _AGEClient(DBClientBase):
    """AGE client for connecting to a PostgreSQL database with Apache AGE extension.
    Requires environment variables:
    - AGE_USER: The username for the AGE database.
    - AGE_PASSWORD: The password for the AGE database.
    - AGE_HOST: The host of the AGE database (default: localhost).
    - AGE_PORT: The port of the AGE database (default: 5432).
    - AGE_DB: The name of the AGE database.
    - AGE_GRAPH: The name of the AGE graph (default: knowledge_graph).
    """
    def __init__(self):
        user = os.getenv("AGE_USER")
        password = os.getenv("AGE_PASSWORD")
        host = os.getenv("AGE_HOST", "localhost")
        port = os.getenv("AGE_PORT", "5432")
        dbname = os.getenv("AGE_DB")
        self.graph_name = os.getenv("AGE_GRAPH", "knowledge_graph")

        if not all([user, password, dbname]):
            raise EnvironmentError("Missing required AGE environment variables")

        self.connection_params = {
            "host": host,
            "port": port,
            "dbname": dbname,
            "user": user,
            "password": password
        }

    @contextmanager
    def scoped_session(self):
        """Scoped connection with auto commit/rollback/close."""
        conn: Connection = psycopg.connect(**self.connection_params, row_factory=dict_row)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def get_persistent_session(self) -> Connection:
        """Caller is responsible for commit/rollback/close."""
        return psycopg.connect(**self.connection_params, row_factory=dict_row)

    # AGE-specific operations
    def execute_cypher(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict]:
        """Execute a Cypher query and return results."""
        with self.scoped_session() as conn:
            with conn.cursor() as cur:
                # Prepare the AGE query
                age_query = f"SELECT * FROM cypher('{self.graph_name}', $${query}$$) as (result agtype);"
                cur.execute(age_query, params or {})
                return cur.fetchall()

    def execute_cypher_single(self, query: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict]:
        """Execute a Cypher query and return single result."""
        results = self.execute_cypher(query, params)
        return results[0] if results else None

    def create_graph(self) -> bool:
        """Create the AGE graph if it doesn't exist."""
        try:
            with self.scoped_session() as conn:
                with conn.cursor() as cur:
                    cur.execute(f"SELECT create_graph('{self.graph_name}');")
            return True
        except Exception:
            # Graph might already exist
            return False

    def drop_graph(self) -> bool:
        """Drop the AGE graph."""
        try:
            with self.scoped_session() as conn:
                with conn.cursor() as cur:
                    cur.execute(f"SELECT drop_graph('{self.graph_name}', true);")
            return True
        except Exception:
            return False

    def load_age_extension(self) -> bool:
        """Load the AGE extension."""
        try:
            with self.scoped_session() as conn:
                with conn.cursor() as cur:
                    cur.execute("CREATE EXTENSION IF NOT EXISTS age;")
                    cur.execute("LOAD 'age';")
                    cur.execute("SET search_path = ag_catalog, '$user', public;")
            return True
        except Exception:
            return False

    # Utility methods
    def create_node(self, label: str, properties: Dict[str, Any]) -> Optional[Dict]:
        """Create a node with given label and properties."""
        props_str = ", ".join([f"{k}: '{v}'" for k, v in properties.items()])
        query = f"CREATE (n:{label} {{{props_str}}}) RETURN n"
        return self.execute_cypher_single(query)

    def create_edge(self, from_node_id: str, to_node_id: str, edge_type: str, 
                   properties: Optional[Dict[str, Any]] = None) -> Optional[Dict]:
        """Create an edge between two nodes."""
        props_str = ""
        if properties:
            props_str = "{" + ", ".join([f"{k}: '{v}'" for k, v in properties.items()]) + "}"
        
        query = f"""
        MATCH (a), (b) 
        WHERE id(a) = {from_node_id} AND id(b) = {to_node_id}
        CREATE (a)-[r:{edge_type} {props_str}]->(b) 
        RETURN r
        """
        return self.execute_cypher_single(query)

    def find_nodes(self, label: Optional[str] = None, 
                  properties: Optional[Dict[str, Any]] = None) -> List[Dict]:
        """Find nodes by label and/or properties."""
        query = "MATCH (n"
        if label:
            query += f":{label}"
        query += ")"
        
        if properties:
            where_clauses = [f"n.{k} = '{v}'" for k, v in properties.items()]
            query += " WHERE " + " AND ".join(where_clauses)
        
        query += " RETURN n"
        return self.execute_cypher(query)

age_client = _AGEClient()  # module level singleton instance
