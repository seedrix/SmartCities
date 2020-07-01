from flask import Response, request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson.json_util import dumps
from jsonschema import validate, ValidationError
from .db_models import UserShops
from .errors import NoJsonError, SchemaValidationError, InternalServerError

shop_list_schema = {
    "type": "array",
    "items": {
        "type": "string"
    }
}

class ShopListApi(Resource):
    @jwt_required
    def get(self):
        try:
            user_id = get_jwt_identity()
            user_shops = UserShops.objects.get(user_id=user_id)
            return Response(dumps(user_shops.shops), mimetype="application/json", status=200)
        except Exception as e:
            raise e

    @jwt_required
    def post(self):
        if request.is_json:
            try:
                body = request.get_json()
                validate(body, schema=shop_list_schema)
                user_id = get_jwt_identity()
                user_shops = UserShops.objects.get(user_id=user_id)
                user_shops.shops = body
                user_shops.save()
                return "", 200
            except ValidationError:
                raise SchemaValidationError
            except Exception as e:
                raise InternalServerError
        else:
            raise NoJsonError

class NextShopApi(Resource):
    @jwt_required
    def get(self):
        try:
            user_id = get_jwt_identity()
            user_shops = UserShops.objects.get(user_id=user_id)
            return Response(dumps(user_shops.next_shop), mimetype="application/json", status=200)
        except Exception as e:
            raise InternalServerError