import pytest
from requests import get
from config import Config


@pytest.mark.integration
def test_get_currencies(seed_records):
    resp = get(f'http://{Config.WEBHOST}:5000/api/v1/currencies').json()
    assert ['GBP', 'BTC', 'LTC', 'ETH']==resp['result']
