SELECT
    number,
    `hash`,
    coinbase_param,
    bits,
    timestamp,
    transaction_count,
    size,
    stripped_size,
    weight
FROM
    {{ source('onchain_bitcoin', 'blocks') }}
WHERE
    timestamp_month = '2026-03-01'