import pytest
import unittest
from unittest import mock

from app.validators import validate_date, validate_currency
from app.models import get_all_currencies


@pytest.mark.parametrize(
    'input, expected', [('2020-01-01', 0), ('20203-01-01', 2), ('2025-10-10', 1)]
)
def test_validate_date(input, expected):
    assert validate_date(input) == expected



def test_validate_currency():
    with mock.patch('app.models.get_all_currencies', return_value=['ETH', 'BTC', 'LTC']) as mock_codes:
        assert validate_currency('ETH') == 0
        assert validate_currency('GBP') == 3


