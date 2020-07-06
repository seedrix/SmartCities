import logging
from MqttHandler import MqttHandler, get_sensor_topic
from Aggregator import Aggregator


class CamAggregator(Aggregator):
    def __init__(self, mqtt_handler):
        super().__init__(mqtt_handler,
                         get_sensor_topic('+', 'cam', '+', 'count', is_raw=True), 'cam')

    def _extract_payload(self, message):
        if 'count' not in message:
            return None
        return message['count']

    def aggregate_values(self, shop_id, values):
        result = 0
        for value in values.values():
            result += value
        count_topic = get_sensor_topic(shop_id, self.sensor_type, None, 'count')
        count_result = MqttHandler.MqttMessage(count_topic, self.generate_payload(shop_id, {'count': result}))
        return count_result

def main(mqtt_handler):
    cam_aggregator = CamAggregator(mqtt_handler)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    mqtt_handler = MqttHandler()
    main(mqtt_handler)
    mqtt_handler.loop_forever()