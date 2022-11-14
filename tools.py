from datetime import (
    datetime,
    date,
    time as mktime
    )
from decimal import Decimal
import unicodedata
import re


MIDNIGHT_TIME = mktime(0, 0, 0)


def split_time(t):
    if isinstance(t, datetime):
        return t.date(), t.time()
    return t, MIDNIGHT_TIME


def is_same(a, b):
    if a == b:
        return True
    if not (isinstance(a, date) or isinstance(a, datetime)):
        return False
    date_a, time_a = split_time(a)
    date_b, time_b = split_time(b)
    if date_a != date_b:
        return False
    if isinstance(a, date) or isinstance(b, date):
        return True
    if time_a == time_b:
        return True
    return False


def time_str(v):
    return '{y}-{m}-{d} {hh}:{mm}:{ss}'.format(
        d=v.day, m=v.month, y=v.year, hh=v.hour, mm=v.minute, ss=v.second)


def plain_value(v):
    if isinstance(v, str):
        return v
    if isinstance(v, datetime):
        return time_str(v)
    if isinstance(v, date):
        return date_str(v)
    if isinstance(v, Decimal):
        return float(v)
    return v


def plain_values(d):
    r = dict()
    for key in d:
        v = d[key]
        r[str(key)] = plain_value(v)
    return r


# https://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename
def slugify(value, allow_unicode=False):
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).\
                encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')
