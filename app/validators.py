from datetime import datetime
from app.models import get_all_currencies


def validate_date(date):
    try:
        d = datetime.strptime(date, '%Y-%m-%d').date()
        if d > datetime.today().date():
            return 1
        else:
            return 0
    except Exception as e:
        return 2


def validate_currency(currency):
    if currency in get_all_currencies():
        return 0
    else:
        return 3