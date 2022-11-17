from urllib.parse import (
    quote,
    urlparse,
    parse_qsl,
    urlencode,
    )
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from parser import Parser as BaseParser


XPATH_PRODUCT = '//div[contains(@data-testid,"divProductWrapper")]//a'


class Crawler:
    def __init__(self, driver):
        self.driver = driver
        self.page = 1

    def start_url(self, keywords, page=None):
        d = dict(st='product', q=keywords)
        if page:
            d['page'] = page
        return 'https://www.tokopedia.com/search?' + urlencode(d)

    def get_product_urls(self):
        urls = []
        for xs in self.driver.find_elements(By.XPATH, XPATH_PRODUCT):
            url = xs.get_attribute('href')
            p = urlparse(url)
            if p.netloc != 'www.tokopedia.com':
                continue
            if url not in urls:
                urls.append(url)
        return urls

    def current_page(self):
        p = urlparse(self.driver.current_url)
        d = dict(parse_qsl(p.query))
        if 'page' in d:
            return int(d['page'])
        return 1

    def next_page_url(self):
        p = urlparse(self.driver.current_url)
        d = dict(parse_qsl(p.query))
        if 'page' in d:
            page = int(d['page'])
        else:
            page = 1
        page += 1
        d.update(dict(page=page))
        return f'{p.scheme}://{p.netloc}{p.path}?' + urlencode(d)

    def is_product_list(self):
        return self.driver.page_source.lower().find(
                'dari total') > -1

    def is_page_not_found(self):
        return self.driver.page_source.lower().find(
                'produk nggak ditemukan') > -1


XPATH_TITLE = '//h1/text()'
XPATH_PRICE = '//div[@class="price"]/text()'
XPATH_URL = '//meta[contains(@name,"desktop_url")]/@content'
XPATH_IMAGE = '//meta[@property="og:image"]/@content'
XPATH_SHOP_NAME = '//a[@data-testid="llbPDPFooterShopName"]/h2/text()'
XPATH_CITY = '//h2[contains(@data-unify,"Typography")]/b/text()'
XPATH_STOCK = '//p[@data-testid="stock-label"]/b/text()'


class Parser(BaseParser):
    XPATH_INFO = '//ul[@data-testid="lblPDPInfoProduk"]/li'
    XPATH_DESC = '//div[@data-testid="lblPDPDescriptionProduk"]'

    def get_title(self) -> str:  # Override
        return self.response.xpath(XPATH_TITLE).extract()[0]

    def get_price(self) -> float:  # Override
        s = self.response.xpath(XPATH_PRICE).extract()[0].lstrip('Rp')
        return float(s.replace('.', ''))

    def get_url(self) -> str:  # Override
        return self.response.xpath(XPATH_URL).extract()[0]

    def get_image(self) -> str:  # Override
        return self.response.xpath(XPATH_IMAGE).extract()[0]

    def get_shop_name(self) -> str:
        return self.response.xpath(XPATH_SHOP_NAME).extract()[0]

    def get_shop_url(self) -> str:
        product_url = self.get_url()
        p = urlparse(product_url)
        return 'https://www.tokopedia.com/' + p.path.split('/')[1]

    def get_city(self) -> str:
        s = self.response.xpath(XPATH_CITY).extract()
        if s:
            return s[0]

    def get_stock(self) -> int:
        t = self.response.xpath(XPATH_STOCK).extract()
        return int(t[-1].replace('Sisa ', ''))
