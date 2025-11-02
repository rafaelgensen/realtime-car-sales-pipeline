resource "google_pubsub_topic" "events" {
  name    = "cars-sales-${var.project_id}-${var.env}-events"
  project = var.project_id
}

resource "google_pubsub_subscription" "events_sub" {
  name  = "cars-sales-${var.project_id}-${var.env}-events-sub"
  topic = google_pubsub_topic.events.name
  project = var.project_id
}

output "events_topic" {
  value = google_pubsub_topic.events.name
}

output "events_subscription" {
  value = google_pubsub_subscription.events_sub.name
}

resource "google_pubsub_topic_iam_member" "dataflow_pubsub" {
  topic  = google_pubsub_topic.events.name  
  role   = "roles/pubsub.subscriber"        
  member = "serviceAccount:terraform-runner@${var.project_id}.iam.gserviceaccount.com"  # Conta do Dataflow
}
