# Project
Bitcoin data pipeline processing Bybit BTCUSDT tick data.
Batch pipeline downloads daily tick data, converts to Parquet, stores in GCS.
Streaming pipeline processes live tick data into OHLCV candles for a Plotly dashboard.

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
- batch/airflow/ - Airflow DAGs and orchestration
- batch/spark/ - PySpark jobs for local and GCP Dataproc
- batch/ingest/ - Ingestion container deployed on Cloud Run
- batch/dbt/ - dbt (BigQuery) deployed on Cloud Run
- streaming/kafka/ - Redpanda/Kafka producer
- streaming/flink/ - PyFlink stream processing
- dashboard/ - Plotly Dash application
- terraform/ - GCP infrastructure

# Data Storage
- GCS data bucket: gs://{data_bucket}/{symbol}/date=YYYY-MM-DD/data.parquet - Hive partitioned by date
- GCS staging bucket: gs://{staging_bucket}/spark/jobs/ - Spark job scripts
- GCS staging bucket: gs://{staging_bucket}/temp/ - Temporary files
- BigQuery external tables reference GCS Parquet files