#!/usr/bin/env python3
"""
Monitoring setup and validation script
"""
import asyncio
import httpx
import time
from app.common.logging import get_logger

logger = get_logger(__name__)

async def wait_for_service(url, service_name, timeout=60):
    """Wait for a service to become available"""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"✅ {service_name} is ready at {url}")
                    return True
        except Exception:
            pass
        
        print(f"⏳ Waiting for {service_name}...")
        await asyncio.sleep(5)
    
    print(f"❌ {service_name} failed to start within {timeout} seconds")
    return False

async def setup_grafana_datasource():
    """Setup Grafana datasource if not already configured"""
    try:
        async with httpx.AsyncClient() as client:
            # Check if datasource exists
            response = await client.get(
                "http://localhost:3000/api/datasources",
                auth=("admin", "admin")
            )
            
            if response.status_code == 200:
                datasources = response.json()
                prometheus_exists = any(ds.get('type') == 'prometheus' for ds in datasources)
                
                if prometheus_exists:
                    print("✅ Prometheus datasource already configured")
                    return True
                
                # Create datasource
                datasource_config = {
                    "name": "Prometheus",
                    "type": "prometheus",
                    "url": "http://prometheus:9090",
                    "access": "proxy",
                    "isDefault": True
                }
                
                response = await client.post(
                    "http://localhost:3000/api/datasources",
                    json=datasource_config,
                    auth=("admin", "admin")
                )
                
                if response.status_code == 200:
                    print("✅ Prometheus datasource created")
                    return True
                else:
                    print(f"❌ Failed to create datasource: {response.text}")
                    return False
                    
    except Exception as e:
        print(f"❌ Error setting up Grafana: {e}")
        return False

async def validate_metrics():
    """Validate that application metrics are being exposed"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/metrics", timeout=5)
            
            if response.status_code == 200:
                metrics_text = response.text
                
                # Check for key metrics
                expected_metrics = [
                    'events_received_total',
                    'events_processed_total',
                    'processing_duration_seconds'
                ]
                
                found_metrics = []
                for metric in expected_metrics:
                    if metric in metrics_text:
                        found_metrics.append(metric)
                
                print(f"✅ Found {len(found_metrics)}/{len(expected_metrics)} expected metrics")
                
                if len(found_metrics) == len(expected_metrics):
                    return True
                else:
                    missing = set(expected_metrics) - set(found_metrics)
                    print(f"❌ Missing metrics: {missing}")
                    return False
            else:
                print(f"❌ Metrics endpoint returned {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Cannot reach metrics endpoint: {e}")
        print("💡 Make sure the consumer is running with: make run-consumer")
        return False

async def main():
    """Main monitoring setup"""
    print("🔧 Setting up monitoring stack...\n")
    
    # Wait for services
    services = [
        ("http://localhost:9090/-/healthy", "Prometheus"),
        ("http://localhost:3000/api/health", "Grafana")
    ]
    
    all_ready = True
    for url, name in services:
        ready = await wait_for_service(url, name)
        if not ready:
            all_ready = False
    
    if not all_ready:
        print("\n❌ Some services are not ready. Check docker-compose logs.")
        return 1
    
    print("\n🔧 Configuring Grafana...")
    grafana_ok = await setup_grafana_datasource()
    
    print("\n📊 Validating application metrics...")
    metrics_ok = await validate_metrics()
    
    print("\n" + "="*50)
    
    if grafana_ok and metrics_ok:
        print("🎉 Monitoring setup complete!")
        print("\n🌐 Access your dashboards:")
        print("  • Grafana: http://localhost:3000 (admin/admin)")
        print("  • Prometheus: http://localhost:9090")
        print("  • Kafka UI: http://localhost:8080")
        print("\n📊 To view metrics:")
        print("  make metrics")
        return 0
    else:
        print("⚠️  Monitoring setup completed with issues.")
        print("Check the logs above for details.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)