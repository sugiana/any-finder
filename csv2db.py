import sys
from logging import getLogger
from configparser import ConfigParser
from argparse import ArgumentParser
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from zope.sqlalchemy import register
import transaction
from tools import (
    is_same,
    plain_value,
    )
from models import Product
from logger import setup_logging


default_csv_file = 'all.csv'
help_csv_file = 'default ' + default_csv_file

pars = ArgumentParser()
pars.add_argument('conf')
pars.add_argument('--csv-file', default=default_csv_file, help=help_csv_file)
option = pars.parse_args(sys.argv[1:])

setup_logging(option.conf)
log = getLogger(sys.argv[0])

conf = ConfigParser()
conf.read(option.conf)

db_url = conf.get('main', 'db_url')
engine = create_engine(db_url)
factory = sessionmaker(bind=engine)
db_session = factory()
register(db_session)

df = pd.read_csv(option.csv_file)
base_q = db_session.query(Product)
update_fields = ('title', 'price', 'description', 'image')
for i in df.index:
    url = df['url'][i]
    source = dict(
            url=url, title=df['title'][i], price=float(df['price'][i]),
            description=df['description'][i], image=df['image'][i])
    q = base_q.filter_by(url=url)
    p = q.first()
    target_update = dict()
    target_insert = False
    log_msg = []
    if p:
        target = p.to_dict()
        for field in update_fields:
            source_value = source[field]
            target_value = target[field]
            if is_same(source_value, target_value):
                continue
            target_update[field] = source_value
            log_source_value = plain_value(source_value)
            log_target_value = plain_value(target_value)
            msg = '{f} {t} to be {s}'.format(
                    f=field, t=[log_target_value], s=[log_source_value])
            log_msg.append(msg)
        if target_update:
            target_update['updated'] = datetime.now()
            p.from_dict(target_update)
            msg = ', '.join(log_msg)
            msg = f'{url} UPDATE change {msg}'
            log_func = log.info
        else:
            for field in update_fields:
                source_value = source[field]
                target_update[field] = plain_value(source_value)
            msg = f'{url} already same {target_update}'
            log_func = log.warning
    else:
        p = Product(**source)
        target_insert = True
        msg = f'INSERT {source}'
        log_func = log.info
    if target_insert or target_update:
        with transaction.manager:
            db_session.add(p)
    log_func(msg)
