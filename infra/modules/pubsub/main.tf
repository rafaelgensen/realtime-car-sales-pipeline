data "google_project" "project" {}

resource "google_pubsub_topic" "events" {
  name    = "cars-sales-${var.project_id}-${var.env}-events"
  project = var.project_id
}

resource "google_pubsub_subscription" "events_sub" {
  name    = "cars-sales-${var.project_id}-${var.env}-events-sub"
  topic   = google_pubsub_topic.events.name
  project = var.project_id
}

# Dataflow lê da subscription
resource "google_pubsub_subscription_iam_member" "dataflow_sub" {
  subscription = google_pubsub_subscription.events_sub.name
  role         = "roles/pubsub.subscriber"
  member       = "serviceAccount:service-${data.google_project.project.number}@dataflow-service-producer-prod.iam.gserviceaccount.com"
}

# Compute default SA (workers)
resource "google_pubsub_subscription_iam_member" "compute_sub" {
  subscription = google_pubsub_subscription.events_sub.name
  role         = "roles/pubsub.subscriber"
  member       = "serviceAccount:${data.google_project.project.number}-compute@developer.gserviceaccount.com"
}
