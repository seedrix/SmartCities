from flask import Flask
from flask import request, Response
from flask_cors import CORS

from pymongo import MongoClient
from bson.json_util import dumps

import re


app = Flask(__name__)
CORS(app)

MONGO_IP = "localhost"
MONGO_PORT = 27017
MONGO_USER = "root"
MONGO_PW = "rootpassword"
MONGO_DB = "smart_cities"
MONGO_COLLECTION = "mqtt"
MONGO_TIMEOUT = 1000  # Time in ms

print("Connecting Mongo")
client = MongoClient(f"mongodb://{MONGO_USER}:{MONGO_PW}@{MONGO_IP}:{MONGO_PORT}", serverSelectionTimeoutMS=MONGO_TIMEOUT)
database = client.get_database(MONGO_DB)
collection = database.get_collection(MONGO_COLLECTION)


@app.route('/')
def index():
    return 'Hello World'

@app.route('/db/all', methods=['GET'])
def get_all():
    try:
        return Response(response=dumps(collection.find()),
                    status=200,
                    mimetype="application/json")
    except Exception as e:
            return str(e), 500

@app.route('/sensors/ble/get_all', methods=['GET'])
def ble_get_all():
    try:
        regx = re.compile("^de/smartcity/2020/mymall/sensors/ble/*")
        return Response(response=dumps(collection.find({"topic": regx})),
                    status=200,
                    mimetype="application/json")
    except Exception as e:
            return str(e), 500
    

if __name__ == '__main__':
    app.run(debug=True, port=5000) #run app in debug mode on port 5000