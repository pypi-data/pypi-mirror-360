from abc import ABC, abstractmethod
from typing import Any, ContextManager

class DBClientBase(ABC):
    """Abstract base class for database clients."""

    @abstractmethod
    def __init__(self) -> None:
        """Initialize the database client with connection parameters."""

    @abstractmethod
    def scoped_session(self) -> ContextManager[Any]:
        """Context manager for scoped database operations with auto commit/rollback/close."""

    @abstractmethod
    def get_persistent_session(self) -> Any:
        """Get a persistent session/connection that caller must manage."""
