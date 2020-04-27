from flask import request, jsonify, make_response
from app import app, db
from app.models import Transaction
from app.validators import validate_query_string, validate_date, validate_currency


@app.route('/api/v1/transactions', methods=['GET'])
def get_transactions():
    query_parameters = request.args
    validators = {
        'user_id': (None, True),
        'from_date': (validate_date, False),
        'to_date': (validate_date, False),
        'buy_currency': (validate_currency, False),
        'sell_currency': (validate_currency, False),
    }
    errors = validate_query_string(query_parameters, validators)
    if bool(errors):
        return make_response(jsonify(errors), 400)
    else:
        user_id = query_parameters['user_id']
        from_date = query_parameters.get('from_date', None)
        to_date = query_parameters.get('to_date', None)
        buy_currency = query_parameters.get('buy_currency', None)
        sell_currency = query_parameters.get('to_currency', None)
        query = Transaction.query.filter_by(user_id=user_id)
        if from_date!=None:
            query = query.filter(Transaction.date>=from_date)
        if to_date!=None:
            query = query.filter(Transaction.date<=to_date)
        if buy_currency!=None:
            query = query.filter_by(buy_currency=buy_currency)
        if sell_currency!=None:
            query = query.filter_by(sell_currency=sell_currency)
        return make_response(jsonify(json_list = [trans.serialize for trans in query.all()]), 200)


@app.route('/api/v1/transactions/<id>', methods=['DELETE'])
def delete_transaction(id):
    trans = Transaction.query.get(id)
    print(trans)
    if trans==None:
        return make_response(jsonify({"error": "Transaction not found"}), 404)
    else:
        db.session.delete(trans)
        db.session.commit()
        return make_response(jsonify({}), 204)
