import os

import redis.asyncio as redis

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
client = redis.from_url(REDIS_URL)

async def get_client() -> redis.Redis:
    return client
