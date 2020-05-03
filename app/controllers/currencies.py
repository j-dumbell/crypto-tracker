from flask import request, jsonify, make_response
from app import app, db
from app.models import Currency

@app.route('/api/v1/currencies', methods=['GET'])
def get_currencies():
    return make_response(jsonify(result = Currency.list_codes()), 200)
