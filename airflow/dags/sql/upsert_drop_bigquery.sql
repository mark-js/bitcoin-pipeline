MERGE `core.{{ var.json.bybit.product|lower }}` C
USING `staging.{{ var.json.bybit.product }}{{ ds_nodash }}` S
ON C.timestamp = S.timestamp
WHEN MATCHED THEN
    UPDATE SET 
        open = s.open,
        high = s.high,
        low = s.low,
        close = s.close,
        volume = s.volume
WHEN NOT MATCHED THEN
    INSERT (timestamp, open, high, low, close, volume)
    VALUES (timestamp, open, high, low, close, volume);
DROP TABLE `staging.{{ var.json.bybit.product }}{{ ds_nodash }}`;