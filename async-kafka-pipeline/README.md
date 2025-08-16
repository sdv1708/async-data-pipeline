# Async Kafka Pipeline

A production-ready async event processing pipeline built with Python, Kafka, PostgreSQL, and Redis.

## 🏗️ Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Producer  │───▶│    Kafka    │───▶│  Consumer   │───▶│ PostgreSQL  │
│             │    │             │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                              │
                                              ▼
                                      ┌─────────────┐
                                      │    Redis    │
                                      │   (Cache)   │
                                      └─────────────┘
```

### Components

- **Kafka**: Event streaming platform
- **PostgreSQL**: Event store and order state persistence
- **Redis**: Caching and deduplication
- **Consumer**: Async event processor with enrichment and fraud detection

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Poetry
- Docker & Docker Compose

### 1. Setup

```bash
# Clone and navigate to the project
cd async-kafka-pipeline

# Complete setup (install dependencies + start services + init database)
make setup
```

### 2. Run the Pipeline

**Terminal 1 - Start Consumer:**
```bash
make run-consumer
```

**Terminal 2 - Send Test Events:**
```bash
make run-producer
```

### 3. Monitor Results

```bash
# Check database
make check-db

# View service logs
make logs

# Monitor Redis
make monitor-redis
```

## 📋 Available Commands

Run `make help` to see all available commands:

```bash
make help
```

### Key Commands

| Command | Description |
|---------|-------------|
| `make setup` | Complete first-time setup |
| `make up` | Start infrastructure services |
| `make run-consumer` | Start the event consumer |
| `make run-producer` | Generate test events |
| `make test-pipeline` | Run automated pipeline test |
| `make health-check` | Check service connectivity |
| `make clean` | Clean up everything |

## 🔧 Manual Setup Steps

If you prefer to run steps manually:

### 1. Install Dependencies
```bash
poetry install
```

### 2. Start Infrastructure
```bash
docker-compose up -d
```

### 3. Wait for Services
```bash
# Check health
make health-check
```

### 4. Initialize Database
```bash
poetry run python scripts/init_db.py
```

### 5. Run Consumer
```bash
poetry run python app/consumer/worker.py
```

### 6. Generate Events
```bash
# Generate 10 events with 2s delay
poetry run python tools/event_producer.py --count 10 --delay 2

# Or run continuously
poetry run python tools/event_producer.py --continuous
```

## 🧪 Testing

### Automated Test
```bash
make test-pipeline
```

### Manual Testing

1. **Generate Events:**
   ```bash
   make run-producer
   ```

2. **Process Events:**
   ```bash
   make run-consumer
   ```

3. **Check Results:**
   ```bash
   make check-db
   ```

### Monitoring

- **Grafana Dashboard**: http://localhost:3000 (admin/admin)
- **Prometheus Metrics**: http://localhost:9090
- **Kafka UI**: http://localhost:8080
- **Application Metrics**: `make metrics`
- **Database**: `make check-db`
- **Redis**: `make monitor-redis`
- **Logs**: `make logs`

## 📊 Event Flow

1. **Event Generation**: Producer sends ORDER_CREATED events to Kafka
2. **Deduplication**: Redis checks prevent duplicate processing
3. **Enrichment**: User and product data added from cache/external APIs
4. **Fraud Detection**: ML-based fraud analysis
5. **Persistence**: Events saved to PostgreSQL
6. **Caching**: Order states cached in Redis
7. **Routing**: Events routed to specific business logic handlers

## 🗄️ Database Schema

### Tables

- `order_events`: Raw event storage (event sourcing)
- `order_states`: Current order states (materialized view)
- `processing_errors`: Failed events for retry/analysis

### Sample Queries

```sql
-- View recent events
SELECT event_type, order_id, timestamp 
FROM order_events 
ORDER BY timestamp DESC 
LIMIT 10;

-- Check order states
SELECT order_id, status, total_amount, created_at 
FROM order_states 
ORDER BY created_at DESC;
```

## 🔍 Troubleshooting

### Services Not Starting
```bash
# Check Docker
docker-compose ps

# View logs
make logs

# Restart services
make down && make up
```

### Consumer Not Processing
```bash
# Check Kafka topics
make list-topics

# Listen to raw events
make consume-raw

# Check consumer logs
make logs
```

### Database Issues
```bash
# Check connection
make health-check

# Reinitialize
make init-db
```

## 🏭 Production Considerations

- **Scaling**: Increase Kafka partitions and consumer instances
- **Monitoring**: Add Prometheus/Grafana for metrics
- **Security**: Enable Kafka SASL/SSL, database encryption
- **Backup**: Implement database backup strategy
- **Error Handling**: Set up dead letter queues
- **Circuit Breakers**: Add resilience patterns

## 📁 Project Structure

```
async-kafka-pipeline/
├── app/
│   ├── cache/           # Redis client
│   ├── common/          # Shared utilities
│   ├── consumer/        # Kafka consumer & processors
│   └── db/              # Database models & connection
├── scripts/             # Database initialization
├── tools/               # Testing & utility scripts
├── configs/             # Configuration files
├── docker-compose.yml   # Infrastructure setup
└── Makefile            # Automation commands
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.