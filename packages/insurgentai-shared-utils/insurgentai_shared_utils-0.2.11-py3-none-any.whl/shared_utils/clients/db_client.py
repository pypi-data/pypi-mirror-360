import os
from contextlib import contextmanager
from sqlmodel import Session, create_engine
from .db_client_base import DBClientBase

class _DBClient(DBClientBase):
    """Database client for connecting to a Postgres database.
    Requires environment variables:
    - POSTGRES_USER: The username for the database.
    - POSTGRES_PASSWORD: The password for the database.
    - POSTGRES_HOST: The host of the database (default: localhost).
    - POSTGRES_PORT: The port of the database (default: 5432).
    - POSTGRES_DB: The name of the database.
    """
    def __init__(self):
        user = os.getenv("POSTGRES_USER")
        password = os.getenv("POSTGRES_PASSWORD")
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432")
        dbname = os.getenv("POSTGRES_DB")

        if not all([user, password, dbname]):
            raise EnvironmentError("Missing required Postgres environment variables")

        self.database_url = f"postgresql+psycopg://{user}:{password}@{host}:{port}/{dbname}"
        self.engine = create_engine(self.database_url, echo=False)

    @contextmanager
    def scoped_session(self):
        """Scoped session with auto commit/rollback/close."""
        session = Session(self.engine)
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def get_persistent_session(self) -> Session:
        """Caller is responsible for commit/rollback/close."""
        return Session(self.engine)


db_client = _DBClient() # module level singleton instance
