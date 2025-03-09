from airflow.decorators import dag, task
from airflow.sensors.base import PokeReturnValue
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from pendulum import datetime
import requests


@dag(
    start_date=datetime(2025,3,1),
    description='Download from ByBit using sensor',
    schedule='@daily',
    catchup=True
)
def bybit_pipeline():

    download_url = '{{ var.json.bybit.url }}/{{ var.json.bybit.product}}'
    product = '{{ var.json.bybit.product}}'    
    date = '{{ ds }}'
    data_storage = '{{ var.value.data_storage }}'
    
    @task.sensor(mode='poke', poke_interval=60, timeout=300)
    def download_file(download_url: str, product: str, date: str, data_storage: str) -> PokeReturnValue:
        response = requests.get(
            url=f'{download_url}/{product}{date}.csv.gz'
        )

        if response.status_code == 200:
            condition_met = True
            with open(f'{data_storage}/temp/{product}{date}.csv.gz', 'wb') as f:
                f.write(response.content)
        else:
            condition_met = False

        return PokeReturnValue(is_done=condition_met)
    
    store_parquet = SparkSubmitOperator(
        task_id='read_data',
        application='include/transform_spark.py',
        conn_id='spark_master',
        application_args=[
            '--input',
            f'{data_storage}/temp/{product}{date}.csv.gz',
            '--output_raw',
            f'{data_storage}/raw/{product}/{date}',
            '--output_transform',
            f'{data_storage}/ohlc/{product}/{date}'
        ]
    )

    @task.bash
    def delete_temp_file(data_storage: str, product: str, date: str) -> None:
        return f'rm {data_storage}/temp/{product}{date}.csv.gz'

    download_file(download_url, product, date, data_storage) >> store_parquet >> delete_temp_file(data_storage, product, date)

bybit_pipeline()