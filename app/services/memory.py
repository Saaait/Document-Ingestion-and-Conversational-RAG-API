import json
import redis
from app.config import settings
from typing import List, Dict

class RedisMemory:
    """
    Redis-based chat history management.
    """
    def __init__(self) -> None:
        """Initialize Redis client using settings.REDIS_URL."""
        self.client = redis.from_url(settings.REDIS_URL, decode_responses=True)

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        """
        Retrieve JSON list from chat:{session_id}.
        Returns empty list if not found.
        """
        key = f"chat:{session_id}"
        data = self.client.get(key)
        if data:
            return json.loads(data)
        return []

    def add_message(self, session_id: str, role: str, content: str) -> None:
        """
        Append message to history and save back to Redis.
        """
        key = f"chat:{session_id}"
        history = self.get_history(session_id)
        history.append({"role": role, "content": content})
        self.client.set(key, json.dumps(history))

    def clear_history(self, session_id: str) -> None:
        """
        Delete the chat history key for the given session.
        """
        key = f"chat:{session_id}"
        self.client.delete(key)

# Singleton instance at module level
redis_memory = RedisMemory()
