from pendulum import datetime, duration

from airflow.decorators import dag
from airflow.providers.google.cloud.operators.cloud_run import CloudRunExecuteJobOperator


@dag(
    start_date=datetime(2026, 3, 14),
    description='Trigger Cloud Run container for Bybit data ingestion',
    schedule='@daily',
    catchup=True,
    max_active_runs=5,
    default_args={
        'retries': 3,
        'retry_delay': duration(minutes=1),
        'retry_exponential_backoff': True
    }
)
def bybit_ingest_tick_data():
    execute_cloudrun_ingest_tick_data = CloudRunExecuteJobOperator(
        task_id='execute_cloudrun_ingest_tick_data',
        gcp_conn_id='gcp',
        project_id='{{ var.value.gcp_project_id }}',
        region='{{ var.value.gcp_region }}',
        job_name='ingest_tick_data',
        overrides={
            'container_overrides': [
                {
                    'args': [
                        '--url',
                        '{{ var.json.bybit.url }}/{{ var.json.bybit.product }}/{{ var.json.bybit.product }}{{ ds }}.csv.gz',
                        '--bucket',
                        '{{ var.value.gcp_analytics_data_bucket_name }}',
                        '--object',
                        'bybit/{{ var.json.bybit.product }}/date={{ ds }}/data.parquet'
                    ]
                }
            ]
        }
    )

    execute_cloudrun_ingest_tick_data

bybit_ingest_tick_data()

