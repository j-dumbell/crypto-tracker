from flask import request, jsonify, make_response
from marshmallow import Schema, fields, validates, validates_schema, ValidationError

from app import app, db
from app.models import Transaction, token_required
from app.utils import validate_currency, future_date


class TransactionGetSchema(Schema):
    from_date = fields.Date(required=False, validate=future_date)
    to_date = fields.Date(required=False, validate=future_date)
    buy_currency = fields.String(required=False, validate=validate_currency)
    sell_currency = fields.String(required=False, validate=validate_currency)

    @validates_schema
    def from_date_greater_to_date(self, data, **kwargs):
        from_date = data.get('from_date', None)
        to_date = data.get('to_date', None)
        if from_date==None or to_date==None:
            return
        if from_date > to_date:
            raise ValidationError("From_date greater than to_date")


class TransactionPostSchema(Schema):
    date = fields.Date(required=True, validate=future_date)
    buy_currency = fields.String(required=True, validate=validate_currency)
    buy_amount = fields.Float(required=True)
    sell_currency = fields.String(required=False, validate=validate_currency)
    sell_amount = fields.Float(required=True)

    @validates_schema
    def buy_equals_sell(self, data, **kwargs):
        buy_currency = data.get('buy_currency', None)
        sell_currency = data.get('sell_currency', None)
        if buy_currency==sell_currency:
            raise ValidationError('Buy currency equals sell currency')


@app.route('/api/v1/transactions', methods=['GET'])
@token_required
def get_transactions(current_user):
    validator = TransactionGetSchema()
    query_params = request.args
    errors = validator.validate(query_params)
    if bool(errors):
        return make_response(jsonify(errors), 400)
    from_date = query_params.get('from_date', None)
    to_date = query_params.get('to_date', None)
    buy_currency = query_params.get('buy_currency', None)
    sell_currency = query_params.get('to_currency', None)
    query = Transaction.query.filter_by(user_id=current_user)
    if from_date!=None:
        query = query.filter(Transaction.date>=from_date)
    if to_date!=None:
        query = query.filter(Transaction.date<=to_date)
    if buy_currency!=None:
        query = query.filter_by(buy_currency=buy_currency)
    if sell_currency!=None:
        query = query.filter_by(sell_currency=sell_currency)
    query_results = [trans.serialize for trans in query.all()]
    return make_response(jsonify(result=query_results), 200)


@app.route('/api/v1/transactions/<id>', methods=['DELETE'])
@token_required
def delete_transaction(current_user, id):
    trans = Transaction.query.get(id)
    if trans==None or trans.user_id!=current_user:
        return make_response(jsonify({"error": "Transaction not found"}), 404)
    db.session.delete(trans)
    db.session.commit()
    return make_response(jsonify({}), 204)


@app.route('/api/v1/transactions', methods=['POST'])
@token_required
def post_transaction(current_user):
    body = request.json
    validator = TransactionPostSchema()
    errors = validator.validate(body)
    if errors:
        return make_response(jsonify(errors), 400)
    transaction = Transaction(
        date=body['date'],
        buy_currency=body['buy_currency'],
        buy_amount=body['buy_amount'],
        sell_currency=body['sell_currency'],
        sell_amount=body['sell_amount'],
        user_id=current_user
    )
    db.session.add(transaction)
    db.session.commit()
    return make_response(jsonify(result=transaction.serialize), 201)
