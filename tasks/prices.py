from datetime import datetime

from requests import get
import pandas as pd
from google.cloud import storage

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
