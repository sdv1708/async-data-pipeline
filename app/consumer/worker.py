import asyncio
import io
import json
import os

import boto3
from aiokafka import AIOKafkaConsumer
from fastavro import schemaless_reader

from app.consumer.dedup import deduplicate
from app.consumer.processors import enrich, fraud

with open(
    os.path.join(os.path.dirname(__file__), "../producer/schemas/order_event.avsc")
) as f:
    ORDER_SCHEMA = json.load(f)


RAW_EVENTS_BUCKET = os.getenv("TODO_S3_BUCKET_RAW_EVENTS")
S3 = boto3.client("s3") if RAW_EVENTS_BUCKET else None


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
            if S3:
                await asyncio.to_thread(
                    S3.put_object,
                    Bucket=RAW_EVENTS_BUCKET,
                    Key=f"{data['event_id']}.avro",
                    Body=msg.value,
                )
            data = await enrich.process(data)
            flagged = await fraud.check(data)
            if flagged:
                # TODO: publish to flagged topic
                pass
    finally:
        await consumer.stop()


if __name__ == "__main__":
    asyncio.run(consume())
