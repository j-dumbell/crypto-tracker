import pytest
from requests import get, delete, post
from config import Config


@pytest.mark.integration
@pytest.mark.parametrize(
    'req_body, exp_body, status_code',
    [
        ({'email': 'james@gmail.com'}, {'password': ['Missing data for required field.']}, 400),
        ({'password': 'qwerty'}, {'email': ['Missing data for required field.']}, 400),
        ({}, {'email': ['Missing data for required field.'], 'password': ['Missing data for required field.']}, 400),
        ({'email': 'notreal@gmail.com', 'password': 'blah'}, {}, 404),
        ({'email': 'james@gmail.com', 'password': 'wrongpassword'}, {}, 401),
        ({'email': 'james@gmail.com', 'password': 'james'}, None, 200)
    ]
)
def test_login(seed_records, req_body, exp_body, status_code):
    url = f'http://{Config.WEBHOST}:5000/api/v1/login'
    resp = post(url, json=req_body)
    assert resp.status_code == status_code
    if req_body != {'email': 'james@gmail.com', 'password': 'james'}:
        assert resp.json() == exp_body
