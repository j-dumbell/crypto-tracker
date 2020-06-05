from tempfile import NamedTemporaryFile
from datetime import datetime, timedelta, date
from os import environ as env
from argparse import ArgumentParser

from sqlalchemy import create_engine

from tasks.currency_mapping import crypto_mapping, fiat_mapping
from tasks.prices import call_crypto_api, call_fiat_api, transform_fiat, transform_crypto, load_gcs


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
