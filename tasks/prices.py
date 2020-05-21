from tempfile import NamedTemporaryFile
from datetime import datetime, timedelta, date
from os import environ as env
import time

from requests import get
from sqlalchemy import create_engine
from google.cloud import storage
import pandas as pd
from tasks.currency_mapping import crypto_mapping


def call_api(coin, start_dt, end_dt):
    start_unix = int(start_dt.timestamp()*1000)
    end_unix = int(end_dt.timestamp()*1000)
    resp = get(
        url=f'http://api.coincap.io/v2/assets/{coin}/history',
        params={
            'interval': 'd1',
            'start': start_unix,
            'end': end_unix
        }
    )
    return resp.json()


def load_gcs(bucket, local_path, remote_path):
    client = storage.Client()
    bucket = client.get_bucket(bucket)
    blob = bucket.blob(remote_path)
    blob.upload_from_filename(filename=local_path)


def transform(data, coin, coin_mapping):
    df = pd.DataFrame(data)
    df.drop(labels='time', axis=1, inplace=True)
    df['buy_currency']=coin_mapping[coin]
    df['sell_currency']='USD'
    df.rename(columns={'date': 'ts', 'priceUsd': 'rate'}, inplace=True)
    df = df.astype({'ts': 'datetime64', 'buy_currency': 'str', 'sell_currency': 'str', 'rate': 'float'})
    df = df[['ts', 'buy_currency', 'sell_currency', 'rate']]
    return df


if __name__=='__main__':
    yesterday = date.today() + timedelta(days=-1)
    start_dt = datetime.combine(yesterday, datetime.min.time())
    end_dt = start_dt+timedelta(days=1)
    bucket = env['BUCKET']
    engine = create_engine(f"postgres://{env['PGUSER']}:{env['PGPASSWORD']}@{env['PGHOST']}:5432/{env['PGDATABASE']}")

    for coin in crypto_mapping.keys():
        print(f'Querying API: {coin}')
        raw = call_api(coin=coin, start_dt=start_dt, end_dt=end_dt)
        print(f'Transforming: {coin}')
        df = transform(data=raw['data'], coin=coin, coin_mapping=crypto_mapping)
        print(df)
        with NamedTemporaryFile('w') as fp:
            print(f'Writing CSV: {coin}')
            df.to_csv(fp.name)
            print(f'Uploading to GCS: {coin}')
            load_gcs(bucket, fp.name, f"{start_dt.strftime('%Y-%m-%d')}/{crypto_mapping[coin]}.csv")
        print(f'Writing to database: {coin}')
        df.to_sql(name='price', con=engine , if_exists='append', index=False)
        time.sleep(2)
