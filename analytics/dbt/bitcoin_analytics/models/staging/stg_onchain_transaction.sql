SELECT
    `hash`,
    block_number,
    is_coinbase,
    size,
    virtual_size,
    input_count,
    output_count,
    input_value,
    output_value,
    fee
FROM
    {{ source('onchain_bitcoin', 'transactions') }}
WHERE
    block_timestamp_month = '2026-03-01'