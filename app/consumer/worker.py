import asyncio
import io
import json
import logging.config
import os
from pathlib import Path

import yaml
from aiokafka import AIOKafkaConsumer
from fastavro import schemaless_reader
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from prometheus_client import Counter, start_http_server

from app.consumer.dedup import deduplicate
from app.consumer.processors import enrich, fraud

CONFIG_DIR = Path(__file__).resolve().parents[2] / "configs"
with open(CONFIG_DIR / "logging.yaml") as f:
    logging.config.dictConfig(yaml.safe_load(f))

with open(CONFIG_DIR / "otel.yaml") as f:
    otel_config = yaml.safe_load(f)

endpoint = os.path.expandvars(otel_config["exporter"]["otlp"]["endpoint"])
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint))
)
tracer = trace.get_tracer(__name__)

processed_events = Counter("consumer_events_total", "Total events consumed")
start_http_server(int(os.getenv("METRICS_PORT", "8001")))

with open(
    os.path.join(os.path.dirname(__file__), "../producer/schemas/order_event.avsc")
) as f:
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
            processed_events.inc()
            with tracer.start_as_current_span("consume_message"):
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
