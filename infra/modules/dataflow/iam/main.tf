data "google_project" "project" {}

# Dataflow managed service account (orquestra o job)
resource "google_storage_bucket_iam_member" "dataflow_temp_worker" {
  bucket = "cars-sales-${var.project_id}-${var.env}-dataflow-temp"
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:service-${data.google_project.project.number}@dataflow-service-producer-prod.iam.gserviceaccount.com"
}

#resource "google_storage_bucket_iam_member" "dataflow_staging_worker" {
#  bucket = "cars-sales-${var.project_id}-${var.env}-events-staging"
#  role   = "roles/storage.objectAdmin"
#  member = "serviceAccount:service-${data.google_project.project.number}@dataflow-service-producer-prod.iam.gserviceaccount.com"
#}

# Compute default service account (workers que acessam GCS)
resource "google_storage_bucket_iam_member" "compute_default_temp" {
  bucket = "cars-sales-${var.project_id}-${var.env}-dataflow-temp"
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${data.google_project.project.number}-compute@developer.gserviceaccount.com"
}

#resource "google_storage_bucket_iam_member" "compute_default_staging" {
#  bucket = "cars-sales-${var.project_id}-${var.env}-events-staging"
#  role   = "roles/storage.objectAdmin"
#  member = "serviceAccount:${data.google_project.project.number}-compute@developer.gserviceaccount.com"
#}