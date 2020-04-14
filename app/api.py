from flask import request, jsonify
from app import app, db
from app.models import User, Transaction, get_all_currencies
from flask_login import current_user
from datetime import datetime


@app.route('/api/v1/transactions', methods=['GET', 'POST', 'DELETE'])
def login():
    user_id = current_user.id
    query_parameters = request.args
    from_date = query_parameters.get('from_date', None)
    to_date = query_parameters.get('to_date', None)
    buy_currency = query_parameters.get('buy_currency', None)
    sell_currency = query_parameters.get('sell_currency', None)

    validation = []
    if from_date is not None:
        validation.append(validate_date(from_date))

    if to_date is not None:
        validation.append(validate_date(to_date))



    Transaction.query.filter(user_id=current_user.id).filter(buy_currency='GBP')
    return


#queries = [X.y == 'a']
#if b:
#    queries.append(X.z == 'b')
#q.filter(*queries)


def validate_date(date):
    try:
        d = datetime.strptime(date, '%Y-%m-%d')
        if d > datetime.today().date():
            return 1
        else:
            return 0
    except:
        return 2


def validate_currency(currency):
    if currency in get_all_currencies():
        return 0
    else:
        return 3


validate_dict = {
    from_date: validate_date,
    field2: fn2
}

error_dict = {
    0: 'No errors',
    1: 'Date in future'
    2: 'Invalid date.  Please enter in format YYYY-MM-DD.',
    3: 'Invalid currency code.'
}


def validate_query_string(query_params, validators, error_codes):
    errors = {}
    for field in validators:
        errors[field] = validators[field](query_params[field])








class Validator:
    def __init__(self, field_list):
        self.valid_fields = field_list

    error_codes = {
        0: 'No errors',
        1: 'Date in future'
        2: 'Invalid date.  Please enter in format YYYY-MM-DD.',
        3: 'Invalid currency code.'
    }

    validate_mapping = {
        'from_date': validate_date,
        'to_date': validate_date,
        'from_currency': validate_currency,
        'to_currency': validate_currency
    }

    def validate_date(self, date):
        try:
            d = datetime.strptime(date, '%Y-%m-%d')
            if d > datetime.today().date():
                return 1
            else:
                return 0
        except:
            return 2

    def validate_currency(self, currency):
        if currency in get_all_currencies():
            return 0
        else:
            return 3


    def validate(self, query_params):
        errors = {}
        for field in query_params:
            errors[field] = validate_mapping[field](query_params[field])



validator = new Validator('list valid field')
validator.validate(query_params)


class NicheValidator extends BaseValidor {
init ()
}