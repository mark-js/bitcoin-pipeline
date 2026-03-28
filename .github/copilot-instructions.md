# Project
Bitcoin platform processing Bybit BTCUSDT tick data and bitcoin onchain data.
Market data pipeline
- Batch pipeline downloads daily tick data, converts to Parquet, stores in GCS.
- Streaming pipeline processes live tick data into OHLCV candles for a Plotly dashboard.
Analytics pipeline
- Cloud run tick data ingestion to Bigquery external tables
- dbt transformations and comparisons to bitcoin onchain data

# Tech Stack
- Transformations: Python, Polars, PySpark, PyFlink, SQL
- Streaming: Redpanda, Flink
- Batch: Airflow, Spark, dbt
- GCP: BigQuery, GCS, Cloud Run, Dataproc
- IaC: Terraform

# Code Style
- PEP8
- Type hints on all functions
- argparse for CLI arguments
- Polars over pandas always

# Project Structure
- airflow/ - Airflow DAGs and orchestration
- terraform/ - GCP infrastructure
- market_data/spark/ - PySpark jobs for local and GCP Dataproc
- market_data/kafka/ - Redpanda/Kafka producer
- market_data/flink/ - PyFlink stream processing
- market_data/dashboard/ - Plotly Dash application
- analytics/ingestion/ - Ingestion container deployed on Cloud Run
- analytics/dbt/ - dbt (BigQuery) deployed on Cloud Run


# Data Storage
- GCS staging bucket: gs://{staging_bucket}/spark/jobs/ - Spark job scripts
- GCS staging bucket: gs://{staging_bucket}/temp/ - Temporary files
- GCS data bucket: gs://{data_bucket}/{symbol}/date=YYYY-MM-DD/data.parquet - Hive partitioned by date
- BigQuery external tables reference GCS Parquet files