# tools/event_generator.py
import asyncio
import httpx
from faker import Faker
import random
import uuid
import click

fake = Faker()

class EventGenerator:
    def __init__(self, api_url="http://localhost:8000"):
        self.api_url = api_url
        self.order_sequences = {}  # Track order lifecycle
        
    def generate_order_created(self, order_id=None):
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
            "event_type": "ORDER_CREATED",
            "order_id": order_id,
            "payload": {
                "user_id": f"USR-{fake.random_number(digits=6)}",
                "items": items,
                "total_amount": round(total, 2)
            }
        }
    
    def generate_payment_authorized(self, order_id, amount):
        """Generate PAYMENT_AUTHORIZED event"""
        return {
            "event_type": "PAYMENT_AUTHORIZED",
            "order_id": order_id,
            "payload": {
                "payment_id": f"PAY-{uuid.uuid4().hex[:8]}",
                "payment_method": random.choice(["CARD", "APPLE_PAY", "PAYPAL"]),
                "amount": amount
            }
        }
    
    async def send_event(self, event):
        """Send event to API"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/events",
                json=event
            )
            return response.json()
    
    async def generate_order_lifecycle(self):
        """Generate a complete order lifecycle"""
        # Create order
        order_event = self.generate_order_created()
        order_id = order_event["order_id"]
        amount = order_event["payload"]["total_amount"]
        
        print(f"Creating order {order_id}")
        await self.send_event(order_event)
        await asyncio.sleep(random.uniform(0.5, 2))
        
        # Authorize payment
        payment_event = self.generate_payment_authorized(order_id, amount)
        print(f"Authorizing payment for {order_id}")
        await self.send_event(payment_event)

@click.command()
@click.option('--count', default=10, help='Number of order lifecycles to generate')
@click.option('--delay', default=1.0, help='Delay between orders (seconds)')
async def main(count, delay):
    """Generate test events"""
    generator = EventGenerator()
    
    print(f"Generating {count} order lifecycles...")
    
    for i in range(count):
        await generator.generate_order_lifecycle()
        if i < count - 1:
            await asyncio.sleep(delay)
    
    print("Done")

if __name__ == "__main__":
    asyncio.run(main())