import argparse

import polars as pl
from google.cloud import storage

FrameType = pl.DataFrame | pl.LazyFrame
     
        
def clean(df: FrameType) -> FrameType:
    df = df.with_columns(
        pl.col('timestamp').alias('unix_timestamp'),
        pl.from_epoch(pl.col('timestamp')*1_000_000, time_unit='us').alias('timestamp'),
        pl.col('grossValue').round().cast(pl.Int64).alias('grossValue'),
        pl.col('foreignNotional').round(4).alias('foreignNotional')
    )
    return df.rename({
        'tickDirection': 'tick_direction',
        'trdMatchID': 'trd_match_id',
        'grossValue': 'gross_value',
        'homeNotional': 'home_notional',
        'foreignNotional': 'foreign_notional',
        'RPI': 'rpi'
    })


def upload_to_gcs(file_path: str, bucket_name: str, object_name: str) -> None:
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(object_name)
    blob.upload_from_filename(file_path)
        

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', required=True)
    parser.add_argument('--bucket', required=True)
    parser.add_argument('--object', required=True)
    args = parser.parse_args()

    schema = pl.Schema(
        [
            ('timestamp', pl.Float64),
            ('symbol', pl.String),
            ('side', pl.String),
            ('size', pl.Float64),
            ('price', pl.Float64),
            ('tickDirection', pl.String),
            ('trdMatchID', pl.String),
            ('grossValue', pl.Float64),
            ('homeNotional', pl.Float64),
            ('foreignNotional', pl.Float64),
            ('RPI', pl.Int64)
        ]
    )

    df = pl.scan_csv(args.url, schema=schema)
    df_clean = clean(df=df)

    tmp_file = '/tmp/data.parquet'
    df_clean.collect().write_parquet(tmp_file, compression='zstd', compression_level=5)
    upload_to_gcs(file_path=tmp_file, bucket_name=args.bucket, object_name=args.object)


if __name__ == '__main__':
    main()
