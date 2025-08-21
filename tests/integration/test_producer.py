import asyncio
import os
import uuid

import asyncpg
import pytest
from aiokafka import AIOKafkaConsumer
from httpx import AsyncClient
from testcontainers.kafka import KafkaContainer
from testcontainers.postgres import PostgresContainer

from app.producer.main import app


@pytest.mark.asyncio
async def test_producer_kafka() -> None:
    """Producer publishes to Kafka with backing Postgres using Testcontainers."""
    with PostgresContainer("postgres:16") as pg, KafkaContainer() as kafka:
        os.environ["DATABASE_URL"] = pg.get_connection_url()
        os.environ["KAFKA_BOOTSTRAP_SERVERS"] = kafka.get_bootstrap_server()

        # Verify Postgres is reachable
        conn = await asyncpg.connect(pg.get_connection_url())
        await conn.execute("SELECT 1;")
        await conn.close()

        # Produce event via FastAPI endpoint
        event = {
            "event_id": str(uuid.uuid4()),
            "order_id": str(uuid.uuid4()),
            "timestamp": 1,
            "source": "test",
            "event_type": "ORDER_CREATED",
            "payload": "{}",
        }
        async with AsyncClient(app=app, base_url="http://test") as client:
            resp = await client.post("/events", json=event)
            assert resp.status_code == 200

        # Consume produced message from Kafka
        consumer = AIOKafkaConsumer(
            os.getenv("KAFKA_TOPIC_ORDERS", "orders.raw"),
            bootstrap_servers=os.environ["KAFKA_BOOTSTRAP_SERVERS"],
            group_id="test-group",
            auto_offset_reset="earliest",
        )
        await consumer.start()
        try:
            msg = await asyncio.wait_for(consumer.getone(), timeout=10)
            assert msg is not None
        finally:
            await consumer.stop()
