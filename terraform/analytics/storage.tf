resource "google_storage_bucket" "data" {
  name          = "${var.project}-${var.location_code}-analytics-data"
  location      = var.multi_region
  force_destroy = true
}