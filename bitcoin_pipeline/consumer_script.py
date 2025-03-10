from confluent_kafka import Consumer
import json
from datetime import datetime, timezone


def key_deserializer(key):
    return str(key.decode('utf-8'))

def value_deserializer(value):
    return json.loads(value.decode('utf-8'))


bybit_consumer = Consumer(
    {
        'bootstrap.servers':'redpanda-0:9092',
        'auto.offset.reset':'latest',       
        'group.id':'consumer.1'
    }
)

bybit_consumer.subscribe(topics=['BTCUSDT-bybit'])

while True:
    try:
        message = bybit_consumer.poll(0)
        if message is None:
            continue
        key = key_deserializer(message.key())
        record = value_deserializer(message.value())
        record['timestamp'] = datetime.timestamp(datetime.now(timezone.utc)) * 1000
        if 'ts' in record.keys() and record is not None:
            # print(f'{key}, {record}')
            print(f'delay in seconds - {(record['timestamp'] - record['ts']) / 1000}')
    except KeyboardInterrupt:
        break

bybit_consumer.close() 