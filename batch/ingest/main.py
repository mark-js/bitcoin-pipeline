import urllib3
import argparse
import polars as pl


def download_file(url_file: str, path_file: str) -> None:
    http = urllib3.PoolManager()
    with http.request(method='GET', url=url_file, preload_content=False) as response:
        if response.status == 200:
            with open(path_file, mode='wb') as f:
                for chunk in response.stream(12*1024*1024):
                    f.write(chunk)
        else:
            raise Exception(f"Failed to download file: HTTP {response.status}")
        
        
# def clean(df:DataFrame) -> DataFrame:
#     df = df.withColumns({
#         'unix_timestamp': col('timestamp'),
#         'timestamp': to_timestamp(col('timestamp')),
#         'grossValue': round(col('grossValue')).cast(LongType()),
#         'foreignNotional': round(col('foreignNotional'), 7).cast(DoubleType())
#     })

#     return df.withColumnsRenamed({
#         'tickDirection': 'tick_direction',
#         'trdMatchID': 'trd_match_id',
#         'grossValue': 'gross_value',
#         'homeNotional': 'home_notional',
#         'foreignNotional': 'foreign_notional',
#         'RPI': 'rpi'
#     })
        

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', required=True)
    parser.add_argument('--bucket', required=True)
    parser.add_argument('--object', required=True)


df = pl.read_csv('https://public.bybit.com/trading/BTCUSDT/BTCUSDT2026-03-09.csv.gz')

df
