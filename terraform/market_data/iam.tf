resource "google_service_account" "dataproc_ingestion" {
  account_id   = "dataproc-ingestion"
  display_name = "Dataproc ingestion Service Account"
  description  = "Service account for Dataproc ingestion"
}

resource "google_project_iam_member" "dataproc_storage_admin" {
  project = var.project
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.dataproc_ingestion.email}"
}

resource "google_project_iam_member" "dataproc_bigquery_editor" {
  project = var.project
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.dataproc_ingestion.email}"
}

resource "google_project_iam_member" "dataproc_bigquery_user" {
  project = var.project
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.dataproc_ingestion.email}"
}

resource "google_project_iam_member" "dataproc_worker" {
  project = var.project
  role    = "roles/dataproc.worker"
  member  = "serviceAccount:${google_service_account.dataproc_ingestion.email}"
}