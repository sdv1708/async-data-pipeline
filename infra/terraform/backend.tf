terraform {
  required_version = ">= 1.5.0"
  backend "s3" {
    bucket         = "TODO_TF_STATE_BUCKET"
    key            = "TODO_TF_STATE_KEY"
    region         = "TODO_AWS_REGION"
    dynamodb_table = "TODO_TF_LOCK_TABLE"
  }
}
