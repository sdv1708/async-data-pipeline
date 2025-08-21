import argparse
import asyncio
import io
import json
import os
import random
import time
import uuid

from aiokafka import AIOKafkaProducer
from fastavro import schemaless_writer

with open(os.path.join("app", "producer", "schemas", "order_event.avsc")) as f:
    SCHEMA = json.load(f)

EVENT_TYPES = ["ORDER_CREATED", "PAYMENT_AUTHORIZED", "ITEM_PICKED", "SHIPMENT_DISPATCHED"]

async def produce(rps: int, duration: int) -> None:
    producer = AIOKafkaProducer(bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"))
    await producer.start()
    end = time.time() + duration
    try:
        while time.time() < end:
            event = {
                "event_id": str(uuid.uuid4()),
                "order_id": str(uuid.uuid4()),
                "timestamp": int(time.time() * 1000),
                "source": "simulator",
                "event_type": random.choice(EVENT_TYPES),
                "payload": "{}",
            }
            buf = io.BytesIO()
            schemaless_writer(buf, SCHEMA, event)
            await producer.send_and_wait(
                os.getenv("KAFKA_TOPIC_ORDERS", "orders.raw"),
                buf.getvalue(),
                key=event["order_id"].encode(),
            )
            await asyncio.sleep(1 / rps)
    finally:
        await producer.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rps", type=int, default=1)
    parser.add_argument("--duration", type=int, default=10)
    args = parser.parse_args()
    asyncio.run(produce(args.rps, args.duration))
