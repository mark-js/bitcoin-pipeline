resource "google_bigquery_dataset" "tick_data_dataset" {
  dataset_id = "analytics_tick_data"
  location   = var.multi_region
}

resource "google_bigquery_table" "tick_data_bybit" {
    dataset_id = google_bigquery_dataset.tick_data_dataset.dataset_id
    table_id = "bybit"

    external_data_configuration {
      autodetect = false
      source_format = "PARQUET"
      schema = file("tick-data-schema.json")
      hive_partitioning_options {
        mode = "CUSTOM"
        source_uri_prefix = "${google_storage_bucket.data.url}/tick_data/bybit/{product:STRING}/{date:DATE}"
      }
      source_uris = ["${google_storage_bucket.data.url}/tick_data/bybit/*.parquet"]
    }
}