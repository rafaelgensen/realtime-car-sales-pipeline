resource "google_pubsub_topic" "events" {
  name    = "${var.project_id}-${var.env}-events"
  project = var.project_id
}

resource "google_pubsub_subscription" "events_sub" {
  name  = "${var.project_id}-${var.env}-events-sub"
  topic = google_pubsub_topic.events.name
  project = var.project_id
}

output "events_topic" {
  value = google_pubsub_topic.events.name
}

output "events_subscription" {
  value = google_pubsub_subscription.events_sub.name
}

