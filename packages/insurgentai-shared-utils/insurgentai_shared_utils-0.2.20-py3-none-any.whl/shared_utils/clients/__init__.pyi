from .age_client import AGEClient
from .db_client import DBClient
from .redis_client import RedisClient
from .s3_client import S3Client
from .mock_client import MockClient

# These type hints are essential for IDEs and type checkers
age_client: AGEClient
db_client: DBClient
redis_client: RedisClient
s3_client: S3Client
mock_client: MockClient

__all__ = [
    "db_client",
    "redis_client",
    "s3_client",
    "age_client",
    "mock_client",
    "DBClient",
    "RedisClient",
    "S3Client",
    "AGEClient",
    "MockClient",
]