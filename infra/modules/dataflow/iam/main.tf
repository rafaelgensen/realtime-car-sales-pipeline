# Obtém o e-mail do service account autenticado
data "google_client_config" "current" {}

# IAM para buckets
resource "google_storage_bucket_iam_member" "dataflow_temp" {
  bucket = replace("gs://cars-sales-${var.project_id}-${var.env}-dataflow-temp/", "gs://", "")
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${data.google_client_config.current.email}"
}

resource "google_storage_bucket_iam_member" "dataflow_staging" {
  bucket = replace("gs://cars-sales-${var.project_id}-${var.env}-events-staging/", "gs://", "")
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${data.google_client_config.current.email}"
}

# IAM para Pub/Sub
resource "google_pubsub_topic_iam_member" "dataflow_pubsub" {
  topic  = "${var.project_id}-${var.env}-events"
  role   = "roles/pubsub.subscriber"
  member = "serviceAccount:${data.google_client_config.current.email}"
}