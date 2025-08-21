import hashlib
import json
import logging
import logging.config
from typing import Any, Dict, Optional

import yaml
from fastapi import FastAPI, HTTPException
from sqlmodel import select

from app.cache.redis_client import get_client
from app.db import OrderEvent, async_session

# Load logging configuration
with open("configs/logging.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)
logging.config.dictConfig(config)
logger = logging.getLogger("app.read_api")

app = FastAPI(title="Order Read API")


class BloomFilter:
    """Simple in-memory Bloom filter for dedup hints."""

    def __init__(self, size: int = 1024, hash_count: int = 3) -> None:
        self.size = size
        self.hash_count = hash_count
        self.bits = bytearray(size)

    def _hashes(self, item: str):
        for i in range(self.hash_count):
            digest = hashlib.sha256(f"{item}:{i}".encode()).hexdigest()
            yield int(digest, 16) % self.size

    def add(self, item: str) -> None:
        for idx in self._hashes(item):
            self.bits[idx] = 1

    def __contains__(self, item: str) -> bool:
        return all(self.bits[idx] for idx in self._hashes(item))


bloom_filter = BloomFilter()


async def _db_lookup(order_id: str) -> Optional[Dict[str, Any]]:
    """Query the database for the latest order state."""
    try:
        async with async_session() as session:
            result = await session.execute(
                select(OrderEvent)
                .where(OrderEvent.order_id == order_id)
                .order_by(OrderEvent.id.desc())
                .limit(1)
            )
            event = result.scalar_one_or_none()
            if event is None:
                return None
            return json.loads(event.payload)
    except Exception as exc:  # pragma: no cover - DB errors shouldn't fail API
        logger.error("db_error", error=str(exc))
        return None


async def _fetch_order_state(order_id: str) -> Dict[str, Any]:
    """Fetch order state, using cache with TTL of 30 seconds."""
    cache_key = f"order:{order_id}"
    redis = await get_client()

    # Bloom filter check for dedup hints
    if order_id in bloom_filter:
        logger.info("dedup_hint", order_id=order_id)
    else:
        bloom_filter.add(order_id)

    try:
        cached = await redis.get(cache_key)
    except Exception as exc:  # pragma: no cover - cache errors shouldn't fail API
        logger.warning("cache_error", error=str(exc))
        cached = None
    if cached:
        return json.loads(cached)

    state = await _db_lookup(order_id)
    if state is None:
        raise HTTPException(status_code=404, detail="order state not found")

    try:
        await redis.set(cache_key, json.dumps(state), ex=30)
    except Exception as exc:  # pragma: no cover - cache errors shouldn't fail API
        logger.warning("cache_error", error=str(exc))
    return state


@app.get("/orders/{order_id}")
async def get_order(order_id: str) -> Dict[str, Any]:
    """Return full order state."""
    return await _fetch_order_state(order_id)


@app.get("/orders/{order_id}/status")
async def get_order_status(order_id: str) -> Dict[str, Any]:
    """Return only the status field of the order state."""
    state = await _fetch_order_state(order_id)
    return {"order_id": order_id, "status": state.get("status")}
