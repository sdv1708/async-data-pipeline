# app/consumer/worker.py
import asyncio
import json
from typing import List, Optional
from app.common.logging import get_logger
from app.common.avro_kafka_client import AvroKafkaConsumer
from app.consumer.processors.enrichment import EventEnricher
from app.consumer.processors.fraud import FraudDetector
from app.cache.redis_client import redis_cache
from app.db.database import init_db, get_session
from app.db.models import OrderEvent, OrderState
from datetime import datetime
from app.common.metrics import (
    timing_decorator, record_event_received, record_event_processed,
    record_event_enriched, start_metrics_server, set_active_consumers
)

logger = get_logger(__name__)

class OrderEventConsumer:
    def __init__(
        self,
        topics: List[str] = ["orders.raw"],
        bootstrap_servers: str = "localhost:9092",
        group_id: str = "order-processor-group"
    ):
        self.topics = topics
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.consumer: Optional[AvroKafkaConsumer] = None
        self.running = False
        
    async def start(self):
        """Start the consumer"""
        # Start metrics server
        start_metrics_server(port=8000)
        
        # Initialize database
        await init_db()

        # Connect to Redis
        await redis_cache.connect()
        
        # Create and start Avro consumer
        self.consumer = AvroKafkaConsumer(
            topics=self.topics,
            group_id=self.group_id,
            bootstrap_servers=self.bootstrap_servers,
            use_avro=True
        )
        
        await self.consumer.start()
        self.running = True
        set_active_consumers(1)
        
        logger.info(
            "avro_consumer_started",
            topics=self.topics,
            group_id=self.group_id,
            serialization="avro"
        )
    
        
    async def stop(self):
        """Stop the consumer"""
        self.running = False
        if self.consumer:
            await self.consumer.stop()
        
        # Disconnect Redis
        await redis_cache.disconnect()
        logger.info("consumer_stopped")
    
    @timing_decorator('processing')
    async def process_message(self, message):
        """Process message through the pipeline"""
        event = message.value
        event_id = event.get('event_id')
        
        try:
            # Record event received
            record_event_received(event.get('event_type', 'unknown'))
            
            # Step 1: Check for duplicates
            if await redis_cache.is_duplicate(event_id):
                logger.warning("duplicate_event_skipped", event_id=event_id)
                return  # Skip duplicate
            
            # Step 2: Enrich event
            if event.get('event_type') == 'ORDER_CREATED':
                event = await EventEnricher.enrich_order_created_event(event)
                record_event_enriched(event.get('event_type'))
            
            # Step 3: Fraud detection
            fraud_result = await FraudDetector.analyze_order(event)
            event['fraud_analysis'] = fraud_result
            
            # Step 4: Save to database
            await self.save_to_database(event, message)
            
            # Step 5: Cache order state
            await self.cache_order_state(event)
            
            # Step 6: Route to specific handlers
            await self.route_event(event)
            
            # Record successful processing
            record_event_processed(event.get('event_type', 'unknown'), 'success')
            
            logger.info(
                "event_processed_successfully",
                event_id=event_id,
                enriched=event.get('enriched', False),
                is_fraudulent=fraud_result.get('is_fraudulent', False)
            )
            
        except Exception as e:
            # Record failed processing
            record_event_processed(event.get('event_type', 'unknown'), 'error')
            
            logger.error(
                "pipeline_processing_failed",
                error=str(e),
                event_id=event_id
            )
            raise
    
    async def handle_order_created(self, event):
        """Handle ORDER_CREATED events"""
        order_id = event.get('order_id')
        payload = event.get('payload', {})
        
        # Simulate processing
        await asyncio.sleep(0.1)
        
        logger.info(
            "order_created_processed",
            order_id=order_id,
            user_id=payload.get('user_id'),
            total_amount=payload.get('total_amount'),
            item_count=len(payload.get('items', []))
        )
    
    async def handle_payment_authorized(self, event):
        """Handle PAYMENT_AUTHORIZED events"""
        order_id = event.get('order_id')
        payload = event.get('payload', {})
        
        # Simulate processing
        await asyncio.sleep(0.1)
        
        logger.info(
            "payment_authorized_processed",
            order_id=order_id,
            payment_id=payload.get('payment_id'),
            amount=payload.get('amount')
        )
    
    async def save_to_database(self, event, message):
        """Save event to database"""
        async with get_session() as session:
            # Save raw event
            order_event = OrderEvent(
                event_id=event.get('event_id'),
                event_type=event.get('event_type'),
                order_id=event.get('order_id'),
                timestamp=datetime.fromtimestamp(event.get('timestamp', 0) / 1000),
                payload=event.get('payload', {}),
                kafka_partition=message.partition,
                kafka_offset=message.offset,
                source=event.get('source', 'synthetic')
            )
            session.add(order_event)
            
            # Update order state if it's an ORDER_CREATED event
            if event.get('event_type') == 'ORDER_CREATED':
                payload = event.get('payload', {})
                order_state = OrderState(
                    order_id=event.get('order_id'),
                    user_id=payload.get('user_id'),
                    total_amount=payload.get('total_amount'),
                    status='pending',
                    created_at=datetime.fromtimestamp(event.get('timestamp', 0) / 1000)
                )
                session.merge(order_state)  # Use merge for upsert behavior
    
    async def cache_order_state(self, event):
        """Cache order state in Redis"""
        if event.get('event_type') == 'ORDER_CREATED':
            order_id = event.get('order_id')
            payload = event.get('payload', {})
            
            state = {
                'order_id': order_id,
                'user_id': payload.get('user_id'),
                'total_amount': payload.get('total_amount'),
                'status': 'pending',
                'fraud_analysis': event.get('fraud_analysis', {}),
                'enriched': event.get('enriched', False)
            }
            
            await redis_cache.cache_order_state(order_id, state)
    
    async def route_event(self, event):
        """Route event to appropriate handlers"""
        event_type = event.get('event_type')
        
        if event_type == 'ORDER_CREATED':
            await self.handle_order_created(event)
        elif event_type == 'PAYMENT_AUTHORIZED':
            await self.handle_payment_authorized(event)
        else:
            logger.warning("unknown_event_type", event_type=event_type)
    
    async def consume(self):
        """Main consumption loop using Avro consumer"""
        try:
            await self.consumer.consume_messages(self.process_message)
        except Exception as e:
            logger.error("avro_consumer_error", error=str(e))
        finally:
            await self.stop()

async def main():
    """Run the consumer"""
    consumer = OrderEventConsumer()
    
    try:
        await consumer.start()
        logger.info("consumer_running")
        await consumer.consume()
    except KeyboardInterrupt:
        logger.info("shutdown_requested")
    finally:
        await consumer.stop()

if __name__ == "__main__":
    # Run the consumer
    asyncio.run(main())