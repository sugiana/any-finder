import sys
from configparser import ConfigParser
from argparse import ArgumentParser
from sqlalchemy import create_engine
from models import Base


pars = ArgumentParser()
pars.add_argument('conf')
option = pars.parse_args(sys.argv[1:])

conf = ConfigParser()
conf.read(option.conf)

db_url = conf.get('main', 'db_url')
engine = create_engine(db_url)
Base.metadata.create_all(engine)
