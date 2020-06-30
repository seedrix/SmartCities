from flask import Flask
from flask import request, Response
from flask_cors import CORS
from flask_mongoengine import MongoEngine
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_restful import Api


from pymongo import MongoClient
from bson.json_util import dumps

from .auth import SignupApi
from .db import initialize_db

import re



MONGO_IP = "localhost"
MONGO_PORT = 27017
MONGO_USER = "root"
MONGO_PW = "rootpassword"
MONGO_DB_DATA = "smart_cities"
MONGO_DB_AUTH = "auth"
MONGO_COLLECTION = "mqtt"
MONGO_TIMEOUT = 1000  # Time in ms



# Class-based application configuration
class ConfigClass(object):
    """ Flask application config """

    # Flask settings
    SECRET_KEY = 'This is an INSECURE secret!! DO NOT use this in production!!'

    # Flask-MongoEngine settings
    MONGODB_SETTINGS = {
        'db': MONGO_DB_AUTH,
        'host': "localhost",
        'port': 27017,
        'username': "root",
        'password': "rootpassword",
        "authentication_source": "admin"
    }

     # Flask-User settings
    USER_APP_NAME = "Flask-User MongoDB App"      # Shown in and email templates and page footers
    USER_ENABLE_EMAIL = False      # Disable email authentication
    USER_ENABLE_USERNAME = True    # Enable username authentication
    USER_REQUIRE_RETYPE_PASSWORD = False    # Simplify register form



def initialize_routes(api):
    api.add_resource(SignupApi, '/auth/signup')



def create_app():
    """ Flask application factory """
    
    # Setup Flask and load app.config
    app = Flask(__name__)
    app.config.from_object(__name__+'.ConfigClass')
    api = Api(app)

    initialize_db(app)

    initialize_routes(api)

    CORS(app)
    return app

app = create_app()

print("Connecting Mongo")
client = MongoClient(f"mongodb://{MONGO_USER}:{MONGO_PW}@{MONGO_IP}:{MONGO_PORT}", serverSelectionTimeoutMS=MONGO_TIMEOUT)
database = client.get_database(MONGO_DB_DATA)
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

@app.route('/sensors/ble/get_all_count', methods=['GET'])
def ble_get_all_count():
    try:
        regx = re.compile("^de/smartcity/2020/mymall/sensors/ble/.*/count")
        return Response(response=dumps(collection.find({"topic": regx})),
                    status=200,
                    mimetype="application/json")
    except Exception as e:
            return str(e), 500

@app.route('/sensors/ble/get_all_list', methods=['GET'])
def ble_get_all_list():
    try:
        regx = re.compile("^de/smartcity/2020/mymall/sensors/ble/.*/list")
        return Response(response=dumps(collection.find({"topic": regx})),
                    status=200,
                    mimetype="application/json")
    except Exception as e:
            return str(e), 500
    

if __name__ == '__main__':
    app.run(debug=True, port=5000) #run app in debug mode on port 5000