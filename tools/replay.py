"""Replay archived events to Kafka."""

from __future__ import annotations

import argparse
import asyncio
import io
import json
import os
from pathlib import Path
from typing import Any, Iterator
from urllib.parse import urlparse

from aiokafka import AIOKafkaProducer  # type: ignore[import-untyped]
from fastavro import reader, schemaless_writer

with open(Path("app/producer/schemas/order_event.avsc")) as f:
    SCHEMA = json.load(f)


def _iter_records(path: str) -> Iterator[dict[str, Any]]:
    """Yield records from a local or S3 Avro file."""

    if path.startswith("s3://"):
        import boto3  # type: ignore[import-not-found]

        parsed = urlparse(path)
        obj = boto3.client("s3").get_object(
            Bucket=parsed.netloc, Key=parsed.path.lstrip("/")
        )
        data = io.BytesIO(obj["Body"].read())
        yield from reader(data)  # type: ignore[misc]
    else:
        with open(path, "rb") as f:
            yield from reader(f)  # type: ignore[misc]


async def replay(path: str, rps: int) -> None:
    """Republish events to Kafka using ``order_id`` as partition key."""

    producer = AIOKafkaProducer(
        bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
    )
    await producer.start()
    try:
        for record in _iter_records(path):
            buf = io.BytesIO()
            schemaless_writer(buf, SCHEMA, record)
            await producer.send_and_wait(
                os.getenv("KAFKA_TOPIC_ORDERS", "orders.raw"),
                buf.getvalue(),
                key=record["order_id"].encode(),
            )
            if rps > 0:
                await asyncio.sleep(1 / rps)
    finally:
        await producer.stop()


def main() -> None:  # pragma: no cover - CLI entrypoint
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Path to Avro file (disk or S3)")
    parser.add_argument("--rps", type=int, default=0, help="Replay rate per second")
    args = parser.parse_args()
    asyncio.run(replay(args.input, args.rps))


if __name__ == "__main__":  # pragma: no cover
    main()
