from app import app, db, cache

from app.models import User, Transaction, Currency

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Transaction': Transaction, 'Currency': Currency, 'cache': cache}