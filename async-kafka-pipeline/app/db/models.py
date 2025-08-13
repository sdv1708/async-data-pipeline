# app/db/models.py
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, JSON, Index
import uuid

class OrderEvent(SQLModel, table=True):
    """Store raw events for event sourcing"""
    __tablename__ = "order_events"
    
    # Primary key
    event_id: str = Field(primary_key=True)
    
    # Event metadata
    event_type: str = Field(index=True)
    order_id: str = Field(index=True)
    timestamp: datetime
    source: str = Field(default="synthetic")
    
    # Raw event data
    payload: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    
    # Processing metadata
    processed_at: datetime = Field(default_factory=datetime.utcnow)
    kafka_partition: Optional[int] = None
    kafka_offset: Optional[int] = None
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_order_timestamp', 'order_id', 'timestamp'),
        Index('idx_event_type_timestamp', 'event_type', 'timestamp'),
    )

class OrderState(SQLModel, table=True):
    """Current state of orders (materialized view)"""
    __tablename__ = "order_states"
    
    # Primary key
    order_id: str = Field(primary_key=True)
    
    # Order details
    user_id: Optional[str] = None
    total_amount: Optional[float] = None
    
    # State tracking
    status: str = Field(default="pending")  # pending, paid, picked, shipped
    
    # Timestamps for each state
    created_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    picked_at: Optional[datetime] = None
    shipped_at: Optional[datetime] = None
    
    # Metadata
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    version: int = Field(default=1)  # For optimistic locking

class ProcessingError(SQLModel, table=True):
    """Track processing errors for retry/DLQ"""
    __tablename__ = "processing_errors"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    event_id: str = Field(index=True)
    order_id: str = Field(index=True)
    error_type: str
    error_message: str
    raw_event: Dict[str, Any] = Field(sa_column=Column(JSON))
    retry_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)