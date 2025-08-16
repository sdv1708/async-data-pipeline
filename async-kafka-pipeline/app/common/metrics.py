from prometheus_client import Counter, Gauge, Histogram, generate_latest, start_http_server
import time
from functools import wraps
from app.common.logging import get_logger

logger = get_logger(__name__)

# Define Metrics
events_received = Counter('events_received_total', 'Total number of events received', ['event_type'])
events_processed = Counter('events_processed_total', 'Total number of events processed', ['event_type', 'status'])
events_enriched = Counter('events_enriched_total', 'Total number of events enriched', ['event_type'])
fraud_checks = Counter('fraud_checks_total', 'Total number of fraud checks', ['result'])
cache_hits = Counter('cache_hits_total', 'Total cache hits', ['cache_type'])
cache_misses = Counter('cache_misses_total', 'Total cache misses', ['cache_type'])

processing_duration = Histogram('event_processing_duration_seconds', 'Duration of event processing in seconds', ['event_type'])
enrichment_duration = Histogram('enrichment_duration_seconds', 'Duration of event enrichment in seconds', ['event_type'])
fraud_check_duration = Histogram('fraud_check_duration_seconds', 'Duration of fraud checks in seconds')

kafka_lag = Gauge('kafka_lag', 'Current Kafka lag', ['topic', 'partition'])
active_consumers = Gauge('active_consumers', 'Number of active consumers')
redis_connections = Gauge('redis_connections', 'Number of Redis connections')
db_connections = Gauge('db_connections', 'Number of database connections')

def timing_decorator(metric_name):
    """Decorator to time function execution"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                if metric_name == 'processing':
                    # Extract event_type from args if available
                    event_type = 'unknown'
                    if len(args) > 1 and hasattr(args[1], 'value'):
                        event_type = args[1].value.get('event_type', 'unknown')
                    processing_duration.labels(event_type=event_type).observe(duration)
                elif metric_name == 'enrichment':
                    event_type = 'unknown'
                    if len(args) > 0 and isinstance(args[0], dict):
                        event_type = args[0].get('event_type', 'unknown')
                    enrichment_duration.labels(event_type=event_type).observe(duration)
                elif metric_name == 'fraud':
                    fraud_check_duration.observe(duration)
                    
                return result
            except Exception as e:
                duration = time.time() - start_time
                # Still record the duration even on error
                if metric_name == 'processing':
                    event_type = 'unknown'
                    if len(args) > 1 and hasattr(args[1], 'value'):
                        event_type = args[1].value.get('event_type', 'unknown')
                    processing_duration.labels(event_type=event_type).observe(duration)
                raise
        return wrapper
    return decorator

def start_metrics_server(port=8000):
    """Start Prometheus metrics HTTP server"""
    try:
        start_http_server(port)
        logger.info("metrics_server_started", port=port)
    except Exception as e:
        logger.error("metrics_server_failed", error=str(e), port=port)

def record_event_received(event_type):
    """Record an event received"""
    events_received.labels(event_type=event_type).inc()

def record_event_processed(event_type, status='success'):
    """Record an event processed"""
    events_processed.labels(event_type=event_type, status=status).inc()

def record_event_enriched(event_type):
    """Record an event enriched"""
    events_enriched.labels(event_type=event_type).inc()

def record_fraud_check(result):
    """Record a fraud check result"""
    fraud_checks.labels(result=result).inc()

def record_cache_hit(cache_type):
    """Record a cache hit"""
    cache_hits.labels(cache_type=cache_type).inc()

def record_cache_miss(cache_type):
    """Record a cache miss"""
    cache_misses.labels(cache_type=cache_type).inc()

def update_kafka_lag(topic, partition, lag):
    """Update Kafka consumer lag"""
    kafka_lag.labels(topic=topic, partition=partition).set(lag)

def set_active_consumers(count):
    """Set number of active consumers"""
    active_consumers.set(count)