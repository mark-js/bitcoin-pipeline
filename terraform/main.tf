terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "6.29.0"
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

# moved to airflow
# resource "google_dataproc_cluster" "single-cluster" {
#   name   = "single-cluster"
#   region = var.region

#   cluster_config {
#     master_config {
#       num_instances = 1
#       machine_type  = "e2-standard-2"
#     }
#     software_config {
#       override_properties = {
#         "dataproc:dataproc.allow.zero.workers" = "true"
#       }
#     }
#   }
# }