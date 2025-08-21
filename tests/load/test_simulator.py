import asyncio
import os
import sys
import uuid
from pathlib import Path

import pytest
from aiokafka import AIOKafkaConsumer
from testcontainers.kafka import KafkaContainer

sys.path.append(str(Path(__file__).resolve().parents[2] / "tools"))
import simulator


@pytest.fixture(scope="module")
def kafka_bootstrap() -> str:
    with KafkaContainer() as kafka:
        server = kafka.get_bootstrap_server()
        os.environ["KAFKA_BOOTSTRAP_SERVERS"] = server
        yield server


async def consume_one(bootstrap: str, group_id: str) -> None:
    consumer = AIOKafkaConsumer(
        os.getenv("KAFKA_TOPIC_ORDERS", "orders.raw"),
        bootstrap_servers=bootstrap,
        group_id=group_id,
        auto_offset_reset="earliest",
    )
    await consumer.start()
    try:
        msg = await asyncio.wait_for(consumer.getone(), timeout=10)
        assert msg is not None
    finally:
        await consumer.stop()


@pytest.mark.asyncio
@pytest.mark.parametrize("rps", [1, 5])
async def test_load_simulator(kafka_bootstrap: str, rps: int) -> None:
    await simulator.produce(rps, 1)
    await consume_one(kafka_bootstrap, f"load-{rps}-{uuid.uuid4()}")
