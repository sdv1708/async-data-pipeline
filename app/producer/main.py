import io
import json
import os

from aiokafka import AIOKafkaProducer
from fastapi import FastAPI
from fastavro import schemaless_writer

app = FastAPI()
producer: AIOKafkaProducer | None = None

with open(os.path.join(os.path.dirname(__file__), "schemas", "order_event.avsc")) as f:
    ORDER_SCHEMA = json.load(f)


@app.on_event("startup")
async def startup() -> None:
    global producer
    producer = AIOKafkaProducer(
        bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
    )
    await producer.start()


@app.on_event("shutdown")
async def shutdown() -> None:
    if producer:
        await producer.stop()


@app.post("/events")
async def publish_event(event: dict) -> dict:
    buf = io.BytesIO()
    schemaless_writer(buf, ORDER_SCHEMA, event)
    await producer.send_and_wait(
        os.getenv("KAFKA_TOPIC_ORDERS", "orders.raw"),
        buf.getvalue(),
        key=event["order_id"].encode(),
    )
    return {"status": "ok"}
