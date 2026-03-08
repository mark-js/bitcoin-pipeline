import argparse

from pyspark.sql import SparkSession, types, DataFrame
import pyspark.sql.functions as F


def clean_types(df: DataFrame) -> DataFrame:
    return df.withColumns({
        'grossValue':F.round(df.grossValue).cast(types.LongType()),
        'foreignNotional':F.round(df.foreignNotional, 4).cast(types.DoubleType())
    })


def transform_ohlcv(df: DataFrame) -> DataFrame:
    df_transform = df.select(
        F.to_timestamp(df.timestamp).alias('timestamp'),
        df.symbol,
        df.price,
        df.size
    )
    w = df_transform.groupby(F.window(df_transform.timestamp, '1 minute')).agg(
        F.first(df.symbol).alias('symbol'),
        F.first(df.price).cast(types.DecimalType(9, 1)).alias('open'),
        F.max(df.price).cast(types.DecimalType(9, 1)).alias('high'),
        F.min(df.price).cast(types.DecimalType(9, 1)).alias('low'),
        F.last(df.price).cast(types.DecimalType(9, 1)).alias('close'),
        F.sum(df.size).cast(types.DecimalType(15, 3)).alias('volume')
    )
    return w.select(
        w.window.start.alias('timestamp'),
        w.open,
        w.high,
        w.low,
        w.close,
        w.volume
    ).sort(w.window.start)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--temp_bucket', required=True)
    parser.add_argument('--input', required=True)
    parser.add_argument('--output_raw', required=True)
    parser.add_argument('--output_table', required=True)
    args = parser.parse_args()

    schema = types.StructType(
        [
            types.StructField('timestamp', types.DecimalType(15, 4), True),
            types.StructField('symbol', types.StringType(), True),
            types.StructField('side', types.StringType(), True),
            types.StructField('size', types.DecimalType(15, 3), True),
            types.StructField('price', types.DecimalType(9, 1), True),
            types.StructField('tickDirection', types.StringType(), True),
            types.StructField('trdMatchID', types.StringType(), True),
            types.StructField('grossValue', types.DoubleType(), True),
            types.StructField('homeNotional', types.DoubleType(), True),
            types.StructField('foreignNotional', types.DoubleType(), True)
        ]
    )

    spark = SparkSession.builder \
        .appName('bybit pipeline') \
        .getOrCreate()
    spark.conf.set('temporaryGcsBucket', args.temp_bucket)
    
    df = spark.read \
        .option('header', True) \
        .schema(schema) \
        .csv(args.input)
    df_clean = clean_types(df)
    df_ohlcv = transform_ohlcv(df_clean)
    df_clean.write.parquet(args.output_raw, mode='overwrite')
    df_ohlcv.write.format('bigquery') \
        .option('table', args.output_table) \
        .save()


if __name__ == '__main__':
    main()

    