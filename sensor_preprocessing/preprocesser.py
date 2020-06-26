import paho.mqtt.client as mqtt
import json
import logging
import re

broker_hostname = "broker.hivemq.com"
broker_port = 1883

namespace = 'de/smartcity/2020/mymall'

relative_shop_base_topic = '/shops/{shop_id}'

retain_messages = False
# Set to true to ignore all messages with the retain flag. Only useful for debugging
ignore_retained_messages = False
# Set to true to delete all received messages with the retain flag on the broker. Only useful for debugging
delete_retained_messages = False


def get_sensor_topic(shop_id, sensor_type, sensor_id, suffix, use_type_subtopic=True, is_raw=False):
    """Generates a string or format string for one topic.
        If shop_id, sensor_type, sensor_id, suffix is True or False, for the respective argument a placeholder will be
        inserted, so it could be substituted with String.format manually.
        If one of these values is set to None, the corresponding part will not be included in the topic.
        If one of these values is set to any other type (likely a string), the value is inserted in the topic.
        If use_type_subtopic is set to False, the outer grouping topic to group all sensor types will not be inserted.
        If is_raw is set to True, for the sensor grouping topic 'sensors_raw' will used instead of 'sensors'.
    """
    topic = namespace
    if shop_id is not None:
        if isinstance(shop_id, bool):
            topic += relative_shop_base_topic
        else:
            topic += relative_shop_base_topic.format(shop_id=shop_id)
    if use_type_subtopic:
        if is_raw:
            topic += '/sensors_raw'
        else:
            topic += '/sensors'
    if isinstance(sensor_type, bool):
        topic += '/{sensor_type}'
    else:
        topic += '/' + str(sensor_type)
    if sensor_id is not None:
        if isinstance(sensor_id, bool):
            topic += '/{sensor_id}'
        else:
            topic += '/' + str(sensor_id)
    if suffix is not None:
        if isinstance(suffix, bool):
            topic += '/{suffix}'
        else:
            topic += '/' + str(suffix)
    return topic


class SensorShopMapper:

    def __init__(self):
        # Todo get Database handler?
        pass

    def get_sensors_to_shops_mapping(self):
        # Todo: retrieve mapping from database
        pass


class MqttHandler:
    # import paho.mqtt.client as mqtt

    class MqttMessage:

        def __init__(self, topic, message):
            self.topic = topic
            self.message = message

    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_message = self._default_handler
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.connect(broker_hostname, broker_port, 60)

    def _on_connect(self, client, userdata, flags, rc):
        logging.info("Connected to mqtt broker with result code %s", str(rc))

    def _on_disconnect(self, client, userdata, rc):
        logging.warning("Mqtt client disconnected with result code %s", str(rc))

    def register_handler(self, input_topic, data_callback):
        logging.debug("Register topic %s", input_topic)
        self.client.subscribe(input_topic)

        def _callback(client, userdata, msg):
            if msg.payload is None or len(msg.payload) == 0:
                logging.debug("Ignore message with empty payload from topic: %s", msg.topic)
                return
            if delete_retained_messages:
                client.publish(msg.topic, retain=True)
                logging.info("Deleted received message from broker from topic: %s", msg.topic)
            if ignore_retained_messages and msg.retain == 1:
                logging.info("Dropping retained message from topic %s: %s", msg.topic, msg.payload)
                return
            logging.info("Got message from topic %s: %s", msg.topic, msg.payload)
            try:
                msg_dict = json.loads(msg.payload)
            except json.JSONDecodeError as e:
                logging.warning('Could not parse message to json from topic %s: %s  \nException: %s', msg.topic,
                                msg.payload, e)
                return
            if not isinstance(msg_dict, dict):
                logging.warning('Got message from %s with illegal format (expect dict, got %s): %s', msg.topic,
                                type(msg_dict), msg.payload)
                return
            results = data_callback(msg.topic, msg_dict)
            if results is None:
                return
            if type(results) is not list:
                results = [results]
            assert isinstance(results[0], MqttHandler.MqttMessage)
            for result in results:
                assert isinstance(result, MqttHandler.MqttMessage)
                logging.info("Publishing result to topic %s: %s", result.topic, result.message)
                client.publish(result.topic, payload=json.dumps(result.message), retain=retain_messages)

        self.client.message_callback_add(input_topic, callback=_callback)

    def _default_handler(self, client, userdata, msg):
        logging.warning("Message for topic %s is not caught by any filter: %s", msg.topic, msg.payload)

    def loop_forever(self):
        self.client.loop_forever()

    def start_loop_thread(self):
        self.client.loop_start()

    @staticmethod
    def extract_placeholder_value(subscribed_topic, topic_name):
        # works only with one placeholder in topic
        splited = subscribed_topic.split("+")
        left_part = re.escape(splited[0])
        right_part = ""
        if len(splited) > 1:
            if splited[1][-1] == '#':
                # multilevel wildcard at the end
                right_part = re.escape(subscribed_topic.split("+")[1][:-2]) + "(?:/.*)?$"
            else:
                right_part = re.escape(subscribed_topic.split("+")[1])
        pattern = re.compile(left_part + r"([^/]+)" + right_part)
        return pattern.match(topic_name).group(1)


