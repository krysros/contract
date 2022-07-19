import datetime
from babel.numbers import format_currency
from babel.dates import (
    format_date,
    format_datetime,
)
from slownie import slownie_zl100gr


def fmt_datetime(dt):
    return format_datetime(dt, format="dd.MM.YYYY", locale="pl_PL")


def fmt_date(d):
    return format_date(d, format="long", locale="pl_PL")


def fmt_currency(number):
    return format_currency(number, "PLN", locale="pl_PL")


def delta(dt, days=30):
    return dt + datetime.timedelta(days)


def slownie(amount):
    return slownie_zl100gr(amount)


def begin(tasks):
    dates = []
    for task in tasks:
        dates.append(task['begin'])
    return min(dates)


def end(tasks):
    dates = []
    for task in tasks:
        dates.append(task['end'])
    return max(dates)


def total(tasks):
    total = 0
    for task in tasks:
        total += task['value']
    return total
