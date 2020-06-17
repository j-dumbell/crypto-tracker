from datetime import datetime, date, timedelta
from decimal import Decimal

from marshmallow import ValidationError
import pytest

from app.utils import validate_currency, future_date, calc_holdings, calc_metrics


def test_validate_currency(mocker):
    mocker.patch('app.utils.Currency.list_codes', return_value=['BTC', 'ETH', 'USD'])
    with pytest.raises(ValidationError) as exc:
        validate_currency('CHRT')
        assert "Invalid currency" in str(exc.value)


def test_future_date():
    at_date = date.today() + timedelta(days=10)
    with pytest.raises(ValidationError) as exc:
        future_date(at_date)
        assert "Date in future" in str(exc.value)


@pytest.mark.parametrize(
    'date, expected',
    [
        (
            date.today(),
            {
                ('BTC', Decimal('0.40000'), 'crypto'),
                ('ETH', Decimal('5.00000'), 'crypto'),
                ('USD', Decimal('-1600.00000'), 'fiat')
            }
         ),
        (
            date(2019,4,1),
            {
                ('BTC', Decimal('0.40000'), 'crypto'),
                ('USD', Decimal('-400.00000'), 'fiat')
            }
        ),
    ],
)
def test_calc_holdings(seed_records, date, expected):
    result = calc_holdings(1, date)
    assert expected == set(result)


def test_calc_metrics():
    values = [
        ('BTC', 1.1, 'crypto', 1000, 1100),
        ('ETH', 10, 'crypto', 100, 1000),
        ('USD', 1200, 'fiat', 1, 1200),
    ]
    result = calc_metrics(values)
    expected = {
        'crypto_value': 2100,
        'fiat_value': 1200,
        'profit': 3300
    }
    assert expected == result