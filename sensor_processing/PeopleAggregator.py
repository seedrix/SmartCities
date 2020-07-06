import logging
from math import ceil
from MqttHandler import MqttHandler, get_sensor_topic
from Aggregator import Aggregator


class PeopleAggregator(Aggregator):
    def __init__(self, mqtt_handler):
        super().__init__(mqtt_handler,
                         get_sensor_topic('+', '+', None, 'count'), 'people')

    def _extract_payload(self, message):
        if 'count' not in message:
            return None
        return {'count': message['count'], 'aggregated_sensors': message['aggregated_sensors']}

    def _extract_identifiers(self, message):
        assert isinstance(message, dict)
        if 'sensor_type' not in message or 'shop_id' not in message:
            return None, None
        return message['shop_id'], message['sensor_type']

    def aggregate_values(self, shop_id, values):
        import statistics
        counts = [value['count'] for value in values.values()]
        aggregated_sensors = [value['aggregated_sensors'] for value in values.values()]
        result = ceil(statistics.median(counts))
        total_aggregated_sensors = sum(aggregated_sensors)
        count_topic = get_sensor_topic(shop_id, 'people', None, 'count', use_type_subtopic=False)
        count_result = MqttHandler.MqttMessage(count_topic, self.generate_payload(shop_id, {'count': result,
                                                                                            'aggregated_sensors': total_aggregated_sensors,
                                                                                            'aggregated_sensor_types': list(
                                                                                                values.keys())}))
        return count_result

def main(mqtt_handler):
    people_aggregator = PeopleAggregator(mqtt_handler)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    mqtt_handler = MqttHandler()
    main(mqtt_handler)
    mqtt_handler.loop_forever()