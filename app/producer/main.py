import io
import json
import logging.config
import os
from pathlib import Path

import yaml
from aiokafka import AIOKafkaProducer
from fastapi import FastAPI, Response
from fastavro import schemaless_writer
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest

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

app = FastAPI()
FastAPIInstrumentor.instrument_app(app)
producer: AIOKafkaProducer | None = None

with open(os.path.join(os.path.dirname(__file__), "schemas", "order_event.avsc")) as f:
    ORDER_SCHEMA = json.load(f)

events_counter = Counter("producer_events_total", "Total events produced")


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
    events_counter.inc()
    buf = io.BytesIO()
    schemaless_writer(buf, ORDER_SCHEMA, event)
    with tracer.start_as_current_span("send_kafka_message"):
        await producer.send_and_wait(
            os.getenv("KAFKA_TOPIC_ORDERS", "orders.raw"),
            buf.getvalue(),
            key=event["order_id"].encode(),
        )
    return {"status": "ok"}


@app.get("/metrics")
async def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
