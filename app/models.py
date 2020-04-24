from app import db, login, cache
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, db.Model):
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


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Currency(db.Model):
    cd = db.Column(db.String(3), primary_key=True)
    name = db.Column(db.String(100))

    def __repr__(self):
        return f'Currency {self.cd}, {self.name}'


@cache.cached(timeout=3600, key_prefix='all_currencies_form')
def get_all_currencies():
    return [(currency.cd, currency.cd) for currency in Currency.query.all()]


@cache.cached(timeout=3600, key_prefix='all_currencies')
def get_all_currencies():
    return [currency.cd for currency in Currency.query.all()]
