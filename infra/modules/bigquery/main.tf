resource "google_bigquery_dataset" "streaming" {
  dataset_id = "streaming"
  location   = var.region
}

resource "google_bigquery_table" "staging_purchase" {
  dataset_id = google_bigquery_dataset.streaming.dataset_id
  table_id   = "staging_purchase"

  schema = <<EOF
[
  {"name": "type", "type": "STRING"},
  {"name": "order_id", "type": "STRING"},
  {"name": "customer_id", "type": "STRING"},
  {"name": "car_model", "type": "STRING"},
  {"name": "amount", "type": "FLOAT"},
  {"name": "timestamp", "type": "TIMESTAMP"},
  {"name": "destination", "type": "STRING"}
]
EOF
}

resource "google_bigquery_table" "staging_cancellation" {
  dataset_id = google_bigquery_dataset.streaming.dataset_id
  table_id   = "staging_cancellation"

  schema = <<EOF
[
  {"name": "type", "type": "STRING"},
  {"name": "order_id", "type": "STRING"},
  {"name": "customer_id", "type": "STRING"},
  {"name": "car_model", "type": "STRING"},
  {"name": "reason", "type": "STRING"},
  {"name": "timestamp", "type": "TIMESTAMP"},
  {"name": "destination", "type": "STRING"}
]
EOF
}