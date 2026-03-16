terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "7.23.0"
    }
  }
}

provider "google" {
  project = var.project
  region  = var.region
}

resource "google_storage_bucket" "data" {
  name          = "${var.project}-data"
  location      = var.region
  force_destroy = true
}

resource "google_storage_bucket" "staging" {
  name          = "${var.project}-staging"
  location      = var.region
  force_destroy = true
}

resource "google_storage_bucket_object" "spark_job" {
  name = "spark/jobs/transform_load_dataproc.py"
  source = "${path.root}/../batch/spark/jobs/transform_load_dataproc.py"
  bucket = google_storage_bucket.staging.name
}

resource "google_bigquery_dataset" "core_dataset" {
  dataset_id = "core"
  location   = var.region
}

resource "google_bigquery_dataset" "staging_dataset" {
  dataset_id = "staging"
  location   = var.region
}

resource "google_bigquery_table" "core_table" {
  dataset_id = google_bigquery_dataset.core_dataset.dataset_id
  table_id   = "btcusdt"
  schema     = file("ohlcv-schema.json")
  table_constraints {
    primary_key {
      columns = ["timestamp"]
    }
  }
  deletion_protection = false
}

resource "google_bigquery_table" "core_table_live" {
  dataset_id = google_bigquery_dataset.core_dataset.dataset_id
  table_id   = "btcusdt_live"
  schema     = file("ohlcv-schema.json")
  table_constraints {
    primary_key {
      columns = ["timestamp"]
    }
  }
  deletion_protection = false
}

resource "google_artifact_registry_repository" "pipeline" {
  location = var.region
  repository_id = "pipeline"
  format = "DOCKER"
}

resource "google_cloud_run_v2_job" "ingest" {
  name     = "ingest"
  location = var.region

  template {
    template {
      containers {
        image = "${google_artifact_registry_repository.pipeline.registry_uri}/ingest:latest"
        resources {
          limits = {
            memory = "1Gi"
            cpu    = "1"
          }
        }
      }
      service_account = google_service_account.ingest.email
      timeout         = "1200s"
      max_retries     = 1
    }
  }

  depends_on = [
    google_project_iam_member.ingest_storage_admin
  ]
}

resource "google_service_account" "ingest" {
  account_id   = "ingest"
  display_name = "Ingest Service Account"
  description  = "Service account for Cloud Run Job - ingest"
}

resource "google_project_iam_member" "ingest_storage_admin" {
  project = var.project
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.ingest.email}"
}