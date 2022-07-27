import scrapy


class TinhteSpider(scrapy.Spider):
    name = 'tinhte'
    allowed_domains = ['tinhte.vn']
    start_urls = ['http://tinhte.vn/']

    def parse(self, response):
        pass
