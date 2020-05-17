from datetime import date

from app.models import User, Transaction, Currency
from seeds.utils import drop_create_tables, add_records


def test_seed():
    user_list = [
        User(email='van@gmail.com'),
        User(email='james@gmail.com')
    ]
    transaction_list = [
        Transaction(date=date(2019, 1, 12), buy_currency='BTC', buy_amount=1.1, sell_currency='GBP',
                    sell_amount=1000, user_id=1),
        Transaction(date=date(2019, 5, 20), buy_currency='ETH', buy_amount=5, sell_currency='GBP',
                    sell_amount=1200, user_id=1),
        Transaction(date=date(2019, 5, 20), buy_currency='ETH', buy_amount=5, sell_currency='GBP',
                    sell_amount=1200, user_id=2)
    ]
    currency_list = [
        Currency(cd='GBP', name='Sterling'),
        Currency(cd='BTC', name='Bitcoin'),
        Currency(cd='LTC', name='Litecoin'),
        Currency(cd='ETH', name='Ethereum')
    ]
    drop_create_tables(3, 5)
    add_records(user_list, transaction_list, currency_list)


if __name__=='__main__':
    test_seed()
