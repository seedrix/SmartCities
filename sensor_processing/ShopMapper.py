import logging as pylog
from pymongo import MongoClient
from pymongo import errors as mongoErrors
from MqttHandler import MqttHandler, get_sensor_topic

logging = pylog.getLogger(__name__)

if __name__ == '__main__':
    MqttHandler.retain_messages = False
    # Set to true to ignore all messages with the retain flag. Only useful for debugging
    MqttHandler.ignore_retained_messages = False
    # Set to true to delete all received messages with the retain flag on the broker. Only useful for debugging
    MqttHandler.delete_retained_messages = False



class DB_Handler_Pre:

    def __init__(self):
        from MongoCredentials import MONGO_IP, MONGO_PORT, MONGO_USER, MONGO_PW, MONGO_DB
        MONGO_COLLECTION_SHOPS = "shops"
        MONGO_TIMEOUT = 1000  # Time in ms

        logging.info("Connecting Mongo")
        self.client = MongoClient(f"mongodb://{MONGO_USER}:{MONGO_PW}@{MONGO_IP}:{MONGO_PORT}", serverSelectionTimeoutMS=MONGO_TIMEOUT)
        try:
            self.client.server_info()
        except mongoErrors.PyMongoError as e:
            logging.error("Mongo connection failed: "+ str(e))
            raise
        database = self.client.get_database(MONGO_DB)
        self.shops_collection = database.get_collection(MONGO_COLLECTION_SHOPS)
    
    def __del__(self):
        logging.info("Close DB connection")
        if self.client is not None:
            self.client.close()

    def get_shops(self):
        shops = list(self.shops_collection.find( {}, { "shop_id": 1, "max_people": 1, "sensors": 1 } ))
        for shop in shops:
            del shop['_id']
        return shops



class SensorShopMapper:

    def __init__(self, connection_keep_alive=False):
        self.db_handler = None
        if connection_keep_alive:
            self.db_handler = DB_Handler_Pre()

    def _get_db_handler(self):
        if self.db_handler is None:
            return DB_Handler_Pre()
        return self.db_handler

    def get_sensors_to_shops_mapping(self):
        db = self._get_db_handler()
        shops = db.get_shops()
        sensor_mapping = dict()
        for shop in shops:
            if 'shop_id' not in shop or 'sensors' not in shop:
                logging.warning("DB Shop entry %s is missung attribuites: shop_id or shops", str(shop))
                continue
            shop_id = shop['shop_id']
            sensors = shop['sensors']
            for sensor_id in sensors:
                if sensor_id in sensor_mapping:
                    logging.warning("Sensor %s is assigned to multiple shops: %s and %s",sensor_id, shop_id, sensor_mapping[sensor_id])
                    continue
                sensor_mapping[sensor_id] = shop_id
        return sensor_mapping

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

def main(mqtt_handler):
    sensor_mapper = SensorShopMapper()
    shop_mapping = sensor_mapper.get_sensors_to_shops_mapping()

    if shop_mapping is None:
        # remove if database connection is implemented
        shop_mapping = {"bB8:27:EB:2A:C9:E6": "shop1", "wb8:27:eb:d5:36:19": "shop1", "ccamera0": "shop1"}
    else:
        logging.debug("Shop mapping: %s", str(shop_mapping))

    wifi_mapper = ShopMapper(mqtt_handler, "wifi", shop_mapping)
    ble_mapper = ShopMapper(mqtt_handler, "ble", shop_mapping)
    cam_mapper = ShopMapper(mqtt_handler, "cam", shop_mapping)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    mqtt_handler = MqttHandler()
    main(mqtt_handler)
    mqtt_handler.loop_forever()