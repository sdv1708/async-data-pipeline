import asyncio
import io
import json
import os

from aiokafka import AIOKafkaConsumer
from fastavro import schemaless_reader

from app.consumer.processors import enrich, fraud
from app.consumer.dedup import deduplicate

with open(os.path.join(os.path.dirname(__file__), "../producer/schemas/order_event.avsc")) as f:
    ORDER_SCHEMA = json.load(f)


async def consume() -> None:
    consumer = AIOKafkaConsumer(
        os.getenv("KAFKA_TOPIC_ORDERS", "orders.raw"),
        bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
        group_id="worker",
    )
    await consumer.start()
    try:
        async for msg in consumer:
            data = schemaless_reader(io.BytesIO(msg.value), ORDER_SCHEMA)
            if await deduplicate(data["event_id"]):
                continue
            data = await enrich.process(data)
            flagged = await fraud.check(data)
            if flagged:
                # TODO: publish to flagged topic
                pass
    finally:
        await consumer.stop()


if __name__ == "__main__":
    asyncio.run(consume())
