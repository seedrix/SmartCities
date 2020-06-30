from flask import Response
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from .db_models import UserShops


class UserShopsAPI(Resource):
    @jwt_required
    def get(self):
        user_id = get_jwt_identity()
        shop_user = UserShops.objects.get(user_id=user_id)
        return Response(shop_user.to_json(), mimetype="application/json", status=200)

    @jwt_required
    def put(self):
        user_id = get_jwt_identity()
        shop_user = UserShops.objects.get(user_id=user_id)
        return Response(shop_user.to_json(), mimetype="application/json", status=200)
