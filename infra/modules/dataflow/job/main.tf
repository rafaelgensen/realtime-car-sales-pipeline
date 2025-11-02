resource "google_dataflow_job" "streaming" {
  name              = var.job_name
  template_gcs_path = null
  temp_gcs_location = "gs://cars-sales-${var.project_id}-${var.env}-dataflow-temp/temp"
  region            = var.region
  on_delete         = "cancel"

  parameters = {
    input_subscription = "projects/${var.project_id}/subscriptions/cars-sales-${var.project_id}-${var.env}-events-sub"
    output_bucket      = "cars-sales-${var.project_id}-${var.env}-events-staging"
  }
}

output "dataflow_job_id" {
  value = google_dataflow_job.streaming.id
}