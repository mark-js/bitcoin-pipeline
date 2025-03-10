import websocket
import json
from confluent_kafka import Producer
from datetime import datetime, timezone

params = {
    'op':'subscribe',
    'args':[
        'publicTrade.BTCUSDT'
    ]
}

def delivery_report(err, msg):
    if err is not None:
        print("Delivery failed for record {}: {}".format(msg.key(), err))
        return
    print(f'Record {msg.key()} successfully produced to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}')
    
def serializer(x):
    return str(x).encode()

def on_open(ws):
    ws.send(json.dumps(params))

def on_message(ws, message):
    bybit_producer.produce(
        topic='BTCUSDT-bybit',
        key=serializer('BTCUSDT-bybit'),
        value=serializer(message),
        on_delivery=delivery_report
    )
    bybit_producer.poll(0)

def on_message_test_delay(ws, message):
    data = json.loads(message)
    if 'ts' in data.keys():
        print(f'delay in seconds - {(datetime.timestamp(datetime.now(timezone.utc)) * 1000 - data['ts']) / 1000}')

def on_error(ws, error):
    print(error)

def websocket_connect():
    wsapp = websocket.WebSocketApp(
        'wss://stream.bybit.com/v5/public/linear', 
        on_open=on_open,
        on_message=on_message, 
        on_error=on_error)
    wsapp.run_forever()

bybit_producer = Producer({
    'bootstrap.servers':'redpanda-0:9092'
})

websocket_connect()