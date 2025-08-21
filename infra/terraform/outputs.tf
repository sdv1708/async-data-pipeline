output "vpc_id" {
  value = aws_vpc.main.id
}

output "public_subnet_ids" {
  value = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  value = aws_subnet.private[*].id
}

output "security_group_ids" {
  value = concat([aws_security_group.default.id], aws_security_group.extra[*].id)
}

output "msk_cluster_arn" {
  value = aws_msk_serverless_cluster.this.arn
}

output "msk_bootstrap_brokers" {
  value = aws_msk_serverless_cluster.this.bootstrap_brokers_sasl_iam
}

output "ecs_cluster_arn" {
  value = aws_ecs_cluster.main.arn
}

output "ecs_service_arns" {
  value = aws_ecs_service.this[*].id
}

output "rds_instance_arn" {
  value = aws_db_instance.main.arn
}

output "rds_endpoint" {
  value = aws_db_instance.main.endpoint
}

output "redis_endpoint" {
  value = aws_elasticache_replication_group.main.primary_endpoint_address
}

output "grafana_workspace_arn" {
  value = aws_grafana_workspace.main.arn
}
