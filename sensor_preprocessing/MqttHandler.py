import paho.mqtt.client as mqtt
import json
import logging
import re

broker_hostname = "broker.hivemq.com"
broker_port = 1883

namespace = 'de/smartcity/2020/mymall'

relative_shop_base_topic = '/shops/{shop_id}'

def get_sensor_topic(shop_id, sensor_type, sensor_id, suffix, use_type_subtopic=True, is_raw=False):
    """Generates a string or format string for one topic.
        If shop_id, sensor_type, sensor_id, suffix is True or False, for the respective argument a placeholder will be
        inserted, so it could be substituted with String.format manually.
        If one of these values is set to None, the corresponding part will not be included in the topic.
        If one of these values is set to any other type (likely a string), the value is inserted in the topic.
        If use_type_subtopic is set to False, the outer grouping topic to group all sensor types will not be inserted. 
        If use_type_subtopic is set to a string, this value will be used for the outer grouping topic
        If is_raw is set to True, for the sensor grouping topic 'sensors_raw' will used instead of 'sensors'.
    """
    topic = namespace
    if shop_id is not None:
        if isinstance(shop_id, bool):
            topic += relative_shop_base_topic
        else:
            topic += relative_shop_base_topic.format(shop_id=shop_id)
    if use_type_subtopic is not None:
        if isinstance(use_type_subtopic, bool) and use_type_subtopic:
            if is_raw:
                topic += '/sensors_raw'
            else:
                topic += '/sensors'
        else:
            if isinstance(use_type_subtopic, str):
                topic += '/'+use_type_subtopic

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


class MqttHandler:
    # import paho.mqtt.client as mqtt
    retain_messages = False
    # Set to true to ignore all messages with the retain flag. Only useful for debugging
    ignore_retained_messages = False
    # Set to true to delete all received messages with the retain flag on the broker. Only useful for debugging
    delete_retained_messages = False
    
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
            if __class__.delete_retained_messages:
                client.publish(msg.topic, retain=True)
                logging.info("Deleted received message from broker from topic: %s", msg.topic)
            if __class__.ignore_retained_messages and msg.retain == 1:
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
                client.publish(result.topic, payload=json.dumps(result.message), retain=__class__.retain_messages)

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
