from flask import Response, request
from flask_restful import Resource
from flask_jwt_extended import create_access_token
import datetime
from mongoengine.errors import FieldDoesNotExist, NotUniqueError, DoesNotExist
from .errors import SchemaValidationError, EmailAlreadyExistsError, UnauthorizedError, InternalServerError
from .db_models import User, UserShops


class SignupApi(Resource):
    def post(self):
        try:
            body = request.get_json()
            user = User(**body)
            user.hash_password()
            user.save()
            id = user.id
            user_shops = UserShops(**{"user_id": str(id), "shops": [], "next_shop": ""})
            user_shops.save()
            return {'id': str(id)}, 200
        except FieldDoesNotExist:
            raise SchemaValidationError
        except NotUniqueError:
            raise EmailAlreadyExistsError
        except Exception as e:
            raise InternalServerError

class LoginApi(Resource):
    def post(self):
        try:
            body = request.get_json()
            user = User.objects.get(email=body.get('email'))
            authorized = user.check_password(body.get('password'))
            if not authorized:
                return {'error': 'Email or password invalid'}, 401
            
            expires = datetime.timedelta(days=1)
            access_token = create_access_token(identity=str(user.id), expires_delta=expires)
            return {'token': access_token}, 200
        except (UnauthorizedError, DoesNotExist):
            raise UnauthorizedError
        except Exception as e:
            raise InternalServerError
