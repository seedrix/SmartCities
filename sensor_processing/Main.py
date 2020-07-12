import logging
from MqttHandler import MqttHandler
from ShopMapper import main as shop_mapper
from DisplayController import main as display_controller
from WifiAggregator import main as wifi_aggregator
from BleAggregator import main as ble_aggregator
from CamAggregator import main as cam_aggregator
from PeopleAggregator import main as people_aggregator

if __name__ == '__main__':
    MqttHandler.retain_messages = True
    # Set to true to ignore all messages with the retain flag. Only useful for debugging
    MqttHandler.ignore_retained_messages = False
    # Set to true to delete all received messages with the retain flag on the broker. Only useful for debugging
    MqttHandler.delete_retained_messages = False


def main(mqtt_handler):
    shop_mapper(mqtt_handler)
    wifi_aggregator(mqtt_handler)
    ble_aggregator(mqtt_handler)
    cam_aggregator(mqtt_handler)
    people_aggregator(mqtt_handler)
    display_controller(mqtt_handler)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    mqtt_handler = MqttHandler()
    main(mqtt_handler)
    mqtt_handler.loop_forever()
