import pandas as pd
from pandas.testing import assert_frame_equal
from datetime import datetime

from tasks.prices import transform



def test_transform():
    data = [
       {'priceUsd': '8295.4023956179716919', 'time': 1526428800000, 'date': '2018-05-16T00:00:00.000Z'},
       {'priceUsd': '8297.2587963462737933', 'time': 1526515200000, 'date': '2018-05-17T00:00:00.000Z'}
    ]
    mapping = {'bitcoin': 'BTC'}
    result = transform(data=data, coin='bitcoin', coin_mapping=mapping)
    expected = pd.DataFrame(
        {
            'ts': [datetime(2018,5,16), datetime(2018,5,17)],
            'buy_currency': ['BTC', 'BTC'],
            'sell_currency': ['USD', 'USD'],
            'rate': [8295.4023956179716919, 8297.2587963462737933]
        }
    )
    assert_frame_equal(result, expected)





