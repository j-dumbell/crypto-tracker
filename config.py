import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = 'postgres://james.dumbell:@localhost:5432/crypto_tracker'
    SQLALCHEMY_TRACK_MODIFICATIONS = False