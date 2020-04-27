import pytest
from requests import get


@pytest.mark.integration
@pytest.mark.parametrize(
    'payload, expected',
    [
        ({'user_id': '1'}, [1, 2]),
        ({'user_id': '1', 'buy_currency': 'BTC'}, [1]),
        ({'user_id': '1', 'from_date': '2019-04-20'}, [2]),
        ({'user_id': '1', 'sell_currency': 'GBP'}, [1,2]),
        ({'user_id': '2'}, []),
    ]
)
def test_get_transactions(payload, expected):
    resp = get('http://localhost:5000/api/v1/transactions', params=payload).json()
    assert expected==[record['id'] for record in resp['json_list']]
