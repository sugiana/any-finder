import sys
from argparse import ArgumentParser
from configparser import ConfigParser
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import transaction
from zope.sqlalchemy import register
from models import (
    Product,
    Wilayah,
    )


cities = [
    'bandung',
    'banjar',
    'bekasi',
    'blitar',
    'bogor',
    'cirebon',
    'kediri',
    'madiun',
    'magelang',
    'malang',
    'mojokerto',
    'pasuruan',
    'probolinggo',
    'semarang',
    'serang',
    'tangerang',
    'tasikmalaya',
    'tegal',
    ]
cities_convertion = {
    'gunung kidul': 'gunungkidul',
    'kota surakarta (solo)': 'surakarta',
    'solo': 'surakarta',
    }
cache = dict()


def real_name(s):
    t = s.split('-')
    s = t[0].rstrip()
    if s in cities_convertion:
        r = cities_convertion[s]
        return r, Wilayah.nama
    if s in cities:
        return 'kota ' + s, Wilayah.nama_lengkap
    if s.find('jakarta') == 0:
        r = 'adm. ' + s
        return r, Wilayah.nama
    if s.find('kota jakarta') == 0:
        t = s.split()
        r = 'adm. ' + ' '.join(t[1:])
        return r, Wilayah.nama
    if s.find('kab.') == 0:
        t = s.split('kab.')
        r = 'kabupaten ' + t[1].lstrip()
        return r, Wilayah.nama_lengkap
    if s.find('kota ') == 0:
        return s, Wilayah.nama_lengkap
    return s, Wilayah.nama


pars = ArgumentParser()
pars.add_argument('conf')
option = pars.parse_args(sys.argv[1:])

conf = ConfigParser()
conf.read(option.conf)

db_url = conf.get('main', 'db_url')
engine = create_engine(db_url)
factory = sessionmaker(bind=engine)
db_session = factory()
register(db_session)

base_q_wilayah = db_session.query(Wilayah).filter_by(tingkat_id=2)
q = db_session.query(Product).filter(
        Product.city.__ne__(None),
        Product.wilayah_id.__eq__(None))
q = q.order_by(Product.id)
while True:
    p = q.first()
    if not p:
        break
    city, field = real_name(p.city.lower())
    if city in cache:
        w = cache[city]
    else:
        if field == Wilayah.nama:
            q_wilayah = base_q_wilayah.filter(field.ilike(city))
        else:
            pola = f'{city},%'
            q_wilayah = base_q_wilayah.filter(field.ilike(pola))
        wilayah_list = []
        for w in q_wilayah:
            wilayah_list.append(f'{w.id} {w.nama_lengkap}')
        if wilayah_list[1:]:
            print(f'City {city} ada {len(wilayah_list)}:')
            for w in wilayah_list:
                print(w)
            raise Exception('Perbaiki script.')
        w = q_wilayah.first()
        if not w:
            raise Exception(f'City {city} belum dipahami, perbaiki script.')
        cache[city] = w
    print(f'ID {p.id} city {p.city} -> {w.nama_lengkap} ({w.id})')
    p.wilayah_id = w.id
    with transaction.manager:
        db_session.add(p)
