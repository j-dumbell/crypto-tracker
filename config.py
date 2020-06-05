from os import environ as env

class Config:
    DEBUG = True
    SECRET_KEY = env.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = f"postgres://{env.get('PGUSER')}:{env.get('PGPASSWORD')}@{env.get('PGHOST')}:5432/{env.get('PGDATABASE')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    WEBHOST = env.get('WEBHOST')
