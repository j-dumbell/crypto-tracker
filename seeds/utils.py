from time import sleep

from app import db
from app.models import User


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


def add_records(*args):
    print('Adding records...')
    for arg in args:
        for record in arg:
            if isinstance(record, User):
                record.set_password('james')
            db.session.add(record)
            db.session.commit()
    print('Finished adding records')
