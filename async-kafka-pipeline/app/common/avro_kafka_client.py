# app/common/avro_kafka_client.py
"""
Avro-enabled Kafka client for both producer and consumer operations
"""
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from aiokafka.errors import KafkaError
import json
from typing import Any, Dict, List, Optional, Union, Callable
from app.common.logging import get_logger
from app.producer.avro_utils import serialize_order_event, deserialize_order_event

logger = get_logger(__name__)

class AvroKafkaProducer:
    """Kafka producer with Avro serialization support"""
    
    def __init__(
        self, 
        bootstrap_servers: str = 'localhost:9092',
        use_avro: bool = True,
        compression_type: str = 'gzip'
    ):
        self.bootstrap_servers = bootstrap_servers
        self.use_avro = use_avro
        self.compression_type = compression_type
        self.producer: Optional[AIOKafkaProducer] = None
        
    async def start(self):
        """Initialize and start the Kafka producer"""
        try:
            # Configure serializers
            if self.use_avro:
                value_serializer = self._avro_value_serializer
                logger.info("Using Avro serialization")
            else:
                value_serializer = self._json_value_serializer
                logger.info("Using JSON serialization")
            
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=value_serializer,
                key_serializer=self._key_serializer,
                acks='all',  # Wait for all replicas
                enable_idempotence=True,  # Exactly-once semantics
                max_in_flight_requests_per_connection=5,
                compression_type=self.compression_type,
                retry_backoff_ms=100,
                request_timeout_ms=30000,
                delivery_timeout_ms=120000
            )
            
            await self.producer.start()
            logger.info(
                "avro_kafka_producer_started",
                servers=self.bootstrap_servers,
                serialization="avro" if self.use_avro else "json",
                compression=self.compression_type
            )
            
        except Exception as e:
            logger.error("avro_kafka_producer_start_failed", error=str(e))
            raise
    
    async def stop(self):
        """Stop the Kafka producer"""
        if self.producer:
            try:
                await self.producer.stop()
                logger.info("avro_kafka_producer_stopped")
            except Exception as e:
                logger.error("avro_kafka_producer_stop_failed", error=str(e))
    
    def _avro_value_serializer(self, value: Dict[str, Any]) -> bytes:
        """Serialize value using Avro schema"""
        try:
            return serialize_order_event(value)
        except Exception as e:
            logger.error(
                "avro_serialization_failed",
                error=str(e),
                value_type=type(value).__name__,
                value_keys=list(value.keys()) if isinstance(value, dict) else None
            )
            raise
    
    def _json_value_serializer(self, value: Dict[str, Any]) -> bytes:
        """Serialize value using JSON (fallback)"""
        try:
            return json.dumps(value).encode('utf-8')
        except Exception as e:
            logger.error("json_serialization_failed", error=str(e))
            raise
    
    def _key_serializer(self, key: Optional[str]) -> Optional[bytes]:
        """Serialize key as UTF-8 string"""
        return key.encode('utf-8') if key else None
    
    async def send_event(
        self,
        topic: str,
        event: Dict[str, Any],
        key: Optional[str] = None,
        partition: Optional[int] = None,
        headers: Optional[Dict[str, bytes]] = None
    ) -> Dict[str, Any]:
        """Send an event to Kafka topic"""
        if not self.producer:
            raise RuntimeError("Producer not started. Call start() first.")
        
        try:
            # Add metadata headers
            if headers is None:
                headers = {}
            
            headers.update({
                'serialization': b'avro' if self.use_avro else b'json',
                'schema_version': b'1.0',
                'producer': b'async-kafka-pipeline'
            })
            
            # Send the event
            result = await self.producer.send_and_wait(
                topic=topic,
                value=event,
                key=key,
                partition=partition,
                headers=headers
            )
            
            logger.info(
                "event_sent_successfully",
                topic=topic,
                partition=result.partition,
                offset=result.offset,
                key=key,
                event_id=event.get('event_id'),
                serialization="avro" if self.use_avro else "json"
            )
            
            return {
                "topic": topic,
                "partition": result.partition,
                "offset": result.offset,
                "key": key,
                "timestamp": result.timestamp
            }
            
        except KafkaError as e:
            logger.error(
                "kafka_send_failed",
                topic=topic,
                key=key,
                error=str(e),
                event_id=event.get('event_id')
            )
            raise
        except Exception as e:
            logger.error(
                "event_send_failed",
                topic=topic,
                key=key,
                error=str(e),
                event_id=event.get('event_id')
            )
            raise

