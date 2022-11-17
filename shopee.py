import json
from urllib.parse import (
    urlparse,
    urlencode,
    parse_qsl,
    )
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from parser import Parser as BaseParser


XPATH_PRODUCT = '//div[contains(@class,"shopee-search-item-result__items")]//a'


class Crawler:
    def __init__(self, driver):
        self.driver = driver
        self.page = 1

    def start_url(self, keywords, page=None):
        d = dict(keyword=keywords)
        if page:
            d['page'] = page
        return 'https://shopee.co.id/search?' + urlencode(d)

    def get_product_urls(self):
        urls = []
        for xs in self.driver.find_elements(By.XPATH, XPATH_PRODUCT):
            url = xs.get_attribute('href')
            if url not in urls:
                urls.append(url)
        return urls

    def current_page(self):
        p = urlparse(self.driver.current_url)
        d = dict(parse_qsl(p.query))
        if 'page' in d:
            # page=1 berarti halaman 2
            return int(d['page']) + 1
        return 1

    def next_page_url(self):
        p = urlparse(self.driver.current_url)
        d = dict(parse_qsl(p.query))
        if 'page' in d:
            page = int(d['page'])
        else:
            page = 0
        page += 1
        d.update(dict(page=page))
        return f'{p.scheme}://{p.netloc}{p.path}?' + urlencode(d)

    def is_page_not_found(self):
        return self.driver.page_source.lower().find('shopee-sort-bar') < 0


XPATH_TITLE = '//title/text()'
XPATH_PRICE = '//div[contains(@class,"items-center")]'\
              '/div[contains(@class,"items-center")]/div/div'
XPATH_URL = '//meta[@property="og:url"]/@content'
XPATH_IMAGE = '//meta[@property="og:image"]/@content'
XPATH_JSON = '//script[@type="application/ld+json"]/text()'
XPATH_INFO = '//div[contains(@class,"product-detail")]/div/div'


class Parser(BaseParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.meta = dict()
        for xs in self.response.xpath(XPATH_JSON):
            s = xs.extract()
            d = json.loads(s)
            if d['@type'] == 'Product':
                self.meta = d
                break

    def parse_desc(self):
        x = self.response.xpath(
                '//div[contains(@class,"product-detail")]/div/div')
        return x[3].xpath('div').extract()[0]

    XPATH_DESC = parse_desc

    def get_info(self):  # Override
        d = dict()
        for xs in self.response.xpath(XPATH_INFO)[1].xpath('div'):
            key = xs.xpath('label/text()').extract()[0]
            for tag in ['div', 'a']:
                val = xs.xpath(f'{tag}/text()').extract()
                if val:
                    val = val[0]
                    break
            d[key] = val
        return d

    def get_title(self) -> str:  # Override
        return self.response.xpath(XPATH_TITLE).extract()[0]

    def get_price(self) -> float:  # Override
        d = self.meta['offers']
        if 'lowPrice' in d:
            s = d['lowPrice']
        else:
            s = d['price']
        return float(s)

    def get_url(self) -> str:  # Override
        return self.response.xpath(XPATH_URL).extract()[0]

    def get_image(self) -> str:  # Override
        return self.response.xpath(XPATH_IMAGE).extract()[0]

    def get_shop_name(self) -> str:
        return self.meta['offers']['seller']['name']

    def get_shop_url(self) -> str:
        return self.meta['offers']['seller']['url']

    def get_city(self) -> str:
        return self.info['Dikirim Dari']

    def get_stock(self) -> int:
        if 'Stok Lain' in self.info:
            s = self.info['Stok Lain']
        else:
            s = self.info['Stok']
        return int(s)
