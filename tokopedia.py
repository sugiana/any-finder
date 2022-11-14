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
XPATH_NEXT = '//button[@aria-label="Laman berikutnya"]'
XPATH_IMAGE = '//meta[@property="og:image"]/@content'


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


class Parser(BaseParser):
    XPATH_INFO = '//ul[@data-testid="lblPDPInfoProduk"]/li'
    XPATH_DESC = '//div[@data-testid="lblPDPDescriptionProduk"]'

    def get_title(self) -> str:  # Override
        return self.response.xpath(XPATH_TITLE).extract()[0]

    def get_price(self) -> str:  # Override
        s = self.response.xpath(XPATH_PRICE).extract()[0].lstrip('Rp')
        return s.replace('.', '')

    def get_url(self) -> str:  # Override
        return self.response.xpath(XPATH_URL).extract()[0]

    def get_image(self) -> str:  # Override
        return self.response.xpath(XPATH_IMAGE).extract()[0]
