import sys
import threading
from pymongo import MongoClient
from pymongo import errors as mongoErrors
import re
from math import ceil
import time
from datetime import datetime, timedelta

week1 = [{"weekday":0,"times":[{"height":"11","time":"07"},{"height":"20","time":"08"},{"height":"32","time":"09"},{"height":"44","time":"10"},{"height":"53","time":"11"},{"height":"55","time":"12"},{"height":"49","time":"13"},{"height":"40","time":"14"},{"height":"36","time":"15"},{"height":"41","time":"16"},{"height":"50","time":"17"},{"height":"48","time":"18"},{"height":"32","time":"19"},{"height":"13","time":"20"}]},{"weekday":1,"times":[{"height":"14","time":"07"},{"height":"25","time":"08"},{"height":"39","time":"09"},{"height":"50","time":"10"},{"height":"54","time":"11"},{"height":"51","time":"12"},{"height":"42","time":"13"},{"height":"32","time":"14"},{"height":"30","time":"15"},{"height":"43","time":"16"},{"height":"58","time":"17"},{"height":"59","time":"18"},{"height":"39","time":"19"},{"height":"18","time":"20"}]},{"weekday":2,"times":[{"height":"20","time":"07"},{"height":"34","time":"08"},{"height":"40","time":"09"},{"height":"44","time":"10"},{"height":"49","time":"11"},{"height":"53","time":"12"},{"height":"51","time":"13"},{"height":"43","time":"14"},{"height":"35","time":"15"},{"height":"38","time":"16"},{"height":"53","time":"17"},{"height":"59","time":"18"},{"height":"47","time":"19"},{"height":"23","time":"20"}]},{"weekday":3,"times":[{"height":"13","time":"07"},{"height":"23","time":"08"},{"height":"33","time":"09"},{"height":"41","time":"10"},{"height":"44","time":"11"},{"height":"40","time":"12"},{"height":"32","time":"13"},{"height":"26","time":"14"},{"height":"32","time":"15"},{"height":"47","time":"16"},{"height":"59","time":"17"},{"height":"54","time":"18"},{"height":"34","time":"19"},{"height":"14","time":"20"}]},{"weekday":4,"times":[{"height":"18","time":"07"},{"height":"35","time":"08"},{"height":"49","time":"09"},{"height":"54","time":"10"},{"height":"53","time":"11"},{"height":"50","time":"12"},{"height":"47","time":"13"},{"height":"42","time":"14"},{"height":"36","time":"15"},{"height":"42","time":"16"},{"height":"56","time":"17"},{"height":"57","time":"18"},{"height":"35","time":"19"},{"height":"12","time":"20"}]},{"weekday":5,"times":[{"height":"16","time":"07"},{"height":"36","time":"08"},{"height":"59","time":"09"},{"height":"75","time":"10"},{"height":"75","time":"11"},{"height":"65","time":"12"},{"height":"58","time":"13"},{"height":"55","time":"14"},{"height":"52","time":"15"},{"height":"48","time":"16"},{"height":"51","time":"17"},{"height":"62","time":"18"},{"height":"59","time":"19"},{"height":"33","time":"20"}]}]
week2 = [{"weekday":0,"times":[{"height":"7","time":"07"},{"height":"13","time":"08"},{"height":"21","time":"09"},{"height":"30","time":"10"},{"height":"36","time":"11"},{"height":"38","time":"12"},{"height":"34","time":"13"},{"height":"29","time":"14"},{"height":"30","time":"15"},{"height":"40","time":"16"},{"height":"53","time":"17"},{"height":"55","time":"18"},{"height":"41","time":"19"},{"height":"21","time":"20"}]},{"weekday":1,"times":[{"height":"9","time":"07"},{"height":"16","time":"08"},{"height":"24","time":"09"},{"height":"30","time":"10"},{"height":"34","time":"11"},{"height":"34","time":"12"},{"height":"31","time":"13"},{"height":"30","time":"14"},{"height":"38","time":"15"},{"height":"51","time":"16"},{"height":"63","time":"17"},{"height":"62","time":"18"},{"height":"45","time":"19"},{"height":"25","time":"20"}]},{"weekday":2,"times":[{"height":"8","time":"07"},{"height":"14","time":"08"},{"height":"23","time":"09"},{"height":"32","time":"10"},{"height":"38","time":"11"},{"height":"41","time":"12"},{"height":"39","time":"13"},{"height":"38","time":"14"},{"height":"44","time":"15"},{"height":"58","time":"16"},{"height":"72","time":"17"},{"height":"73","time":"18"},{"height":"56","time":"19"},{"height":"32","time":"20"}]},{"weekday":3,"times":[{"height":"6","time":"07"},{"height":"13","time":"08"},{"height":"21","time":"09"},{"height":"29","time":"10"},{"height":"35","time":"11"},{"height":"36","time":"12"},{"height":"33","time":"13"},{"height":"32","time":"14"},{"height":"37","time":"15"},{"height":"45","time":"16"},{"height":"47","time":"17"},{"height":"45","time":"18"},{"height":"41","time":"19"},{"height":"27","time":"20"}]},{"weekday":4,"times":[{"height":"5","time":"07"},{"height":"11","time":"08"},{"height":"18","time":"09"},{"height":"28","time":"10"},{"height":"37","time":"11"},{"height":"43","time":"12"},{"height":"44","time":"13"},{"height":"41","time":"14"},{"height":"38","time":"15"},{"height":"42","time":"16"},{"height":"52","time":"17"},{"height":"57","time":"18"},{"height":"50","time":"19"},{"height":"32","time":"20"}]},{"weekday":5,"times":[{"height":"20","time":"07"},{"height":"23","time":"08"},{"height":"29","time":"09"},{"height":"46","time":"10"},{"height":"62","time":"11"},{"height":"71","time":"12"},{"height":"71","time":"13"},{"height":"62","time":"14"},{"height":"53","time":"15"},{"height":"54","time":"16"},{"height":"66","time":"17"},{"height":"75","time":"18"},{"height":"63","time":"19"},{"height":"37","time":"20"}]}]
week3 = [{"weekday":0,"times":[{"height":"3","time":"07"},{"height":"8","time":"08"},{"height":"15","time":"09"},{"height":"26","time":"10"},{"height":"33","time":"11"},{"height":"37","time":"12"},{"height":"34","time":"13"},{"height":"27","time":"14"},{"height":"24","time":"15"},{"height":"36","time":"16"},{"height":"53","time":"17"},{"height":"48","time":"18"},{"height":"23","time":"19"}]},{"weekday":1,"times":[{"height":"3","time":"07"},{"height":"12","time":"08"},{"height":"25","time":"09"},{"height":"38","time":"10"},{"height":"42","time":"11"},{"height":"38","time":"12"},{"height":"36","time":"13"},{"height":"39","time":"14"},{"height":"42","time":"15"},{"height":"46","time":"16"},{"height":"52","time":"17"},{"height":"43","time":"18"},{"height":"19","time":"19"}]},{"weekday":2,"times":[{"height":"2","time":"07"},{"height":"10","time":"08"},{"height":"20","time":"09"},{"height":"28","time":"10"},{"height":"32","time":"11"},{"height":"36","time":"12"},{"height":"38","time":"13"},{"height":"38","time":"14"},{"height":"44","time":"15"},{"height":"56","time":"16"},{"height":"62","time":"17"},{"height":"51","time":"18"},{"height":"29","time":"19"}]},{"weekday":3,"times":[{"height":"2","time":"07"},{"height":"8","time":"08"},{"height":"16","time":"09"},{"height":"27","time":"10"},{"height":"36","time":"11"},{"height":"38","time":"12"},{"height":"31","time":"13"},{"height":"26","time":"14"},{"height":"32","time":"15"},{"height":"47","time":"16"},{"height":"56","time":"17"},{"height":"43","time":"18"},{"height":"21","time":"19"}]},{"weekday":4,"times":[{"height":"3","time":"07"},{"height":"10","time":"08"},{"height":"22","time":"09"},{"height":"32","time":"10"},{"height":"37","time":"11"},{"height":"38","time":"12"},{"height":"40","time":"13"},{"height":"40","time":"14"},{"height":"36","time":"15"},{"height":"33","time":"16"},{"height":"48","time":"17"},{"height":"62","time":"18"},{"height":"36","time":"19"}]},{"weekday":5,"times":[{"height":"8","time":"07"},{"height":"17","time":"08"},{"height":"31","time":"09"},{"height":"49","time":"10"},{"height":"65","time":"11"},{"height":"74","time":"12"},{"height":"70","time":"13"},{"height":"56","time":"14"},{"height":"40","time":"15"},{"height":"36","time":"16"},{"height":"59","time":"17"},{"height":"75","time":"18"},{"height":"41","time":"19"}]}]
week4 = [{"weekday":0,"times":[{"height":"14","time":"07"},{"height":"27","time":"08"},{"height":"16","time":"09"},{"height":"11","time":"10"},{"height":"20","time":"11"},{"height":"29","time":"12"},{"height":"29","time":"13"},{"height":"25","time":"14"},{"height":"29","time":"15"},{"height":"41","time":"16"},{"height":"45","time":"17"},{"height":"34","time":"18"},{"height":"14","time":"19"}]},{"weekday":1,"times":[{"height":"22","time":"07"},{"height":"29","time":"08"},{"height":"36","time":"09"},{"height":"40","time":"10"},{"height":"40","time":"11"},{"height":"36","time":"12"},{"height":"31","time":"13"},{"height":"24","time":"14"},{"height":"24","time":"15"},{"height":"38","time":"16"},{"height":"51","time":"17"},{"height":"45","time":"18"},{"height":"20","time":"19"}]},{"weekday":2,"times":[{"height":"20","time":"07"},{"height":"32","time":"08"},{"height":"43","time":"09"},{"height":"50","time":"10"},{"height":"52","time":"11"},{"height":"45","time":"12"},{"height":"36","time":"13"},{"height":"27","time":"14"},{"height":"32","time":"15"},{"height":"47","time":"16"},{"height":"52","time":"17"},{"height":"50","time":"18"},{"height":"38","time":"19"}]},{"weekday":3,"times":[{"height":"14","time":"07"},{"height":"20","time":"08"},{"height":"27","time":"09"},{"height":"32","time":"10"},{"height":"34","time":"11"},{"height":"34","time":"12"},{"height":"29","time":"13"},{"height":"25","time":"14"},{"height":"20","time":"15"},{"height":"23","time":"16"},{"height":"41","time":"17"},{"height":"41","time":"18"},{"height":"16","time":"19"}]},{"weekday":4,"times":[{"height":"61","time":"07"},{"height":"75","time":"08"},{"height":"50","time":"09"},{"height":"27","time":"10"},{"height":"27","time":"11"},{"height":"38","time":"12"},{"height":"47","time":"13"},{"height":"43","time":"14"},{"height":"36","time":"15"},{"height":"34","time":"16"},{"height":"29","time":"17"},{"height":"23","time":"18"},{"height":"9","time":"19"}]},{"weekday":5,"times":[{"height":"27","time":"07"},{"height":"43","time":"08"},{"height":"52","time":"09"},{"height":"54","time":"10"},{"height":"54","time":"11"},{"height":"54","time":"12"},{"height":"56","time":"13"},{"height":"52","time":"14"},{"height":"41","time":"15"},{"height":"32","time":"16"},{"height":"36","time":"17"},{"height":"41","time":"18"},{"height":"27","time":"19"}]}]
week5 = [{"weekday":0,"times":[{"height":"14","time":"07"},{"height":"22","time":"08"},{"height":"23","time":"09"},{"height":"29","time":"10"},{"height":"47","time":"11"},{"height":"55","time":"12"},{"height":"42","time":"13"},{"height":"29","time":"14"},{"height":"35","time":"15"},{"height":"50","time":"16"},{"height":"58","time":"17"},{"height":"53","time":"18"},{"height":"36","time":"19"},{"height":"19","time":"20"}]},{"weekday":1,"times":[{"height":"7","time":"07"},{"height":"17","time":"08"},{"height":"30","time":"09"},{"height":"46","time":"10"},{"height":"60","time":"11"},{"height":"66","time":"12"},{"height":"60","time":"13"},{"height":"50","time":"14"},{"height":"49","time":"15"},{"height":"61","time":"16"},{"height":"73","time":"17"},{"height":"69","time":"18"},{"height":"48","time":"19"},{"height":"24","time":"20"}]},{"weekday":2,"times":[{"height":"26","time":"07"},{"height":"35","time":"08"},{"height":"35","time":"09"},{"height":"43","time":"10"},{"height":"60","time":"11"},{"height":"68","time":"12"},{"height":"61","time":"13"},{"height":"49","time":"14"},{"height":"48","time":"15"},{"height":"61","time":"16"},{"height":"72","time":"17"},{"height":"68","time":"18"},{"height":"47","time":"19"},{"height":"25","time":"20"}]},{"weekday":3,"times":[{"height":"12","time":"07"},{"height":"26","time":"08"},{"height":"29","time":"09"},{"height":"35","time":"10"},{"height":"53","time":"11"},{"height":"65","time":"12"},{"height":"54","time":"13"},{"height":"40","time":"14"},{"height":"39","time":"15"},{"height":"50","time":"16"},{"height":"57","time":"17"},{"height":"53","time":"18"},{"height":"38","time":"19"},{"height":"22","time":"20"}]},{"weekday":4,"times":[{"height":"10","time":"07"},{"height":"24","time":"08"},{"height":"36","time":"09"},{"height":"41","time":"10"},{"height":"46","time":"11"},{"height":"53","time":"12"},{"height":"55","time":"13"},{"height":"53","time":"14"},{"height":"51","time":"15"},{"height":"56","time":"16"},{"height":"62","time":"17"},{"height":"59","time":"18"},{"height":"44","time":"19"},{"height":"23","time":"20"}]},{"weekday":5,"times":[{"height":"14","time":"07"},{"height":"26","time":"08"},{"height":"38","time":"09"},{"height":"47","time":"10"},{"height":"57","time":"11"},{"height":"68","time":"12"},{"height":"74","time":"13"},{"height":"71","time":"14"},{"height":"65","time":"15"},{"height":"65","time":"16"},{"height":"74","time":"17"},{"height":"75","time":"18"},{"height":"58","time":"19"},{"height":"31","time":"20"}]}]
week6 = [{"weekday":0,"times":[{"height":"2","time":"07"},{"height":"8","time":"08"},{"height":"18","time":"09"},{"height":"26","time":"10"},{"height":"26","time":"11"},{"height":"24","time":"12"},{"height":"24","time":"13"},{"height":"23","time":"14"},{"height":"23","time":"15"},{"height":"27","time":"16"},{"height":"35","time":"17"},{"height":"38","time":"18"},{"height":"32","time":"19"},{"height":"20","time":"20"},{"height":"9","time":"21"}]},{"weekday":1,"times":[{"height":"3","time":"07"},{"height":"8","time":"08"},{"height":"17","time":"09"},{"height":"27","time":"10"},{"height":"30","time":"11"},{"height":"26","time":"12"},{"height":"21","time":"13"},{"height":"24","time":"14"},{"height":"34","time":"15"},{"height":"48","time":"16"},{"height":"55","time":"17"},{"height":"50","time":"18"},{"height":"36","time":"19"},{"height":"20","time":"20"},{"height":"9","time":"21"}]},{"weekday":2,"times":[{"height":"6","time":"07"},{"height":"15","time":"08"},{"height":"26","time":"09"},{"height":"35","time":"10"},{"height":"35","time":"11"},{"height":"29","time":"12"},{"height":"23","time":"13"},{"height":"29","time":"14"},{"height":"50","time":"15"},{"height":"65","time":"16"},{"height":"62","time":"17"},{"height":"53","time":"18"},{"height":"44","time":"19"},{"height":"29","time":"20"},{"height":"14","time":"21"}]},{"weekday":3,"times":[{"height":"3","time":"07"},{"height":"9","time":"08"},{"height":"14","time":"09"},{"height":"17","time":"10"},{"height":"23","time":"11"},{"height":"26","time":"12"},{"height":"25","time":"13"},{"height":"24","time":"14"},{"height":"29","time":"15"},{"height":"36","time":"16"},{"height":"41","time":"17"},{"height":"39","time":"18"},{"height":"29","time":"19"},{"height":"18","time":"20"},{"height":"8","time":"21"}]},{"weekday":4,"times":[{"height":"3","time":"07"},{"height":"8","time":"08"},{"height":"18","time":"09"},{"height":"29","time":"10"},{"height":"36","time":"11"},{"height":"36","time":"12"},{"height":"33","time":"13"},{"height":"35","time":"14"},{"height":"47","time":"15"},{"height":"59","time":"16"},{"height":"58","time":"17"},{"height":"43","time":"18"},{"height":"32","time":"19"},{"height":"29","time":"20"},{"height":"13","time":"21"}]},{"weekday":5,"times":[{"height":"10","time":"07"},{"height":"20","time":"08"},{"height":"36","time":"09"},{"height":"54","time":"10"},{"height":"68","time":"11"},{"height":"75","time":"12"},{"height":"70","time":"13"},{"height":"60","time":"14"},{"height":"54","time":"15"},{"height":"59","time":"16"},{"height":"66","time":"17"},{"height":"60","time":"18"},{"height":"42","time":"19"},{"height":"44","time":"20"},{"height":"39","time":"21"}]}]
week7 = [{"weekday":0,"times":[{"height":"2","time":"07"},{"height":"7","time":"08"},{"height":"15","time":"09"},{"height":"23","time":"10"},{"height":"26","time":"11"},{"height":"23","time":"12"},{"height":"20","time":"13"},{"height":"23","time":"14"},{"height":"31","time":"15"},{"height":"38","time":"16"},{"height":"43","time":"17"},{"height":"51","time":"18"},{"height":"50","time":"19"},{"height":"32","time":"20"},{"height":"11","time":"21"}]},{"weekday":1,"times":[{"height":"2","time":"07"},{"height":"7","time":"08"},{"height":"15","time":"09"},{"height":"22","time":"10"},{"height":"28","time":"11"},{"height":"30","time":"12"},{"height":"27","time":"13"},{"height":"23","time":"14"},{"height":"21","time":"15"},{"height":"29","time":"16"},{"height":"44","time":"17"},{"height":"57","time":"18"},{"height":"55","time":"19"},{"height":"39","time":"20"},{"height":"19","time":"21"}]},{"weekday":2,"times":[{"height":"5","time":"08"},{"height":"11","time":"09"},{"height":"20","time":"10"},{"height":"27","time":"11"},{"height":"31","time":"12"},{"height":"29","time":"13"},{"height":"25","time":"14"},{"height":"25","time":"15"},{"height":"38","time":"16"},{"height":"59","time":"17"},{"height":"63","time":"18"},{"height":"47","time":"19"},{"height":"46","time":"20"},{"height":"26","time":"21"}]},{"weekday":3,"times":[{"height":"4","time":"07"},{"height":"8","time":"08"},{"height":"14","time":"09"},{"height":"20","time":"10"},{"height":"24","time":"11"},{"height":"26","time":"12"},{"height":"23","time":"13"},{"height":"20","time":"14"},{"height":"21","time":"15"},{"height":"33","time":"16"},{"height":"50","time":"17"},{"height":"51","time":"18"},{"height":"40","time":"19"},{"height":"28","time":"20"},{"height":"14","time":"21"}]},{"weekday":4,"times":[{"height":"4","time":"07"},{"height":"11","time":"08"},{"height":"21","time":"09"},{"height":"29","time":"10"},{"height":"32","time":"11"},{"height":"34","time":"12"},{"height":"36","time":"13"},{"height":"41","time":"14"},{"height":"44","time":"15"},{"height":"47","time":"16"},{"height":"50","time":"17"},{"height":"52","time":"18"},{"height":"49","time":"19"},{"height":"35","time":"20"},{"height":"17","time":"21"}]},{"weekday":5,"times":[{"height":"6","time":"07"},{"height":"17","time":"08"},{"height":"32","time":"09"},{"height":"45","time":"10"},{"height":"50","time":"11"},{"height":"50","time":"12"},{"height":"51","time":"13"},{"height":"59","time":"14"},{"height":"65","time":"15"},{"height":"59","time":"16"},{"height":"53","time":"17"},{"height":"64","time":"18"},{"height":"75","time":"19"},{"height":"63","time":"20"},{"height":"35","time":"21"}]}]
week8 = [{"weekday":0,"times":[{"height":"4","time":"07"},{"height":"8","time":"08"},{"height":"15","time":"09"},{"height":"23","time":"10"},{"height":"29","time":"11"},{"height":"32","time":"12"},{"height":"32","time":"13"},{"height":"29","time":"14"},{"height":"31","time":"15"},{"height":"39","time":"16"},{"height":"50","time":"17"},{"height":"56","time":"18"},{"height":"49","time":"19"},{"height":"32","time":"20"},{"height":"17","time":"21"}]},{"weekday":1,"times":[{"height":"6","time":"07"},{"height":"12","time":"08"},{"height":"20","time":"09"},{"height":"27","time":"10"},{"height":"32","time":"11"},{"height":"32","time":"12"},{"height":"27","time":"13"},{"height":"23","time":"14"},{"height":"24","time":"15"},{"height":"39","time":"16"},{"height":"57","time":"17"},{"height":"57","time":"18"},{"height":"46","time":"19"},{"height":"42","time":"20"},{"height":"23","time":"21"}]},{"weekday":2,"times":[{"height":"7","time":"07"},{"height":"13","time":"08"},{"height":"20","time":"09"},{"height":"27","time":"10"},{"height":"32","time":"11"},{"height":"33","time":"12"},{"height":"31","time":"13"},{"height":"29","time":"14"},{"height":"32","time":"15"},{"height":"45","time":"16"},{"height":"59","time":"17"},{"height":"59","time":"18"},{"height":"48","time":"19"},{"height":"59","time":"20"},{"height":"35","time":"21"}]},{"weekday":3,"times":[{"height":"5","time":"07"},{"height":"11","time":"08"},{"height":"18","time":"09"},{"height":"25","time":"10"},{"height":"30","time":"11"},{"height":"32","time":"12"},{"height":"29","time":"13"},{"height":"29","time":"14"},{"height":"35","time":"15"},{"height":"44","time":"16"},{"height":"43","time":"17"},{"height":"36","time":"18"},{"height":"40","time":"19"},{"height":"44","time":"20"},{"height":"26","time":"21"}]},{"weekday":4,"times":[{"height":"8","time":"07"},{"height":"17","time":"08"},{"height":"23","time":"09"},{"height":"30","time":"10"},{"height":"38","time":"11"},{"height":"41","time":"12"},{"height":"36","time":"13"},{"height":"32","time":"14"},{"height":"36","time":"15"},{"height":"46","time":"16"},{"height":"55","time":"17"},{"height":"54","time":"18"},{"height":"43","time":"19"},{"height":"27","time":"20"},{"height":"14","time":"21"}]},{"weekday":5,"times":[{"height":"10","time":"07"},{"height":"18","time":"08"},{"height":"29","time":"09"},{"height":"41","time":"10"},{"height":"53","time":"11"},{"height":"61","time":"12"},{"height":"62","time":"13"},{"height":"59","time":"14"},{"height":"55","time":"15"},{"height":"57","time":"16"},{"height":"67","time":"17"},{"height":"75","time":"18"},{"height":"68","time":"19"},{"height":"47","time":"20"},{"height":"24","time":"21"}]}]

