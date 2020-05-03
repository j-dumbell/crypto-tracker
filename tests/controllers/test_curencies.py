import pytest
from requests import get
from app.models import Currency
import os

@pytest.mark.integration
def test_get_currencies(seed_records):
    host = os.environ['WEBHOST']
    resp = get(f'http://{host}:5000/api/v1/currencies').json()
    assert ['GBP', 'BTC', 'LTC', 'ETH']==resp['result']
