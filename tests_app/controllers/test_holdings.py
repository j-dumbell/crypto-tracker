from datetime import date

from requests import get

from app.utils import gen_token
from config import Config


def test_get_holdings(seed_records):
    token = gen_token(1)
    resp = get(
        url = f'http://{Config.WEBHOST}:5000/api/v1/holdings',
        params = {'date': date.today().strftime('%Y-%m-%d')},
        headers = {'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 200


