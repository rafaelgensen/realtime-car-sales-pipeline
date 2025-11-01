# IAM para buckets
resource "google_storage_bucket_iam_member" "dataflow_temp" {
  bucket = replace("gs://cars-sales-${var.project_id}-${var.env}-dataflow-temp/", "gs://", "")
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${data.google_service_account.default.email}"
}

resource "google_storage_bucket_iam_member" "dataflow_staging" {
  bucket = replace("cars-sales-${var.project_id}-${var.env}-events-staging/", "gs://", "")
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${data.google_service_account.default.email}"
}

# IAM para Pub/Sub
resource "google_pubsub_topic_iam_member" "dataflow_pubsub" {
  topic  = "${var.project_id}-${var.env}-events"
  role   = "roles/pubsub.subscriber"
  member = "serviceAccount:${data.google_service_account.default.email}"
}