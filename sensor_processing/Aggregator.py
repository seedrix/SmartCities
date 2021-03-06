from MqttHandler import MqttHandler, get_sensor_topic
import logging

class Aggregator:
    def __init__(self, mqtt_handler, in_topic, sensor_type):
        self.log = logging.getLogger(self.__class__.__name__)
        self.shop_values = {}
        self.in_topic = in_topic
        self.sensor_type = sensor_type
        mqtt_handler.register_handler(self.in_topic, self._aggregate_message)
        self.log.info('Created %s', self.__class__.__name__)

    def update(self, shop_id, sensor_id, value):
        if shop_id not in self.shop_values:
            self.shop_values[shop_id] = {}
            self.log.info("New shop: %s", shop_id)
        shop_value = self.shop_values[shop_id]
        if sensor_id not in shop_value:
            self.log.info('Added sensor instance for shop %s: %s', shop_id, sensor_id)
        shop_value[sensor_id] = value

    def delete(self, shop_id, sensor_id):
        if shop_id not in self.shop_values:
            self.log.info("New shop: %s", shop_id)
            self.shop_values[shop_id] = {}
            return
        shop_value = self.shop_values[shop_id]
        if sensor_id not in shop_value:
            return
        self.log.info('Deleted sensor instance for shop %s: %s', shop_id, sensor_id)   
        del shop_value[sensor_id]  

    def get_values(self, shop_id):
        if shop_id not in self.shop_values:
            return
        return self.shop_values[shop_id]

    def _extract_payload(self, message):
        # Must be overridden in child class
        pass

    def _extract_identifiers(self, message):
        assert isinstance(message, dict)
        if 'sensor_id' not in message or 'shop_id' not in message:
            return None, None
        return message['shop_id'], message['sensor_id']

    def _aggregate_message(self, topic, message):
        assert isinstance(message, dict)
        shop_id, sensor_id = self._extract_identifiers(message)
        if shop_id is None or sensor_id is None:
            self.log.warning("Can not aggregate message for sensor type %s from topic %s: identifier(s) missing",
                            self.sensor_type, topic)
            return
        payload = self._extract_payload(message)
        if payload is None:
            self.log.warning("Can not aggregate message for sensor %s %s from topic %s: payload missing",
                            self.sensor_type, sensor_id, topic)
            return
        if 'delete' in message and message['delete']:
            # delete this sensor
            self.delete(shop_id, sensor_id)
        else:
            self.update(shop_id, sensor_id, payload)
        return self.aggregate_values(shop_id, self.get_values(shop_id))

    def generate_payload(self, shop_id, data):
        payload = {'shop_id': shop_id, 'aggregated_sensors': len(self.get_values(shop_id)),
                   'sensor_type': self.sensor_type}
        if len(self.get_values(shop_id)) == 0:
            payload.update({'delete': True})
        payload.update(data)
        return payload
