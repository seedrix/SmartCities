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

# Source: Adam Luchjenbroers, https://stackoverflow.com/questions/1969240/mapping-a-range-of-values-to-another
def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

class DB_Handler_Act:

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


class DisplayActorController:
    # from Ashraf jawad eshtawe, https://www.iconfinder.com/icons/387517/character_math_minus_sign_stop_icon, no link back required
    symbol_stop = "data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiA/PjwhRE9DVFlQRSBzdmcgIFBVQkxJQyAnLS8vVzNDLy9EVEQgU1ZHIDEuMC8vRU4nICAnaHR0cDovL3d3dy53My5vcmcvVFIvMjAwMS9SRUMtU1ZHLTIwMDEwOTA0L0RURC9zdmcxMC5kdGQnPjxzdmcgZW5hYmxlLWJhY2tncm91bmQ9Im5ldyAwIDAgOTEuOCA5Mi42IiBpZD0iTGF5ZXJfMSIgdmVyc2lvbj0iMS4wIiB2aWV3Qm94PSIwIDAgOTEuOCA5Mi42IiB4bWw6c3BhY2U9InByZXNlcnZlIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIj48cGF0aCBkPSJNNDYuMywzLjZjLTIzLjUsMC00Mi41LDE5LTQyLjUsNDIuNWMwLDIzLjUsMTksNDIuNSw0Mi41LDQyLjVjMjMuNSwwLDQyLjUtMTksNDIuNS00Mi41ICBDODguOSwyMi43LDY5LjgsMy42LDQ2LjMsMy42eiBNNzYuNCw1My4zSDE1LjNjLTIuMSwwLTMuOS0xLjgtMy45LTMuOXYtNi40YzAtMi4xLDEuOC0zLjksMy45LTMuOWg2MS4xYzIuMSwwLDMuOSwxLjgsMy45LDMuOXY2LjQgIEM4MC4zLDUxLjUsNzguNiw1My4zLDc2LjQsNTMuM3oiIGZpbGw9IiMxRTFFMUUiLz48L3N2Zz4="
    # from Icons8, https://www.iconfinder.com/icons/2639876/check_checkmark_icon, no link back required
    symbol_checkmark = "data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiA/PjxzdmcgaWQ9IkxheWVyXzEiIHN0eWxlPSJlbmFibGUtYmFja2dyb3VuZDpuZXcgMCAwIDMwIDMwOyIgdmVyc2lvbj0iMS4xIiB2aWV3Qm94PSIwIDAgMzAgMzAiIHhtbDpzcGFjZT0icHJlc2VydmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiPjxwYXRoIGQ9Ik0xNSwzQzguMzczLDMsMyw4LjM3MywzLDE1YzAsNi42MjcsNS4zNzMsMTIsMTIsMTJzMTItNS4zNzMsMTItMTJDMjcsOC4zNzMsMjEuNjI3LDMsMTUsM3ogTTIxLjcwNywxMi43MDdsLTcuNTYsNy41NiAgYy0wLjE4OCwwLjE4OC0wLjQ0MiwwLjI5My0wLjcwNywwLjI5M3MtMC41Mi0wLjEwNS0wLjcwNy0wLjI5M2wtMy40NTMtMy40NTNjLTAuMzkxLTAuMzkxLTAuMzkxLTEuMDIzLDAtMS40MTRzMS4wMjMtMC4zOTEsMS40MTQsMCAgbDIuNzQ2LDIuNzQ2bDYuODUzLTYuODUzYzAuMzkxLTAuMzkxLDEuMDIzLTAuMzkxLDEuNDE0LDBTMjIuMDk4LDEyLjMxNiwyMS43MDcsMTIuNzA3eiIvPjwvc3ZnPg=="
    # from phoenix icon, https://www.iconfinder.com/icons/3338998/board_business_tools_label_open_opening_board_icon, no link back required
    symbol_open = "data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiA/PjwhRE9DVFlQRSBzdmcgIFBVQkxJQyAnLS8vVzNDLy9EVEQgU1ZHIDEuMS8vRU4nICAnaHR0cDovL3d3dy53My5vcmcvR3JhcGhpY3MvU1ZHLzEuMS9EVEQvc3ZnMTEuZHRkJz48c3ZnIGlkPSJDYXBhXzEiIHN0eWxlPSJlbmFibGUtYmFja2dyb3VuZDpuZXcgMCAwIDYwIDYwOyIgdmVyc2lvbj0iMS4xIiB2aWV3Qm94PSIwIDAgNjAgNjAiIHhtbDpzcGFjZT0icHJlc2VydmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiPjxnPjxwYXRoIGQ9Ik01MS40MTQsMjMuNUwzNC45NTMsNy4wMzlDMzQuNzE3LDQuNTAxLDMyLjU5OSwyLjUsMzAsMi41cy00LjcxNywyLjAwMS00Ljk1Myw0LjUzOUw4LjU4NiwyMy41SDB2MzRoNjB2LTM0SDUxLjQxNHogICAgTTMwLDQuNWMxLjY1NCwwLDMsMS4zNDYsMywzcy0xLjM0NiwzLTMsM3MtMy0xLjM0Ni0zLTNTMjguMzQ2LDQuNSwzMCw0LjV6IE0yNS40Miw5LjQ5NEMyNi4xOTMsMTEuMjYsMjcuOTUyLDEyLjUsMzAsMTIuNSAgIHMzLjgwNy0xLjI0LDQuNTgtMy4wMDZMNDguNTg2LDIzLjVIMTEuNDE0TDI1LjQyLDkuNDk0eiBNNTgsNTUuNUgydi0zMGg1NlY1NS41eiIvPjxwYXRoIGQ9Ik0xMiwyOS41Yy0yLjc1NywwLTUsMi4yNDMtNSw1djEyYzAsMi43NTcsMi4yNDMsNSw1LDVzNS0yLjI0Myw1LTV2LTEyQzE3LDMxLjc0MywxNC43NTcsMjkuNSwxMiwyOS41eiBNMTUsNDYuNSAgIGMwLDEuNjU0LTEuMzQ2LDMtMywzcy0zLTEuMzQ2LTMtM3YtMTJjMC0xLjY1NCwxLjM0Ni0zLDMtM3MzLDEuMzQ2LDMsM1Y0Ni41eiIvPjxwYXRoIGQ9Ik0yNCwyOS41Yy0yLjc1NywwLTUsMi4yNDMtNSw1djV2MTFjMCwwLjU1MywwLjQ0OCwxLDEsMXMxLTAuNDQ3LDEtMXYtNy4wMjZjMC44MzgsMC42MzUsMS44NywxLjAyNiwzLDEuMDI2ICAgYzIuNzU3LDAsNS0yLjI0Myw1LTV2LTVDMjksMzEuNzQzLDI2Ljc1NywyOS41LDI0LDI5LjV6IE0yNywzOS41YzAsMS42NTQtMS4zNDYsMy0zLDNzLTMtMS4zNDYtMy0zdi01YzAtMS42NTQsMS4zNDYtMywzLTMgICBzMywxLjM0NiwzLDNWMzkuNXoiLz48cGF0aCBkPSJNNTEsNDUuMzA3bC02LjA3MS0xNS4xNzhjLTAuMDAxLTAuMDAzLTAuMDA0LTAuMDA1LTAuMDA1LTAuMDA4Yy0wLjAzNy0wLjA4OS0wLjA5Ni0wLjE2My0wLjE1NS0wLjIzNyAgIGMtMC4wMjItMC4wMjgtMC4wMzUtMC4wNjQtMC4wNi0wLjA5Yy0wLjAyNi0wLjAyNi0wLjA2My0wLjAzOS0wLjA5Mi0wLjA2M2MtMC4wNzEtMC4wNTctMC4xNDEtMC4xMTYtMC4yMjUtMC4xNTIgICBjLTAuMDItMC4wMDktMC4wNDQtMC4wMDctMC4wNjUtMC4wMTRjLTAuMTAyLTAuMDM2LTAuMjA4LTAuMDYzLTAuMzE4LTAuMDY0Yy0wLjAwMywwLTAuMDA1LTAuMDAyLTAuMDA5LTAuMDAyICAgYy0wLjA2MywwLTAuMTE3LDAuMDI1LTAuMTc2LDAuMDM2Yy0wLjA2NSwwLjAxMi0wLjEzMSwwLjAxLTAuMTk1LDAuMDM2Yy0wLjAwMywwLjAwMS0wLjAwNSwwLjAwNC0wLjAwOCwwLjAwNSAgIGMtMC4wODksMC4wMzctMC4xNjQsMC4wOTYtMC4yMzgsMC4xNTZjLTAuMDI4LDAuMDIyLTAuMDY0LDAuMDM1LTAuMDg4LDAuMDZjLTAuMDM1LDAuMDM1LTAuMDU0LDAuMDgzLTAuMDg0LDAuMTIzICAgYy0wLjA0NiwwLjA2My0wLjEsMC4xMjItMC4xMywwLjE5M2MtMC4wMSwwLjAyNC0wLjAwOCwwLjA1Mi0wLjAxNywwLjA3N2MtMC4wMzMsMC4wOTktMC4wNjEsMC4yLTAuMDYyLDAuMzA2ICAgYzAsMC4wMDMtMC4wMDIsMC4wMDUtMC4wMDIsMC4wMDl2MjBjMCwwLjU1MywwLjQ0OCwxLDEsMXMxLTAuNDQ3LDEtMVYzNS42OTNsNi4wNzEsMTUuMTc4YzAuMDAxLDAuMDAzLDAuMDA0LDAuMDA2LDAuMDA1LDAuMDA5ICAgYzAuMDA4LDAuMDE5LDAuMDIxLDAuMDMzLDAuMDMsMC4wNTFjMC4wNDQsMC4wOTEsMC4wOTgsMC4xNzIsMC4xNjQsMC4yNDNjMC4wMjUsMC4wMjcsMC4wNTIsMC4wNDgsMC4wNzksMC4wNzEgICBjMC4wNjMsMC4wNTUsMC4xMzEsMC4xMDEsMC4yMDUsMC4xMzhjMC4wMzMsMC4wMTcsMC4wNjMsMC4wMzMsMC4wOTgsMC4wNDZjMC4xMTEsMC4wNDEsMC4yMjYsMC4wNywwLjM0NiwwLjA3bDAuMDAxLDBoMGgwICAgYzAuMTI0LDAsMC4yNDktMC4wMjIsMC4zNzEtMC4wNzFjMC4wMDMtMC4wMDEsMC4wMDUtMC4wMDQsMC4wMDgtMC4wMDVjMC4wODgtMC4wMzYsMC4xNjItMC4wOTUsMC4yMzUtMC4xNTQgICBjMC4wMjgtMC4wMjMsMC4wNjUtMC4wMzYsMC4wOTEtMC4wNjFjMC4wMzMtMC4wMzIsMC4wNDktMC4wNzcsMC4wNzctMC4xMTRjMC4wNDktMC4wNjUsMC4xMDUtMC4xMjcsMC4xMzctMC4yMDMgICBjMC4wMS0wLjAyMywwLjAwOC0wLjA1MSwwLjAxNi0wLjA3NWMwLjAzNC0wLjA5OSwwLjA2MS0wLjIwMSwwLjA2Mi0wLjMwOGMwLTAuMDAzLDAuMDAyLTAuMDA2LDAuMDAyLTAuMDA5di0yMCAgIGMwLTAuNTUzLTAuNDQ4LTEtMS0xcy0xLDAuNDQ3LTEsMVY0NS4zMDd6Ii8+PHBhdGggZD0iTTQwLDMxLjVjMC41NTIsMCwxLTAuNDQ3LDEtMXMtMC40NDgtMS0xLTFoLThjLTAuNTUyLDAtMSwwLjQ0Ny0xLDF2MjBjMCwwLjU1MywwLjQ0OCwxLDEsMWg4YzAuNTUyLDAsMS0wLjQ0NywxLTEgICBzLTAuNDQ4LTEtMS0xaC03di04aDdjMC41NTIsMCwxLTAuNDQ3LDEtMXMtMC40NDgtMS0xLTFoLTd2LThINDB6Ii8+PC9nPjxnLz48Zy8+PGcvPjxnLz48Zy8+PGcvPjxnLz48Zy8+PGcvPjxnLz48Zy8+PGcvPjxnLz48Zy8+PGcvPjwvc3ZnPg=="
    # from Yannick Lung, https://www.iconfinder.com/icons/183533/warning_icon, no link back required
    symbol_warning = "data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiA/PjxzdmcgaGVpZ2h0PSIzMnB4IiB2ZXJzaW9uPSIxLjEiIHZpZXdCb3g9IjAgMCAzMiAzMiIgd2lkdGg9IjMycHgiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6c2tldGNoPSJodHRwOi8vd3d3LmJvaGVtaWFuY29kaW5nLmNvbS9za2V0Y2gvbnMiIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIj48dGl0bGUvPjxkZWZzLz48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiIGlkPSJJY29ucyBuZXcgQXJyYW5nZWQgTmFtZXMiIHN0cm9rZT0ibm9uZSIgc3Ryb2tlLXdpZHRoPSIxIj48ZyBmaWxsPSIjMDAwMDAwIiBpZD0iMTAxIFdhcm5pbmciPjxwYXRoIGQ9Ik0xNC40MjQyMzI3LDYuMTQ4MzkyNzUgQzE1LjI5NDI5ODcsNC43NDA3Mjk3NiAxNi43MDcwMjgsNC43NDQwODQ0MiAxNy41NzUwMjA1LDYuMTQ4MzkyNzUgTDI4LjM2MDEwOTksMjMuNTk3MzggQzI5LjUyMTYzODgsMjUuNDc2NTk1MSAyOC42NzU1NDYyLDI3IDI2LjQ3MTQwNjgsMjcgTDUuNTI3ODQ2NCwyNyBDMy4zMjMyMTU1NywyNyAyLjQ3Mzg2MzE3LDI1LjQ4MjY2NDIgMy42MzkxNDMzMSwyMy41OTczOCBaIE0xNiwyMCBDMTYuNTUyMjg0NywyMCAxNywxOS41NDY5NjM3IDE3LDE5LjAwMjk2OTkgTDE3LDEyLjk5NzAzMDEgQzE3LDEyLjQ0NjM4NTYgMTYuNTU2MTM1MiwxMiAxNiwxMiBDMTUuNDQ3NzE1MywxMiAxNSwxMi40NTMwMzYzIDE1LDEyLjk5NzAzMDEgTDE1LDE5LjAwMjk2OTkgQzE1LDE5LjU1MzYxNDQgMTUuNDQzODY0OCwyMCAxNiwyMCBaIE0xNiwyNCBDMTYuNTUyMjg0OCwyNCAxNywyMy41NTIyODQ4IDE3LDIzIEMxNywyMi40NDc3MTUyIDE2LjU1MjI4NDgsMjIgMTYsMjIgQzE1LjQ0NzcxNTIsMjIgMTUsMjIuNDQ3NzE1MiAxNSwyMyBDMTUsMjMuNTUyMjg0OCAxNS40NDc3MTUyLDI0IDE2LDI0IFogTTE2LDI0IiBpZD0iVHJpYW5nbGUgMjkiLz48L2c+PC9nPjwvc3ZnPg=="
    
    
    def __init__(self, mqtt_handler, shops_max_people_dict):
        assert isinstance(mqtt_handler, MqttHandler)
        self.mqtt_handler = mqtt_handler
        self.shops_max_people_dict = shops_max_people_dict
        input_topic = get_sensor_topic('+', 'people', None, 'count', use_type_subtopic=False)
        mqtt_handler.register_handler(input_topic, self._process)
        logging.info("Created DisplayActorController")

    def _process(self, topic, message):
        assert isinstance(message, dict)
        if 'shop_id' not in message or 'count' not in message:
            logging.warning("Can not process people count message: shop_id or count attribute missing, topic: %s", topic)
            return
        shop_id = message['shop_id']
        people_count = message['count']
        if shop_id not in self.shops_max_people_dict:
            logging.warning("Shop not found in max_people dict: %s", shop_id)
            return
        max_peoples = self.shops_max_people_dict[shop_id]
        utilization = translate(people_count,0, max_peoples, 0,100)
        action = self._utilization_action(utilization)
        message = {"shop_id": shop_id, "actor_type":"display", "action": action}
        logging.debug("Action message for shop %s with utilization %s: %s", shop_id, utilization, action['message'])
        return MqttHandler.MqttMessage(get_sensor_topic(shop_id, 'display', None, 'action', use_type_subtopic='actuators'),
                                       message)

    def _utilization_action(self, utilization):
        if(utilization > 95):
            return {"color":"red", "message":"Don't enter! Please wait", "symbol": __class__.symbol_stop}
        else:
            return {"color":"green", "message":"Welcome! Please enter", "symbol": __class__.symbol_open}

def get_shops_people_map():
    db = DB_Handler_Act()
    shops = db.get_shops()
    shop_map = dict()
    for shop in shops:
        assert 'shop_id' in shop
        assert 'max_people' in shop
        shop_map[shop['shop_id']] = shop['max_people']
    return shop_map

def main(mqtt_handler):
    shop_people_map = get_shops_people_map()
    disp = DisplayActorController(mqtt_handler, shop_people_map)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    mqtt_handler = MqttHandler()
    main()
    mqtt_handler.loop_forever()