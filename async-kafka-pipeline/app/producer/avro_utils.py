# app/producer/avro_utils.py
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import fastavro
from fastavro import writer, reader, parse_schema
from io import BytesIO
from app.common.logging import get_logger

logger = get_logger(__name__)

class AvroSchemaManager:
    """Manages Avro schemas for the producer"""
    
    def __init__(self, schema_dir: Optional[str] = None):
        if schema_dir is None:
            # Default to schemas directory relative to this file
            self.schema_dir = Path(__file__).parent / "schemas"
        else:
            self.schema_dir = Path(schema_dir)
        
        self._schemas: Dict[str, Dict] = {}
        self._parsed_schemas: Dict[str, Dict] = {}
        
    def load_schema(self, schema_name: str) -> Dict[str, Any]:
        """Load and cache an Avro schema from file"""
        if schema_name in self._schemas:
            return self._schemas[schema_name]
        
        schema_file = self.schema_dir / f"{schema_name}.avsc"
        
        if not schema_file.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_file}")
        
        try:
            with open(schema_file, 'r') as f:
                schema = json.load(f)
            
            # Parse and validate the schema
            parsed_schema = parse_schema(schema)
            
            self._schemas[schema_name] = schema
            self._parsed_schemas[schema_name] = parsed_schema
            
            logger.info("avro_schema_loaded", schema_name=schema_name, file=str(schema_file))
            return schema
            
        except Exception as e:
            logger.error("avro_schema_load_failed", schema_name=schema_name, error=str(e))
            raise
    
    def get_parsed_schema(self, schema_name: str) -> Dict[str, Any]:
        """Get the parsed schema for serialization"""
        if schema_name not in self._parsed_schemas:
            self.load_schema(schema_name)
        return self._parsed_schemas[schema_name]
    
    def serialize(self, schema_name: str, data: Dict[str, Any]) -> bytes:
        """Serialize data using the specified schema"""
        try:
            parsed_schema = self.get_parsed_schema(schema_name)
            
            # Create a BytesIO buffer
            buffer = BytesIO()
            
            # Write the data using fastavro
            writer(buffer, parsed_schema, [data])
            
            # Get the serialized bytes
            serialized_data = buffer.getvalue()
            buffer.close()
            
            logger.debug("avro_serialization_success", 
                        schema_name=schema_name, 
                        data_size=len(serialized_data))
            
            return serialized_data
            
        except Exception as e:
            logger.error("avro_serialization_failed", 
                        schema_name=schema_name, 
                        error=str(e))
            raise
    
    def deserialize(self, schema_name: str, data: bytes) -> Dict[str, Any]:
        """Deserialize data using the specified schema"""
        try:
            parsed_schema = self.get_parsed_schema(schema_name)
            
            # Create a BytesIO buffer from the data
            buffer = BytesIO(data)
            
            # Read the data using fastavro
            records = list(reader(buffer, parsed_schema))
            buffer.close()
            
            if not records:
                raise ValueError("No records found in serialized data")
            
            # Return the first (and should be only) record
            result = records[0]
            
            logger.debug("avro_deserialization_success", 
                        schema_name=schema_name, 
                        record_count=len(records))
            
            return result
            
        except Exception as e:
            logger.error("avro_deserialization_failed", 
                        schema_name=schema_name, 
                        error=str(e))
            raise
    
    def validate_data(self, schema_name: str, data: Dict[str, Any]) -> bool:
        """Validate data against the schema without serializing"""
        try:
            parsed_schema = self.get_parsed_schema(schema_name)
            
            # Try to serialize to validate - if it works, data is valid
            buffer = BytesIO()
            writer(buffer, parsed_schema, [data])
            buffer.close()
            
            logger.debug("avro_validation_success", schema_name=schema_name)
            return True
            
        except Exception as e:
            logger.warning("avro_validation_failed", 
                          schema_name=schema_name, 
                          error=str(e))
            return False

# Global schema manager instance
schema_manager = AvroSchemaManager()

def get_order_event_schema() -> Dict[str, Any]:
    """Get the order event schema"""
    return schema_manager.load_schema("order_event")

def serialize_order_event(data: Dict[str, Any]) -> bytes:
    """Serialize order event data to Avro bytes"""
    return schema_manager.serialize("order_event", data)

def deserialize_order_event(data: bytes) -> Dict[str, Any]:
    """Deserialize order event data from Avro bytes"""
    return schema_manager.deserialize("order_event", data)

def validate_order_event(data: Dict[str, Any]) -> bool:
    """Validate order event data against schema"""
    return schema_manager.validate_data("order_event", data)