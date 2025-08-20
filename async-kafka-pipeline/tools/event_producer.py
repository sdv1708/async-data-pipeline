# tools/event_producer.py
import asyncio
import json
import uuid
import time
import random
import click
from faker import Faker
from app.common.logging import get_logger
from app.common.avro_kafka_client import AvroKafkaProducer
from app.producer.schemas import OrderEvent, OrderItem, Address, EventType, PaymentMethod, create_order_created_event, create_payment_authorized_event

fake = Faker()
logger = get_logger(__name__)

class KafkaEventProducer:
    def __init__(self, bootstrap_servers="localhost:9092", topic="orders.raw"):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.producer = None
        
    async def start(self):
        """Start the Avro Kafka producer"""
        self.producer = AvroKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            use_avro=True
        )
        await self.producer.start()
        logger.info("avro_kafka_producer_started", topic=self.topic)
    
    async def stop(self):
        """Stop the Kafka producer"""
        if self.producer:
            await self.producer.stop()
            logger.info("avro_kafka_producer_stopped")
    
    def generate_order_created_event(self, order_id=None):
        """Generate ORDER_CREATED event using Pydantic schema"""
        if not order_id:
            order_id = f"ORD-{fake.random_number(digits=8)}"
            
        # Generate items using Pydantic models
        items = []
        for _ in range(random.randint(1, 4)):
            items.append(OrderItem(
                sku=f"SKU-{fake.random_number(digits=5)}",
                product_name=fake.catch_phrase(),
                quantity=random.randint(1, 5),
                unit_price=round(random.uniform(10.0, 500.0), 2),
                category=random.choice(["electronics", "clothing", "books", "home", "sports"])
            ))
        
        # Generate shipping address
        shipping_address = Address(
            street=fake.street_address(),
            city=fake.city(),
            state=fake.state_abbr(),
            postal_code=fake.postcode(),
            country="US"
        )
        
        # Create the event using the helper function
        event = create_order_created_event(
            order_id=order_id,
            user_id=f"USR-{fake.random_number(digits=6)}",
            items=items,
            shipping_address=shipping_address
        )
        
        # Override source for test producer
        event.source = "test_producer"
        
        return event.to_avro_dict()
    
    def generate_payment_authorized_event(self, order_id, amount):
        """Generate PAYMENT_AUTHORIZED event using Pydantic schema"""
        event = create_payment_authorized_event(
            order_id=order_id,
            payment_id=f"PAY-{uuid.uuid4().hex[:8]}",
            amount=amount,
            payment_method=random.choice(list(PaymentMethod))
        )
        
        # Override source for test producer
        event.source = "test_producer"
        
        return event.to_avro_dict()
    
    async def send_event(self, event):
        """Send event to Kafka using Avro serialization"""
        result = await self.producer.send_event(
            topic=self.topic,
            event=event,
            key=event["order_id"],
            headers={
                'event_type': event["event_type"].encode('utf-8'),
                'source': event.get("source", "test_producer").encode('utf-8')
            }
        )
        logger.info(
            "avro_event_sent",
            event_id=event["event_id"],
            event_type=event["event_type"],
            order_id=event["order_id"],
            partition=result["partition"],
            offset=result["offset"]
        )
    
    async def generate_order_lifecycle(self):
        """Generate a complete order lifecycle"""
        # Create order
        order_event = self.generate_order_created_event()
        order_id = order_event["order_id"]
        amount = order_event["payload"]["total_amount"]
        
        print(f" Creating order {order_id} (${amount})")
        await self.send_event(order_event)
        
        # Wait a bit before payment
        await asyncio.sleep(random.uniform(0.5, 2))
        
        # Authorize payment (80% of the time)
        if random.random() < 0.8:
            payment_event = self.generate_payment_authorized_event(order_id, amount)
            print(f" Authorizing payment for {order_id}")
            await self.send_event(payment_event)

@click.command()
@click.option('--count', default=10, help='Number of order lifecycles to generate')
@click.option('--delay', default=2.0, help='Delay between orders (seconds)')
@click.option('--topic', default='orders.raw', help='Kafka topic to send events to')
@click.option('--continuous', is_flag=True, help='Run continuously until stopped')
async def main(count, delay, topic, continuous):
    """Generate test events and send to Kafka"""
    producer = KafkaEventProducer(topic=topic)
    
    try:
        await producer.start()
        
        if continuous:
            print(f" Generating events continuously (delay: {delay}s). Press Ctrl+C to stop...")
            i = 0
            while True:
                i += 1
                print(f"\n--- Event Cycle {i} ---")
                await producer.generate_order_lifecycle()
                await asyncio.sleep(delay)
        else:
            print(f"📤 Generating {count} order lifecycles...")
            for i in range(count):
                print(f"\n--- Order Lifecycle {i+1}/{count} ---")
                await producer.generate_order_lifecycle()
                if i < count - 1:
                    await asyncio.sleep(delay)
            
            print("\n Event generation completed!")
            
    except KeyboardInterrupt:
        print("\n Stopping event producer...")
    finally:
        await producer.stop()

if __name__ == "__main__":
    asyncio.run(main())