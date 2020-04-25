from app import db
from app.models import User, Transaction, Currency
from datetime import date
from time import sleep


user_list = [
    User(id=1, email='van@gmail.com'),
    User(id=2, email='james@gmail.com')
]

transaction_list = [
    Transaction(date=date(2019,1,12), buy_currency='BTC', buy_amount=1.1, sell_currency='GBP', sell_amount=1000, user_id=1),
    Transaction(date=date(2019,5,20), buy_currency='ETH', buy_amount=5, sell_currency='GBP', sell_amount=1200, user_id=1)
]

currency_list = [
    Currency(cd='GBP', name='Sterling'),
    Currency(cd='BTC', name='Bitcoin'),
    Currency(cd='LTC', name='Litecoin'),
    Currency(cd='ETH', name='Ethereum')
]

mapping = {
    Transaction: transaction_list,
    User: user_list,
    Currency: currency_list
}


if __name__=='__main__':
    while True:
        try:
            db.create_all()

            for user in user_list:
                user.set_password('james')

            for model in mapping:
                model.query.delete()
                print(f'Truncating table: {model}')

            for model, records in mapping.items():
                db.session.add_all(records)
                print(f'Adding records to table {model}')
            db.session.commit()
            print('Finished')
            break
        except:
            print(f'DB not ready.  Retrying in 10s.')
            sleep(10)
