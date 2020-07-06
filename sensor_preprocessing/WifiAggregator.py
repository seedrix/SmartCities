import logging
from MqttHandler import MqttHandler, get_sensor_topic
from Aggregator import Aggregator

class WifiAggregator(Aggregator):
    def __init__(self, mqtt_handler):
        super().__init__(mqtt_handler, get_sensor_topic('+', 'wifi', '+', 'list', is_raw=True), 'wifi')

    def _extract_payload(self, message):
        if 'clients' not in message:
            return None
        return message['clients']

    def aggregate_values(self, shop_id, values):
        result_transposed = {}
        for value in values.values():
            value_transposed = {value: key for key, value in value.items()}
            result_transposed.update(value_transposed)
        result = {value: key for key, value in result_transposed.items()}
        count_topic = get_sensor_topic(shop_id, self.sensor_type, None, 'count')
        count_result = MqttHandler.MqttMessage(count_topic, self.generate_payload(shop_id, {'count': len(result)}))
        list_topic = get_sensor_topic(shop_id, self.sensor_type, None, 'list')
        list_result = MqttHandler.MqttMessage(list_topic, self.generate_payload(shop_id, {'clients': result}))
        return [count_result, list_result]


def main(mqtt_handler):
    wifi_aggregator = WifiAggregator(mqtt_handler)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    mqtt_handler = MqttHandler()
    main(mqtt_handler)
    mqtt_handler.loop_forever()