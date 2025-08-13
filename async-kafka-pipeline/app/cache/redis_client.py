# app/cache/redis_client.py
import redis.asyncio as redis
import json
from typing import Optional, Any, Set
from datetime import timedelta
import hashlib
from app.common.logging import get_logger

logger = get_logger(__name__)

class RedisCache:
    def __init__(self, url: str = "redis://localhost:6379"):
        self.url = url
        self.client: Optional[redis.Redis] = None
        
    async def connect(self):
        """Connect to Redis"""
        self.client = redis.from_url(
            self.url,
            encoding="utf-8",
            decode_responses=True
        )
        await self.client.ping()
        logger.info("redis_connected", url=self.url)
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.client:
            await self.client.close()
            logger.info("redis_disconnected")
    
    # Cache operations
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        value = await self.client.get(key)
        if value:
            return json.loads(value)
        return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = 3600
    ):
        """Set value in cache with TTL"""
        await self.client.set(
            key,
            json.dumps(value),
            ex=ttl
        )
    
    # Deduplication using Bloom filter (simplified)
    async def is_duplicate(
        self,
        event_id: str,
        window_seconds: int = 3600
    ) -> bool:
        """Check if event was recently processed"""
        key = f"dedup:{event_id}"
        
        # Try to set with NX (only if not exists)
        result = await self.client.set(
            key,
            "1",
            ex=window_seconds,
            nx=True
        )
        
        # If result is None, key already existed (duplicate)
        return result is None
    
    # Sliding window rate limiting
    async def check_rate_limit(
        self,
        user_id: str,
        limit: int = 100,
        window_seconds: int = 3600
    ) -> bool:
        """Check if user exceeded rate limit"""
        key = f"rate:{user_id}"
        now = int(datetime.now().timestamp())
        window_start = now - window_seconds
        
        pipe = self.client.pipeline()
        
        # Remove old entries
        pipe.zremrangebyscore(key, 0, window_start)
        
        # Count current entries
        pipe.zcard(key)
        
        # Add current request
        pipe.zadd(key, {str(now): now})
        
        # Set expiry
        pipe.expire(key, window_seconds)
        
        results = await pipe.execute()
        count = results[1]
        
        return count < limit
    
    # Order state caching
    async def cache_order_state(
        self,
        order_id: str,
        state: dict,
        ttl: int = 300
    ):
        """Cache order state for fast lookups"""
        key = f"order:{order_id}"
        await self.set(key, state, ttl)
    
    async def get_order_state(self, order_id: str) -> Optional[dict]:
        """Get cached order state"""
        key = f"order:{order_id}"
        return await self.get(key)

# Global instance
redis_cache = RedisCache()