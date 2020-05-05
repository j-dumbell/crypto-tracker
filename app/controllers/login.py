from flask import request, jsonify, make_response
from app import app
from marshmallow import Schema, fields, validates, validates_schema, ValidationError
from app.models import User


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)


@app.route('/api/v1/login', methods=['POST'])
def login():
    validator = LoginSchema()
    body = request.json
    errors = validator.validate(body)
    if errors:
        return make_response(jsonify(errors), 400)
    email = body['email']
    password = body['password']
    user = User.query.filter_by(email=email).first()
    if not user:
        return make_response(jsonify({}), 404)
    if not user.check_password(password):
        return make_response(jsonify({}), 401)
    token = user.encode_auth_token()
    dec_token = token.decode('utf-8')
    return make_response(jsonify(dec_token), 200)