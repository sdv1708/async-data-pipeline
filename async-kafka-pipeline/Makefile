.PHONY: help up down logs ps clean

help:
	@echo "Available commands:"
	@echo "  make up     - Start all services"
	@echo "  make down   - Stop all services"
	@echo "  make logs   - Show logs"
	@echo "  make ps     - Show running containers"
	@echo "  make clean  - Clean up everything"

up:
	docker-compose up -d
	@echo "Waiting for services to be healthy..."
	@sleep 10
	@echo "Services are running!"
	@echo "Kafka UI: http://localhost:8080"

down:
	docker-compose down

logs:
	docker-compose logs -f

ps:
	docker-compose ps

clean:
	docker-compose down -v
	rm -rf __pycache__ .pytest_cache .coverage