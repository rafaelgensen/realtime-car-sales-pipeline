resource "google_pubsub_topic" "events" {
  name    = "cars-sales-${var.project_id}-${var.env}-events"
  project = var.project_id
}

resource "google_pubsub_subscription" "events_sub" {
  name    = "cars-sales-${var.project_id}-${var.env}-events-sub"
  topic   = google_pubsub_topic.events.name
  project = var.project_id
}

resource "google_pubsub_subscription_iam_member" "dataflow_sub" {
  subscription = google_pubsub_subscription.events_sub.name
  role         = "roles/pubsub.subscriber"
  member       = "serviceAccount:dataflow-sa@${var.project_id}.iam.gserviceaccount.com"
}
