import scrapy

from ...utils import xpath_exract_first_text

XPATH_TITLE = '//*[@class="main-container"]//h1[@class="h2"]'
XPATH_MEMBER = '//*[@id="tab-team"]//div[contains(@class, "card-body")]'
XPATH_LINKEDIN_LINK = '//a[contains(@href, "linkedin.com")]/@href'

MAX_PAGE = 163


class TrackicoSpider(scrapy.Spider):
    name = "trackico_members"

    def start_requests(self):
        urls = ('https://www.trackico.io/{}/'.format(i) for i in range(1, MAX_PAGE + 1))
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        next_pages = response.css(
            '.row.equal-height .col-md-6.col-xl-4 a::attr(href)'
        ).extract()
        for next_page in next_pages:
            yield response.follow(next_page, callback=self.parse_ico)

    def parse_ico(self, response):
        ico_title = xpath_exract_first_text(response, XPATH_TITLE)

        members_links = response.xpath(XPATH_MEMBER + '/h5/a/@href').extract()[:3]
        members_names = response.xpath(XPATH_MEMBER + '/h5/a/text()').extract()[:3]
        members_postions = response.xpath(XPATH_MEMBER + '/span[text() != "\n"]/text()').extract()[:3]

        for link, name, position in zip(members_links, members_names, members_postions):
            yield response.follow(
                link,
                callback=self.parse_member,
                meta={
                    'ico_title': ico_title,
                    'member_name': name.replace('\n', '').lower(),
                    'member_position': position
                }
            )

    def parse_member(self, response):
        yield {
            'ico_title': response.meta['ico_title'],
            'member_name': response.meta['member_name'],
            'member_position': response.meta['member_position'],
            'member_linkedin_link': response.xpath(XPATH_LINKEDIN_LINK).extract_first(),
        }
