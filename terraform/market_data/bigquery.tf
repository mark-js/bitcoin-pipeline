resource "google_bigquery_dataset" "core_dataset" {
  dataset_id = "market_data_core"
  location   = var.region
}

resource "google_bigquery_dataset" "staging_dataset" {
  dataset_id = "market_data_staging"
  location   = var.region
}

resource "google_bigquery_table" "btcusdt_batch" {
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

resource "google_bigquery_table" "btcusdt_streaming" {
  dataset_id = google_bigquery_dataset.core_dataset.dataset_id
  table_id   = "btcusdt_streaming"
  schema     = file("ohlcv-schema.json")
  table_constraints {
    primary_key {
      columns = ["timestamp"]
    }
  }
  deletion_protection = false
}