from app import db, cache
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import jwt
from config import Config
from functools import wraps
from flask import request


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    transactions = db.relationship('Transaction', backref='user', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.email}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def encode_auth_token(self):
        payload = {
            'exp': datetime.utcnow() + timedelta(days=1),
            'iat': datetime.utcnow(),
            'sub': self.id
        }
        byte_token = jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')
        return byte_token.decode('utf-8')

    @staticmethod
    def decode_auth_token(token):
        byte_token = token.encode('utf-8')
        try:
            payload = jwt.decode(byte_token, Config.SECRET_KEY)
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    buy_currency = db.Column(db.String(3))
    buy_amount = db.Column(db.Float)
    sell_currency = db.Column(db.String(3))
    sell_amount = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)

    def __repr__(self):
        return f'<Transaction {self.id}, {self.buy_currency}, {self.buy_amount}, {self.sell_currency}, {self.sell_amount}, {self.user_id}>'

    @property
    def serialize(self):
       return {
           'id': self.id,
           'date': self.date.strftime('%Y-%m-%d'),
           'buy_currency': self.buy_currency,
           'buy_amount': self.buy_amount,
           'sell_currency': self.sell_currency,
           'sell_amount': self.sell_amount,
           'user_id': self.user_id
       }


class Currency(db.Model):
    cd = db.Column(db.String(3), primary_key=True)
    name = db.Column(db.String(100))

    def __repr__(self):
        return f'Currency {self.cd}, {self.name}'

    @staticmethod
    @cache.cached(timeout=3600, key_prefix='all_currencies')
    def list_codes():
        return [currency.cd for currency in Currency.query.all()]


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if 'x-access-tokens' in request.headers:
            token = request.headers['x-access-tokens']
        if not token:
            return jsonify({'message': 'a valid token is missing'})
        current_user = User.decode_auth_token(token)
        return f(current_user, *args, **kwargs)
    return decorator