# Settings
week = week6
shop_id = "shop2"
date_first_day = datetime.strptime('02/07/20', '%d/%m/%y')
override_real_data = False

print("date_first_day referd to a "+date_first_day.strftime('%A'))
print("Replacing data from "+date_first_day.strftime('%A %d/%m/%y')+' to '+(date_first_day+timedelta(days=6)).strftime('%A %d/%m/%y'))

class DB_Handler_F:
    # Todo: implement
    people_topic_regex = re.compile("^de/smartcity/2020/mymall/shops/[^/]+/people/count")

    def __init__(self, offline_test=False):
        self.offline_test = offline_test
        if offline_test:
            print("Offline test mode, no database connection will be used!")
            return
        MONGO_IP = "t1.max-reichel.de"
        MONGO_PORT = 27017
        MONGO_USER = "root"
        MONGO_PW = "rootpassword"
        MONGO_DB = "smart_cities"
        MONGO_COLLECTION_SHOPS = "shops"
        MONGO_COLLECTION_MQTT = "mqtt"
        MONGO_TIMEOUT = 1000  # Time in ms

        print("Connecting Mongo")
        client = MongoClient(f"mongodb://{MONGO_USER}:{MONGO_PW}@{MONGO_IP}:{MONGO_PORT}", serverSelectionTimeoutMS=MONGO_TIMEOUT)
        try:
            client.server_info()
        except mongoErrors.PyMongoError as e:
            print("Mongo connection failed: "+ str(e))
            sys.exit("Mongo connection failed: "+ str(e))
        database = client.get_database(MONGO_DB)
        self.shops_collection = database.get_collection(MONGO_COLLECTION_SHOPS)
        self.mqtt_collection = database.get_collection(MONGO_COLLECTION_MQTT)


    def get_shops(self):
        if self.offline_test:
            return [{"shop_id": "s1", "max_people": 1, "people_count": 1},{"shop_id": "s2","max_people": 2, "people_count": 2},{"shop_id": "s3","max_people": 1, "people_count": 0},{"shop_id": "s4","max_people": 1, "people_count": 1}]
        shops = list(self.shops_collection.find( {}, { "shop_id": 1, "max_people": 1 } ))
        people_map = self.get_current_peoples()
        for shop in shops:
            del shop['_id']
            if shop['shop_id'] in people_map:
                shop.update({"people_count": people_map[shop['shop_id']]})
            else:
                shop.update({"people_count": 0})
        return shops

    def get_current_peoples(self):
        if self.offline_test:
            return {"s0": 1, "s1": 2, "s2": 0, "s3": 1}
        # retrieves for all matching topic the database entry with the newest timestamp
        cursor = self.mqtt_collection.aggregate([
            { "$match": { "topic": __class__.people_topic_regex } },
            { "$sort": { "timestamp": -1 }},
            { "$group": { 
                "_id": "$topic", 
                "topic": { "$first": "$$ROOT" } 
            }},
            { "$replaceRoot": {
                "newRoot": "$topic"
            }}
        ])
        shops_map = dict()
        for doc in cursor:
            #print("doc: "+str(doc))
            if 'payload' not in doc:
                continue
            payload = doc['payload']
            if 'shop_id' not in payload:
                continue
            if 'count' not in payload:
                continue
            shop_id = payload['shop_id']
            shops_map[shop_id] = ceil(payload['count'])
            #print(f"Shop {shop_id} with people: {shops_map[shop_id]}")
        #print(shops_map)
        return shops_map

    def store_users_shop_mapping(self, users_shop_map):
        if self.offline_test:
            print(users_shop_map)
            return
        for user_id, shop_id in users_shop_map.items():
            result = self.users_collection.update_one( { "user_id" : user_id },
                { "$set": { "next_shop" : shop_id } })
            if result is None or result.matched_count == 0:
                print("Could not update next shop for user: "+user_id)
    def replace(self, documents):
        filter_orig = {"topic": "de/smartcity/2020/mymall/shops/"+shop_id+"/people/count",
        'timestamp':{'$gte':min([doc['timestamp'] for doc in documents]), '$lte':max([doc['timestamp'] for doc in documents])}}
        filter = filter_orig.copy()
        if not override_real_data:
            filter.update({'payload.aggregated_sensor_types':{'$in':['dummy']}})
        del_count = self.mqtt_collection.delete_many(filter).deleted_count
        print('deleted documents: '+str(del_count))
        if not override_real_data:
            remaing_count = self.mqtt_collection.count_documents(filter_orig)
            print('remaining original documents in this time period: '+str(remaing_count))
        ins_ids = self.mqtt_collection.insert_many(documents).inserted_ids
        print('inserted documents: '+str(len(ins_ids)))

