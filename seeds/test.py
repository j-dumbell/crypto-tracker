from datetime import date, datetime, timedelta

from app.models import User, Transaction, Currency, Price
from seeds.utils import drop_create_tables, add_records


def test_seed():
    user_list = [
        User(email='van@gmail.com'),
        User(email='james@gmail.com')
    ]
    transaction_list = [
        Transaction(date=date(2019, 1, 12), buy_currency='BTC', buy_amount=1.1, sell_currency='USD',
                    sell_amount=1000, user_id=1),
        Transaction(date=date(2019, 3, 12), buy_currency='USD', buy_amount=600.0, sell_currency='BTC',
                    sell_amount=0.7, user_id=1),
        Transaction(date=date(2019, 5, 20), buy_currency='ETH', buy_amount=5.0, sell_currency='USD',
                    sell_amount=1200.0, user_id=1),
        Transaction(date=date(2019, 5, 20), buy_currency='ETH', buy_amount=5.0, sell_currency='USD',
                    sell_amount=1200.0, user_id=2)
    ]
    currency_list = [
        Currency(cd='USD', name='United States Dollar', asset_type='fiat'),
        Currency(cd='GBP', name='British Pound', asset_type='fiat'),
        Currency(cd='BTC', name='Bitcoin', asset_type='crypto'),
        Currency(cd='LTC', name='Litecoin', asset_type='crypto'),
        Currency(cd='ETH', name='Ethereum', asset_type='crypto')
    ]

    curr_dt = datetime.today()
    last_month = curr_dt + timedelta(days=-30)
    price_list = [
        Price(ts=last_month, buy_currency='BTC', sell_currency='USD', rate=10000),
        Price(ts=curr_dt, buy_currency='BTC', sell_currency='USD', rate=15000),
        Price(ts=last_month, buy_currency='ETH', sell_currency='USD', rate=100),
        Price(ts=curr_dt, buy_currency='ETH', sell_currency='USD', rate=200),
        Price(ts=last_month, buy_currency='USD', sell_currency='USD', rate=1),
        Price(ts=curr_dt, buy_currency='USD', sell_currency='USD', rate=1)
    ]

    drop_create_tables(3, 5)
    add_records(user_list, transaction_list, currency_list, price_list)


if __name__=='__main__':
    test_seed()
