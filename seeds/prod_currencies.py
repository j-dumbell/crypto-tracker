from tasks.currency_mapping import crypto_mapping, fiat_mapping
from app.models import Currency
from app import db


print('Truncating currency table...')
Currency.query.delete()

print('Adding currencies...')
for name, code in crypto_mapping:
    curr = Currency(cd=code, name=name, asset_type='crypto')
    db.session.add(curr)
for name, code in fiat_mapping:
    curr = Currency(cd=code, name=name, asset_type='fiat')
    db.session.add(curr)
db.session.commit()
print('Finished')
