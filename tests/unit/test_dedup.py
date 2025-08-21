import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[2]))
from app.consumer.dedup import deduplicate


class FakeRedis:
    def __init__(self) -> None:
        self.filter = set()
        self.expire_called_with: int | None = None

    async def execute_command(self, command: str, key: str, value: str) -> int:
        if command == "BF.EXISTS":
            return 1 if value in self.filter else 0
        if command == "BF.ADD":
            already = value in self.filter
            self.filter.add(value)
            return int(already)
        raise NotImplementedError(command)

    async def expire(self, key: str, ttl: int) -> bool:
        self.expire_called_with = ttl
        return True


@pytest.mark.asyncio
async def test_deduplicate_detects_duplicates(monkeypatch):
    fake = FakeRedis()

    async def fake_get_client():
        return fake

    monkeypatch.setattr("app.consumer.dedup.get_client", fake_get_client)
    monkeypatch.setenv("DEDUP_BLOOM_ENABLED", "true")

    assert await deduplicate("event-1") is False
    assert await deduplicate("event-1") is True
    assert fake.expire_called_with == 3600


@pytest.mark.asyncio
async def test_deduplicate_disabled(monkeypatch):
    async def fake_get_client():
        raise AssertionError("Redis should not be called when dedup disabled")

    monkeypatch.setattr("app.consumer.dedup.get_client", fake_get_client)
    monkeypatch.setenv("DEDUP_BLOOM_ENABLED", "false")

    assert await deduplicate("event-1") is False
    assert await deduplicate("event-1") is False
