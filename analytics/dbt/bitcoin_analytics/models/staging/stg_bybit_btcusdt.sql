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
    {{ source('tick_data', 'bybit') }}
WHERE
    product = 'BTCUSDT'
    AND date = '2026-03-28'