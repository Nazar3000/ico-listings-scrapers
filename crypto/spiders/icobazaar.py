import scrapy

from crypto.items import load_organization
from crypto.utils import to_common_format, xpath_exract_first_text

XPATHS = {
    # general
    'NAME': '//*[@id="ico-profile"]/div[1]/div[1]/div/div[2]/h1/text()',
    'SITE': '//*[@id="ico-profile"]/div[1]/div[1]/div/div[2]/ul/li/a[text()[contains(., "Website")]]/@href',
    'WHITEPAPER': '//*[@id="ico-profile"]/div[1]/div[1]/div/div[2]/ul/'
                  'li/a[text()[contains(., "Whitepaper")]]/@href',

    # social link
    'SOCIAL_LINK': '//div[@class="com-sidebar__socialbar"]//a/@href[contains(., "{href_contains}")]',

    # statistics
    'HARDCAP': '//div[@class="com-sidebar__info"]//div[span[contains(., "Cap")]]/child::span[2]/text()',

    # dates
    'ICO_DATE_RANGE': '//div[@class="com-sidebar__info"]//div[span[contains(., "Public sale")]]/child::span[2]',

    # extra
    'DESCRIPTION': '//*[@id="ico-profile"]/div[1]/div[1]/div/div[2]/p/text()',
    # 'GOAL': '/html/body/div[1]/main/div/div/div[2]/div[1]/div/'
    #         'div/div[span[contains(., "Goal")]]/child::span[2]/text()',
    'RATING': '/html/body/div[1]/main/div/div/div[2]/div[1]/div/div[2]/div[1]/text()',
    # 'STATUS': '/html/body/div[1]/main/div/div/div[2]/div[1]/div/div/'
    #           'div[span[contains(., "Status")]]/child::span[2]/span/text()',
    'TOKEN_PRICE': '/html/body/div[1]/main/div/div/div[2]/div[1]/'
                   'div/div/div[span[contains(., "Price")]]/child::span[2]',
    'UPDATED': '//*[@id="ico-profile"]/div[1]/div[1]/div/div[2]/div/span/text()',

    # rating
    'ICOBAZAAR_RATING': '//*[@class="ico-rating__count"]/text()',
    'ICOBAZAAR_SITE_RATING': '//*[@class="ico-rating-details"]//li[contains(., "Site")]'
                             '/div[@class="ico-rating-details__count"]/text()',
    'ICOBAZAAR_TEAM_RATING': '//*[@class="ico-rating-details"]//li[contains(., "Team")]'
                             '/div[@class="ico-rating-details__count"]/text()',
    'ICOBAZAAR_IDEA_RATING': '//*[@class="ico-rating-details"]//li[contains(., "Idea")]'
                             '/div[@class="ico-rating-details__count"]/text()',
    'ICOBAZAAR_TECH_RATING': '//*[@class="ico-rating-details"]//li[contains(., "Tech")]'
                             '/div[@class="ico-rating-details__count"]/text()',
    'ICOBAZAAR_MEDIA_RATING': '//*[@class="ico-rating-details"]//li[contains(., "Media")]'
                             '/div[@class="ico-rating-details__count"]/text()',
    'ICOBAZAAR_USERS_RATING': '//*[@class="ico-rating-details"]//li[contains(., "Users")]'
                              '/div[@class="ico-rating-details__count"]/text()',

}

MAX_PAGE = 31


def dates_from_range(date_range):
    return (
        to_common_format(d.strip(), ['%d %b`%y'])
        for d in date_range.split('-')
    )


class IcobazaarSpider(scrapy.Spider):
    name = "icobazaar"

    def start_requests(self):
        urls = ('https://icobazaar.com/v2/ico-list?page={}'.format(i) for i in range(1, MAX_PAGE + 1))
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        next_pages = response.xpath('//div[contains(@class, "ico")]/a[@class="ico-link"]/@href').extract()
        names = response.xpath('//div[contains(@class, "ico")]/h5/text()').extract()
        for next_page, name in zip(next_pages, names):
            yield response.follow(next_page, callback=self.parse_ico, meta={'name': name})

    def parse_ico(self, response):
        ico_date_range = xpath_exract_first_text(response, XPATHS['ICO_DATE_RANGE'])

        ico_date_range_from = ico_date_range_to = ''

        if ico_date_range:
            ico_date_range_from, ico_date_range_to = dates_from_range(ico_date_range)

        return load_organization(response, XPATHS, context={
            'name': response.meta['name'],
            'source': self.name,
            'ico_date_range_from': ico_date_range_from,
            'ico_date_range_to': ico_date_range_to,
            'total_ico_date_range_from': ico_date_range_from,
            'total_ico_date_range_to': ico_date_range_to,
        })
