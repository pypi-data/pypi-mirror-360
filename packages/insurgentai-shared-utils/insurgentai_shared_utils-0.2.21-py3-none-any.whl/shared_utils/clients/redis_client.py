import os
import json
import redis
import threading
from typing import Optional, Union, Any

class RedisClient:
    def __init__(self):
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self._client = redis.from_url(redis_url)
        self._consumers = {}
        self._callbacks = {}
        self._stop_flags = {}

    def send(self, stream: str, value: dict):
        # Serialize entire dict as single JSON string under 'data' field
        message = {"data": json.dumps(value)}
        self._client.xadd(stream, message)

    def flush(self):
        # No flush needed for Redis Streams
        pass

    # Key-Value Operations
    def get(self, key: str) -> Optional[str]:
        """Get a value from Redis by key."""
        value = self._client.get(key)
        return value.decode('utf-8') if value else None

    def set(self, key: str, value: Union[str, int, float], ex: Optional[int] = None) -> bool:
        """Set a key-value pair in Redis with optional expiration."""
        try:
            return self._client.set(key, str(value), ex=ex)
        except Exception:
            return False

    def get_json(self, key: str) -> Optional[Any]:
        """Get a JSON value from Redis by key and deserialize it."""
        value = self.get(key)
        if value is None:
            return None
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return None

    def set_json(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """Set a JSON-serializable value in Redis."""
        try:
            json_str = json.dumps(value)
            return self.set(key, json_str, ex=ex)
        except (TypeError, ValueError):
            return False

    def increment(self, key: str, amount: int = 1) -> int:
        """Increment a numeric value in Redis."""
        return self._client.incrby(key, amount)

    def decrement(self, key: str, amount: int = 1) -> int:
        """Decrement a numeric value in Redis."""
        return self._client.decrby(key, amount)

    def delete(self, *keys: str) -> int:
        """Delete one or more keys from Redis."""
        return self._client.delete(*keys)

    def exists(self, key: str) -> bool:
        """Check if a key exists in Redis."""
        return bool(self._client.exists(key))

    def expire(self, key: str, seconds: int) -> bool:
        """Set an expiration time for a key."""
        return bool(self._client.expire(key, seconds))

    def ttl(self, key: str) -> int:
        """Get the time-to-live of a key in seconds."""
        return self._client.ttl(key)

    def register_callback(self, stream: str, group_id: str, callback):
        if stream in self._consumers:
            self._callbacks[stream].append(callback)
            return

        try:
            self._client.xgroup_create(stream, group_id, id='0', mkstream=True)
        except redis.exceptions.ResponseError as e:
            if "BUSYGROUP" not in str(e):
                raise

        self._callbacks[stream] = [callback]
        self._stop_flags[stream] = False

        def consume_loop():
            consumer_name = f"{group_id}-consumer"
            while not self._stop_flags[stream]:
                resp = self._client.xreadgroup(
                    groupname=group_id,
                    consumername=consumer_name,
                    streams={stream: '>'},
                    count=10,
                    block=1000
                )
                if not resp:
                    continue
                for _, messages in resp:
                    for msg_id, fields in messages:
                        data_json = fields.get(b'data') or fields.get('data')
                        if data_json:
                            try:
                                val = json.loads(data_json)
                            except Exception:
                                val = None
                        else:
                            val = None
                        for cb in self._callbacks[stream]:
                            cb(msg_id, val)
                        self._client.xack(stream, group_id, msg_id)

        t = threading.Thread(target=consume_loop, daemon=True)
        t.start()
        self._consumers[stream] = t

    def stop_consumer(self, stream: str):
        if stream in self._stop_flags:
            self._stop_flags[stream] = True
            self._consumers[stream].join()
            del self._consumers[stream]
            del self._callbacks[stream]
            del self._stop_flags[stream]

redis_client = RedisClient()  # module level singleton instance