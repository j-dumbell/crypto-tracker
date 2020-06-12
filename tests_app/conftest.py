import pytest
from freezegun import freeze_time
from datetime import datetime

from seeds.test import test_seed
from app.models import User

@pytest.fixture()
def seed_records():
    test_seed()


def gen_token_at_dt(id, dt=datetime.now()):
    user = User(email='james@gmail.com', id=id)
    with freeze_time(dt.strftime('%Y-%m-%d')):
        return user.encode_auth_token()
