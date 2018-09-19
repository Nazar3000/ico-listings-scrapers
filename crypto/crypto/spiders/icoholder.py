from functools import partial

import scrapy

from ..utils import xpath_exract_first_text, parse_social_link, xpath_tolerant


XPATH_SOCIAL_LINK = ''
XPATH_TITLE = '//div[contains(@class, "logo-name")]//h1'


class IcoholderSpider(scrapy.Spider):
    name = "icoholder"

    def start_requests(self):
        urls = ('https://icoholder.com/en/icos/all',)
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        next_pages = response.xpath('//*[@id="features"]/div/div/div/div/div/div/div/a/@href').extract()

        for next_page in next_pages:
            yield response.follow(next_page, callback=self.parse_ico)

    def parse_ico(self, response):
        xpath_wrap = partial(xpath_exract_first_text, response)
        parse_social_wrap = partial(parse_social_link, response, XPATH_SOCIAL_LINK)
        yield {
            'title': xpath_wrap(XPATH_TITLE),
        }
