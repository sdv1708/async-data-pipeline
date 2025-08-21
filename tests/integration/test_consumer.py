import asyncio
import io
import json
import os
import uuid

import asyncpg
import pytest
from aiokafka import AIOKafkaProducer
from fastavro import schemaless_writer
from testcontainers.kafka import KafkaContainer
from testcontainers.postgres import PostgresContainer


@pytest.mark.asyncio
async def test_consumer_writes_postgres() -> None:
    with PostgresContainer("postgres:16") as pg, KafkaContainer() as kafka:
        os.environ["DATABASE_URL"] = pg.get_connection_url()
        os.environ["KAFKA_BOOTSTRAP_SERVERS"] = kafka.get_bootstrap_server()

        from app.consumer import worker
        from app.db.session import engine
        from sqlmodel import SQLModel

        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

        consume_task = asyncio.create_task(worker.consume())

        producer = AIOKafkaProducer(bootstrap_servers=kafka.get_bootstrap_server())
        await producer.start()
        try:
            event = {
                "event_id": str(uuid.uuid4()),
                "order_id": str(uuid.uuid4()),
                "timestamp": 1,
                "source": "test",
                "event_type": "ORDER_CREATED",
                "payload": "{}",
            }
            buf = io.BytesIO()
            schemaless_writer(
                buf,
                json.load(open("app/producer/schemas/order_event.avsc")),
                event,
            )
            await producer.send_and_wait(
                os.getenv("KAFKA_TOPIC_ORDERS", "orders.raw"),
                buf.getvalue(),
                key=event["order_id"].encode(),
            )
        finally:
            await producer.stop()

        async with asyncpg.connect(pg.get_connection_url()) as conn:
            for _ in range(20):
                row = await conn.fetchrow("SELECT count(*) FROM orderevent")
                if row and row[0] > 0:
                    break
                await asyncio.sleep(0.5)
            assert row[0] > 0

        consume_task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await consume_task
