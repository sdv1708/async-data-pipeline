resource "aws_msk_serverless_cluster" "this" {
  cluster_name = "async-pipeline"

  vpc_config {
    subnet_ids     = aws_subnet.private[*].id
    security_groups = [aws_security_group.default.id]
  }

  client_authentication {
    sasl {
      iam = true
    }
  }
}

resource "aws_msk_topic" "orders" {
  cluster_arn = aws_msk_serverless_cluster.this.arn
  topic_name  = var.TODO_KAFKA_TOPIC_ORDERS
  partitions  = 1
}

resource "aws_msk_topic" "flagged" {
  cluster_arn = aws_msk_serverless_cluster.this.arn
  topic_name  = var.TODO_KAFKA_TOPIC_FLAGGED
  partitions  = 1
}
