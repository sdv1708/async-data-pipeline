# tools/health_check.py
import asyncio
import redis.asyncio as redis
import asyncpg
from aiokafka import AIOKafkaProducer
from app.common.logging import get_logger

logger = get_logger(__name__)

async def check_kafka():
    """Check Kafka connectivity"""
    try:
        producer = AIOKafkaProducer(bootstrap_servers="localhost:9092")
        await producer.start()
        await producer.stop()
        print("✅ Kafka: Connected")
        return True
    except Exception as e:
        print(f"❌ Kafka: Failed - {e}")
        return False

async def check_redis():
    """Check Redis connectivity"""
    try:
        client = redis.from_url("redis://localhost:6379")
        await client.ping()
        await client.close()
        print("✅ Redis: Connected")
        return True
    except Exception as e:
        print(f"❌ Redis: Failed - {e}")
        return False

async def check_postgres():
    """Check PostgreSQL connectivity"""
    try:
        conn = await asyncpg.connect(
            "postgresql://pipeline_user:pipeline_pass@localhost:5432/orders_db"
        )
        await conn.execute("SELECT 1")
        await conn.close()
        print("✅ PostgreSQL: Connected")
        return True
    except Exception as e:
        print(f"❌ PostgreSQL: Failed - {e}")
        return False

async def main():
    """Run all health checks"""
    print("🔍 Running health checks...\n")
    
    results = await asyncio.gather(
        check_kafka(),
        check_redis(),
        check_postgres(),
        return_exceptions=True
    )
    
    success_count = sum(1 for r in results if r is True)
    total_count = len(results)
    
    print(f"\n📊 Health Check Results: {success_count}/{total_count} services healthy")
    
    if success_count == total_count:
        print("🎉 All services are healthy!")
        return 0
    else:
        print("⚠️  Some services are not healthy. Check the logs above.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)