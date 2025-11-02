resource "google_dataflow_job" "streaming" {
  name              = var.job_name
  template_gcs_path = "gs://cars-sales-${var.project_id}-${var.env}-dataflow-temp/template/main-template"
  temp_gcs_location = "gs://cars-sales-${var.project_id}-${var.env}-dataflow-temp/temp"
  region            = var.region
  on_delete         = "cancel"

  parameters = {
    template_mode = "false"
  }
}

output "dataflow_job_id" {
  value = google_dataflow_job.streaming.id
}

