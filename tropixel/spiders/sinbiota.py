# -*- coding: utf-8 -*-
import json

import scrapy
import scrapylib.processors
from purl import URL
from scrapy.http import FormRequest
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Identity, TakeFirst, Join, MapCompose, SelectJmes
from scrapy.spiders import CrawlSpider, Rule

class GetURLParam(object):
    def __init__(self, param):
        self.param = param
    def __call__(self, value):
        return URL(value).query_param(self.param)


class SinbiotaItemLoader(ItemLoader):
    default_item_class = dict
    default_input_processor = scrapylib.processors.default_input_processor
    default_output_processor = TakeFirst()
    habitats_out = Identity()
    microhabitats_out = Identity()
    keywords_out = Identity()
    taxonomic_groups_out = Identity()
    ecosystems_out = Identity()
    project_out = Join()
    geo_in = MapCompose(GetURLParam('center'))
    taxonomies_in = MapCompose(json.loads, SelectJmes(
        '{name: taxonomic_classification, id: taxon_id}'))
    taxonomies_out = Identity()


class SinbiotaSpider(CrawlSpider):
    name = 'sinbiota'
    allowed_domains = ['sinbiota.biota.org.br']
    search_url = 'http://sinbiota.biota.org.br/occurrence/search/'
    municipality = '624' # ubatuba

    rules = (
        # Follow pagination links, set priority to avoid search expiring.
        Rule(LinkExtractor(restrict_css='.occurrence_pagination a:nth-child(3)'),
             follow=True, process_request='set_pagination_priority'),
        # Visit every occurence url to get the data.
        Rule(LinkExtractor(restrict_css='.table-striped a'),
             callback='parse_item'),
    )

    def set_pagination_priority(self, request):
        request.priority = 100
        return request

    def start_requests(self):
        # Kickoff by loading the search form, let parse_search fill that form.
        return [scrapy.Request(self.search_url, callback=self.parse_search)]

    def parse_search(self, response):
        # Perform a search and let CrawlSpider.parse take over from here.
        return FormRequest.from_response(
            response,
            formxpath='//form[@id = "occurrence_search_form"]',
            formdata={'search_type': '5', # municipality
                      'municipality': self.municipality})

    def parse_item(self, response):
        loader = SinbiotaItemLoader(response=response)
        loader.add_value('url', response.url)

        fields = {
            # occurrence details
            'date': 'Date',
            'method': 'Method',
            'description': 'Description',
            'additional_observations': 'Additional observations',
            # occurrence author
            'name': 'Name',
            'address': 'Address',
            'institution': 'Institution',
            'website': 'Website',
            'reference': 'Reference',
            'date_and_user': 'Date & user',
            # location
            'municipality': 'Municipality',
            'location': 'Location',
            'environment': 'Environment',
            'conservation_unit': 'Conservation unit',
            'basin': 'Basin',
            'gps_precision': 'GPS Precision',
            'occurrence_precision': 'Occurrence Precision',
            'occurence_extension': 'Occurrence Extension',
            'ecosystems': 'Ecosystems',
            'habitats': 'Habitats',
            'microhabitats': 'Microhabitats',
            # taxonomic information
            'taxonomic_groups': 'Taxonomic Groups',
            'content': 'Content',
            # additional data for aquaric environment
            'temperature': u'Temperature (°C)',
            'conductivity': u'Conductivity (µS/cm)',
            'dissolved_oxygen': 'Dissolved Oxygen (mg/l)',
            'secchi_disk': 'Secchi Disk (m)',
            'ph': 'pH',
            'salinity': 'Salinity',
            'turbidity': 'Turbidity',
            'river_order': 'River Order',
        }
        content_cell_xpath = u'//th[text()="{label}"]/following-sibling::td/text()'
        for field_name, field_label in fields.iteritems():
            loader.add_xpath(field_name,
                             content_cell_xpath.format(label=field_label))

        link_fields = {
            # occurrence details
            'keywords': 'Keywords',
            'project': 'Project',
        }
        content_link_xpath = u'//th[text()="{label}"]/following-sibling::td/a/text()'
        for field_name, field_label in link_fields.iteritems():
            loader.add_xpath(field_name,
                             content_link_xpath.format(label=field_label))

        content_url_xpath = u'//th[text()="{label}"]/following-sibling::td/a/@href'
        loader.add_xpath('project_url',
                            content_url_xpath.format(label='Project'))

        # Get the coordinates from Google Maps image
        loader.add_css('geo', 'img[src^="http://maps.googleapis.com"]::attr("src")')

        # Get the taxonomic data from embedded javascript
        loader.add_value('taxonomies',
                         response.xpath('//script[contains(., "SpecimenArray")]').extract_first().splitlines()[1][28:])

        return loader.load_item()
