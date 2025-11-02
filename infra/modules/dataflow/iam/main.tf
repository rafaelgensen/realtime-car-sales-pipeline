resource "google_storage_bucket_iam_member" "dataflow_temp" {
  bucket = "cars-sales-${var.project_id}-${var.env}-dataflow-temp" 
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:terraform-runner@${var.project_id}.iam.gserviceaccount.com"
}

resource "google_storage_bucket_iam_member" "dataflow_staging" {
  bucket = "cars-sales-${var.project_id}-${var.env}-events-staging"  
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:terraform-runner@${var.project_id}.iam.gserviceaccount.com"
}

