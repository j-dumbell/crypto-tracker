from app import db
from app.models import User, Transaction, Currency
from datetime import date


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
    for user in user_list:
        user.set_password('james')

    for model in mapping.keys():
        model.query.delete()
        print(f'Truncating table: {model}')

    for model in mapping.keys():
        for record in mapping[model]:
            db.session.add(record)
            print(f'Adding record to table {model}: {record}')

    db.session.commit()
