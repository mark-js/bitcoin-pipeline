import os

from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment
from pyflink.table.window import Tumble
from pyflink.table.expressions import col, lit

from bitcoin_pipeline.flink.stream_tables import (
    create_source_schema, 
    create_kafka_source, 
    create_sink_schema, 
    create_bigquery_sink,
    create_jdbc_sink
)


def main():
    bigquery_project = os.environ['FLINK_BIGQUERY_PROJECT']
    bigquery_dataset = os.environ['FLINK_BIGQUERY_DATASET']
    bigquery_table = os.environ['FLINK_BIGQUERY_TABLE']
    postgres_url = os.environ['FLINK_POSTGRES_URL']
    postgres_username = os.environ['FLINK_POSTGRES_USERNAME']
    postgres_password = os.environ['FLINK_POSTGRES_PASSWORD']
    postgres_table = os.environ['FLINK_POSTGRES_TABLE']
    redpanda_addr = os.environ['FLINK_REDPANDA_ADDR']

    env = StreamExecutionEnvironment.get_execution_environment()
    env.enable_checkpointing(interval=10 * 1000)
    env.set_parallelism(1)
    t_env = StreamTableEnvironment.create(stream_execution_environment=env)

    source_schema = create_source_schema()
    path_source = create_kafka_source(t_env, source_schema, redpanda_addr)
    table = t_env.from_path(path_source)

    sink_schema = create_sink_schema()
    bigquery_sink = create_bigquery_sink(
        t_env, sink_schema, bigquery_project, bigquery_dataset, bigquery_table)
    postgres_sink = create_jdbc_sink(
        t_env, sink_schema, postgres_url, postgres_username, postgres_password, postgres_table)    

    try:
        table = table \
            .select(
                col('watermark_strategy'),
                col('p'),
                col('v')) \
            .window(Tumble.over(lit(1).minutes).on(col('watermark_strategy')).alias('w')) \
            .group_by(col('w')) \
            .select(
                col('w').start.alias('timestamp'), 
                col('p').first_value.alias('open'),
                col('p').max.alias('high'),
                col('p').min.alias('low'),
                col('p').last_value.alias('close'),
                col('v').sum.alias('volume'))
        table.execute_insert(postgres_sink)
        table.execute_insert(bigquery_sink)
    except Exception as e:
        print("Writing records from Kafka to JDBC failed:", str(e))


if __name__ == '__main__':
    main()