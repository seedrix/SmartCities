from flask import Response, request
from flask_restful import Resource
from bson.json_util import dumps
from jsonschema import validate, ValidationError
from flask_mongoengine import DoesNotExist
from .db_models import Shop
from .errors import NoJsonError, SchemaValidationError, InternalServerError, ResourceDoesNotExist

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