# -*- coding: utf-8 -*-
import json

import scrapy
from fuzzywuzzy import process
from scrapy.spiders.init import InitSpider

from tropixel.spiders.sinbiota import SinbiotaSpider


class SinbiotachooseSpider(InitSpider, SinbiotaSpider):
    name = "sinbiotachoose"
    allowed_domains = ["sinbiota.biota.org.br"]

    def init_request(self):
        return scrapy.Request('http://sinbiota.biota.org.br/municipality_get_all/',
                       callback=self.parse_municipalities)

    def municipality_input(self):
        municipality_input = raw_input('Please, type in the name of a municipality: ')
        choices = process.extract(
            municipality_input, [item['name'] for item in self.data], limit=5)

        return self.municipality_choice(choices)

    def municipality_choice(self, choices):
        print 'Please choice the most appropriate option:'
        print '0. Enter the name again.'
        for index, (choice, _) in enumerate(choices, start=1):
            print u'{index}. {choice}.'.format(index=index, choice=choice)

        try:
            municipality_choice = int(raw_input('Please type the number: '))
        except ValueError:
            return self.municipality_choice(choices)

        if municipality_choice == 0:
            return self.municipality_input()

        try:
            return [choice for choice, _ in choices][municipality_choice - 1]
        except IndexError:
            print 'Invalid option, please type a number between 1 and {}'.format(
                 len(choices)
            )
            return self.municipality_choice(choices)

    def parse_municipalities(self, response):
        self.data = json.loads(response.body)['data']
        municipality_name = self.municipality_input()
        self.municipality = str([item['id'] for item in self.data if item['name'] == municipality_name][0])
        return self.initialized()
