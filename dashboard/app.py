import argparse
import os
from datetime import datetime
import threading
from typing import Tuple

from dash import Dash, Output, Input
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import polars as pl

from bitcoin_pipeline.dash_app.subplot import make_candlestick_subplot
from bitcoin_pipeline.dash_app.layout import layout
from bitcoin_pipeline.duckdb_cache.duckdb_cache import DuckDBCache
from bitcoin_pipeline.kafka.consumer import LiveDataConsumer


def dash_app(
        live_query: str, 
        historical_query: str,
        cache_live: DuckDBCache, 
        cache_historical: DuckDBCache, 
        kafka_consumer: LiveDataConsumer) -> None:
    app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
    app.layout = layout

    @app.callback(
        Output('live-graph', 'figure'),
        Input('live-graph-interval-component', 'n_intervals')
    )
    def update_live_graph(n):
        df_live = cache_live.get_data(live_query).pl()

        candlestick_stream = go.Candlestick(
            x=[kafka_consumer.live_graph_previous.get('timestamp'), kafka_consumer.live_graph.get('timestamp')],
            open=[kafka_consumer.live_graph_previous.get('open'), kafka_consumer.live_graph.get('open')],
            high=[kafka_consumer.live_graph_previous.get('high'), kafka_consumer.live_graph.get('high')],
            low=[kafka_consumer.live_graph_previous.get('low'), kafka_consumer.live_graph.get('low')],
            close=[kafka_consumer.live_graph_previous.get('close'), kafka_consumer.live_graph.get('close')])
        candlestick_database = go.Candlestick(
            x=df_live.to_series(0).to_list(),
            open=df_live.to_series(1).to_list(),
            high=df_live.to_series(2).to_list(),
            low=df_live.to_series(3).to_list(),
            close=df_live.to_series(4).to_list())

        bar_stream = go.Bar(
            x=[kafka_consumer.live_graph_previous.get('timestamp'), kafka_consumer.live_graph.get('timestamp')],
            y=[kafka_consumer.live_graph_previous.get('volume'), kafka_consumer.live_graph.get('volume')])
        bar_database = go.Bar(
            x=df_live.to_series(0).to_list(),
            y=df_live.to_series(5).to_list())

        fig = make_candlestick_subplot(
            candlestick_traces=[candlestick_database, candlestick_stream],
            bar_traces=[bar_database, bar_stream])
        fig.add_hline(
            y=kafka_consumer.live_graph.get('close'),
            line_dash='dot',
            annotation_text=f"{kafka_consumer.live_graph.get('close'):.1f}",
            annotation_position='right',
            annotation_bgcolor='black',
            annotation_font={'color':'white'},
            row=1, col=1
        )
        fig.add_hline(
            y=kafka_consumer.live_graph.get('volume'),
            annotation_text=f'{kafka_consumer.live_graph.get('volume'):.3f}',
            line_width=0,
            annotation_position='right',
            annotation_bgcolor='black',
            annotation_font={'color':'white'},
            row=2, col=1
        )
        return fig
    
    @app.callback(
        Output('live-table', 'data'),
        Input('live-table-interval-component', 'n_intervals')
    )
    def update_live_table(n):
        return list(kafka_consumer.live_table)

    @app.callback(
        Output('historical-graph', 'figure'),
        Input('historical-selection', 'value')
    )
    def update_historical_graph(value):
        df_historic = cache_historical.get_data(historical_query).pl() \
            .sort('timestamp') \
            .group_by_dynamic('timestamp', every=f'{value}m') \
            .agg(
                pl.col('open').first(),
                pl.col('high').max(),
                pl.col('low').min(),
                pl.col('close').last(),
                pl.col('volume').sum()) \
            .slice(-240)
            
        candlestick_historic = go.Candlestick(
                x=df_historic.to_series(0).to_list(),
                open=df_historic.to_series(1).to_list(),
                high=df_historic.to_series(2).to_list(),
                low=df_historic.to_series(3).to_list(),
                close=df_historic.to_series(4).to_list())
        bar_historic = go.Bar(
            x=df_historic.to_series(0).to_list(),
            y=df_historic.to_series(5).to_list())
        
        fig = make_candlestick_subplot(
            candlestick_traces=[candlestick_historic], 
            bar_traces=[bar_historic])
        return fig
    
    app.run(host='0.0.0.0', port=8050)


