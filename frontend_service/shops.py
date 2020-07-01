from flask import Response, request
from flask_restful import Resource
from bson.json_util import dumps
from jsonschema import validate, ValidationError
from flask_mongoengine import DoesNotExist
from .db_models import Shop, MqttData
from .errors import NoJsonError, SchemaValidationError, InternalServerError, ResourceDoesNotExist

import re

shop_schema = {
    "type": "object",
    "properties":{
        "max_people" : {"type" : "number"},
        "sensors" : {"type": "array", "items": {"type": "string"}},
        "shop_name" : {"type" : "string"},
        "logo" : {"type" : "string"}
    },
    "required": ["max_people", "sensors"]
}

class ShopApi(Resource):
    def get(self, shop_id):
        try:
            shop = Shop.objects.get(shop_id=shop_id)
            return Response(shop.to_json(), mimetype="application/json", status=200)
        except DoesNotExist:
            raise ResourceDoesNotExist
        except Exception as e:
            raise InternalServerError

    def put(self, shop_id):
        if request.is_json:
            try:
                body = request.get_json()
                validate(body, shop_schema)
                body["shop_id"] = shop_id
                shop = Shop.objects(shop_id=shop_id).upsert_one(**body)
                return "", 200
            except ValidationError:
                raise SchemaValidationError
            except Exception as e:
                raise InternalServerError
        else:
            raise NoJsonError

            

class AllShopsApi(Resource):
    def get(self):
        try:
            return Response(Shop.objects.all().to_json(), mimetype="application/json", status=200)
        except Exception as e:
            raise InternalServerError

class ShopCurrentPeopleDataApi(Resource):
    def get(self, shop_id):
        if Shop.objects(shop_id=shop_id).count() == 0:
            raise ResourceDoesNotExist
        try:
            docs = get_newest_topic_data(f"^de/smartcity/2020/mymall/shops/{shop_id}/people/count")
        except Exception as e:
            raise InternalServerError
        if len(docs) == 0:
            raise ResourceDoesNotExist
        return Response(dumps(filter_mqtt_data(docs[0])), mimetype="application/json", status=200)

class ShopHistoricalPeopleDataApi(Resource):
    def get(self, shop_id, timestamp):
        if Shop.objects(shop_id=shop_id).count() == 0:
            raise ResourceDoesNotExist
        try:
            data = MqttData.objects(topic=f"de/smartcity/2020/mymall/shops/{shop_id}/people/count", timestamp__gte=timestamp).all()
        except Exception as e:
            raise InternalServerError
        filtered_data = [filter_mqtt_data(mqtt_data) for mqtt_data in data]
        return Response(dumps(filtered_data), mimetype="application/json", status=200)


def get_newest_topic_data(topic_regex):
    pipline = [
            { "$match": { "topic": re.compile(topic_regex) } },
            { "$sort": { "timestamp": -1 }},
            { "$group": { 
                "_id": "$topic", 
                "topic": { "$first": "$$ROOT" } 
            }},
            { "$replaceRoot": {
                "newRoot": "$topic"
            }}
        ]
    return list(MqttData.objects().aggregate(pipline))

def filter_mqtt_data(mqtt_data):
    relevant_keys = ["payload", "timestamp", "datetime"]
    return { key: mqtt_data[key] for key in relevant_keys }