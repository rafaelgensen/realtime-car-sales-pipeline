resource "google_storage_bucket" "dataflow_temp" {
  name                        = "${var.project_id}-${var.env}-dataflow-temp"
  location                    = var.region
  uniform_bucket_level_access = true
}

resource "google_storage_bucket" "events_landing" {
  name                        = "${var.project_id}-${var.env}-events-staging"
  location                    = var.region
  uniform_bucket_level_access = true
}