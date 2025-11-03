# Enable required APIs
resource "google_project_service" "grafana_api" {
  service = "grafana.googleapis.com"
}

# IAM — allow your user or SA to access Grafana
resource "google_project_iam_member" "grafana_admin" {
  role   = "roles/grafana.admin"
  member = var.grafana_user
  project = var.project_id
}

# Create Grafana workspace
resource "google_grafana_instance" "main" {
  instance_id = "grafana-analytics"
  location    = "us-central1"

  grafana {
    version       = "9.0"   
    license_type  = "GRAFANA_LICENSE_TYPE_GROWTH"
  }

  # Optional features
  notification_channels_enabled = true
  single_sign_on {
    enabled = true
  }
}

output "grafana_url" {
  description = "URL to access the Managed Grafana workspace"
  value       = google_grafana_instance.main.grafana_uri
}

output "grafana_instance_id" {
  description = "Grafana instance ID"
  value       = google_grafana_instance.main.name
}