import logging
from MqttHandler import MqttHandler, get_sensor_topic
from Aggregator import Aggregator


class BleAggregator(Aggregator):
    def __init__(self, mqtt_handler):
        super().__init__(mqtt_handler, get_sensor_topic('+', 'ble', '+', 'list', is_raw=True), 'ble')

    def _extract_payload(self, message):
        if 'clients' not in message:
            return None
        return message['clients']

    def aggregate_values(self, shop_id, values):
        result_dup = []
        for value in values.values():
            result_dup = result_dup + value
        result = list(set(result_dup))
        count_topic = get_sensor_topic(shop_id, self.sensor_type, None, 'count')
        count_result = MqttHandler.MqttMessage(count_topic, self.generate_payload(shop_id, {'count': len(result)}))
        list_topic = get_sensor_topic(shop_id, self.sensor_type, None, 'list')
        list_result = MqttHandler.MqttMessage(list_topic, self.generate_payload(shop_id, {'clients': result}))
        return [count_result, list_result]


def main(mqtt_handler):
    ble_aggregator = BleAggregator(mqtt_handler)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    mqtt_handler = MqttHandler()
    main(mqtt_handler)
    mqtt_handler.loop_forever()