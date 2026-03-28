import json
import os
from typing import Dict

from websocket import WebSocketApp
from confluent_kafka import Producer


class BybitWebsocketProducer:
    def __init__(
            self, websocket_url: str, 
            subscription_params: Dict[str, str], 
            kafka_config: Dict[str, str], 
            topic_name: str):
        self.websocket_url = websocket_url
        self.subscription_params = subscription_params
        self.topic_name = topic_name
        self.producer = Producer(kafka_config)

    def connect(self) -> None:
        wsapp = WebSocketApp(
            self.websocket_url, 
            on_open=self._on_open,
            on_message=self._on_message, 
            on_error=self._on_error)
        wsapp.run_forever()

    def _on_open(self, ws) -> None:
        ws.send(json.dumps(self.subscription_params))

    def _on_message(self, ws, message) -> None:
        data_list = json.loads(message)['data']
        for data in data_list:
            self.producer.produce(
                topic=self.topic_name,
                key=self.topic_name.encode(),
                value=self._serializer(data),
                on_delivery=self._delivery_report
            )
        self.producer.poll(0)

    @staticmethod
    def _on_error(ws, error) -> None:
        print(error)

    @staticmethod
    def _delivery_report(error, msg) -> None:
        if error is not None:
            print("Delivery failed for record {}: {}".format(msg.key(), error))

    @staticmethod
    def _serializer(x: str) -> bytes:
        return json.dumps(x).encode()
    

def main():
    websocket_url = 'wss://stream.bybit.com/v5/public/linear'
    subscription_params = {
        'op':'subscribe',
        'args':['publicTrade.BTCUSDT']
    }
    kafka_config = {'bootstrap.servers':os.environ['REDPANDA_ADDR']}
    topic_name = 'btcusdt-bybit'

    producer = BybitWebsocketProducer(
        websocket_url, subscription_params, kafka_config, topic_name)
    producer.connect()

    
if __name__ == '__main__':
    main()
    