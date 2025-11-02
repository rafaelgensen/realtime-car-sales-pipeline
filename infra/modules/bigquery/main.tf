resource "google_bigquery_dataset" "streaming" {
  dataset_id = "streaming"
  location   = var.region
}

resource "google_bigquery_table" "raw_events" {
  dataset_id = google_bigquery_dataset.streaming.dataset_id
  table_id   = "raw_events"

  schema = <<EOF
[
  {
    "name": "payload",
    "type": "STRING",
    "mode": "REQUIRED"
  }
]
EOF
}