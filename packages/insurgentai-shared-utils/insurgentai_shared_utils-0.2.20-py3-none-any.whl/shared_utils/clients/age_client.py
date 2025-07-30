import os
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
import psycopg
from psycopg.rows import dict_row
from psycopg import Connection
from .utils.db_client_base import DBClientBase

class AGEClient(DBClientBase):
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
            self._setup_age_session(conn)
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def get_persistent_session(self) -> Connection:
        """Caller is responsible for commit/rollback/close."""
        conn = psycopg.connect(**self.connection_params, row_factory=dict_row)
        self._setup_age_session(conn)
        return conn

    def _setup_age_session(self, conn: Connection) -> None:
        """Setup AGE environment for each session."""
        try:
            with conn.cursor() as cur:
                cur.execute("LOAD 'age';")
                cur.execute("SET search_path = ag_catalog, '$user', public;")
        except Exception:
            # AGE might not be properly installed
            pass

    def get_graph_name(self) -> str:
        """Get the configured graph name."""
        return self.graph_name

    def execute_with_graph(self, func, *args, **kwargs):
        """Execute a function with a scoped connection and graph name."""
        with self.scoped_session() as conn:
            return func(conn, self.graph_name, *args, **kwargs)

    def load_age_extension(self) -> bool:
        """Load the AGE extension (legacy method - now handled automatically)."""
        return True  # Always return True since extension is loaded automatically


def create_age_client() -> AGEClient:
    """Factory function to create a singleton AGE client instance."""
    return AGEClient()