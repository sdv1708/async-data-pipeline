.PHONY: help install setup up down logs ps clean init-db run-consumer run-producer test-pipeline health-check

help:
	@echo "🚀 Async Kafka Pipeline - Available Commands:"
	@echo ""
	@echo "📦 Setup & Installation:"
	@echo "  make install      - Install Python dependencies"
	@echo "  make setup        - Complete setup (install + infrastructure + init-db)"
	@echo ""
	@echo "🏗️  Infrastructure:"
	@echo "  make up           - Start all services (Kafka, PostgreSQL, Redis)"
	@echo "  make down         - Stop all services"
	@echo "  make logs         - Show service logs"
	@echo "  make ps           - Show running containers"
	@echo "  make health-check - Check service health"
	@echo ""
	@echo "🗄️  Database:"
	@echo "  make init-db      - Initialize database tables"
	@echo ""
	@echo "🔄 Pipeline:"
	@echo "  make run-consumer - Start the Kafka consumer"
	@echo "  make run-producer - Start the event producer (for testing)"
	@echo "  make test-avro    - Test Avro schema and serialization"
	@echo "  make test-avro-integration - Test Avro with Kafka integration"
	@echo "  make test-pipeline - Run complete pipeline test"
	@echo ""
	@echo "📊 Monitoring:"
	@echo "  make open-grafana  - Open Grafana dashboard"
	@echo "  make open-prometheus - Open Prometheus"
	@echo "  make metrics       - Show current metrics"
	@echo "  make monitoring-status - Check monitoring stack"
	@echo ""
	@echo "🧹 Cleanup:"
	@echo "  make clean        - Clean up everything"
	@echo ""
	@echo "🌐 Web UIs:"
	@echo "  Kafka UI: http://localhost:8080"
	@echo "  Grafana: http://localhost:3000 (admin/admin)"
	@echo "  Prometheus: http://localhost:9090"

# Installation and Setup
install:
	@echo "📦 Installing Python dependencies..."
	poetry install
	@echo "✅ Dependencies installed!"

setup: install up init-db setup-monitoring
	@echo "🎉 Setup complete! Ready to run the pipeline."

setup-monitoring:
	@echo "🔧 Setting up monitoring..."
	poetry run python tools/monitoring_setup.py

# Infrastructure Management
up:
	@echo "🏗️  Starting infrastructure services..."
	docker-compose up -d
	@echo "⏳ Waiting for services to be healthy..."
	@sleep 15
	@make health-check
	@echo "✅ Services are running!"
	@echo "🌐 Kafka UI: http://localhost:8080"
	@echo "🌐 Grafana: http://localhost:3000 (admin/admin)"
	@echo "🌐 Prometheus: http://localhost:9090"

down:
	@echo "🛑 Stopping all services..."
	docker-compose down

logs:
	docker-compose logs -f

ps:
	docker-compose ps

health-check:
	@echo "🔍 Checking service health..."
	poetry run python tools/health_check.py

# Database Operations
init-db:
	@echo "🗄️  Initializing database..."
	poetry run python scripts/init_db.py
	@echo "✅ Database initialized!"

# Pipeline Operations
run-consumer:
	@echo "🔄 Starting Kafka consumer..."
	@echo "Press Ctrl+C to stop"
	poetry run python app/consumer/worker.py

run-producer:
	@echo "📤 Starting event producer..."
	@echo "This will generate test events. Press Ctrl+C to stop"
	poetry run python tools/event_producer.py

# Testing
test-avro:
	@echo "🧪 Testing Avro schema and serialization..."
	poetry run python tools/test_avro_schema.py

test-avro-integration:
	@echo "🧪 Testing Avro integration with Kafka..."
	poetry run python tools/test_avro_integration.py

test-pipeline: 
	@echo "🧪 Running complete pipeline test..."
	@echo "1. Testing Avro schema..."
	@make test-avro
	@echo "2. Checking if services are healthy..."
	@poetry run python tools/health_check.py || (echo "❌ Services not ready. Run 'make up' first." && exit 1)
	@echo "3. Testing Avro integration..."
	@make test-avro-integration
	@echo "4. Generating test events..."
	poetry run python tools/event_producer.py --count 5 --delay 1
	@echo "5. Check results in database..."
	@make check-db
	@echo "✅ Pipeline test completed!"

# Development helpers
create-topics:
	@echo "📝 Creating Kafka topics..."
	docker exec kafka kafka-topics --create --topic orders.raw --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1 --if-not-exists
	docker exec kafka kafka-topics --create --topic orders.processed --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1 --if-not-exists
	@echo "✅ Topics created!"

list-topics:
	@echo "📋 Kafka topics:"
	docker exec kafka kafka-topics --list --bootstrap-server localhost:9092

consume-raw:
	@echo "👂 Listening to raw events (Ctrl+C to stop)..."
	docker exec kafka kafka-console-consumer --topic orders.raw --bootstrap-server localhost:9092 --from-beginning

# Monitoring
monitor-redis:
	@echo "📊 Redis monitoring (Ctrl+C to stop)..."
	docker exec -it redis redis-cli monitor

check-db:
	@echo "🔍 Database status:"
	docker exec postgres psql -U pipeline_user -d orders_db -c "\dt"
	@echo ""
	@echo "Event count:"
	docker exec postgres psql -U pipeline_user -d orders_db -c "SELECT COUNT(*) as total_events FROM order_events;"
	@echo ""
	@echo "Order states:"
	docker exec postgres psql -U pipeline_user -d orders_db -c "SELECT order_id, status, total_amount FROM order_states LIMIT 5;"

# Monitoring commands
open-grafana:
	@echo "🌐 Opening Grafana dashboard..."
	@echo "URL: http://localhost:3000"
	@echo "Login: admin/admin"

open-prometheus:
	@echo "🌐 Opening Prometheus..."
	@echo "URL: http://localhost:9090"

metrics:
	@echo "📊 Application metrics:"
	@curl -s http://localhost:8000/metrics | grep -E "(events_|processing_|fraud_)" || echo "Metrics server not running. Start consumer first."

monitoring-status:
	@echo "📊 Monitoring Stack Status:"
	@docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" --filter "name=prometheus" --filter "name=grafana" --filter "name=node-exporter"

# Cleanup
clean:
	@echo "🧹 Cleaning up..."
	docker-compose down -v
	docker system prune -f
	rm -rf __pycache__ .pytest_cache .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Cleanup complete!"

# Quick start for new users
quickstart:
	@echo "🚀 Quick Start Guide:"
	@echo ""
	@echo "1. First time setup:"
	@echo "   make setup"
	@echo ""
	@echo "2. Run the pipeline:"
	@echo "   # Terminal 1: Start consumer"
	@echo "   make run-consumer"
	@echo ""
	@echo "   # Terminal 2: Send test events"
	@echo "   make run-producer"
	@echo ""
	@echo "3. Monitor:"
	@echo "   make check-db"
	@echo "   make logs"