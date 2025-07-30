from typing import TypeVar, TYPE_CHECKING, Any, Callable, Dict

# Import the client classes themselves for type hinting
from .mock_client import MockClient
from .db_client import DBClient
from .redis_client import RedisClient
from .s3_client import S3Client
from .age_client import AGEClient

# Import the create functions (factories)
from .mock_client import create_mock_client
from .db_client import create_db_client
from .redis_client import create_redis_client
from .s3_client import create_s3_client
from .age_client import create_age_client

# Define a TypeVar for the client types for generic typing in the proxy
_ClientType = TypeVar('_ClientType')

class _ClientProxy:
    """
    A descriptor that acts as a proxy for lazy-loaded client instances.
    """
    def __init__(self, factory_func: Callable[[], _ClientType], client_name: str):
        self._factory_func = factory_func
        self._instance: _ClientType | None = None
        self._client_name = client_name # Store name for potential debugging

    def __get__(self, instance: Any, owner: Any) -> _ClientType:
        # 'instance' is the module (None for module attributes)
        # 'owner' is the module class (type(shared_utils.clients))
        if self._instance is None:
            # print(f"Initializing {self._client_name} client...") # For debugging
            self._instance = self._factory_func()
        return self._instance

    # ensure the proxy itself doesn't show up in dir() or introspections
    def __set_name__(self, owner: Any, name: str) -> None:
        self._client_name = name


# Dictionary to map client names to their creation factories
_client_factories: Dict[str, Callable[[], Any]] = {
    "mock_client": create_mock_client,
    "db_client": create_db_client,
    "redis_client": create_redis_client,
    "s3_client": create_s3_client,
    "age_client": create_age_client,
}

if TYPE_CHECKING:
    # During type checking, we can just define these as the client types directly.
    # This helps IDEs and static analysis, while the runtime uses the proxy.
    db_client: DBClient
    redis_client: RedisClient
    s3_client: S3Client
    age_client: AGEClient
    mock_client: MockClient
else:
    # At runtime, we define them as _ClientProxy instances
    db_client = _ClientProxy(_client_factories["db_client"], "db_client")
    redis_client = _ClientProxy(_client_factories["redis_client"], "redis_client")
    s3_client = _ClientProxy(_client_factories["s3_client"], "s3_client")
    age_client = _ClientProxy(_client_factories["age_client"], "age_client")
    mock_client = _ClientProxy(_client_factories["mock_client"], "mock_client")

# Define __all__ for import * (good practice)
__all__ = [
    "db_client",
    "redis_client",
    "s3_client",
    "age_client",
    "mock_client",
    # expose the client classes themselves
    "DBClient",
    "RedisClient",
    "S3Client",
    "AGEClient",
    "MockClient",
]