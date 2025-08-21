import json
from pathlib import Path

def test_schema_partition_key() -> None:
    path = Path("app/producer/schemas/order_event.avsc")
    schema = json.loads(path.read_text())
    assert any(f["name"] == "order_id" for f in schema["fields"])
