# tools/event_producer.py
import asyncio
import json
import uuid
import time
import random
import click
from aiokafka import AIOKafkaProducer
from faker import Faker
from app.common.logging import get_logger

fake = Faker()
logger = get_logger(__name__)

class KafkaEventProducer:
    def __init__(self, bootstrap_servers="localhost:9092", topic="orders.raw"):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.producer = None
        
    async def start(self):
        """Start the Kafka producer"""
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )
        await self.producer.start()
        logger.info("kafka_producer_started", topic=self.topic)
    
    async def stop(self):
        """Stop the Kafka producer"""
        if self.producer:
            await self.producer.stop()
            logger.info("kafka_producer_stopped")
    
    def generate_order_created_event(self, order_id=None):
        """Generate ORDER_CREATED event"""
        if not order_id:
            order_id = f"ORD-{fake.random_number(digits=8)}"
            
        items = []
        for _ in range(random.randint(1, 4)):
            items.append({
                "sku": f"SKU-{fake.random_number(digits=5)}",
                "quantity": random.randint(1, 5),
                "unit_price": round(random.uniform(10.0, 500.0), 2)
            })
        
        total = sum(item["quantity"] * item["unit_price"] for item in items)
        
        return {
            "event_id": str(uuid.uuid4()),
            "event_type": "ORDER_CREATED",
            "order_id": order_id,
            "timestamp": int(time.time() * 1000),  # milliseconds
            "source": "test_producer",
            "payload": {
                "user_id": f"USR-{fake.random_number(digits=6)}",
                "items": items,
                "total_amount": round(total, 2)
            }
        }
    
    def generate_payment_authorized_event(self, order_id, amount):
        """Generate PAYMENT_AUTHORIZED event"""
        return {
            "event_id": str(uuid.uuid4()),
            "event_type": "PAYMENT_AUTHORIZED",
            "order_id": order_id,
            "timestamp": int(time.time() * 1000),
            "source": "test_producer",
            "payload": {
                "payment_id": f"PAY-{uuid.uuid4().hex[:8]}",
                "payment_method": random.choice(["CARD", "APPLE_PAY", "PAYPAL"]),
                "amount": amount
            }
        }
    
    async def send_event(self, event):
        """Send event to Kafka"""
        await self.producer.send_and_wait(
            self.topic,
            value=event,
            key=event["order_id"]
        )
        logger.info(
            "event_sent",
            event_id=event["event_id"],
            event_type=event["event_type"],
            order_id=event["order_id"]
        )
    
    async def generate_order_lifecycle(self):
        """Generate a complete order lifecycle"""
        # Create order
        order_event = self.generate_order_created_event()
        order_id = order_event["order_id"]
        amount = order_event["payload"]["total_amount"]
        
        print(f"📦 Creating order {order_id} (${amount})")
        await self.send_event(order_event)
        
        # Wait a bit before payment
        await asyncio.sleep(random.uniform(0.5, 2))
        
        # Authorize payment (80% of the time)
        if random.random() < 0.8:
            payment_event = self.generate_payment_authorized_event(order_id, amount)
            print(f"💳 Authorizing payment for {order_id}")
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
            print(f"🔄 Generating events continuously (delay: {delay}s). Press Ctrl+C to stop...")
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
            
            print("\n✅ Event generation completed!")
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping event producer...")
    finally:
        await producer.stop()

if __name__ == "__main__":
    asyncio.run(main())