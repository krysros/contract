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


def fmt_currency(c):
    return format_currency(c, "PLN", locale="pl_PL")


def slownie(v):
    return slownie_zl100gr(v)


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


def final(tasks, delta=30):
    return end(tasks) + datetime.timedelta(delta)


def total(tasks):
    total = 0
    for task in tasks:
        total += task['value']
    return total


def factor(tasks, c=0.05):
    return c * total(tasks)
