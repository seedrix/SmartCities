from flask import Flask
from flask_cors import CORS
from flask_mongoengine import MongoEngine
from flask_restful import Api
from flask_jwt_extended import JWTManager


from bson.json_util import dumps

from .auth import SignupApi, LoginApi
from .user_shops import UserShopListApi, UserNextShopApi, UserDelShopApi
from .shops import ShopApi, AllShopsApi, ShopCurrentPeopleDataApi, ShopHistoricalPeopleDataApi
from .db import initialize_db
from .errors import errors




# Class-based application configuration
class ConfigClass(object):
    """ Flask application config """

    # Flask settings
    SECRET_KEY = 'This is an INSECURE secret!! DO NOT use this in production!!'

    # Flask-MongoEngine settings
    MONGODB_SETTINGS = [
        {
            'alias': 'auth',
            'db': "auth",
            'host': "localhost",
            'port': 27017,
            'username': "root",
            'password': "rootpassword",
            "authentication_source": "admin"
        },
        {
            'alias': 'app',
            'db': "smart_cities",
            'host': "localhost",
            'port': 27017,
            'username': "root",
            'password': "rootpassword",
            "authentication_source": "admin"
        }
    ]




def initialize_routes(api):
    api.add_resource(SignupApi, '/auth/signup')
    api.add_resource(LoginApi, '/auth/login')
    api.add_resource(UserShopListApi, '/user/shops')
    api.add_resource(UserNextShopApi, '/user/next_shop')
    api.add_resource(UserDelShopApi, '/user/del/<string:shop_id>')
    api.add_resource(AllShopsApi, '/shops/all')
    api.add_resource(ShopApi, '/shops/shop/<string:shop_id>')
    api.add_resource(ShopCurrentPeopleDataApi, '/shops/people/<string:shop_id>')
    api.add_resource(ShopHistoricalPeopleDataApi, '/shops/people/<string:shop_id>/<int:timestamp>')



def create_app():
    """ Flask application factory """
    
    # Setup Flask and load app.config
    app = Flask(__name__)
    app.config.from_object(__name__+'.ConfigClass')
    app.config.from_envvar('ENV_FILE_LOCATION')
    api = Api(app, errors=errors)
    jwt = JWTManager(app)

    initialize_db(app)

    initialize_routes(api)

    CORS(app)
    return app


    
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000) #run app in debug mode on port 5000