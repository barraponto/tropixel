# -*- coding: utf-8 -*-
from urlparse import urljoin

import scrapy
from scrapy.http import FormRequest


class SinbiotaSpider(scrapy.Spider):
    name = "sinbiota"
    allowed_domains = ["sinbiota.biota.org.br"]
    root_url = 'http://sinbiota.biota.org.br'
    start_urls = (
        'http://sinbiota.biota.org.br/occurrence/search/',
    )

    def parse(self, response):
        return FormRequest.from_response(
            response,
            formxpath='//form[@id = "occurrence_search_form"]',
            formdata={'search_type': '5', # municipality
                      'municipality': '624'}, # ubatuba
            callback=self.parse_results_page)

    def parse_results_page(self, response):
        for item_url in response.css('.table-striped a::attr("href")').extract():
            yield scrapy.Request(urljoin(self.root_url, item_url), callback=self.parse_item)
        for page_url in response.css('.occurrence_pagination a:nth-child(3)::attr("href")').extract():
            yield scrapy.Request(urljoin(self.root_url, page_url), callback=self.parse_results_page)

    def parse_item(self, response):
        pass
