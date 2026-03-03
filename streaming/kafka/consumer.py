from collections import deque
from datetime import datetime
import json
from typing import List, Dict

from confluent_kafka import Consumer


class LiveDataConsumer:
    def __init__(self, config: dict):
        self.live_graph = {}
        self.live_graph_previous = {}
        self.live_table = deque([], 15)
        self.consumer = Consumer(config)

    def consume(self, topics: List[str]) -> None:
        self.consumer.subscribe(topics=topics)
        while True:
            message = self.consumer.poll(0)
            if message is None:
                continue
            key = self._key_deserializer(message.key())
            record = self._value_deserializer(message.value())
            self._update_live_graph_data(record)
            self._update_live_table_data(record)

    def close(self) -> None:
        self.consumer.close()

    def _update_live_graph_data(self, record: Dict) -> None:
        if not record:
            return

        current_ts = datetime.fromtimestamp(record.get('T')/1000).replace(second=0, microsecond=0)
        previous_ts = self.live_graph.get('timestamp')
        current_price = float(record.get('p'))
        current_volume = float(record.get('v'))
        
        if previous_ts and current_ts.minute == previous_ts.minute:
            self.live_graph['high'] = max(self.live_graph.get('high', 0), current_price)
            self.live_graph['low'] = min(self.live_graph.get('low', 0), current_price)
            self.live_graph['volume'] += current_volume 
        else:
            self.live_graph_previous = self.live_graph.copy()
            self.live_graph['open'] = current_price
            self.live_graph['high'] = current_price
            self.live_graph['low'] = current_price
            self.live_graph['volume'] = 0

        self.live_graph['timestamp'] = current_ts
        self.live_graph['close'] = current_price

    def _update_live_table_data(self, record: Dict) -> None:
        if not record:
            return
        data = {
            'timestamp':datetime.fromtimestamp(record.get('T')/1000).strftime('%H:%M:%S.%f')[:-3],
            'price':float(record.get('p')),
            'volume':float(record.get('v')),
            'direction':record.get('S')
        }
        self.live_table.appendleft(data)
        
    @staticmethod
    def _key_deserializer(key: bytes) -> str:
        return str(key.decode('utf-8'))

    @staticmethod
    def _value_deserializer(value: bytes) -> Dict:
        return json.loads(value.decode('utf-8'))


    