from .mock_client import MockClient, create_mock_client
mock_client = create_mock_client()

from .db_client import DBClient, create_db_client
from .redis_client import RedisClient, create_redis_client
from .s3_client import S3Client, create_s3_client
from .age_client import AGEClient, create_age_client

_factories = {
    "db_client": create_db_client,
    "redis_client": create_redis_client,
    "s3_client": create_s3_client,
    "age_client": create_age_client,
}

_instances = {}

def __getattr__(name: str):
    if name in _factories:
        if name not in _instances:
            _instances[name] = _factories[name]()
        return _instances[name]
    raise AttributeError(f"module {__name__} has no attribute {name}")
