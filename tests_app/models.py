from app.models import User
from freezegun import freeze_time
import pytest
import jwt
from config import Config


def test_User_encode():
    u = User(id=1)
    token = u.encode_auth_token()
    payload = jwt.decode(token, Config.SECRET_KEY)
    keys = ['exp', 'iat', 'sub']
    for key in keys:
        assert payload.get(key, None)


@pytest.mark.parametrize(
    'token, dt, expected',
    [
        ('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjEzMjU0NjI0MDAsImlhdCI6MTMyNTM3NjAwMCwic3ViIjoxfQ._MJtnaJK2tXlK0RuLyOZa97J8BZ7DZwifETGty3RuEM',
            '2012-01-01 00:00:00', 1),
        ('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjEzMjU0NjI0MDAsImlhdCI6MTMyNTM3NjAwMCwic3ViIjoxfQ._MJtnaJK2tXlK0RuLyOZa97J8BZ7DZwifETGty3RuEM',
            '2020-01-10 00:00:00', 'Signature expired. Please log in again.'),
        ('thisisnotatoken', '2020-01-10 00:00:00', 'Invalid token. Please log in again.')
    ]
)
def test_User_decode(token, dt, expected):
    with freeze_time(dt):
        assert User.decode_auth_token(token) == expected
