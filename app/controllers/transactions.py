from flask import request, jsonify, make_response
from app import app, db
from app.models import Transaction, Currency, token_required
from marshmallow import Schema, fields, validates, validates_schema, ValidationError
from datetime import datetime


class TransactionGetSchema(Schema):
    from_date = fields.Date(required=False)
    to_date = fields.Date(required=False)
    buy_currency = fields.String(required=False)
    sell_currency = fields.String(required=False)

    @validates('buy_currency')
    def valid_buy_currency(self, value):
        if value not in Currency.list_codes():
            raise ValidationError("Invalid currency")

    @validates('sell_currency')
    def valid_sell_currency(self, value):
        if value not in Currency.list_codes():
            raise ValidationError("Invalid currency")

    @validates('from_date')
    def from_date_future(self, value):
        now = datetime.now().date()
        if value > now:
            raise ValidationError("Date in future")

    @validates('to_date')
    def to_date_future(self, value):
        now = datetime.now().date()
        if value > now:
            raise ValidationError("Date in future")

    @validates_schema
    def from_date_greater_to_date(self, data, **kwargs):
        from_date = data.get('from_date', None)
        to_date = data.get('to_date', None)
        if from_date==None or to_date==None:
            pass
        else:
            if from_date > to_date:
                raise ValidationError("From_date greater than to_date")


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
