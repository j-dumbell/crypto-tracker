from freezegun import freeze_time
import pytest
import jwt
from datetime import datetime

from app.models import User, token_required
from tests_app.conftest import gen_token_at_dt
from app import app
from config import Config


def test_User_encode():
    u = User(id=1)
    token = u.encode_auth_token()
    payload = jwt.decode(token, Config.SECRET_KEY)
    keys = ['exp', 'iat', 'sub']
    for key in keys:
        assert payload.get(key, None)


def test_User_decode():
    token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjEzMjU0NjI0MDAsImlhdCI6MTMyNTM3NjAwMCwic3ViIjoxfQ._MJtnaJK2tXlK0RuLyOZa97J8BZ7DZwifETGty3RuEM'
    with freeze_time('2012-01-01 00:00:00'):
        decoded = User.decode_auth_token(token)
        assert decoded['sub'] == 1


@pytest.mark.parametrize(
    'test_id, headers, expected',
    [
        (1, {'Authorization': f'Bearer {gen_token_at_dt(id=1)}'}, None),
        (2, {'Authorization': f'Bearer {gen_token_at_dt(id=1, dt=datetime(2020,5,1))}'}, {'error': 'Token expired'}),
        (3, {'Authorization': 'Bearer notavalidtoken'}, {'error': 'Invalid token'}),
        (4, {'WrongHeader': 'blahblah'}, {'error': 'No token provided'}),
        (6, {'Authorization': 'Notbearer'}, {'error': 'No token provided'})
    ]
)
def test_token_required(mocker, test_id, headers, expected):
    with app.test_request_context(headers=headers):
        mock_func = mocker.Mock()
        decorated_func = token_required(mock_func)
        resp = decorated_func()
        if test_id==1:
            mock_func.assert_called_with(1)
        else:
            assert resp.json == expected
