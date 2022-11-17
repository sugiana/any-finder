from logging import getLogger
from html.parser import HTMLParser


class HTML2Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.lines = []

    def handle_data(self, data):
        log = getLogger('handle_data')
        s = data.strip()
        if s:
            s = ' '.join(s.split())
            log.debug(s)
            self.lines.append(s)


class Parser:
    def __init__(self, response):
        self.response = response

    @classmethod
    def get_product_urls(cls, response) -> list:  # Override, please
        return []

    @classmethod
    def next_page_url(cls, response) -> str:  # Override, please
        pass

    def get_title(self) -> str:  # Override, please
        pass

    def get_price(self) -> str:  # Override, please
        pass

    def get_url(self) -> str:
        return self.response.url

    def get_info(self, every=2) -> dict:
        lines = []
        for xs in self.response.xpath(self.XPATH_INFO):
            s = xs.extract()
            p = HTML2Text()
            p.feed(s)
            lines += p.lines
        lines = [lines[x:x+every] for x in range(0, len(lines), every)]
        d = dict()
        for t in lines:
            key = t[0]
            val = t[-1]
            key = key.split(':')[0]
            d[key] = val
        return d

    def parse(self) -> dict:
        self.info = self.get_info()
        d = dict()
        d['title'] = self.get_title()
        d['price'] = self.get_price()
        d['image'] = self.get_image()
        d['shop_name'] = self.get_shop_name()
        d['shop_url'] = self.get_shop_url()
        d['city'] = self.get_city()
        d['stock'] = self.get_stock()
        if isinstance(self.XPATH_DESC, str):
            xs = self.response.xpath(self.XPATH_DESC)
            s = xs.extract()[0]
        else:
            s = self.XPATH_DESC()
        p = HTML2Text()
        p.feed(s)
        d['description'] = '\n'.join(p.lines)
        return d
