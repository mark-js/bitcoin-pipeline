from pyflink.table import StreamTableEnvironment, TableDescriptor, Schema, FormatDescriptor, DataTypes
from pyflink.table.expressions import col, from_unixtime, to_timestamp


def create_source_schema() -> Schema:
    return Schema.new_builder() \
        .column('T', DataTypes.BIGINT()) \
        .column('s', DataTypes.STRING()) \
        .column('S', DataTypes.STRING()) \
        .column('v', DataTypes.DECIMAL(15,3)) \
        .column('p', DataTypes.DECIMAL(9,1)) \
        .column('L', DataTypes.STRING()) \
        .column('i', DataTypes.STRING()) \
        .column('BT', DataTypes.STRING()) \
        .column_by_expression('watermark_strategy', to_timestamp(from_unixtime(col('T')/1000))) \
        .watermark('watermark_strategy', 'watermark_strategy') \
        .build()


def create_kafka_source(t_env: StreamTableEnvironment, source_schema: Schema, bootstrap_servers: str) -> str:
    path_source = 'kafka_source'
    source_table_descriptor = TableDescriptor.for_connector('kafka') \
        .schema(source_schema) \
        .option('topic', 'btcusdt-bybit') \
        .option('properties.bootstrap.servers', bootstrap_servers) \
        .option('properties.group.id', 'group_0') \
        .option('scan.startup.mode', 'latest-offset') \
        .format(FormatDescriptor.for_format('json')
            .option('fail-on-missing-field', 'true')
            .option('ignore-parse-errors', 'false')
            .build()) \
        .build()
    t_env.create_temporary_table(
        path=path_source,
        descriptor=source_table_descriptor)
    return path_source


def create_sink_schema() -> Schema:
    return Schema.new_builder() \
        .column('timestamp', DataTypes.TIMESTAMP()) \
        .column('open', DataTypes.DECIMAL(9,1)) \
        .column('high', DataTypes.DECIMAL(9,1)) \
        .column('low', DataTypes.DECIMAL(9,1)) \
        .column('close', DataTypes.DECIMAL(9,1)) \
        .column('volume', DataTypes.DECIMAL(15,3)) \
        .build()


def create_jdbc_sink(
        t_env: StreamTableEnvironment, 
        sink_schema: Schema,
        url: str,
        username: str,
        password: str,
        table_name: str) -> str:
    path_sink = 'jdbc_sink'
    sink_table_descriptor = TableDescriptor.for_connector('jdbc') \
        .schema(sink_schema) \
        .option('url', url) \
        .option('username', username) \
        .option('password', password) \
        .option('table-name', table_name) \
        .option('driver', 'org.postgresql.Driver') \
        .build()
    t_env.create_temporary_table(
        path=path_sink,
        descriptor=sink_table_descriptor)
    return path_sink


def create_bigquery_sink(
        t_env: StreamTableEnvironment, 
        sink_schema: Schema,
        project: str,
        dataset: str,
        table: str) -> str:
    path_sink = 'bigquery_sink'
    sink_table_descriptor = TableDescriptor.for_connector('bigquery') \
        .schema(sink_schema) \
        .option('project', project) \
        .option('dataset', dataset) \
        .option('table', table) \
        .build()
    t_env.create_temporary_table(
        path=path_sink,
        descriptor=sink_table_descriptor)
    return path_sink


def create_print_sink(t_env: StreamTableEnvironment, sink_schema: Schema) -> str:
    path_sink = 'print_sink'
    sink_table_descriptor = TableDescriptor.for_connector('print') \
        .schema(sink_schema) \
        .build()
    t_env.create_temporary_table(
        path=path_sink,
        descriptor=sink_table_descriptor)
    return path_sink