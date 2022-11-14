import sys
import os
from time import sleep
from argparse import ArgumentParser
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from tools import slugify
from tokopedia import Crawler as Tokopedia
from shopee import Crawler as Shopee


tmp_dir = '/tmp'
help_tmp = f'default {tmp_dir}'
start_page = 'auto'
help_start_page = f'default {start_page}'


def nice_filename(url):
    s = urlparse(url).path.lstrip('/').replace('/', '.')
    s = slugify(s)
    return s + '.html'


def mkdir(path):
    if not os.path.exists(path):
        os.mkdir(path)


class App:
    options_class = Options
    parser_classes = {
        'www.tokopedia.com': Tokopedia,
        'shopee.co.id': Shopee,
        }

    def __init__(self, argv=sys.argv[1:]):
        opt = self.options_class()
        pars = self.arg_parser()
        self.option = pars.parse_args(argv)
        name = slugify(self.option.keywords)
        self.keywords_dir = os.path.join(self.option.tmp_dir, name)
        mkdir(self.keywords_dir)
        self.hostname_dir = os.path.join(
                self.keywords_dir, self.option.hostname)
        mkdir(self.hostname_dir)
        self.set_driver(opt)

    def set_driver(self, opt):
        driver_manager = ChromeDriverManager()
        service = Service(driver_manager.install())
        self.driver = webdriver.Chrome(service=service, options=opt)
        self.driver.maximize_window()

    def arg_parser(self):
        pars = ArgumentParser()
        pars.add_argument('--hostname', required=True)
        pars.add_argument('--keywords', required=True)
        pars.add_argument(
            '--start-page', default=start_page, help=help_start_page)
        pars.add_argument('--tmp-dir', default=tmp_dir, help=help_tmp)
        return pars

    def scroll(self, max_count=7, delay=2, height=200):
        x = 0
        while x < max_count:
            script = f'window.scrollTo(0, {height});'
            self.driver.execute_script(script)
            sleep(delay)
            x += 1
            height += height

    def save(self, filename):
        full_path = os.path.join(self.hostname_dir, filename)
        while True:
            try:
                with open(full_path, 'w') as f:
                    f.write(self.driver.page_source)
                    print(f'File {full_path} tersimpan.')
                break
            except OSError as e:
                if e.errno != 36:
                    raise e
                full_path, ext = os.path.splitext(full_path)
                full_path = full_path[:-1]
                full_path = full_path + ext

    def save_products(self, page, product_urls):
        tmp_dir = os.path.join(self.hostname_dir, str(page))
        mkdir(tmp_dir)
        for url in product_urls:
            self.driver.get(url)
            self.scroll(2)
            filename = nice_filename(url)
            filename = os.path.join(tmp_dir, filename)
            self.save(filename)

    def get_start_page(self):
        if self.option.start_page == 'auto':
            pages = [int(page) for page in os.listdir(self.hostname_dir)]
            if not pages:
                return
            pages.sort()
            return pages[-1]
        return int(self.option.start_page)

    def run(self):
        start_page = self.get_start_page()
        cls = self.parser_classes[self.option.hostname]
        p = cls(self.driver)
        url = p.start_url(self.option.keywords, start_page)
        page_urls = []
        product_urls = []
        current_page = p.current_page()
        while True:
            if url in page_urls:
                print(f'{url} terulang.')
                break
            print(f'Product list {url}')
            self.driver.get(url)
            self.scroll()
            if p.is_page_not_found():
                print(f'{url} tidak ada.')
                break
            page_urls.append(url)
            current_page = p.current_page()
            product_urls = p.get_product_urls()
            url = p.next_page_url()
            self.save_products(current_page, product_urls)
        self.driver.quit()


if __name__ == '__main__':
    a = App()
    a.run()
