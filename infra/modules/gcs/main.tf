

resource "google_storage_bucket" "events_staging" {
  name                        = "cars-sales-${var.project_id}-${var.env}-events-staging"
  location                    = var.region
  uniform_bucket_level_access = true
}


output "events_staging_location" {
  value = google_storage_bucket.events_staging.name
}