from marshmallow import ValidationError
from datetime import datetime

from app.models import User, Currency


def gen_token(user_id):
    user = User.query.get(user_id)
    return user.encode_auth_token()


def validate_currency(curr):
    if curr not in Currency.list_codes():
        raise ValidationError("Invalid currency")


def future_date(date):
    now = datetime.now().date()
    if date > now:
        raise ValidationError("Date in future")