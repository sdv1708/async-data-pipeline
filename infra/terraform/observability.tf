resource "aws_cloudwatch_log_group" "api" {
  name              = var.TODO_CLOUDWATCH_LOG_GROUP_API
  retention_in_days = 14
}

resource "aws_cloudwatch_log_group" "worker" {
  name              = var.TODO_CLOUDWATCH_LOG_GROUP_WORKER
  retention_in_days = 14
}

resource "aws_grafana_workspace" "main" {
  name                  = var.TODO_GRAFANA_WORKSPACE
  account_access_type   = "CURRENT_ACCOUNT"
  authentication_providers = ["AWS_SSO"]
}
