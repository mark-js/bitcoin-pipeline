resource "google_service_account" "cloud_run_ingestion" {
  account_id   = "cloud-run-ingestion"
  display_name = "Cloud run ingestion Service Account"
  description  = "Service account for Cloud run ingestion"
}

resource "google_project_iam_member" "cloud_run_storage_admin" {
  project = var.project
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.cloud_run_ingestion.email}"
}