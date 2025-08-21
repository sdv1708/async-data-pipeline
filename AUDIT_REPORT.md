# Audit Report

## CHECKLIST
- ❌ README sections — missing Vision, Scenario & Data Source, Avro schema, Functional Requirements, Architecture diagram, AWS Mapping & Costs, Tech Stack, Local Workflow, Consistency & Logging, dbt Nightly, Repo Structure, Milestones, Immediate Next Steps, and explicit partition key `order_id`.
- ❌ Repo layout paths — expected files and directories (`Makefile`, `pyproject.toml`, `.pre-commit-config.yaml`, `docker-compose.yml`, `.env.example`, `app/`, `tools/`, `infra/terraform/`, `ci/github/workflows/`, `tests/`, `configs/`) are absent.
- ❌ docker-compose services — no compose file defining Kafka, Schema Registry, Postgres, Redis, Prometheus, Grafana, Jaeger, or app services.
- ❌ Makefile — absent, so dev-bootstrap, compose, lint, and test targets are missing.
- ❌ pyproject.toml dependencies — project lacks Python package management and required dependencies.
- ❌ pre-commit hooks — `.pre-commit-config.yaml` missing.
- ❌ tests — no `tests/` directory or placeholders.
- ❌ CI workflows — no GitHub Actions workflows present.
- ❌ Terraform files — no `infra/terraform/` directory.
- ❌ Environment variables sample — `.env.example` missing.
- ❌ Observability configs — no `configs/logging.yaml` or `configs/otel.yaml`.

## MISSING FILES/CONFIGS
- Makefile
- pyproject.toml
- .pre-commit-config.yaml
- docker-compose.yml
- .env.example
- app/producer/main.py
- app/producer/schemas/order_event.avsc
- app/producer/security.py
- app/consumer/worker.py
- app/consumer/processors/enrich.py
- app/consumer/processors/fraud.py
- app/consumer/dedup.py
- app/cache/redis_client.py
- app/db/models.py
- app/db/session.py
- app/db/alembic/
- tools/simulator.py
- tools/replay.py
- configs/logging.yaml
- configs/otel.yaml
- configs/prometheus.yml
- infra/terraform/backend.tf
- infra/terraform/providers.tf
- infra/terraform/networking.tf
- infra/terraform/msk.tf
- infra/terraform/ecs.tf
- infra/terraform/rds.tf
- infra/terraform/redis.tf
- infra/terraform/observability.tf
- infra/terraform/budgets.tf
- infra/terraform/variables.tf
- infra/terraform/outputs.tf
- ci/github/workflows/lint-test.yml
- ci/github/workflows/build-push.yml
- ci/github/workflows/nightly-dbt.yml
- ci/github/workflows/deploy.yml
- tests/unit/
- tests/integration/
- tests/load/

## CLOUD TODOs
TODO_AWS_ACCOUNT_ID
TODO_AWS_REGION
TODO_AWS_OIDC_ROLE_ARN
TODO_TF_STATE_BUCKET
TODO_TF_STATE_KEY
TODO_TF_LOCK_TABLE
TODO_ECR_REPOSITORY
TODO_VPC_CIDR
TODO_PUBLIC_SUBNET_IDS
TODO_PRIVATE_SUBNET_IDS
TODO_SECURITY_GROUP_IDS
TODO_ECS_CLUSTER_NAME
TODO_ECS_API_TASKDEF_NAME
TODO_ECS_WORKER_TASKDEF_NAME
TODO_ECS_SERVICE_NAMES
TODO_ALB_ARN
TODO_TARGET_GROUP_ARN
TODO_MSK_CLUSTER_ARN
TODO_MSK_BOOTSTRAP_SERVERS
TODO_MSK_AUTH_MODE
TODO_KAFKA_TOPIC_ORDERS
TODO_KAFKA_TOPIC_FLAGGED
TODO_SCHEMA_REGISTRY_URL
TODO_RDS_DB_NAME
TODO_RDS_SECRET_ID
TODO_ELASTICACHE_CLUSTER_ID
TODO_REDIS_ENDPOINT
TODO_S3_BUCKET_RAW_EVENTS
TODO_S3_BUCKET_DBT_SNAPSHOTS
TODO_CLOUDWATCH_LOG_GROUP_API
TODO_CLOUDWATCH_LOG_GROUP_WORKER
TODO_BUDGET_AMOUNT
TODO_SNS_TOPIC_ARN_FOR_BUDGETS
TODO_GRAFANA_WORKSPACE
TODO_OTEL_EXPORTER_ENDPOINT

## SUMMARY
The repository currently lacks the entire project scaffolding. Phase B will add a complete skeleton: environment example, docker-compose stack, Makefile, Python project configuration with dependencies and pre-commit hooks, FastAPI producer and consumer services, Redis cache, database session and models with Alembic, tooling scripts, logging and OTEL configs, test placeholders, CI workflows, and Terraform modules with all cloud values marked as TODO placeholders.


## CHANGES APPLIED
- Added project scaffolding including environment sample, docker-compose stack, Makefile, pyproject with dependencies, and pre-commit hooks.
- Implemented FastAPI producer and async consumer with processors, Redis cache, and database models/session.
- Added tooling scripts, configs for logging and OTEL, Terraform skeleton with TODO placeholders, CI workflows, and test placeholders.
