from app import db, cache
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import jwt
from config import Config
from functools import wraps
from flask import request
from flask import make_response, jsonify


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, index=True)
    email = db.Column(db.String(120), unique=True)
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
        return jwt.decode(byte_token, Config.SECRET_KEY)


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
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
    cd = db.Column(db.String(5), primary_key=True)
    name = db.Column(db.String(100))
    asset_type = db.Column(db.String(10))

    def __repr__(self):
        return f'Currency {self.cd}, {self.name}'

    @staticmethod
    @cache.cached(timeout=3600, key_prefix='all_currencies')
    def list_codes():
        return [currency.cd for currency in Currency.query.all()]


class Price(db.Model):
    ts = db.Column(db.DateTime, primary_key=True)
    buy_currency = db.Column(db.String(10), db.ForeignKey('currency.cd'), primary_key=True)
    sell_currency = db.Column(db.String(10), db.ForeignKey('currency.cd'), primary_key=True)
    rate = db.Column(db.Float)

    def __repr__(self):
        return f"Price {self.ts}, {self.buy_currency}, {self.sell_currency}, {self.rate}"


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        try:
            header = request.headers['Authorization']
            token = header.split('Bearer ')[1]
        except:
            return make_response(jsonify({'error': 'No token provided'}), 401)
        try:
            decoded = User.decode_auth_token(token)
            current_user = decoded['sub']
            return f(current_user, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return make_response(jsonify({'error': 'Token expired'}), 401)
        except jwt.InvalidTokenError:
            return make_response(jsonify({'error': 'Invalid token'}), 401)
    return decorator
