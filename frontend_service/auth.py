from flask import Response, request
from flask_restful import Resource
from flask_jwt_extended import create_access_token
import datetime
from mongoengine.errors import FieldDoesNotExist, NotUniqueError, DoesNotExist
from jsonschema import validate, ValidationError
from .errors import SchemaValidationError, EmailAlreadyExistsError, UnauthorizedError, InternalServerError
from .db_models import User, UserShops


credentials_schema = {
    "type": "object",
    "properties": {
        "email": {"type": "string"},
        "password": {"type": "string"}
    },
    "required": ["email", "password"]
}

class SignupApi(Resource):
    def post(self):
        if request.is_json:
            try:
                body = request.get_json()
                validate(body, schema=credentials_schema)
                user = User(**body)
                user.hash_password()
                user.save()
                id = user.id
                user_shops = UserShops(**{"user_id": str(id), "shops": [], "next_shop": ""})
                user_shops.save()
                return {'id': str(id)}, 200
            except (FieldDoesNotExist, ValidationError):
                raise SchemaValidationError
            except NotUniqueError:
                raise EmailAlreadyExistsError
            except Exception as e:
                raise InternalServerError
        else:
            raise NoJsonError

class LoginApi(Resource):
    def post(self):
        if request.is_json:
            try:
                body = request.get_json()
                validate(body, schema=credentials_schema)
                user = User.objects.get(email=body.get('email'))
                authorized = user.check_password(body.get('password'))
                if not authorized:
                    return {'error': 'Email or password invalid'}, 401
                
                expires = datetime.timedelta(days=1)
                access_token = create_access_token(identity=str(user.id), expires_delta=expires)
                return {'token': access_token}, 200
            except (FieldDoesNotExist, ValidationError):
                raise SchemaValidationError
            except (UnauthorizedError, DoesNotExist):
                raise UnauthorizedError
            except Exception as e:
                raise InternalServerError
        else:
            raise NoJsonError
