# -*- coding: utf-8 -*-
import scrapy


class CisuspSpider(scrapy.Spider):
    name = "cisusp"
    allowed_domains = ["nadd.prp.usp.br"]
    url_template = 'http://www.nadd.prp.usp.br/cis/DetalheBancoDados.aspx?cod=B{item_number}'


    def start_requests(self):
        return [scrapy.Request(self.url_template.format(item_number=n))
                for n in range(999)]

    def parse(self, response):
        if response.css('h3.subtitulo'):
            yield {'url': response.url}
        elif not response.url.endswith('a'):
            yield scrapy.Request(response.url+'a')
