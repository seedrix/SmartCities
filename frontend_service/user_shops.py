from flask import Response, request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson.json_util import dumps
from jsonschema import validate, ValidationError
from .db_models import UserShops, Shop
from .errors import NoJsonError, SchemaValidationError, InternalServerError, ResourceDoesNotExist

shop_list_schema = {
    "type": "array",
    "items": {
        "type": "string"
    }
}

class UserShopListApi(Resource):
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
                for shop in body:
                    # check if all shops ids are valid
                    if Shop.objects(shop_id=shop).count() == 0:
                        raise ResourceDoesNotExist
                user_id = get_jwt_identity()
                user_shops = UserShops.objects.get(user_id=user_id)
                user_shops.shops = body
                user_shops.save()
                return "", 200
            except ValidationError:
                raise SchemaValidationError
            except ResourceDoesNotExist as r:
                raise r
            except Exception as e:
                raise InternalServerError
        else:
            raise NoJsonError

class UserNextShopApi(Resource):
    @jwt_required
    def get(self):
        try:
            user_id = get_jwt_identity()
            user_shops = UserShops.objects.get(user_id=user_id)
            return Response(dumps(user_shops.next_shop), mimetype="application/json", status=200)
        except Exception as e:
            raise InternalServerError

class UserDelShopApi(Resource):
    @jwt_required
    def delete(self, shop_id):
        try:
            user_id = get_jwt_identity()
            user_shops = UserShops.objects.get(user_id=user_id)
            user_shops.shops.remove(shop_id)
            user_shops.save()
        except ValueError:
            # shop is not in the list
            pass
        except Exception as e:
            raise InternalServerError
        return "", 200
