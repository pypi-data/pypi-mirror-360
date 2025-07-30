import redis
from typing import Dict, Any, Callable
import threading
import time
class Redis:
    def __init__(self, tool_config: Dict[str, Any]):
        self.tool_config = tool_config
        self.host = tool_config.get("host", "localhost")
        self.port = tool_config.get("port", 6379)
        self.db = tool_config.get("db", 0)
        self.password = tool_config.get("password")  # optional

        self.config = {
            "host": self.host,
            "port": self.port,
            "db": self.db
        }
        if self.password:
            self.config["password"] = self.password

        self.redis = None
        self.connect()

    def connect(self):
        try:
            self.redis = redis.StrictRedis(**self.config)
            # test connection
            self.redis.ping()
        except redis.ConnectionError as e:
            raise ConnectionError(f"Failed to connect to Redis: {e}")

    def set(self, key: str, value: Any, cache_ttl: int = 86400) -> bool:
        """
        Sets a key with an optional TTL (in seconds).
        """
        return self.redis.set(key, value, ex=cache_ttl)

    def get(self, key: str) -> Any:
        return self.redis.get(key)

    def delete(self, key: str) -> int:
        return self.redis.delete(key)

    def read(self, query: str) -> Any:
        if query == "dbsize":
            return self.redis.dbsize()
        else:
            raise ValueError(f"Unsupported Redis query: {query}")

    def exists(self, key: str) -> bool:
        return self.redis.exists(key)
    
    def zadd(self, key: str, score: float, value: Any) -> int:
        return self.redis.zadd(key, score, value)
    
    def zrevrange(self, key: str, start: int, end: int, withscores: bool = False) -> list:
        return self.redis.zrevrange(key, start, end, withscores)
    
    def publish(self, channel: str, message: str):
        """
        Publish a message to a Redis channel.
        """
        return self.redis.publish(channel, message)

    def subscribe(self, channel: str, callback: Callable[[str], None]):
        """
        Subscribe to a Redis channel with proper byte decoding.
        """
        pubsub = self.redis.pubsub()
        pubsub.subscribe(channel)

        def listen():
            while True:
                try:
                    message = pubsub.get_message(ignore_subscribe_messages=True, timeout=1)
                    if message and message.get("data"):
                        # Decode bytes to string if needed
                        data = message["data"]
                        if isinstance(data, bytes):
                            data = data.decode('utf-8')
                        
                        print(f"DEBUG: Redis callback sending: {data}")  # Debug line
                        callback(data)
                except Exception as e:
                    print(f"Error in Redis subscribe listener: {e}")
                    
                time.sleep(0.5)  # prevents high CPU spinning

        thread = threading.Thread(target=listen, daemon=True)
        thread.start()
        return thread  # Return thread for potential cleanup

    def get_pubsub(self):
        return self.redis.pubsub()
    
    def unsubscribe(self, channel: str):
        """
        Unsubscribe from a Redis channel.
        """
        self.redis.pubsub().unsubscribe(channel)
    
    def get_pubsub_channels(self):
        """
        Get all channels that the Redis pubsub is subscribed to.
        """
        return self.redis.pubsub().channels
    
    
