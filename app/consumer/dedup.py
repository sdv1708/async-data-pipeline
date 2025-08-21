import os

from app.cache.redis_client import get_client

BLOOM_KEY = "dedup:bloom"
BLOOM_TTL_SECONDS = int(os.getenv("DEDUP_BLOOM_TTL_SECONDS", "3600"))

async def deduplicate(event_id: str) -> bool:
    """Return True if the event has been seen before."""
    if os.getenv("DEDUP_BLOOM_ENABLED", "true").lower() != "true":
        return False

    client = await get_client()
    exists = await client.execute_command("BF.EXISTS", BLOOM_KEY, event_id)
    if exists:
        return True

    await client.execute_command("BF.ADD", BLOOM_KEY, event_id)
    await client.expire(BLOOM_KEY, BLOOM_TTL_SECONDS)
    return False
