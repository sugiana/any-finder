import sys
import os
from urllib.parse import urlparse
from datetime import (
    datetime,
    timedelta,
    )
from time import sleep
from configparser import ConfigParser
from argparse import ArgumentParser
from subprocess import call
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from zope.sqlalchemy import register
from models import Product


class Browser:
    def __init__(self):
        opt = Options()
        driver_manager = ChromeDriverManager()
        service = Service(driver_manager.install())
        self.driver = webdriver.Chrome(service=service, options=opt)
        self.driver.maximize_window()

    def scroll(self, max_count=7, delay=2, height=200):
        x = 0
        while x < max_count:
            script = f'window.scrollTo(0, {height});'
            self.driver.execute_script(script)
            sleep(delay)
            x += 1
            height += height

    def save(self, url, filename):
        self.driver.get(url)
        self.scroll(2)
        with open(filename, 'w') as f:
            f.write(self.driver.page_source)


def run(cmd):
    print(' '.join(cmd))
    if call(cmd) != 0:
        sys.exit()


pars = ArgumentParser()
pars.add_argument('conf')
option = pars.parse_args(sys.argv[1:])

use_scrapy = ['www.bukalapak.com']
bin_dir = os.path.split(sys.executable)[0]
scrapy_bin = os.path.join(bin_dir, 'scrapy')

br = None

conf = ConfigParser()
conf.read(option.conf)

db_url = conf.get('main', 'db_url')
engine = create_engine(db_url)
factory = sessionmaker(bind=engine)
db_session = factory()
register(db_session)

tgl = datetime.now() - timedelta(30)

q = db_session.query(Product).filter(Product.updated < tgl)
for product in q:
    p = urlparse(product.url)
    if p.netloc in use_scrapy:
        cmd = [
                scrapy_bin, 'runspider', 'crawler.py',
                '-a', f'product_url={product.url}',
                '-O', '/tmp/output.csv']
        run(cmd)
    else:
        if not br:
            br = Browser()
        print(f'Browser {product.url}')
        br.save(product.url, '/tmp/output.html')
        cmd = [
                scrapy_bin, 'runspider', 'crawler.py',
                '-a', f'product_url=file:///tmp/output.html',
                '-a', f'hostname={p.netloc}',
                '-O', '/tmp/output.csv']
        run(cmd)
    cmd = [
            sys.executable, 'csv2db.py', option.conf,
            '--csv-file=/tmp/output.csv']
    run(cmd)
if br:
    br.driver.quit()
