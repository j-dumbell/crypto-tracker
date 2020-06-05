from datetime import datetime

import pandas as pd
from pandas.testing import assert_frame_equal
import pytest

from tasks.prices import (
    transform_crypto,
    transform_fiat,
    call_fiat_api,
    call_crypto_api,
)
from app.models import Price


def test_transform_crypto():
    data = [
        {
            "priceUsd": "8295.4023956179716919",
            "time": 1526428800000,
            "date": "2018-05-16T00:00:00.000Z",
        },
        {
            "priceUsd": "8297.2587963462737933",
            "time": 1526515200000,
            "date": "2018-05-17T00:00:00.000Z",
        },
    ]
    mapping = {"bitcoin": "BTC"}
    result = transform_crypto(data=data, coin="bitcoin", coin_mapping=mapping)
    expected = pd.DataFrame(
        {
            "ts": [datetime(2018, 5, 16), datetime(2018, 5, 17)],
            "buy_currency": ["BTC", "BTC"],
            "sell_currency": ["USD", "USD"],
            "rate": [8295.4023956179716919, 8297.2587963462737933],
        }
    )
    assert_frame_equal(result, expected)


@pytest.mark.parametrize(
    "data, expected",
    [
        (
            {
                "rates": {"2020-05-14": {"EUR": 0.9266123054}},
                "start_at": "2020-05-14",
                "base": "EUR",
                "end_at": "2020-05-14",
            },
            pd.DataFrame(
                {
                    "ts": [datetime(2020, 5, 14)],
                    "buy_currency": ["EUR"],
                    "sell_currency": ["USD"],
                    "rate": [0.9266123054],
                }
            ),
        ),
        (
            {
                "rates": {},
                "start_at": "2020-05-14",
                "base": "EUR",
                "end_at": "2020-05-14",
            },
            pd.DataFrame(
                {
                    "ts": [datetime(2020, 5, 14)],
                    "buy_currency": ["EUR"],
                    "sell_currency": ["USD"],
                    "rate": [0.9266123054],
                }
            ),
        ),
    ],
)
def test_transform_fiat(data, expected, mocker):
    mock_price = mocker.patch(
        "sqlalchemy.orm.query.Query.first",
        return_value=Price(
            ts=datetime(2020, 5, 14),
            buy_currency="EUR",
            sell_currency="USD",
            rate=0.9266123054,
        ),
    )
    result = transform_fiat(data, "EUR")
    assert_frame_equal(result, expected)


def test_call_fiat_api(mocker):
    mock_get = mocker.patch("tasks.prices.get")
    call_fiat_api(
        currency="ETH", start_dt=datetime(2020, 1, 1), end_dt=datetime(2020, 1, 5)
    )
    mock_get.assert_called_with(
        url="https://api.exchangeratesapi.io/history",
        params={
            "start_at": "2020-01-01",
            "end_at": "2020-01-05",
            "symbols": "ETH",
            "base": "USD",
        },
    )


def test_call_crypto_api(mocker):
    mock_get = mocker.patch("tasks.prices.get")
    call_crypto_api(
        coin="btc", start_dt=datetime(2020, 1, 1), end_dt=datetime(2020, 1, 5)
    )
    mock_get.assert_called_with(
        url="http://api.coincap.io/v2/assets/btc/history",
        params={"interval": "d1", "start": 1577836800000, "end": 1578182400000},
    )
