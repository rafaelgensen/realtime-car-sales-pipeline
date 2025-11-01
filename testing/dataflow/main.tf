resource "google_dataflow_flex_template_job" "streaming_job" {
  name              = "${var.env}-streaming-job"
  container_spec_gcs_path = "gs://${var.project_id}-templates/dataflow/streaming_spec.json"

  parameters = {
    input_topic   = var.input_topic
    output_table  = var.output_table
    temp_location = var.temp_location
  }
}