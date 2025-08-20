from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from aiokafka.errors import KafkaError
import json
from typing import Any, Dict, List, Optional, Union
from app.common.logging import get_logger
from app.producer.avro_utils import serialize_order_event

logger = get_logger(__name__)

class KafkaProducerClient:
    def __init__(self, bootstrap_servers: str = 'localhost:9092', use_avro: bool = True):
        self.bootstrap_servers = bootstrap_servers
        self.use_avro = use_avro
        self.producer = Optional[AIOKafkaProducer] = None

    async def start(self):
        """Initialize and start the Kafka producer."""
        try:
            # Choose serializer based on configuration
            if self.use_avro:
                value_serializer = self._avro_serializer
            else:
                value_serializer = lambda v: json.dumps(v).encode('utf-8')
            
            self.producer = AIOKafkaProducer(
                bootstrap_servers = self.bootstrap_servers,
                value_serializer=value_serializer, 
                key_serializer=lambda k: k.encode('utf-8') if k else None,  # Keys are strings (order_id)
                acks='all', # Ensure all replicas acknowledge the write
                enable_idempotence=True, # Enable idempotence to avoid duplicate messages
                max_in_flight_requests_per_connection=5, # Limit in-flight requests,
                compression_type='gzip'
            )

            await self.producer.start()
            logger.info("Kafka producer started successfully", 
                       servers=self.bootstrap_servers, 
                       serialization="avro" if self.use_avro else "json")

        except Exception as e:
            logger.error("Failed to initialize Kafka producer", exc_info=True)
            raise
    
    def _avro_serializer(self, value: Dict[str, Any]) -> bytes:
        """Serialize value using Avro schema"""
        try:
            return serialize_order_event(value)
        except Exception as e:
            logger.error("avro_serialization_error", error=str(e), value_keys=list(value.keys()) if isinstance(value, dict) else "not_dict")
            raise


    async def stop(self):
        """Stop the Kafka producer."""
        if self.producer:
            try:
                await self.producer.stop()
                logger.info("Kafka producer stopped successfully")
            except Exception as e:
                logger.error("Failed to stop Kafka producer", exc_info=True)

    async def send_event(self, topic: str, event: Dict[str, Any], key: Optional[Union[str, int]] = None):
        """Send an event to a Kafka topic."""
        if not self.producer:
            raise RuntimeError("Producer is not started. Call start() before sending messages.")
        try:
            result = await self.producer.send_and_wait(topic=topic,
                                                    value=event,
                                                    key=key)
            logger.info("Event sent successfully", topic=topic, 
                        partition=result.partition, 
                        offset=result.offset, 
                        event_id=event.get("id"))
            
            return {"partition": result.partition, "offset": result.offset, "topic": topic}
        
        except KafkaError as e:
            logger.error("Failed to send event to Kafka", 
                         topic=topic, 
                         error=str(e), 
                         event_id=event.get("id")
                         )
            raise