data "aws_secretsmanager_secret" "db" {
  arn = var.TODO_RDS_SECRET_ID
}

data "aws_secretsmanager_secret_version" "db" {
  secret_id = data.aws_secretsmanager_secret.db.id
}

locals {
  db_creds = jsondecode(data.aws_secretsmanager_secret_version.db.secret_string)
}

resource "aws_db_subnet_group" "main" {
  name       = "${var.TODO_RDS_DB_NAME}-subnet-group"
  subnet_ids = aws_subnet.private[*].id
}

resource "aws_db_instance" "main" {
  identifier              = var.TODO_RDS_DB_NAME
  engine                  = "postgres"
  instance_class          = "db.t3.micro"
  allocated_storage       = 20
  db_name                 = var.TODO_RDS_DB_NAME
  username                = local.db_creds.username
  password                = local.db_creds.password
  skip_final_snapshot     = true
  vpc_security_group_ids  = [aws_security_group.default.id]
  db_subnet_group_name    = aws_db_subnet_group.main.name
}
