import redis.asyncio as redis
from .settings import settings

class RedisClient:
    _instance = None

    @classmethod
    def get_instance(cls) -> redis.Redis:
        if cls._instance is None:
            cls._instance = redis.Redis(
                host=settings.VALKEY_HOST,
                port=settings.VALKEY_PORT,
                password=settings.VALKEY_PASSWORD,
                decode_responses=False # We handle encoding manually for vectors if needed, but for text search we might want True.
                # Actually, standard RediSearch returns bytes often. Let's keep it False or True?
                # If True, vector bytes might get corrupted if we try to read them as string?
                # Usually for RediSearch we get lists.
                # Let's use decode_responses=True but handle vector bytes carefully if we read them. 
                # Wait, FT.SEARCH input params for vector (blob) need to be bytes.
                # If we use decode_responses=True, passing bytes might be okay?
                # Redis-py allows sending bytes.
                # Let's set decode_responses=False to be safe and decode manually where needed.
            )
        return cls._instance

    @classmethod
    async def close(cls):
        if cls._instance:
            await cls._instance.aclose()
            cls._instance = None
