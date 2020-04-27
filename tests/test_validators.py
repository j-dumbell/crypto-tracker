import pytest
from app.validators import validate_date, validate_currency, validate_query_string


@pytest.mark.unit
@pytest.mark.parametrize(
    'input, expected',
    [
        ('2020-01-01', None),
        ('20203-01-01', 'Invalid date.  Please enter in format YYYY-MM-DD.'),
        ('2025-10-10', 'Date in future.')
    ]
)
def test_validate_date(input, expected):
    assert validate_date(input) == expected


@pytest.mark.unit
@pytest.mark.parametrize(
    'input, patch, expected',
    [
        ('ETH', ['ETH', 'BTC', 'LTC'], None),
        ('GBP', ['ETH', 'BTC', 'LTC'], 'Invalid currency code.'),
        ('XRP', ['ETH', 'BTC', 'LTC'], 'Invalid currency code.'),
    ]
)
def test_validate_currency(mocker, input, patch, expected):
    mocker.patch('app.validators.get_all_currencies', return_value=patch)
    assert validate_currency(input) == expected


@pytest.mark.parametrize(
    'query_params, validators, expected',
    [
        (
            {'from_date': '2020-10-10'},
            {'from_date': (validate_date, False), 'to_date': (validate_date, True)},
            {'from_date': 'Date in future.', 'to_date': 'Parameter required but not provided.'}
        ),
        (
            {'from_date': '2020-10-10', 'user_id': 'blahlbah'},
            {'from_date': (validate_date, False), 'to_date': (validate_date, True), 'user_id': (None, True)},
            {'from_date': 'Date in future.', 'to_date': 'Parameter required but not provided.'}
        )
    ]
)
def test_validate_query_string(query_params, validators, expected):
    assert validate_query_string(query_params, validators)==expected