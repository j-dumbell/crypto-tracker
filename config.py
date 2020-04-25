from os import environ as env

class Config:
    DEBUG = True
    SECRET_KEY = env.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = f"postgres://{env['PGUSER']}:{env['PGPASSWORD']}@db:5432/{env['PGDATABASE']}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