class AvroKafkaConsumer:
    """Kafka consumer with Avro deserialization support"""
    
    def __init__(
        self,
        topics: List[str],
        group_id: str,
        bootstrap_servers: str = 'localhost:9092',
        use_avro: bool = True,
        auto_offset_reset: str = 'earliest'
    ):
        self.topics = topics
        self.group_id = group_id
        self.bootstrap_servers = bootstrap_servers
        self.use_avro = use_avro
        self.auto_offset_reset = auto_offset_reset
        self.consumer: Optional[AIOKafkaConsumer] = None
        self.running = False
    
    async def start(self):
        """Initialize and start the Kafka consumer"""
        try:
            # Configure deserializers
            if self.use_avro:
                value_deserializer = self._avro_value_deserializer
                logger.info("Using Avro deserialization")
            else:
                value_deserializer = self._json_value_deserializer
                logger.info("Using JSON deserialization")
            
            self.consumer = AIOKafkaConsumer(
                *self.topics,
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.group_id,
                value_deserializer=value_deserializer,
                key_deserializer=self._key_deserializer,
                enable_auto_commit=False,  # Manual commit for control
                auto_offset_reset=self.auto_offset_reset,
                session_timeout_ms=30000,
                heartbeat_interval_ms=10000,
                max_poll_records=10,
                fetch_max_wait_ms=500
            )
            
            await self.consumer.start()
            self.running = True
            
            logger.info(
                "avro_kafka_consumer_started",
                topics=self.topics,
                group_id=self.group_id,
                servers=self.bootstrap_servers,
                serialization="avro" if self.use_avro else "json"
            )
            
        except Exception as e:
            logger.error("avro_kafka_consumer_start_failed", error=str(e))
            raise
    
    async def stop(self):
        """Stop the Kafka consumer"""
        self.running = False
        if self.consumer:
            try:
                await self.consumer.stop()
                logger.info("avro_kafka_consumer_stopped")
            except Exception as e:
                logger.error("avro_kafka_consumer_stop_failed", error=str(e))
    
    def _avro_value_deserializer(self, value: bytes) -> Optional[Dict[str, Any]]:
        """Deserialize Avro bytes to dictionary"""
        if value is None:
            return None
        
        try:
            return deserialize_order_event(value)
        except Exception as e:
            logger.error("avro_deserialization_failed", error=str(e))
            
            # Attempt JSON fallback for backward compatibility
            try:
                logger.warning("attempting_json_fallback")
                return json.loads(value.decode('utf-8'))
            except Exception as json_error:
                logger.error("json_fallback_failed", error=str(json_error))
                raise e  # Re-raise original Avro error
    
    def _json_value_deserializer(self, value: bytes) -> Optional[Dict[str, Any]]:
        """Deserialize JSON bytes to dictionary"""
        if value is None:
            return None
        
        try:
            return json.loads(value.decode('utf-8'))
        except Exception as e:
            logger.error("json_deserialization_failed", error=str(e))
            raise
    
    def _key_deserializer(self, key: Optional[bytes]) -> Optional[str]:
        """Deserialize key from UTF-8 bytes"""
        return key.decode('utf-8') if key else None
    
    async def consume_messages(self, message_handler: Callable):
        """Consume messages and process them with the provided handler"""
        if not self.consumer:
            raise RuntimeError("Consumer not started. Call start() first.")
        
        try:
            async for message in self.consumer:
                if not self.running:
                    break
                
                try:
                    # Process the message
                    await message_handler(message)
                    
                    # Commit offset after successful processing
                    await self.consumer.commit()
                    
                except Exception as e:
                    logger.error(
                        "message_processing_failed",
                        error=str(e),
                        topic=message.topic,
                        partition=message.partition,
                        offset=message.offset
                    )
                    # Don't commit on error - message will be reprocessed
                    
        except Exception as e:
            logger.error("consume_messages_failed", error=str(e))
            raise
        finally:
            await self.stop()

# Convenience functions for backward compatibility
async def create_avro_producer(
    bootstrap_servers: str = 'localhost:9092',
    use_avro: bool = True
) -> AvroKafkaProducer:
    """Create and start an Avro-enabled Kafka producer"""
    producer = AvroKafkaProducer(bootstrap_servers=bootstrap_servers, use_avro=use_avro)
    await producer.start()
    return producer

async def create_avro_consumer(
    topics: List[str],
    group_id: str,
    bootstrap_servers: str = 'localhost:9092',
    use_avro: bool = True
) -> AvroKafkaConsumer:
    """Create and start an Avro-enabled Kafka consumer"""
    consumer = AvroKafkaConsumer(
        topics=topics,
        group_id=group_id,
        bootstrap_servers=bootstrap_servers,
        use_avro=use_avro
    )
    await consumer.start()
    return consumer