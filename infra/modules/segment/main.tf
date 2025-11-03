resource "google_service_account" "segment" {
  account_id   = "segment-bq-sa"
  display_name = "Segment BigQuery SA"
}

resource "google_project_iam_member" "segment_bq_access" {
  project = var.project_id
  role    = "roles/bigquery.dataViewer"
  member  = "serviceAccount:${google_service_account.segment.email}"
}

resource "google_project_iam_member" "segment_bq_job" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.segment.email}"
}

# gcloud iam service-accounts keys create segment-key.json \
#  --iam-account segment-bq-sa@${PROJECT_ID}.iam.gserviceaccount.com