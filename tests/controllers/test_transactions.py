import pytest
from requests import get, delete
from app.controllers.transactions import TransactionGetSchema
from app.models import Transaction
import os


@pytest.mark.integration
@pytest.mark.parametrize(
    'payload, expected',
    [
        ({'user_id': '1'}, [1, 2]),
        ({'user_id': '1', 'buy_currency': 'BTC'}, [1]),
        ({'user_id': '1', 'from_date': '2019-04-20'}, [2]),
        ({'user_id': '1', 'sell_currency': 'GBP'}, [1, 2])
    ]
)
def test_get_transactions(seed_records, payload, expected):
    host = os.environ['WEBHOST']
    resp = get(f'http://{host}:5000/api/v1/transactions', params=payload).json()
    assert expected==[record['id'] for record in resp['result']]


@pytest.mark.unit
@pytest.mark.parametrize(
    'params, expected',
    [
        ({'user_id': '1', 'from_date': '2025-04-20'}, {'from_date': ['Date in future']}),
        ({'user_id': '1', 'to_date': '2025-04-20'}, {'to_date': ['Date in future']}),
        ({'user_id': '1', 'from_date': '2018-04-20', 'to_date': '2015-01-01'}, {'_schema': ['From_date greater than to_date']}),
        ({'user_id': '1', 'buy_currency': 'GBP'}, {}),
        ({'user_id': '1', 'sell_currency': 'USDT'}, {'sell_currency': ['Invalid currency']}),
    ]
)
def test_TransactionGetSchema(mocker, params, expected):
    mocker.patch('app.models.Currency.list_codes', return_value=['GBP', 'USD'])
    validator = TransactionGetSchema()
    assert validator.validate(params)==expected


@pytest.mark.integration
@pytest.mark.parametrize(
    'id, expected',
    [('3', 204), ('4', 404)],
)
def test_delete_transactions(seed_records, id, expected):
    host = os.environ['WEBHOST']
    resp = delete(f'http://{host}:5000/api/v1/transactions/{id}')
    assert resp.status_code==expected
