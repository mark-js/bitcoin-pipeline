import requests
from pendulum import datetime, duration

from airflow.decorators import dag, task
from airflow.models.baseoperator import chain
from airflow.sensors.base import PokeReturnValue
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from airflow.providers.google.cloud.operators.gcs import GCSDeleteObjectsOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.providers.google.cloud.operators.dataproc import (
    DataprocCreateClusterOperator,
    DataprocSubmitJobOperator
)


@dag(
    start_date=datetime(2025,4,5),
    description='Download from ByBit using sensor',
    schedule='@daily',
    catchup=True,
    max_active_runs=5,
    default_args= {
        'retries': 3,
        'retry_delay': duration(minutes=1),
        'retry_exponential_backoff': True
    }
)
def bybit_pipeline_gcp():
    download_url = '{{ var.json.bybit.url }}/{{ var.json.bybit.product }}'
    product = '{{ var.json.bybit.product }}'    
    date = '{{ ds }}'
    date_nodash = '{{ ds_nodash }}'
    temp_storage = '{{ var.value.local_storage }}'
    gcp_bucket_name = '{{ var.value.gcp_bucket_name }}'
    run_id = '{{ run_id }}'
    
    @task.sensor(mode='poke', poke_interval=60, timeout=300)
    def download_file_local(download_url: str, product: str, date: str, temp_storage: str) -> PokeReturnValue:
        response = requests.get(
            url=f'{download_url}/{product}{date}.csv.gz'
        )

        if response.status_code == 200:
            condition_met = True
            with open(f'{temp_storage}/{product}{date}.csv.gz', 'wb') as f:
                f.write(response.content)
        else:
            condition_met = False

        return PokeReturnValue(is_done=condition_met)
        
    upload_temp_files_gcs = LocalFilesystemToGCSOperator(
        task_id='upload_temp_files_gcs',
        gcp_conn_id='gcp',
        src=[
            '/opt/airflow/include/transform_load_dataproc.py',
            f'{temp_storage}/{product}{date}.csv.gz'
        ],
        dst=f'temp/{run_id}/',
        bucket=gcp_bucket_name
    )

    create_dataproc_cluster = DataprocCreateClusterOperator(
        task_id='create_dataproc_cluster',
        gcp_conn_id='gcp',
        project_id='{{ var.value.gcp_project_id }}',
        region='{{ var.value.gcp_region }}',
        cluster_name='e2-cluster',
        cluster_config={
            'master_config': {
                'num_instances': 1,
                'machine_type_uri': 'e2-standard-2',
                'disk_config': {'boot_disk_type': 'pd-standard', 'boot_disk_size_gb': 32}
            },
            'worker_config': {
                'num_instances': 2,
                'machine_type_uri': 'e2-standard-2',
                'disk_config': {'boot_disk_type': 'pd-standard', 'boot_disk_size_gb': 32}
            },
            'lifecycle_config': {
                'idle_delete_ttl': {'seconds': 300}
            }
        },
        use_if_exists=True
    )
    
    submit_pyspark_dataproc = DataprocSubmitJobOperator(
        task_id='submit_pyspark_dataproc',
        gcp_conn_id='gcp',
        project_id='{{ var.value.gcp_project_id }}',
        region='{{ var.value.gcp_region }}',
        job={
            'placement': {'cluster_name': 'e2-cluster'},
            'pyspark_job': {
                'main_python_file_uri': 
                    f'gs://{gcp_bucket_name}/temp/{run_id}/transform_load_dataproc.py',
                'args': [
                    '--temp_bucket',
                    '{{ var.value.gcp_temp_bucket_name }}',
                    '--input',
                    f'gs://{gcp_bucket_name}/temp/{run_id}/{product}{date}.csv.gz',
                    '--output_raw',
                    f'gs://{gcp_bucket_name}/data/{product}/{date}',
                    '--output_table',
                    f'staging.{product}{date_nodash}'
                ]
            }
        }
    )

    @task.bash
    def delete_file_local(temp_storage: str, product: str, date: str) -> None:
        return f'rm {temp_storage}/{product}{date}.csv.gz'
        
    upsert_drop_bigquery = BigQueryInsertJobOperator(
        task_id='upsert_staging_to_core',
        gcp_conn_id='gcp',
        configuration={
            'query': {
                'query':'{% include "sql/upsert_drop_bigquery.sql" %}',
                'useLegacySql': False,
                'priority': 'BATCH'
            }
        }
    )

    delete_temp_files_gcs = GCSDeleteObjectsOperator(
        task_id='delete_temp_files_gcs',
        gcp_conn_id='gcp',
        bucket_name=gcp_bucket_name,
        objects=[
            f'temp/{run_id}/transform_load_dataproc.py',
            f'temp/{run_id}/{product}{date}.csv.gz'
        ],
    )

    chain(
        [download_file_local(download_url, product, date, temp_storage), create_dataproc_cluster],
        upload_temp_files_gcs,
        submit_pyspark_dataproc,
        [upsert_drop_bigquery, delete_file_local(temp_storage, product, date), delete_temp_files_gcs]
    )

bybit_pipeline_gcp()