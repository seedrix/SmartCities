from ai_planning import Solver, PlanningInstance
import sys
import threading
from pymongo import MongoClient
from pymongo import errors as mongoErrors
import re
from math import ceil
import time

scheduling_interval_seconds = 30

class DB_Handler_Ai:
    people_topic_regex = re.compile("^de/smartcity/2020/mymall/shops/[^/]+/people/count")

    def __init__(self, offline_test=False):
        self.offline_test = offline_test
        if offline_test:
            print("Offline test mode, no database connection will be used!")
            return
        MONGO_IP = "localhost"
        MONGO_PORT = 27017
        MONGO_USER = "root"
        MONGO_PW = "rootpassword"
        MONGO_DB = "smart_cities"
        MONGO_COLLECTION_USERS = "users"
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
        self.users_collection = database.get_collection(MONGO_COLLECTION_USERS)
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

    def get_user_lists(self):
        if self.offline_test:
            return [{"user_id":"u1", "shops":["s1","s2"]}, {"user_id":"u2", "shops":["s1","s2"]},{"user_id":"u3", "shops":["s3"]},{"user_id":"u4", "shops":["s3","s4"]}]
        users = list(self.users_collection.find( {}, { "user_id": 1, "shops": 1 } ))
        for user in users:
            del user['_id']
        return users

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

class SolverIOMapper:
    shop_id_key = 'shop_id'
    user_id_key = 'user_id'
    def __init__(self, shops_info, users_info):
        assert isinstance(shops_info, list)
        assert isinstance(users_info, list)
        self.shops_info = shops_info
        self.users_info = users_info
        self._generate_mapping()

    def _generate_mapping(self):
        self.shops_mapping = dict()
        self.people_at_shop = list()
        self.max_people_per_shop = list()
        shop_to_index = dict()
        for shop_idx, shop_info in enumerate(self.shops_info):
            self.shops_mapping['SHOP'+str(shop_idx)] = shop_info[__class__.shop_id_key]
            shop_to_index[shop_info[__class__.shop_id_key]] = shop_idx
            self.people_at_shop.append(shop_info['people_count'])
            self.max_people_per_shop.append(shop_info['max_people'])

        self.users_mapping = dict()
        self.users_preferences = list()
        for user_idx, user_info in enumerate(self.users_info):
            self.users_mapping['LIST'+str(user_idx)] = user_info[__class__.user_id_key]
            for shop_id in user_info['shops']:
                self.users_preferences.append((user_idx, shop_to_index[shop_id]))

    def get_planning_instance(self, name):
        # Todo: Use information from self.max_people_per_shop ?
        return PlanningInstance(name, len(self.shops_info), len(self.users_info), self.people_at_shop, self.users_preferences)

    def map_result(self, result):
        assert isinstance(result, list)
        user_to_shop = dict()
        for (user, shop) in result:
            assert user in self.users_mapping
            assert shop in self.shops_mapping
            user_id = self.users_mapping[user]
            shop_id = self.shops_mapping[shop]
            # if the user is already assigned to a shop, something went wrong
            assert user_id not in user_to_shop
            user_to_shop[user_id] = shop_id
        return user_to_shop

class Solver_Service:
    def __init__(self, solver, db_handler, period, minimum_time_between_schedules=1):
        assert isinstance(solver, Solver)
        assert isinstance(db_handler, DB_Handler_Ai)
        self.solver = solver
        self.period = period
        self.minimum_time_between_schedules = minimum_time_between_schedules
        self.db = db_handler
        self.scheduling_stopped = True
        self.timer = None
    
    def _solve(self):
        mapper = SolverIOMapper(self.db.get_shops(), self.db.get_user_lists())
        planning_instance = mapper.get_planning_instance("TimerTask")
        result_raw = self.solver.solve(planning_instance)
        result_mapped = mapper.map_result(result_raw)
        print("Solver results: "+ str(result_mapped))
        db.store_users_shop_mapping(result_mapped)

    def _timer_event(self):
        if self.scheduling_stopped:
            return
        start_time = time.time()
        self._solve()
        delta = time.time() - start_time
        print("Solver execution took "+str(delta)+" seconds.")
        remaining_period = max(self.minimum_time_between_schedules, self.period - delta)
        self.timer = threading.Timer(remaining_period, self._timer_event)
        self.timer.start()

    def start_scheduling(self, first_start_delay=10):
        if self.timer is not None:
            print("Service can only be started once!") 
        self.scheduling_stopped = False
        self.timer = threading.Timer(first_start_delay, self._timer_event)
        self.timer.start()

    def stop_scheduling(self):
        if self.timer is None:
            return
        self.scheduling_stopped = True
        self.timer.cancel()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        print("Using solver at: "+sys.argv[1])
        solver = Solver(sys.argv[1])
    else:
        solver = Solver("build/ff")

    db = DB_Handler_Ai()
    s = Solver_Service(solver, db, scheduling_interval_seconds)
    s.start_scheduling()
    

