import redis.asyncio as redis
import json
from typing import Optional, List, Dict
import hashlib
from app.common.logging import get_logger

logger = get_logger(__name__)

class RedisCache:
    def __init__(self, url: str = 'redis://localhost:6379'):
        self.url = url
        self.client: Optional[redis.Redis] = None

    async def connect(self):
        self.client = await redis.from_url(self.url,
                              encoding="utf-8")
        logger.info("Connected to Redis")