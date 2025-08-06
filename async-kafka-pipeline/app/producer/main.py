from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
import uuid
from datetime import datetime
from app.common.logging import get_logger

logger = get_logger(__name__)

app = FastAPI(title="Async Kafka Producer", version="1.0.0")

class OrderItem(BaseModel):
    sku: str = Field(..., description="Stock Keeping Unit")
    quantity: int = Field(..., gt=0, description="Quantity of the item ordered")
    unit_price: float = Field(..., gt=0, description="Unit price of the item")

class OrderCreatePayload(BaseModel):
    user_id: str = Field(..., description="ID of the user placing the order")
    items: List[OrderItem] = Field(..., description="List of items in the order")
    total_amount: float = Field(..., gt=0, description="Total amount for the order")

class OrderEvent(BaseModel):
    event_type: Literal["ORDER_CREATED", "PAYMENT_AUTHORIZED", "ITEM_PICKED", "SHIPMENT_DISPATCHED"]
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique event ID")
    order_id: str = Field(..., description="ID of the order")
    timestamp: Optional[int] = Field(default_factory=lambda: int(datetime.now().timestamp() * 1000), description="Event timestamp")
    source: str = "api"
    payload: Optional[dict] = Field(None, description="Event payload")

@app.get("/")
async def root():
    """Root endpoint to verify service is running"""
    return {"status": "healthy", "service": "producer"}

@app.post("/events")
async def publush_event(event: OrderEvent):
    """Endpoint to publish order events"""
    logger.info("event_received",
                event_id=event.event_id,
                event_type=event.event_type,
                order_id=event.order_id,
                )
    #TODO: Here you would add code to publish the event to Kafka
    return {"status": "event received", "event_id": event.event_id}

@app.get("/health")
async def health():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "checks": {
            "api": "ok",
            "kafka": "not_connected"  # Will update later
        }
    }
