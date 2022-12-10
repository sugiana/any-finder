import json
from urllib.parse import (
    urlparse,
    quote,
    urlencode,
    parse_qsl,
    )
from logging import getLogger
from parser import Parser as BaseParser


QSTRING_KEY = quote('search[keywords]')
XPATH_TITLE = '//h1/text()'
XPATH_PRODUCT = \
        '//div[contains(@class,"bl-flex-container flex-wrap is-gutter-16")]'\
        '/div[contains(@class,"bl-flex-item")]'
XPATH_PRICE_DISC = '//div[contains(@class,"c-product-price -discounted")]'\
                   '/span/text()'
XPATH_PRICE_ORIG = '//div[contains(@class,"c-product-price -original")]'\
                   '/span/text()'
XPATH_IMAGE = '//meta[@property="og:image"]/@content'
XPATH_JSON = '//script[@type="application/ld+json"]/text()'
XPATH_SHOP_URL = '//a[@class="c-avatar"]/@href'
XPATH_CITY = '//a[contains(@class,"c-seller__city")]/text()'
XPATH_EMPTY = '//div[@class="c-main-product__unavailable"]'


class Parser(BaseParser):
    XPATH_INFO = '//table[@class="c-information__table"]/tbody/tr'
    XPATH_DESC = '//div[@class="c-information__description-txt"]'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.meta = dict()
        for xs in self.response.xpath(XPATH_JSON):
            s = xs.extract()
            d = json.loads(s)
            if d['@type'] == 'Product':
                self.meta = d
                break

    @classmethod
    def start_url(self, keywords):
        value = quote(keywords)
        return f'https://www.bukalapak.com/products?{QSTRING_KEY}={value}'

    @classmethod
    def get_product_urls(cls, response) -> list:  # Override
        log = getLogger('get_product_urls()')
        r = []
        for xs in response.xpath(XPATH_PRODUCT):
            url = xs.xpath('observer-tracker/div/div/div/div')
            if not url:
                continue
            url = url[1]
            url = url.xpath('p/a/@href').extract()
            if not url:
                return r
            url = url[0]
            r.append(url)
        return r

    @classmethod
    def next_page_url(cls, response) -> str:  # Override
        p = urlparse(response.url)
        d = dict(parse_qsl(p.query))
        if 'page' in d:
            page = int(d['page'])
        else:
            page = 1
        page += 1
        d.update(dict(page=page))
        return f'{p.scheme}://{p.netloc}{p.path}?' + urlencode(d)

    def is_product_list(self):
        s = self.response.body.lower()
        return s.find(b'hasil pencarian') > -1

    def get_info(self) -> dict:
        return super().get_info(3)

    def get_title(self) -> str:  # Override
        return self.response.xpath(XPATH_TITLE).extract()[0]

    def get_price(self) -> float:  # Override
        xs = self.response.xpath(XPATH_PRICE_DISC)
        if not xs:
            xs = self.response.xpath(XPATH_PRICE_ORIG)
        v = xs.extract()[0]
        v = v.lstrip('Rp').replace('.', '')
        return float(v)

    def get_image(self) -> str:  # Override
        return self.response.xpath(XPATH_IMAGE).extract()[0]

    def get_shop_name(self) -> str:
        return self.meta['offers']['seller']['name']

    def get_shop_url(self) -> str:
        return self.response.xpath(XPATH_SHOP_URL).extract()[0]

    def get_city(self) -> str:
        return self.response.xpath(XPATH_CITY).extract()[0]

    def get_stock(self) -> int:
        if self.response.xpath(XPATH_EMPTY):
            return 0
        return 1
