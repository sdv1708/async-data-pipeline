resource "aws_ecs_cluster" "main" {
  name = var.TODO_ECS_CLUSTER_NAME
}

resource "aws_ecs_task_definition" "api" {
  family                   = var.TODO_ECS_API_TASKDEF_NAME
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  container_definitions    = jsonencode([])
}

resource "aws_ecs_task_definition" "worker" {
  family                   = var.TODO_ECS_WORKER_TASKDEF_NAME
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  container_definitions    = jsonencode([])
}

resource "aws_ecs_service" "this" {
  count           = length(var.TODO_ECS_SERVICE_NAMES)
  name            = var.TODO_ECS_SERVICE_NAMES[count.index]
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = aws_subnet.private[*].id
    security_groups = [aws_security_group.default.id]
  }
}
