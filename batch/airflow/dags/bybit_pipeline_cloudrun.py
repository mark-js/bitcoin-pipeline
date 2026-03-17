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
def bybit_execute_cloudrun():
    gcp_project_id = '{{ var.value.gcp_project_id }}'
    gcp_region = '{{ var.value.gcp_region }}'
    bucket_name = '{{ var.value.gcp_data_bucket_name }}'
    object_name = 'bybit/{{ var.json.bybit.product }}/date={{ ds }}/data.parquet'
    
    download_url = '{{ var.json.bybit.url }}/{{ var.json.bybit.product }}/{{ var.json.bybit.product }}{{ ds }}.csv.gz'

    execute_cloudrun_ingest = CloudRunExecuteJobOperator(
        task_id='execute_cloudrun_ingest',
        gcp_conn_id='gcp',
        project_id=gcp_project_id,
        region=gcp_region,
        job_name='ingest',
        overrides={
            'container_overrides': [
                {
                    'args': [
                        '--url',
                        download_url,
                        '--bucket',
                        bucket_name,
                        '--object',
                        object_name
                    ]
                }
            ]
        }
    )

    execute_cloudrun_ingest

bybit_execute_cloudrun()

