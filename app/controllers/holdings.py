from datetime import datetime, date

from flask import request, jsonify, make_response
from marshmallow import Schema, fields, validates, validates_schema, ValidationError
import simplejson as json

from app import app
from app.models import token_required
from app.utils import future_date, calc_holdings, get_current_prices, calc_historic_values, calc_current_values, calc_metrics


class HoldingsGetSchema(Schema):
    date = fields.Date(required=True, validate=future_date)


@app.route('/api/v1/holdings', methods=['GET'])
@token_required
def get_holdings(current_user):
    validator = HoldingsGetSchema()
    query_params = request.args
    errors = validator.validate(query_params)
    if errors:
        return make_response(jsonify(errors), 400)
    at_date = datetime.strptime(query_params['date'], '%Y-%m-%d').date()
    holdings = calc_holdings(current_user, at_date)
    if at_date==date.today():
        current_prices = get_current_prices()
        values = calc_current_values(holdings, current_prices)
    else:
        values = calc_historic_values(holdings, at_date)
    metrics = calc_metrics(values)
    result = {
        **{'holdings': values},
        **metrics
    }
    return make_response(json.dumps(result), 200)
