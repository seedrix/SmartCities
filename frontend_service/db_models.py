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