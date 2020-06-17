from marshmallow import ValidationError
from requests import get
from sqlalchemy import func
from os import environ as env
from datetime import date, datetime

from app import db
from app.models import User, Currency, Transaction as T, Price


def gen_token(user_id):
    user = User.query.get(user_id)
    return user.encode_auth_token()


def validate_currency(curr):
    if curr not in Currency.list_codes():
        raise ValidationError("Invalid currency")


def future_date(at_date):
    now = datetime.now().date()
    if at_date > now:
        raise ValidationError("Date in future")


def calc_holdings(user_id, at_date):
    session = db.session
    buys = session.query(
        T.buy_currency.label("currency"), func.sum(T.buy_amount).label("amount")
    ).filter_by(user_id=user_id)
    sells = session.query(
        T.sell_currency.label("currency"), func.sum(-T.sell_amount).label("amount")
    ).filter_by(user_id=user_id)
    if at_date!=date.today():
        buys = buys.filter(T.date <= at_date.strftime('%Y-%m-%d'))
        sells = sells.filter(T.date <= at_date.strftime('%Y-%m-%d'))
    buys_agg = buys.group_by(T.buy_currency)
    sells_agg = sells.group_by(T.sell_currency)
    buys_sells = buys_agg.union(sells_agg).subquery()
    holdings = session.query(
            buys_sells.c.currency, func.sum(buys_sells.c.amount).label("amount")
        )\
        .group_by(buys_sells.c.currency)\
        .subquery()
    holdings_type = session.query(holdings, Currency.asset_type).join(
        Currency, holdings.c.currency == Currency.cd
    )
    return holdings_type


def get_current_prices():
    all_cryptos = ",".join(Currency.list_codes())
    resp = get(
        url="https://min-api.cryptocompare.com/data/pricemulti",
        params={"fsyms": all_cryptos, "tsyms": "USD", "api_key": env["PRICE_API_KEY"]},
    )
    return resp.json()


def calc_historic_values(holdings, at_date):
    session = db.session
    holdings_sq = holdings.subquery()
    price_filter = (
        session.query(Price)
        .filter(Price.ts == at_date.strftime("%Y-%m-%d"))
        .subquery()
    )
    value_col = holdings_sq.c.amount * price_filter.c.rate
    values = (
        session.query(
            holdings_sq.c.currency,
            holdings_sq.c.amount,
            holdings_sq.c.asset_type,
            price_filter.c.rate.label("price"),
            value_col.label("value"),
        )
        .join(
            price_filter,
            holdings_sq.c.currency == price_filter.c.buy_currency
        )
        .order_by(value_col.desc())
    )
    return values.all()


def calc_current_values(holdings, current_prices):
    values = []
    for currency, amount, asset_type in holdings:
        price = current_prices[currency]['USD']
        value = price * float(amount)
        values.append((currency, amount, asset_type, price, value))
    return values


def calc_metrics(values):
    crypto_value = 0
    fiat_value = 0
    for currency, amount, asset_type, price, value in values:
        if asset_type=='fiat':
            fiat_value+=value
        else:
            crypto_value+=value
    profit = fiat_value + crypto_value
    return {
        'crypto_value': crypto_value,
        'fiat_value': fiat_value,
        'profit': profit
    }
