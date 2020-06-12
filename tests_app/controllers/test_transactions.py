import pytest
from requests import get, delete, post

from config import Config
from app.controllers.transactions import TransactionGetSchema, TransactionPostSchema
from app.utils import gen_token


@pytest.mark.integration
@pytest.mark.parametrize(
    'user_id, payload, expected',
    [
        (1, {}, [1, 2]),
        (1, {'buy_currency': 'BTC'}, [1]),
        (1, {'from_date': '2019-04-20'}, [2]),
        (1, {'sell_currency': 'USD'}, [1, 2])
    ]
)
def test_get_transactions(seed_records, user_id, payload, expected):
    token = gen_token(user_id)
    resp = get(
        url=f'http://{Config.WEBHOST}:5000/api/v1/transactions',
        params=payload,
        headers={'Authorization': f'Bearer {token}'}
    )
    json_resp = resp.json()
    assert expected==[record['id'] for record in json_resp['result']]


@pytest.mark.unit
@pytest.mark.parametrize(
    'params, expected',
    [
        ({'from_date': '2025-04-20'}, {'from_date': ['Date in future']}),
        ({'to_date': '2025-04-20'}, {'to_date': ['Date in future']}),
        ({'from_date': '2018-04-20', 'to_date': '2015-01-01'}, {'_schema': ['From_date greater than to_date']}),
        ({'buy_currency': 'USD'}, {}),
        ({'sell_currency': 'USDT'}, {'sell_currency': ['Invalid currency']}),
    ]
)
def test_TransactionGetSchema(mocker, params, expected):
    mocker.patch('app.models.Currency.list_codes', return_value=['USD', 'USD'])
    validator = TransactionGetSchema()
    assert validator.validate(params)==expected


@pytest.mark.unit
@pytest.mark.parametrize(
    'params, expected',
    [
        (
            {'date': '2025-04-20', 'buy_currency': 'USD', 'buy_amount':10.1 ,'sell_currency': 'USD', 'sell_amount':3},
            {'date': ['Date in future']}
        ),
        (
            {'date': '2015-01-01', 'buy_currency': 'USD', 'buy_amount':5, 'sell_currency': 'USD', 'sell_amount':3},
            {'_schema': ['Buy currency equals sell currency']}
        ),
        (
            {'date': '2015-01-01', 'buy_currency': 'USD', 'buy_amount':5, 'sell_currency': 'BRCH', 'sell_amount':3},
            {'sell_currency': ['Invalid currency']}
        ),
    ]
)
def test_TransactionPostSchema(mocker, params, expected):
    mocker.patch('app.models.Currency.list_codes', return_value=['USD', 'USD'])
    validator = TransactionPostSchema()
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
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code==expected


@pytest.mark.integration
@pytest.mark.parametrize(
    'user_id, body, exp_code, exp_json',
    [
        (
            1,
            {'date': '2020-04-20', 'buy_currency': 'USD', 'buy_amount': 10.1, 'sell_currency': 'BTC',
             'sell_amount': 3},
            201,
            {'result': {'date': '2020-04-20', 'buy_currency': 'USD', 'buy_amount': 10.1, 'sell_currency': 'BTC',
                        'sell_amount': 3, 'user_id': 1}}
        ),
        (
            1,
            {'date': '2020-04-20', 'buy_amount': 10.1, 'sell_currency': 'BTC', 'sell_amount': 3},
            400,
            {'buy_currency': ['Missing data for required field.']}
        )
    ],
)
def test_post_transactions(seed_records, user_id, body, exp_code, exp_json):
    token = gen_token(user_id)
    resp = post(
        url=f'http://{Config.WEBHOST}:5000/api/v1/transactions',
        json=body,
        headers={'Authorization': f'Bearer {token}'}
    )
    resp_json = resp.json()
    try:
        del resp_json['result']['id']
    except:
        pass

    assert resp.status_code == exp_code
    assert resp_json == exp_json
