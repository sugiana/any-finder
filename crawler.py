import os
from urllib.parse import urlparse
from scrapy import (
    Spider,
    Request,
    )
from scrapy.item import (
    Item,
    Field,
    )
from bukalapak import Parser as Bukalapak
from tokopedia import Parser as Tokopedia
from shopee import Parser as Shopee


class Product(Item):
    title = Field()
    price = Field()
    description = Field()
    image = Field()
    url = Field()
    shop_name = Field()
    shop_url = Field()
    city = Field()
    stock = Field()


class Crawler(Spider):
    name = 'any'
    parser_classes = {
        'www.bukalapak.com': Bukalapak,
        'www.tokopedia.com': Tokopedia,
        'shopee.co.id': Shopee,
        }

    def __init__(
            self, product_url=None, hostname=None, keywords=None, *args,
            **kwargs):
        super().__init__(*args, **kwargs)
        self.product_url = product_url
        self.hostname = hostname
        if product_url:
            # Untuk parsing produk tertentu. Digunakan selama development:
            # ~/env/bin/scrapy runspider laptop.py -O laptop.csv
            # -a product_url=https://...
            if product_url.find('file') == 0:
                filename = product_url[7:]  # Hapus file://
                if os.path.isdir(filename):
                    self.start_urls = [
                        f'file://{filename}/{x}' for x in os.listdir(filename)]
                    self.set_hostname(filename)
                else:
                    self.start_urls = [product_url]
                    if not hostname:
                        tmp_dir = os.path.split(filename)[0]
                        self.set_hostname(tmp_dir)
            else:
                self.start_urls = [product_url]
        elif hostname:
            if not keywords:
                raise Exception('-a keywords=... harus diisi')
            cls = self.get_parser_class()
            url = cls.start_url(keywords)
            self.start_urls = [url]
        else:
            raise Exception(
                '-a product_url=... atau -a hostname=... harus diisi')

    def set_hostname(self, tmp_dir):
        if not self.hostname:
            hostname_dir = os.path.split(tmp_dir)[-2]
            self.hostname = os.path.split(hostname_dir)[-1]

    def parse(self, response):  # Override
        cls = self.get_parser_class(response)
        p = cls(response)
        if response.url.find('file') == 0 or not p.is_product_list():
            yield self.parse_product(response)
        else:
            urls = self.get_product_urls(response)
            for url in urls:
                yield Request(url, callback=self.product_generator)
            if urls:
                yield self.next_page(response)

    def get_parser_class(self, response=None):
        if self.hostname:
            name = self.hostname
        else:
            p = urlparse(response.url)
            name = p.netloc
        return self.parser_classes[name]

    def get_product_urls(self, response) -> list:
        cls = self.get_parser_class(response)
        return cls.get_product_urls(response)

    def product_generator(self, response):
        yield self.parse_product(response)

    def next_page(self, response):
        cls = self.get_parser_class(response)
        url = cls.next_page_url(response)
        if url:
            return Request(url, callback=self.parse)

    def parse_product(self, response) -> dict:
        cls = self.get_parser_class(response)
        p = cls(response)
        d = p.parse()
        d['url'] = p.get_url()
        i = Product()
        for key in d:
            i[key] = d[key]
        return i
