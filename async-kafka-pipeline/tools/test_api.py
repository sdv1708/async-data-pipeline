# tools/test_api.py
import httpx
import json
from datetime import datetime
import uuid

def test_simple_event():
    """Test sending a simple event to the API"""
    
    event = {
        "event_type": "ORDER_CREATED",
        "order_id": f"ORD-{datetime.now().strftime('%Y%m%d')}-001",
        "payload": {
            "user_id": "USR-123",
            "items": [
                {
                    "sku": "LAPTOP-001",
                    "quantity": 1,
                    "unit_price": 999.99
                }
            ],
            "total_amount": 999.99
        }
    }
    
    print("Sending event:")
    print(json.dumps(event, indent=2))
    
    response = httpx.post("http://localhost:8000/events", json=event)
    
    print(f"\nResponse status: {response.status_code}")
    print(f"Response body: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    test_simple_event()