import asyncio
import io
import json
import logging.config
import os
from pathlib import Path

# --- Optional deps: boto3 is only needed if RAW_EVENTS_BUCKET is set ---
try:
    import boto3  # optional; see below
except Exception:  # ImportError or environment without boto3
    boto3 = None

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

# ---------- Config / Logging ----------
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

# ---------- Metrics ----------
processed_events = Counter("consumer_events_total", "Total events consumed")
start_http_server(int(os.getenv("METRICS_PORT", "8001")))

# ---------- Avro Schema ----------
with open(
    os.path.join(os.path.dirname(__file__), "../producer/schemas/order_event.avsc")
) as f:
    ORDER_SCHEMA = json.load(f)

# ---------- Optional S3 raw event archiving ----------
RAW_EVENTS_BUCKET = os.getenv("TODO_S3_BUCKET_RAW_EVENTS")
if RAW_EVENTS_BUCKET and boto3 is None:
    # boto3 not installed but a bucket was configured; log a warning and continue without S3
    logging.getLogger(__name__).warning(
        "RAW_EVENTS_BUCKET is set but boto3 is unavailable; skipping S3 archiving."
    )
S3 = boto3.client("s3") if (RAW_EVENTS_BUCKET and boto3 is not None) else None


async def consume() -> None:
    consumer = AIOKafkaConsumer(
        os.getenv("KAFKA_TOPIC_ORDERS", "orders.raw"),
        bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
        group_id=os.getenv("KAFKA_CONSUMER_GROUP", "worker"),
        # You may also want to set enable_auto_commit=True and auto_offset_reset="earliest"/"latest" per your needs.
    )
    await consumer.start()
    try:
        async for msg in consumer:
            processed_events.inc()
            with tracer.start_as_current_span("consume_message"):
                # Decode Avro
                data = schemaless_reader(io.BytesIO(msg.value), ORDER_SCHEMA)

                # Deduplicate by event_id (skip if we've seen it)
                if await deduplicate(data["event_id"]):
                    continue

                # Raw-event archival BEFORE enrichment/fraud so we retain original bytes
                if S3:
                    # boto3 is sync; offload to thread to avoid blocking event loop
                    await asyncio.to_thread(
                        S3.put_object,
                        Bucket=RAW_EVENTS_BUCKET,
                        Key=f"{data['event_id']}.avro",
                        Body=msg.value,
                    )

                # Enrich + Fraud checks
                data = await enrich.process(data)
                flagged = await fraud.check(data)
                if flagged:
                    # TODO: publish to a flagged topic (e.g., "orders.flagged")
                    # Consider using aiokafka.AIOKafkaProducer here.
                    pass
    finally:
        await consumer.stop()


if __name__ == "__main__":
    asyncio.run(consume())
