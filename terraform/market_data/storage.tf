resource "google_storage_bucket" "data" {
  name          = "${var.project}-${var.location_code}-market-data"
  location      = var.region
  force_destroy = true
}

resource "google_storage_bucket" "staging" {
  name          = "${var.project}-${var.location_code}-market-data-staging"
  location      = var.region
  force_destroy = true
}

resource "google_storage_bucket_object" "spark_job" {
  name = "spark/jobs/transform_load_dataproc.py"
  source = "${path.root}/../../market_data/spark/jobs/transform_load_dataproc.py"
  bucket = google_storage_bucket.staging.name
}

resource "google_storage_bucket" "dataproc_config" {
  name          = "${var.project}-${var.location_code}-dataproc-config"
  location      = var.region
  force_destroy = true
}

resource "google_storage_bucket" "dataproc_temp" {
  name          = "${var.project}-${var.location_code}-dataproc-temp"
  location      = var.region
  force_destroy = true
}