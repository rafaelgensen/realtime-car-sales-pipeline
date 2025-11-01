resource "google_pubsub_topic" "events" {
  name = "${var.env}-events-topic"
}

output "topic_name" {
  value = google_pubsub_topic.events.name
}