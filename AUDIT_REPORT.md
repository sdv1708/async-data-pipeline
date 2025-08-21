# Audit Report

## CHECKLIST
- README sections ........................ ✅
- Repo paths ............................. ✅
- docker-compose services ................ ✅
- Makefile targets ....................... ✅
- pyproject deps ......................... ✅
- pre-commit hooks ....................... ✅
- tests (unit, integration) .............. ✅
- CI workflows ........................... ✅
- Terraform files ........................ ✅
- env vars doc (.env.example & README) ... ✅
- observability configs .................. ✅
- README partition key statement ......... ✅

## MISSING FILES/CONFIGS
- None

## CLOUD TODOs
- TODO_AWS_ACCOUNT_ID
- TODO_AWS_REGION
- TODO_AWS_OIDC_ROLE_ARN
- TODO_TF_STATE_BUCKET
- TODO_TF_STATE_KEY
- TODO_TF_LOCK_TABLE
- TODO_ECR_REPOSITORY
- TODO_VPC_CIDR
- TODO_PUBLIC_SUBNET_IDS
- TODO_PRIVATE_SUBNET_IDS
- TODO_SECURITY_GROUP_IDS
- TODO_ECS_CLUSTER_NAME
- TODO_ECS_API_TASKDEF_NAME
- TODO_ECS_WORKER_TASKDEF_NAME
- TODO_ECS_SERVICE_NAMES
- TODO_ALB_ARN
- TODO_TARGET_GROUP_ARN
- TODO_MSK_CLUSTER_ARN
- TODO_MSK_BOOTSTRAP_SERVERS
- TODO_MSK_AUTH_MODE
- TODO_KAFKA_TOPIC_ORDERS
- TODO_KAFKA_TOPIC_FLAGGED
- TODO_SCHEMA_REGISTRY_URL
- TODO_RDS_DB_NAME
- TODO_RDS_SECRET_ID
- TODO_ELASTICACHE_CLUSTER_ID
- TODO_REDIS_ENDPOINT
- TODO_S3_BUCKET_RAW_EVENTS
- TODO_S3_BUCKET_DBT_SNAPSHOTS
- TODO_CLOUDWATCH_LOG_GROUP_API
- TODO_CLOUDWATCH_LOG_GROUP_WORKER
- TODO_BUDGET_AMOUNT
- TODO_SNS_TOPIC_ARN_FOR_BUDGETS
- TODO_GRAFANA_WORKSPACE
- TODO_OTEL_EXPORTER_ENDPOINT

## SUMMARY
Added env var documentation and idempotency note to README, timestamp-millis to Avro schema, Postgres upsert with integration test, and terraform.tfvars.example placeholder. All checklist items complete.

## CHANGES APPLIED
- README.md
- app/producer/schemas/order_event.avsc
- app/consumer/worker.py
- app/db/models.py
- tests/integration/test_consumer.py
- infra/terraform/terraform.tfvars.example
- AUDIT_REPORT.md