def setup_queries(run_mode: str) -> Tuple[str, str]:
    if run_mode == 'gcp':
        historical_query = """
            SELECT timestamp, open, high, low, close, volume
            FROM bq.core.btcusdt
            WHERE AGE(CAST(CURRENT_DATE + CURRENT_TIME AS TIMESTAMP), timestamp) <= INTERVAL 10 DAYS;
        """
    elif run_mode == 'local':
        historical_query = """
            SELECT timestamp, open, high, low, close, volume
            FROM db.core.btcusdt
            WHERE AGE(CAST(CURRENT_DATE + CURRENT_TIME AS TIMESTAMP), timestamp) <= INTERVAL 10 DAYS;
        """
    else:
        raise ValueError("Unsupported run_mode. Should be 'gcp' or 'local'")
    
    live_query = """
        SELECT timestamp, open, high, low, close, volume
        FROM db.core.btcusdt_live
        WHERE AGE(CAST(CURRENT_DATE + CURRENT_TIME AS TIMESTAMP), timestamp) <= INTERVAL 1 HOUR;
    """
    return live_query, historical_query
    

def setup_cache(run_mode: str, live_query: str, historical_query: str) -> Tuple[DuckDBCache, DuckDBCache]:
    if run_mode == 'gcp':
        attach_query = """
                INSTALL bigquery FROM community;
                LOAD bigquery;
                ATTACH 'project=development-456611' AS bq (TYPE bigquery, READ_ONLY);
            """
        cache_historical = DuckDBCache()
        cache_historical.connect_query(attach_query)
    elif run_mode == 'local':
        cache_historical = DuckDBCache()
        cache_historical.connect_database(database_con=os.environ['DASH_POSTGRES_URL'], database_type='postgres')
    else:
        raise ValueError("Unsupported run_mode. Should be 'gcp' or 'local'")

    cache_live = DuckDBCache()
    cache_live.connect_database(database_con=os.environ['DASH_POSTGRES_URL'], database_type='postgres')

    cache_live.set_schedule_reset(live_query, second=1, interval=60)
    cache_historical.set_schedule_reset(historical_query, hour=0, minute=5, second=0, interval=600)
    return cache_live, cache_historical


def setup_consumer() -> LiveDataConsumer:
    bybit_consumer_config = {
        'bootstrap.servers':os.environ['DASH_REDPANDA_ADDR'],
        'auto.offset.reset':'latest',       
        'group.id':f"dash-consumer-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        'enable.auto.commit':'false'
    }
    return LiveDataConsumer(bybit_consumer_config)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('run_mode', choices=['gcp', 'local'])
    args = parser.parse_args()

    live_query, historical_query = setup_queries(args.run_mode)
    cache_live, cache_historical = setup_cache(args.run_mode, live_query, historical_query)
    kafka_consumer = setup_consumer()

    bybit_consumer_config = {
        'bootstrap.servers':os.environ['DASH_REDPANDA_ADDR'],
        'auto.offset.reset':'latest',       
        'group.id':f"dash-consumer-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        'enable.auto.commit':'false'
    }
    bybit_consumer_topics = ['btcusdt-bybit']
    kafka_consumer = LiveDataConsumer(bybit_consumer_config)  

    t1 = threading.Thread(target=kafka_consumer.consume, args=[bybit_consumer_topics])
    t2 = threading.Thread(target=dash_app, args=[live_query, historical_query, cache_live, cache_historical, kafka_consumer])

    t1.start()
    t2.start()


if __name__ == '__main__':
    main()
    