import json
import sys
from pathlib import Path
from typing import List, Tuple
from unittest.mock import patch

import pytest
from fastavro import writer

sys.path.append(str(Path(__file__).resolve().parents[2]))
from tools import replay


def _create_avro(path: Path) -> Tuple[Path, List[dict]]:
    with open(Path("app/producer/schemas/order_event.avsc")) as f:
        schema = json.load(f)
    records = [
        {
            "event_id": "1",
            "order_id": "abc",
            "timestamp": 0,
            "source": "test",
            "event_type": "ORDER_CREATED",
            "payload": "{}",
        },
        {
            "event_id": "2",
            "order_id": "xyz",
            "timestamp": 0,
            "source": "test",
            "event_type": "PAYMENT_AUTHORIZED",
            "payload": "{}",
        },
    ]
    file_path = path / "events.avro"
    with file_path.open("wb") as f:
        writer(f, schema, records)
    return file_path, records


class DummyProducer:
    def __init__(self) -> None:
        self.sent: List[Tuple[str, bytes, bytes]] = []

    async def start(self) -> None:  # pragma: no cover - no logic
        return None

    async def stop(self) -> None:  # pragma: no cover - no logic
        return None

    async def send_and_wait(self, topic: str, value: bytes, key: bytes) -> None:
        self.sent.append((topic, value, key))


@pytest.mark.asyncio
async def test_replay(tmp_path: Path) -> None:
    avro_file, records = _create_avro(tmp_path)
    producer = DummyProducer()
    with patch("tools.replay.AIOKafkaProducer", return_value=producer):
        await replay.replay(str(avro_file), rps=0)

    assert [k for _, _, k in producer.sent] == [r["order_id"].encode() for r in records]
