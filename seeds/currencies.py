from tasks.currency_mapping import crypto_mapping, fiat_mapping
from app.models import Currency
from app import db


print('Truncating currency table...')
Currency.query.delete()
print('Adding currencies...')

all_assets = {**crypto_mapping, **fiat_mapping}
for name, code in all_assets.items():
    curr = Currency(cd=code, name=name)
    db.session.add(curr)
db.session.commit()
print('Finished')
