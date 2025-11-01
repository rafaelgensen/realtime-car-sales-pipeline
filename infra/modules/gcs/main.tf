resource "google_storage_bucket" "dataflow_temp" {
  name                        = "cars-sales-${var.project_id}-${var.env}-dataflow-temp"
  location                    = var.region
  uniform_bucket_level_access = true
}

resource "google_storage_bucket" "events_staging" {
  name                        = "cars-sales-${var.project_id}-${var.env}-events-staging"
  location                    = var.region
  uniform_bucket_level_access = true
}

# Upload do arquivo JSON com a configuração para o bucket
resource "google_storage_bucket_object" "config_file" {
  name   = "config/input_output_config.json"
  bucket = google_storage_bucket.dataflow_temp.name
  content = jsonencode({
    input_topic   = "${var.project_id}-${var.env}-events-sub"
    output_bucket = "cars-sales-${var.project_id}-${var.env}-events-staging"
  })
}

output "temp_location" {
  value = google_storage_bucket.dataflow_temp.name
}

output "events_staging_location" {
  value = google_storage_bucket.events_staging.name
}