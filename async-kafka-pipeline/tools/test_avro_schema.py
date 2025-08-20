#!/usr/bin/env python3
"""
Test script to validate Avro schema and serialization
"""
import sys
import json
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.producer.schemas import OrderEvent, OrderItem, Address, EventType, PaymentMethod, create_order_created_event
from app.producer.avro_utils import (
    get_order_event_schema, 
    serialize_order_event, 
    deserialize_order_event, 
    validate_order_event
)
from app.common.logging import get_logger

logger = get_logger(__name__)

def test_schema_loading():
    """Test that the Avro schema loads correctly"""
    print("🔍 Testing schema loading...")
    try:
        schema = get_order_event_schema()
        print(f"✅ Schema loaded successfully: {schema['name']}")
        print(f"   Namespace: {schema['namespace']}")
        print(f"   Fields: {len(schema['fields'])}")
        return True
    except Exception as e:
        print(f"❌ Schema loading failed: {e}")
        return False

def test_pydantic_model():
    """Test Pydantic model creation"""
    print("\n🔍 Testing Pydantic model...")
    try:
        # Create sample items
        items = [
            OrderItem(
                sku="SKU-12345",
                product_name="Test Product",
                quantity=2,
                unit_price=29.99,
                category="electronics"
            )
        ]
        
        # Create address
        address = Address(
            street="123 Test St",
            city="Test City",
            state="CA",
            postal_code="12345",
            country="US"
        )
        
        # Create event
        event = create_order_created_event(
            order_id="ORD-TEST-001",
            user_id="USR-123456",
            items=items,
            shipping_address=address
        )
        
        print(f"✅ Pydantic model created successfully")
        print(f"   Event ID: {event.event_id}")
        print(f"   Order ID: {event.order_id}")
        print(f"   Event Type: {event.event_type}")
        print(f"   Total Amount: ${event.payload.total_amount}")
        
        return event
    except Exception as e:
        print(f"❌ Pydantic model creation failed: {e}")
        return None

def test_avro_serialization(event):
    """Test Avro serialization and deserialization"""
    print("\n🔍 Testing Avro serialization...")
    try:
        # Convert to Avro dict
        avro_data = event.to_avro_dict()
        print(f"✅ Converted to Avro dict")
        
        # Validate against schema
        is_valid = validate_order_event(avro_data)
        print(f"✅ Schema validation: {'PASSED' if is_valid else 'FAILED'}")
        
        if not is_valid:
            return False
        
        # Serialize to bytes
        serialized = serialize_order_event(avro_data)
        print(f"✅ Serialized to {len(serialized)} bytes")
        
        # Deserialize back
        deserialized = deserialize_order_event(serialized)
        print(f"✅ Deserialized successfully")
        
        # Compare key fields
        assert deserialized['event_id'] == avro_data['event_id']
        assert deserialized['order_id'] == avro_data['order_id']
        assert deserialized['event_type'] == avro_data['event_type']
        print(f"✅ Round-trip validation passed")
        
        return True
    except Exception as e:
        print(f"❌ Avro serialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_schema_evolution():
    """Test that our schema supports evolution"""
    print("\n🔍 Testing schema evolution compatibility...")
    try:
        # Test with minimal required fields
        minimal_event = {
            "event_id": "test-123",
            "event_type": "ORDER_CREATED",
            "order_id": "ORD-MIN-001",
            "timestamp": 1640995200000,
            "source": "test",
            "version": "1.0",
            "payload": {
                "user_id": None,
                "total_amount": None,
                "currency": "USD",
                "status": None,
                "items": None,
                "shipping_address": None,
                "payment_method": None,
                "payment_id": None,
                "metadata": None
            }
        }
        
        # Validate minimal event
        is_valid = validate_order_event(minimal_event)
        print(f"✅ Minimal event validation: {'PASSED' if is_valid else 'FAILED'}")
        
        if is_valid:
            # Try serialization
            serialized = serialize_order_event(minimal_event)
            deserialized = deserialize_order_event(serialized)
            print(f"✅ Minimal event round-trip: PASSED")
        
        return is_valid
    except Exception as e:
        print(f"❌ Schema evolution test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Avro Schema Validation Tests")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 4
    
    # Test 1: Schema loading
    if test_schema_loading():
        tests_passed += 1
    
    # Test 2: Pydantic model
    event = test_pydantic_model()
    if event:
        tests_passed += 1
        
        # Test 3: Avro serialization (only if Pydantic model worked)
        if test_avro_serialization(event):
            tests_passed += 1
    
    # Test 4: Schema evolution
    if test_schema_evolution():
        tests_passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Avro schema is ready for production.")
        return 0
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)