# Source: Adam Luchjenbroers, https://stackoverflow.com/questions/1969240/mapping-a-range-of-values-to-another
def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

def getMaxHeight(week):
    count = 0
    for day in week:
        count = max(max([int(h['height']) for h in day['times']]), count)
    return count


def getMaxPeople(shops):
    for shop in shops:
        if 'shop_id' not in shop:
            continue
        if shop['shop_id'] == shop_id:
            return shop['max_people']

def create_doc(day_offset, hour, people):
    t = date_first_day.replace(hour=hour, minute = 0, second=0) + timedelta(days=day_offset)
    payload = {
        "shop_id" : "shop1",
        "aggregated_sensors" : 1,
        "sensor_type" : "people",
        "count" : people,
        "aggregated_sensor_types" : [ 
            "dummy"
        ]
        }
    return {
        "topic": "de/smartcity/2020/mymall/shops/"+shop_id+"/people/count",
        "payload": payload,
        "qos": 0,
        "timestamp": int(t.timestamp()),
        "datetime": t.strftime("%d/%m/%Y %H:%M:%S"),
    }

db = DB_Handler_F()
shops = db.get_shops()
max_people = getMaxPeople(shops)
max_height = getMaxHeight(week)
parsed_week = {}
for day in week:
    day_offset = day['weekday']
    times = day['times']
    parsed_times = {}
    for time in times:
        parsed_times[int(time['time'])] = int(translate(int(time['height']),0,max_height, 0,max_people))
    parsed_week[int(day_offset)] = parsed_times
documents = []

for day_offset in range(7):
    today = date_first_day + timedelta(days=day_offset)
    if today.weekday() not in parsed_week:
        print("No data for "+today.strftime('%A'))
        continue
    day = parsed_week[today.weekday()]
    min_hour = min(list(day.keys()))
    min_hour_minus_one = max(min_hour-1,0)
    if min_hour != min_hour_minus_one:
        documents.append(create_doc(day_offset, min_hour_minus_one, 0))
    max_hour = max(list(day.keys()))
    max_hour_plus_one = min(max_hour+1,23)
    if max_hour != max_hour_plus_one:
        documents.append(create_doc(day_offset, max_hour_plus_one, 0))
    for hour, people in day.items():
        documents.append(create_doc(day_offset, hour, people))

print(documents)
db.replace(documents)