resource "aws_elasticache_subnet_group" "main" {
  name       = "${var.TODO_ELASTICACHE_CLUSTER_ID}-subnet-group"
  subnet_ids = aws_subnet.private[*].id
}

resource "aws_elasticache_replication_group" "main" {
  replication_group_id       = var.TODO_ELASTICACHE_CLUSTER_ID
  engine                     = "redis"
  node_type                  = "cache.t3.micro"
  number_cache_clusters      = 1
  subnet_group_name          = aws_elasticache_subnet_group.main.name
  security_group_ids         = [aws_security_group.default.id]
  automatic_failover_enabled = false
}
