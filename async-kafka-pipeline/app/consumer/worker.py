# app/consumer/worker.py
import asyncio
import json
from aiokafka import AIOKafkaConsumer
from aiokafka.errors import CommitFailedError
from typing import List, Optional
from app.common.logging import get_logger

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
        self.consumer: Optional[AIOKafkaConsumer] = None
        self.running = False
        
    async def start(self):
        """Start the consumer"""
        self.consumer = AIOKafkaConsumer(
            *self.topics,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            key_deserializer=lambda k: k.decode('utf-8') if k else None,
            enable_auto_commit=False,  # Manual commit for control
            auto_offset_reset='earliest',  # Start from beginning
            session_timeout_ms=30000,
            heartbeat_interval_ms=10000,
            max_poll_records=10
        )
        
        await self.consumer.start()
        self.running = True
        logger.info(
            "consumer_started",
            topics=self.topics,
            group_id=self.group_id
        )
    
        
    async def stop(self):
        """Stop the consumer"""
        self.running = False
        if self.consumer:
            await self.consumer.stop()
            logger.info("consumer_stopped")
    
    async def process_message(self, message):
        """Process a single message"""
        event = message.value

        try:
            # Extract event details
            event_id = event.get('event_id')
            event_type = event.get('event_type')
            order_id = event.get('order_id')
            timestamp = datetime.fromtimestamp(event.get('timestamp', 0) / 1000)
            
            logger.info(
                "processing_event",
                event_id=event_id,
                event_type=event_type,
                order_id=order_id
            )
            
            # Save raw event (idempotent)
            await EventRepository.save_event(
                event_id=event_id,
                event_type=event_type,
                order_id=order_id,
                timestamp=timestamp,
                payload=event.get('payload', {}),
                kafka_partition=message.partition,
                kafka_offset=message.offset,
                source=event.get('source', 'synthetic')
            )

            await EventRepository.update_order_state(event)
        
        # logger.info(
        #     "processing_event",
        #     event_id=event.get('event_id'),
        #     event_type=event.get('event_type'),
        #     order_id=event.get('order_id'),
        #     partition=message.partition,
        #     offset=message.offset
        # )
        
        # Router based on event type
        event_type = event.get('event_type')
        
        if event_type == 'ORDER_CREATED':
            await self.handle_order_created(event)
        elif event_type == 'PAYMENT_AUTHORIZED':
            await self.handle_payment_authorized(event)
        else:
            logger.warning("unknown_event_type", event_type=event_type)
        
        except Exception as e:
            logger.error(
                "event_processing_failed",
                error=str(e),
                event_id=event.get('event_id')
            )
            
            # Save error for retry/analysis
            await EventRepository.save_error(
                event=event,
                error_type=type(e).__name__,
                error_message=str(e)
            )
            # Re-raise to prevent offset commit
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
    
    async def consume(self):
        """Main consumption loop"""
        try:
            async for message in self.consumer:
                if not self.running:
                    break
                
                try:
                    # Process the message
                    await self.process_message(message)
                    
                    # Commit offset after successful processing
                    await self.consumer.commit()
                    
                except Exception as e:
                    logger.error(
                        "message_processing_failed",
                        error=str(e),
                        offset=message.offset,
                        partition=message.partition
                    )
                    # Don't commit on error - message will be reprocessed
                    
        except CommitFailedError as e:
            logger.error("commit_failed", error=str(e))
        except Exception as e:
            logger.error("consumer_error", error=str(e))
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