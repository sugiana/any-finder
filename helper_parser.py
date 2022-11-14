import sys
import os
from argparse import ArgumentParser
from subprocess import call
from glob import glob
from tools import slugify


def run(cmd):
    print(' '.join(cmd))
    if call(cmd) != 0:
        sys.exit()


default_tmp_dir = '/tmp'
help_tmp_dir = 'default ' + default_tmp_dir

pars = ArgumentParser()
pars.add_argument('conf')
pars.add_argument('--tmp-dir', default=default_tmp_dir, help=help_tmp_dir)
pars.add_argument('--keywords', required=True)
option = pars.parse_args(sys.argv[1:])

bin_dir = os.path.split(sys.executable)[0]
scrapy_bin = os.path.join(bin_dir, 'scrapy')

nice_keywords = slugify(option.keywords)
keywords_dir = os.path.join(option.tmp_dir, nice_keywords)
for hostname in os.listdir(keywords_dir):
    hostname_dir = os.path.join(keywords_dir, hostname)
    last_page = 1
    for csv_file in glob(f'{nice_keywords}_{hostname}_*.csv'):
        t = csv_file.split('_')
        page = t[-1].split('.')[0]
        page = int(page)
        if page > last_page:
            last_page = page
    pages = [int(page) for page in os.listdir(hostname_dir)]
    pages.sort()
    for page in pages:
        path = os.path.join(hostname_dir, str(page))
        csv_file = f'{nice_keywords}_{hostname}_{page}.csv'
        log_file = f'{nice_keywords}_{hostname}_{page}.log'
        if os.path.exists(csv_file):
            if page < last_page:
                print(f'{csv_file} sudah ada.')
                continue
            os.remove(csv_file)
            os.remove(log_file)
        cmd = [
                scrapy_bin, 'runspider', 'crawler.py',
                '-a', 'product_url=file://' + path,
                '-O', csv_file,
                '--logfile=' + log_file]
        run(cmd)
        cmd = [
                sys.executable, 'csv2db.py', option.conf,
                '--csv-file=' + csv_file]
        run(cmd)
