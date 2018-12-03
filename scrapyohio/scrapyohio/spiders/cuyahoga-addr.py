
import json
import re

import scrapy

from ohio import settings
from propertyrecords import models, utils
from bs4 import BeautifulSoup


HEADERS = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, "
                          "like Gecko) Chrome/70.0.3538.102 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "X-MicrosoftAjax": "Delta=true"
            }

HEADERS.update(settings.CONTACT_INFO_HEADINGS)


class WarrenSpider(scrapy.Spider):
    name = 'cuyahoga-addr'
    allowed_domains = ['treasurer.cuyahogacounty.us']

    def retrieve_all_warren_county_urls(self):
        self.cuyahoga_county_object, created = models.County.objects.get_or_create(name="Cuyahoga")
        # all_cuyahoga_properties = models.Property.objects.filter(county=self.cuyahoga_county_object).order_by('?')[:30]
        all_cuyahoga_properties = models.Property.objects.filter(parcel_number='00338373')
        # all_cuyahoga_properties = models.Property.objects.filter(parcel_number='01312118')
        # all_cuyahoga_properties = models.Property.objects.filter(parcel_number='67111244')

        for property in all_cuyahoga_properties:
            yield f'''https://myplace.cuyahogacounty.us/{utils.convert_string_to_base64_bytes_object(property.parcel_number)}?city={utils.convert_string_to_base64_bytes_object('99')}&searchBy={utils.convert_string_to_base64_bytes_object('Parcel')}&dataRequested={utils.convert_string_to_base64_bytes_object('Tax Bill')}'''

    def __init__(self):
        self.logged_out = False

    def start_requests(self):
       # Ensure we have a county in the database
        self.warren_county_object, created = models.County.objects.get_or_create(name="Cuyahoga")

        # We want to assign headers for each request triggered. Override the request object
        # sent over to include Lucia's contact information
        for url in self.retrieve_all_warren_county_urls():
            yield scrapy.Request(url, dont_filter=True,
                          headers=HEADERS
                          )

    def parse(self, response):
        """

        :param response:
        :return:
        """
        """
        *date_sold - can find, but not super accurate
        !date_of_LLC_name_change - 
        *date_of_mortgage -can find, other site 
        *mortgage_amount -can find, other site  
        school_district - could be other site
        *tax_lien - unknown for both 
        *tax_lien_information_source -- unknown for both  
        !cauv_property -- UNKNOWN 
        """

        tax_addr = response.xpath("//div[@class='TaxBillSummaryHeadingTable']//div[2]//div[2]/text()").extract_first()
        print("This  prop addr is: ", tax_addr)

        # print("RESULT: ", utils.cuyahoga_tax_address_parser(tax_addr))

        import pickle
        pickle.dump(tax_addr, open("save.p", "wb"))
