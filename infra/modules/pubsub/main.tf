resource "google_pubsub_topic" "events" {
  name    = "cars-sales-${var.project_id}-${var.env}-events"
  project = var.project_id
}

resource "google_pubsub_subscription" "events_sub" {
  name    = "cars-sales-${var.project_id}-${var.env}-events-sub"
  topic   = google_pubsub_topic.events.name
  project = var.project_id
}

# Permite ao Dataflow ler da subscription
resource "google_pubsub_subscription_iam_member" "dataflow_sub" {
  subscription = google_pubsub_subscription.events_sub.name
  role         = "roles/pubsub.subscriber"

  # Conta padrão de execução do Dataflow (managed service identity)
  member = "serviceAccount:service-${var.project_id}@dataflow-service-producer-prod.iam.gserviceaccount.com"
}

# Permite ao Dataflow publicar (se no futuro você mandar output para Pub/Sub)
resource "google_pubsub_topic_iam_member" "dataflow_pub" {
  topic = google_pubsub_topic.events.name
  role  = "roles/pubsub.publisher"

  member = "serviceAccount:service-${var.project_id}@dataflow-service-producer-prod.iam.gserviceaccount.com"
}

output "events_topic" {
  value = google_pubsub_topic.events.name
}

output "events_subscription" {
  value = google_pubsub_subscription.events_sub.name
}