# Pydantic models for validation
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime
import uuid

class OrderItem(BaseModel):
    sku: str = Field(..., description="Product SKU")
    quantity: int = Field(..., gt=0, description="Quantity ordered")
    unit_price: float = Field(..., gt=0, description="Price per unit")

class OrderCreatedPayload(BaseModel):
    user_id: str
    items: List[OrderItem]
    total_amount: float

class OrderEvent(BaseModel):
    event_type: Literal["ORDER_CREATED", "PAYMENT_AUTHORIZED", "ITEM_PICKED", "SHIPMENT_DISPATCHED"]
    event_id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    order_id: str
    timestamp: Optional[int] = Field(default_factory=lambda: int(datetime.now().timestamp() * 1000))
    source: str = "api"
    payload: Optional[dict] = None