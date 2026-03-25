SELECT
    trd_match_id,
    timestamp,
    symbol,
    side,
    price,
    size,
    tick_direction,
    rpi
FROM
    {{ source('bybit_btcusdt', 'test-gcs-btcusdt') }}
WHERE
    date = '2026-03-15'