from tempfile import NamedTemporaryFile
from datetime import datetime, timedelta, date
from os import environ as env

from requests import get
from sqlalchemy import create_engine
from argparse import ArgumentParser

import pandas as pd
from google.cloud import storage

from tasks.currency_mapping import crypto_mapping, fiat_mapping
from app.models import Price
from app import db


def call_crypto_api(coin, start_dt, end_dt):
    start_unix = int(start_dt.timestamp() * 1000)
    end_unix = int(end_dt.timestamp() * 1000)
    resp = get(
        url=f"http://api.coincap.io/v2/assets/{coin}/history",
        params={"interval": "d1", "start": start_unix, "end": end_unix},
    )
    return resp.json()


def call_fiat_api(currency, start_dt, end_dt):
    resp = get(
        url="https://api.exchangeratesapi.io/history",
        params={
            "start_at": start_dt.strftime("%Y-%m-%d"),
            "end_at": end_dt.strftime("%Y-%m-%d"),
            "symbols": currency,
            "base": "USD",
        },
    ).json()
    return resp


def load_gcs(bucket, local_path, remote_path):
    client = storage.Client()
    bucket = client.get_bucket(bucket)
    blob = bucket.blob(remote_path)
    blob.upload_from_filename(filename=local_path)


def transform_crypto(data, coin, coin_mapping):
    df = pd.DataFrame(data)
    df.drop(labels="time", axis=1, inplace=True)
    df["buy_currency"] = coin_mapping[coin]
    df["sell_currency"] = "USD"
    df.rename(columns={"date": "ts", "priceUsd": "rate"}, inplace=True)
    df = df.astype(
        {
            "ts": "datetime64",
            "buy_currency": "str",
            "sell_currency": "str",
            "rate": "float",
        }
    )
    df = df[["ts", "buy_currency", "sell_currency", "rate"]]
    return df


def transform_fiat(data, currency):
    records = []
    rates = data["rates"]
    if rates == {}:
        last_price = (
            db.session.query(Price)
            .filter(Price.buy_currency == currency)
            .order_by(Price.ts.desc())
            .first()
        )
        df = pd.DataFrame(
            [
                {
                    "ts": datetime.strptime(data["start_at"], "%Y-%m-%d"),
                    "buy_currency": currency,
                    "sell_currency": "USD",
                    "rate": last_price.rate,
                }
            ]
        )
        return df
    for date, rate_pair in rates.items():
        for currency, rate in rate_pair.items():
            ts = datetime.strptime(date, "%Y-%m-%d")
            records.append(
                {
                    "ts": ts,
                    "buy_currency": currency,
                    "sell_currency": "USD",
                    "rate": float(rate),
                }
            )
    df = pd.DataFrame(records)
    return df


yesterday = date.today() + timedelta(days=-1)
default_date = datetime.combine(yesterday, datetime.min.time())

parser = ArgumentParser(
    description="Get crypto & fiat prices for the given date, transform and write to cloud storage and DB."
)
parser.add_argument(
    "--date",
    type=lambda s: datetime.strptime(s, "%Y-%m-%d"),
    default=default_date,
    help="The date to get prices for in YYYY-MM-DD format.",
    dest="date",
)
parser.add_argument(
    "--crypto-codes",
    nargs="*",
    default=crypto_mapping.keys(),
    help="The list of crypto codes to get prices for.",
    dest="crypto_codes",
)
parser.add_argument(
    "--fiat-codes",
    nargs="*",
    default=fiat_mapping.values(),
    help="The list of fiat codes to get prices for.",
    dest="fiat_codes",
)
args = parser.parse_args()

start_dt = args.date
bucket = env["BUCKET"]
engine = create_engine(
    f"postgres://{env['PGUSER']}:{env['PGPASSWORD']}@{env['PGHOST']}:5432/{env['PGDATABASE']}"
)

for coin in args.crypto_codes:
    print(f"Querying API: {coin}")
    raw = call_crypto_api(coin=coin, start_dt=start_dt, end_dt=start_dt + timedelta(days=1))
    print(f"Transforming: {coin}")
    df = transform_crypto(data=raw["data"], coin=coin, coin_mapping=crypto_mapping)
    with NamedTemporaryFile("w") as fp:
        print(f"Writing CSV: {coin}")
        df.to_csv(fp.name)
        print(f"Uploading to GCS: {coin}")
        load_gcs(
            bucket,
            fp.name,
            f"{start_dt.strftime('%Y-%m-%d')}/{crypto_mapping[coin]}.csv",
        )
    print(f"Writing to database: {coin}")
    df.to_sql(name="price", con=engine, if_exists="append", index=False)

for currency in args.fiat_codes:
    print(f"Querying API: {currency}")
    data = call_fiat_api(currency, start_dt, start_dt)
    print(f"Transforming: {currency}")
    df = transform_fiat(data, currency)
    with NamedTemporaryFile("w") as fp:
        print(f"Writing csv: {currency}")
        df.to_csv(fp.name)
        print(f"Uploading to GCS: {currency}")
        load_gcs(bucket, fp.name, f"{start_dt.strftime('%Y-%m-%d')}/{currency}.csv")
    print(f"Writing db: {currency}")
    df.to_sql(name="price", con=engine, if_exists="append", index=False)
