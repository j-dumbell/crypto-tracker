from app import db
from app.models import User, Transaction, Currency
from datetime import date
from time import sleep


def drop_create_tables(max_retries, sleep_time):
    attempt=1
    while attempt <= max_retries:
        try:
            print(f'Dropping & creating tables (attempt {attempt})...')
            db.session.commit()
            db.drop_all()
            db.create_all()
            db.session.commit()
            print(f'Successfully dropped and created all tables')
            break
        except:
            print(f'Attempt {attempt} failed.  Retrying in {sleep_time}')
            attempt+=1
            sleep(sleep_time)


def add_records():

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

    mapping = {
        User: user_list,
        Transaction: transaction_list,
        Currency: currency_list
    }

    for user in user_list:
        user.set_password('james')

    print('Adding records...')
    for model, records in mapping.items():
        for record in records:
            db.session.add(record)
            db.session.commit()
    print('All records added')


if __name__=='__main__':
    drop_create_tables(3, 5)
    add_records()
