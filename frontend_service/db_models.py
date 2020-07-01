from .db import db
from flask_bcrypt import generate_password_hash, check_password_hash

class User(db.Document):
    meta = {'db_alias': 'auth', 'collection': 'users'}
    email = db.EmailField(required=True, unique=True)
    password = db.StringField(required=True, min_length=6)

    def hash_password(self):
        self.password = generate_password_hash(self.password).decode('utf8')

    def check_password(self, password):
        return check_password_hash(self.password, password)

class UserShops(db.Document):
    meta = {'db_alias': 'app', 'collection': 'users'}
    user_id = db.StringField(required=True, unique=True)
    shops = db.ListField(db.StringField())
    next_shop = db.StringField()

class Shop(db.Document):
    meta = {'db_alias': 'app', 'collection': 'shops'}
    shop_id = db.StringField(required=True, unique=True)
    max_people = db.IntField(required=True)
    sensors = db.ListField(db.StringField())
    shop_name = db.StringField()
    logo = db.StringField()

class MqttData(db.Document):
    meta = {'db_alias': 'app', 'collection': 'mqtt'}
    topic = db.StringField(required=True)
    payload = db.DynamicField()
    qos = db.IntField(required=True)
    timestamp = db.IntField(required=True)
    datetime = db.StringField()