resource "aws_vpc" "main" {
  cidr_block = var.TODO_VPC_CIDR
}

resource "aws_subnet" "public" {
  count                   = length(var.TODO_PUBLIC_SUBNET_IDS)
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.TODO_PUBLIC_SUBNET_IDS[count.index]
  map_public_ip_on_launch = true
}

resource "aws_subnet" "private" {
  count      = length(var.TODO_PRIVATE_SUBNET_IDS)
  vpc_id     = aws_vpc.main.id
  cidr_block = var.TODO_PRIVATE_SUBNET_IDS[count.index]
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
}

resource "aws_route_table_association" "public" {
  count          = length(aws_subnet.public)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_security_group" "default" {
  vpc_id = aws_vpc.main.id
  name   = "default"
}

resource "aws_security_group" "extra" {
  count = length(var.TODO_SECURITY_GROUP_IDS)
  vpc_id = aws_vpc.main.id
  name   = var.TODO_SECURITY_GROUP_IDS[count.index]
}
