#!/usr/bin/env python3
"""
End-to-end integration test for Avro serialization in Kafka pipeline
"""
import sys
import asyncio
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.common.avro_kafka_client import AvroKafkaProducer, AvroKafkaConsumer
from app.producer.schemas import create_order_created_event, OrderItem, Address
from app.common.logging import get_logger

logger = get_logger(__name__)

async def test_avro_producer_consumer():
    """Test Avro serialization between producer and consumer"""
    print("🧪 Testing Avro Producer-Consumer Integration")
    print("=" * 60)
    
    # Test configuration
    test_topic = "test.orders.avro"
    bootstrap_servers = "localhost:9092"
    
    producer = None
    consumer = None
    
    try:
        # Create test event
        print("📝 Creating test event...")
        items = [
            OrderItem(
                sku="TEST-SKU-001",
                product_name="Test Product",
                quantity=2,
                unit_price=49.99,
                category="test"
            )
        ]
        
        address = Address(
            street="123 Test Street",
            city="Test City",
            state="TS",
            postal_code="12345",
            country="US"
        )
        
        event = create_order_created_event(
            order_id="TEST-ORDER-001",
            user_id="TEST-USER-001",
            items=items,
            shipping_address=address
        )
        
        event.source = "integration_test"
        avro_data = event.to_avro_dict()
        
        print(f"✅ Test event created: {event.event_id}")
        print(f"   Order ID: {event.order_id}")
        print(f"   Total Amount: ${event.payload.total_amount}")
        
        # Start producer
        print("\n🚀 Starting Avro producer...")
        producer = AvroKafkaProducer(
            bootstrap_servers=bootstrap_servers,
            use_avro=True
        )
        await producer.start()
        print("✅ Producer started")
        
        # Send event
        print("\n📤 Sending Avro event to Kafka...")
        result = await producer.send_event(
            topic=test_topic,
            event=avro_data,
            key=event.order_id,
            headers={
                'test': b'integration',
                'event_type': event.event_type.encode('utf-8')
            }
        )
        
        print(f"✅ Event sent successfully")
        print(f"   Topic: {result['topic']}")
        print(f"   Partition: {result['partition']}")
        print(f"   Offset: {result['offset']}")
        
        # Start consumer
        print("\n🔄 Starting Avro consumer...")
        consumer = AvroKafkaConsumer(
            topics=[test_topic],
            group_id="test-integration-group",
            bootstrap_servers=bootstrap_servers,
            use_avro=True,
            auto_offset_reset='earliest'
        )
        await consumer.start()
        print("✅ Consumer started")
        
        # Consume and validate message
        print("\n📥 Consuming Avro message...")
        message_received = False
        
        async def message_handler(message):
            nonlocal message_received
            
            print(f"📨 Message received:")
            print(f"   Topic: {message.topic}")
            print(f"   Partition: {message.partition}")
            print(f"   Offset: {message.offset}")
            print(f"   Key: {message.key}")
            
            # Validate headers
            if message.headers:
                headers = dict(message.headers)
                print(f"   Headers: {headers}")
            
            # Validate deserialized data
            received_data = message.value
            print(f"   Event ID: {received_data.get('event_id')}")
            print(f"   Event Type: {received_data.get('event_type')}")
            print(f"   Order ID: {received_data.get('order_id')}")
            print(f"   Source: {received_data.get('source')}")
            
            # Validate payload
            payload = received_data.get('payload', {})
            print(f"   User ID: {payload.get('user_id')}")
            print(f"   Total Amount: ${payload.get('total_amount')}")
            print(f"   Items Count: {len(payload.get('items', []))}")
            
            # Validate data integrity
            assert received_data['event_id'] == avro_data['event_id']
            assert received_data['order_id'] == avro_data['order_id']
            assert received_data['event_type'] == avro_data['event_type']
            assert received_data['source'] == avro_data['source']
            assert payload['user_id'] == avro_data['payload']['user_id']
            assert payload['total_amount'] == avro_data['payload']['total_amount']
            
            print("✅ Data integrity validation passed")
            message_received = True
        
        # Set up timeout for message consumption
        try:
            await asyncio.wait_for(
                consumer.consume_messages(message_handler),
                timeout=10.0
            )
        except asyncio.TimeoutError:
            if not message_received:
                print("⏰ Timeout waiting for message")
                return False
        
        if message_received:
            print("\n🎉 Integration test completed successfully!")
            print("✅ Avro serialization/deserialization working correctly")
            print("✅ Producer-Consumer communication established")
            print("✅ Data integrity maintained")
            return True
        else:
            print("\n❌ Integration test failed - no message received")
            return False
            
    except Exception as e:
        print(f"\n❌ Integration test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        print("\n🧹 Cleaning up...")
        if producer:
            await producer.stop()
            print("✅ Producer stopped")
        if consumer:
            await consumer.stop()
            print("✅ Consumer stopped")

async def test_json_fallback():
    """Test JSON fallback compatibility"""
    print("\n🧪 Testing JSON Fallback Compatibility")
    print("=" * 60)
    
    try:
        # Test with JSON producer and Avro consumer
        print("📝 Testing JSON producer → Avro consumer...")
        
        json_producer = AvroKafkaProducer(use_avro=False)  # JSON mode
        avro_consumer = AvroKafkaConsumer(
            topics=["test.json.fallback"],
            group_id="test-json-fallback-group",
            use_avro=True  # Avro mode with JSON fallback
        )
        
        await json_producer.start()
        await avro_consumer.start()
        
        # Send JSON event
        json_event = {
            "event_id": "json-test-001",
            "event_type": "ORDER_CREATED",
            "order_id": "JSON-ORDER-001",
            "timestamp": 1640995200000,
            "source": "json_test",
            "version": "1.0",
            "payload": {
                "user_id": "JSON-USER-001",
                "total_amount": 99.99,
                "currency": "USD"
            }
        }
        
        await json_producer.send_event(
            topic="test.json.fallback",
            event=json_event,
            key=json_event["order_id"]
        )
        
        print("✅ JSON event sent")
        
        # Try to consume with Avro consumer (should fallback to JSON)
        fallback_worked = False
        
        async def fallback_handler(message):
            nonlocal fallback_worked
            received = message.value
            if received and received.get('event_id') == 'json-test-001':
                print("✅ JSON fallback deserialization worked")
                fallback_worked = True
        
        try:
            await asyncio.wait_for(
                avro_consumer.consume_messages(fallback_handler),
                timeout=5.0
            )
        except asyncio.TimeoutError:
            pass
        
        await json_producer.stop()
        await avro_consumer.stop()
        
        if fallback_worked:
            print("✅ JSON fallback compatibility confirmed")
            return True
        else:
            print("❌ JSON fallback failed")
            return False
            
    except Exception as e:
        print(f"❌ JSON fallback test failed: {e}")
        return False

async def main():
    """Run all integration tests"""
    print("🚀 Avro Integration Test Suite")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 2
    
    # Test 1: Avro producer-consumer integration
    if await test_avro_producer_consumer():
        tests_passed += 1
    
    # Test 2: JSON fallback compatibility
    if await test_json_fallback():
        tests_passed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Integration Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All integration tests passed!")
        print("✅ Avro serialization is production-ready")
        return 0
    else:
        print("❌ Some integration tests failed")
        print("💡 Make sure Kafka is running: make up")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)