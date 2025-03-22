INSERT INTO core.{{ var.json.bybit.product }} (timestamp, open, high, low, close, volume)
SELECT timestamp, open, high, low, close, volume FROM staging.{{ var.json.bybit.product }}{{ ds_nodash }}
ON CONFLICT(timestamp) DO UPDATE SET
    open = EXCLUDED.open,
    high = EXCLUDED.high,
    low = EXCLUDED.low,
    close = EXCLUDED.close,
    volume = EXCLUDED.volume;

DROP TABLE staging.{{ var.json.bybit.product }}{{ ds_nodash }};