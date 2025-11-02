
resource "google_dataflow_job" "streaming" {
    name               = var.job_name
    template_gcs_path  = "gs://cars-sales-${var.project_id}-${var.env}-dataflow-temp/template/main.py"
    temp_gcs_location = "gs://cars-sales-${var.project_id}-${var.env}-dataflow-temp/"
    on_delete = "cancel"
}

output "dataflow_job_id" {
  value = google_dataflow_job.streaming.id
}