class Aggregator:
    def __init__(self, mqtt_handler, in_topic, sensor_type):
        self.shop_values = {}
        self.in_topic = in_topic
        self.sensor_type = sensor_type
        mqtt_handler.register_handler(self.in_topic, self._aggregate_message)

    def update(self, shop_id, sensor_id, value):
        if shop_id not in self.shop_values:
            self.shop_values[shop_id] = {}
            logging.info("New shop: %s", shop_id)
        shop_value = self.shop_values[shop_id]
        if sensor_id not in shop_value:
            logging.info('Added sensor instance for shop %s: %s', shop_id, sensor_id)
        shop_value[sensor_id] = value

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
            logging.warning("Can not aggregate message for sensor type %s from topic %s: identifier(s) missing",
                            self.sensor_type, topic)
            return
        payload = self._extract_payload(message)
        if payload is None:
            logging.warning("Can not aggregate message for sensor %s %s from topic %s: payload missing",
                            self.sensor_type, sensor_id, topic)
            return
        self.update(shop_id, sensor_id, payload)
        return self.aggregate_values(shop_id, self.get_values(shop_id))

    def generate_payload(self, shop_id, data):
        payload = {'shop_id': shop_id, 'aggregated_sensors': len(self.get_values(shop_id)),
                   'sensor_type': self.sensor_type}
        payload.update(data)
        return payload


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
        result = round(statistics.median(counts))
        total_aggregated_sensors = sum(aggregated_sensors)
        count_topic = get_sensor_topic(shop_id, 'people', None, 'count', use_type_subtopic=False)
        count_result = MqttHandler.MqttMessage(count_topic, self.generate_payload(shop_id, {'count': result,
                                                                                            'aggregated_sensors': total_aggregated_sensors,
                                                                                            'aggregated_sensor_types': list(
                                                                                                values.keys())}))
        return count_result


class ShopMapper:
    def __init__(self, mqtt_handler, sensor_type, sensor_to_shop_dict):
        assert isinstance(mqtt_handler, MqttHandler)
        self.mqtt_handler = mqtt_handler
        self.sensor_to_shop_dict = sensor_to_shop_dict
        self.sensor_type = sensor_type
        input_topic_list = get_sensor_topic(None, self.sensor_type, '+', 'list')
        mqtt_handler.register_handler(input_topic_list, self._map_message_list)
        input_topic_count = get_sensor_topic(None, self.sensor_type, '+', 'count')
        mqtt_handler.register_handler(input_topic_count, self._map_message_count)
        logging.info("Created shop mapper for %s", sensor_type)

    def _map_message_list(self, topic, message):
        return self._map_message('list', message)

    def _map_message_count(self, topic, message):
        return self._map_message('count', message)

    def _map_message(self, suffix, message):
        if 'sensor_id' not in message:
            logging.warning("Can not map %s sensor message to shop: sensor_id attribute missing", self.sensor_type)
            return
        sensor_id = message['sensor_id']
        if sensor_id not in self.sensor_to_shop_dict:
            logging.warning("No shop found for sensor from type %s with id: %s", self.sensor_type, sensor_id)
            return
        shop = self.sensor_to_shop_dict[sensor_id]
        logging.debug("Mapped sensor %s %s to shop %s", self.sensor_type, sensor_id, shop)
        message.update({'shop_id': shop, 'sensor_type': self.sensor_type})
        return MqttHandler.MqttMessage(get_sensor_topic(shop, self.sensor_type, sensor_id, suffix, is_raw=True),
                                       message)


logging.basicConfig(level=logging.DEBUG)

sensor_mapper = SensorShopMapper()
shop_mapping = sensor_mapper.get_sensors_to_shops_mapping()

if shop_mapping is None:
    # remove if database connection is implemented
    shop_mapping = {"bB8:27:EB:2A:C9:E6": "shop1", "wb8:27:eb:d5:36:19": "shop1", "ccamera0": "shop1"}

mqtt_handler = MqttHandler()
wifi_mapper = ShopMapper(mqtt_handler, "wifi", shop_mapping)
ble_mapper = ShopMapper(mqtt_handler, "ble", shop_mapping)
cam_mapper = ShopMapper(mqtt_handler, "cam", shop_mapping)
wifi_aggregator = WifiAggregator(mqtt_handler)
ble_aggregator = BleAggregator(mqtt_handler)
cam_aggregator = CamAggregator(mqtt_handler)
people_aggregator = PeopleAggregator(mqtt_handler)
mqtt_handler.loop_forever()
