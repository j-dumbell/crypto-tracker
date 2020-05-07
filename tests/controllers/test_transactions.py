import pytest
from requests import get, delete
from app.controllers.transactions import TransactionGetSchema
from config import Config
from app.utils import gen_token


@pytest.mark.integration
@pytest.mark.parametrize(
    'user_id, payload, expected',
    [
        (1, {}, [1, 2]),
        (1, {'buy_currency': 'BTC'}, [1]),
        (1, {'from_date': '2019-04-20'}, [2]),
        (1, {'sell_currency': 'GBP'}, [1, 2])
    ]
)
def test_get_transactions(seed_records, user_id, payload, expected):
    token = gen_token(user_id)
    resp = get(
        url=f'http://{Config.WEBHOST}:5000/api/v1/transactions',
        params=payload,
        headers={'x-access-tokens': token}
    )
    json_resp = resp.json()
    print(json_resp)
    assert expected==[record['id'] for record in json_resp['result']]


@pytest.mark.unit
@pytest.mark.parametrize(
    'params, expected',
    [
        ({'from_date': '2025-04-20'}, {'from_date': ['Date in future']}),
        ({'to_date': '2025-04-20'}, {'to_date': ['Date in future']}),
        ({'from_date': '2018-04-20', 'to_date': '2015-01-01'}, {'_schema': ['From_date greater than to_date']}),
        ({'buy_currency': 'GBP'}, {}),
        ({'sell_currency': 'USDT'}, {'sell_currency': ['Invalid currency']}),
    ]
)
def test_TransactionGetSchema(mocker, params, expected):
    mocker.patch('app.models.Currency.list_codes', return_value=['GBP', 'USD'])
    validator = TransactionGetSchema()
    assert validator.validate(params)==expected


@pytest.mark.integration
@pytest.mark.parametrize(
    'user_id, trans_id, expected',
    [(2, '3', 204), (2, '4', 404)],
)
def test_delete_transactions(seed_records, user_id, trans_id, expected):
    token = gen_token(user_id)
    resp = delete(
        url=f'http://{Config.WEBHOST}:5000/api/v1/transactions/{trans_id}',
        headers={'x-access-tokens': token}
    )
    assert resp.status_code==expected
