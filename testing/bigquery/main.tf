resource "google_bigquery_dataset" "streaming" {
  dataset_id = "${var.env}_streaming"
  location   = "US"
}

resource "google_bigquery_table" "events" {
  dataset_id = google_bigquery_dataset.streaming.dataset_id
  table_id   = "events"
  schema     = file("${path.module}/schema.json")
}

output "table_id" {
  value = "${google_bigquery_dataset.streaming.dataset_id}.${google_bigquery_table.events.table_id}"
}