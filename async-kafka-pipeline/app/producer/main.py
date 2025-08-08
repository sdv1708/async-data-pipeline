# app/producer/main.py (updated)
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime
import uuid
from app.common.logging import get_logger
from app.common.kafka_client import KafkaProducerClient

logger = get_logger(__name__)

# Global Kafka producer
kafka_producer = KafkaProducerClient()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    logger.info("app_starting")
    await kafka_producer.start()
    
    yield
    
    # Shutdown
    logger.info("app_stopping")
    await kafka_producer.stop()

# Create FastAPI app with lifecycle management
app = FastAPI(
    title="Kafka Event Producer",
    description="Accepts order events and publishes to Kafka",
    version="0.1.0",
    lifespan=lifespan
)

# ... (keep the Pydantic models from before) ...

@app.post("/events")
async def publish_event(event: OrderEvent):
    """Accept an event and publish to Kafka"""
    
    try:
        # Log the received event
        logger.info(
            "event_received",
            event_id=event.event_id,
            event_type=event.event_type,
            order_id=event.order_id
        )
        
        # Publish to Kafka
        result = await kafka_producer.send_event(
            topic="orders.raw",
            event=event.model_dump(),
            key=event.order_id
        )
        
        return {
            "status": "published",
            "event_id": event.event_id,
            "kafka": result
        }
        
    except Exception as e:
        logger.error("event_publish_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    """Detailed health check"""
    kafka_status = "connected" if kafka_producer.producer else "disconnected"
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "checks": {
            "api": "ok",
            "kafka": kafka_status
        }
    }