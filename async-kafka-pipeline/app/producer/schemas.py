# app/producer/schemas.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime
import uuid
import time

class EventType(str, Enum):
    ORDER_CREATED = "ORDER_CREATED"
    ORDER_UPDATED = "ORDER_UPDATED"
    ORDER_CANCELLED = "ORDER_CANCELLED"
    PAYMENT_AUTHORIZED = "PAYMENT_AUTHORIZED"
    PAYMENT_CAPTURED = "PAYMENT_CAPTURED"
    PAYMENT_FAILED = "PAYMENT_FAILED"
    ORDER_SHIPPED = "ORDER_SHIPPED"
    ORDER_DELIVERED = "ORDER_DELIVERED"
    ORDER_RETURNED = "ORDER_RETURNED"

class OrderStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    PAID = "PAID"
    PROCESSING = "PROCESSING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    RETURNED = "RETURNED"

class PaymentMethod(str, Enum):
    CREDIT_CARD = "CREDIT_CARD"
    DEBIT_CARD = "DEBIT_CARD"
    PAYPAL = "PAYPAL"
    APPLE_PAY = "APPLE_PAY"
    GOOGLE_PAY = "GOOGLE_PAY"
    BANK_TRANSFER = "BANK_TRANSFER"
    CASH_ON_DELIVERY = "CASH_ON_DELIVERY"

class OrderItem(BaseModel):
    sku: str = Field(..., description="Stock Keeping Unit identifier")
    product_name: Optional[str] = Field(None, description="Human-readable product name")
    quantity: int = Field(..., gt=0, description="Number of items ordered")
    unit_price: float = Field(..., ge=0, description="Price per unit in the order currency")
    category: Optional[str] = Field(None, description="Product category")

class Address(BaseModel):
    street: str = Field(..., description="Street address")
    city: str = Field(..., description="City name")
    state: Optional[str] = Field(None, description="State or province")
    postal_code: str = Field(..., description="Postal or ZIP code")
    country: str = Field(default="US", description="Country code (ISO 3166-1 alpha-2)")

class OrderEventPayload(BaseModel):
    user_id: Optional[str] = Field(None, description="ID of the user who placed the order")
    total_amount: Optional[float] = Field(None, ge=0, description="Total order amount in USD")
    currency: str = Field(default="USD", description="Currency code (ISO 4217)")
    status: Optional[OrderStatus] = Field(None, description="Current order status")
    items: Optional[List[OrderItem]] = Field(None, description="List of items in the order")
    shipping_address: Optional[Address] = Field(None, description="Shipping address for the order")
    payment_method: Optional[PaymentMethod] = Field(None, description="Payment method used for the order")
    payment_id: Optional[str] = Field(None, description="External payment processor transaction ID")
    metadata: Optional[Dict[str, str]] = Field(None, description="Additional event-specific metadata")

class OrderEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for this event")
    event_type: EventType = Field(..., description="Type of the order event")
    order_id: str = Field(..., description="Unique identifier for the order (used as partition key)")
    timestamp: int = Field(default_factory=lambda: int(time.time() * 1000), description="Event timestamp in milliseconds since epoch")
    source: str = Field(default="order-service", description="Source system that generated this event")
    version: str = Field(default="1.0", description="Schema version for backward compatibility")
    payload: OrderEventPayload = Field(..., description="Event-specific payload data")

    @validator('timestamp', pre=True)
    def validate_timestamp(cls, v):
        if isinstance(v, datetime):
            return int(v.timestamp() * 1000)
        elif isinstance(v, (int, float)):
            # Ensure it's in milliseconds
            if v < 1e12:  # If it looks like seconds, convert to milliseconds
                return int(v * 1000)
            return int(v)
        return v

    def to_avro_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format suitable for Avro serialization"""
        data = self.dict()
        
        # Convert enums to their string values for Avro
        if data.get('event_type'):
            data['event_type'] = data['event_type']
        
        if data.get('payload', {}).get('status'):
            data['payload']['status'] = data['payload']['status']
            
        if data.get('payload', {}).get('payment_method'):
            data['payload']['payment_method'] = data['payload']['payment_method']
        
        return data

    class Config:
        use_enum_values = True  # Use enum values instead of enum objects in dict()

# Convenience functions for creating common events
def create_order_created_event(
    order_id: str,
    user_id: str,
    items: List[OrderItem],
    shipping_address: Optional[Address] = None,
    **kwargs
) -> OrderEvent:
    """Create an ORDER_CREATED event"""
    total_amount = sum(item.quantity * item.unit_price for item in items)
    
    payload = OrderEventPayload(
        user_id=user_id,
        total_amount=total_amount,
        status=OrderStatus.PENDING,
        items=items,
        shipping_address=shipping_address,
        **kwargs
    )
    
    return OrderEvent(
        event_type=EventType.ORDER_CREATED,
        order_id=order_id,
        payload=payload
    )

def create_payment_authorized_event(
    order_id: str,
    payment_id: str,
    amount: float,
    payment_method: PaymentMethod,
    **kwargs
) -> OrderEvent:
    """Create a PAYMENT_AUTHORIZED event"""
    payload = OrderEventPayload(
        total_amount=amount,
        payment_method=payment_method,
        payment_id=payment_id,
        status=OrderStatus.PAID,
        **kwargs
    )
    
    return OrderEvent(
        event_type=EventType.PAYMENT_AUTHORIZED,
        order_id=order_id,
        payload=payload
    )