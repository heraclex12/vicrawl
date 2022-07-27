import scrapy


class VozSpider(scrapy.Spider):
    name = 'voz'
    allowed_domains = ['voz.vn']
    start_urls = ['http://voz.vn/']

    def parse(self, response):
        pass
