resource "aws_s3_bucket" "raw_events" {
  bucket = var.TODO_S3_BUCKET_RAW_EVENTS

  lifecycle_rule {
    id      = "raw-events-archive"
    enabled = true
    transition {
      days          = 30
      storage_class = "GLACIER"
    }
  }
}

resource "aws_s3_bucket" "dbt_snapshots" {
  bucket = var.TODO_S3_BUCKET_DBT_SNAPSHOTS

  lifecycle_rule {
    id      = "dbt-snapshots-archive"
    enabled = true
    transition {
      days          = 30
      storage_class = "GLACIER"
    }
  }
}
