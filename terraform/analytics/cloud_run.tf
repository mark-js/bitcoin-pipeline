resource "google_artifact_registry_repository" "analytics" {
  location = var.region
  repository_id = "analytics"
  format = "DOCKER"
}

resource "google_cloud_run_v2_job" "ingest_tick_data" {
  name     = "ingest-tick-data"
  location = var.region
  deletion_protection = false

  template {
    template {
      containers {
        image = "${google_artifact_registry_repository.analytics.registry_uri}/ingest_tick_data:latest"
        resources {
          limits = {
            memory = "1Gi"
            cpu    = "1"
          }
        }
      }
      service_account = google_service_account.cloud_run_ingestion.email
      timeout         = "1200s"
      max_retries     = 1
    }
  }

  depends_on = [
    google_project_iam_member.cloud_run_storage_admin
  ]
}