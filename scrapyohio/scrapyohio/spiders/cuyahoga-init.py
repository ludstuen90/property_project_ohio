# -*- coding: utf-8 -*-
import json

import scrapy

from ohio import settings
from propertyrecords import models


HEADERS = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, "
                          "like Gecko) Chrome/70.0.3538.102 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "X-MicrosoftAjax": "Delta=true"
            }

HEADERS.update(settings.CONTACT_INFO_HEADINGS)


class WarrenSpider(scrapy.Spider):
    name = 'cuyahoga-init'
    allowed_domains = ['co.warren.oh.us', 'oh3laredo.fidlar.com']

    def retrieve_all_warren_county_urls(self):
        self.cuyahoga_county_object, created = models.County.objects.get_or_create(name="Cuyahoga")

        for x in range(0, 1000):
            for y in range(0, 100):
                print(f'''https://myplace.cuyahogacounty.us/MyPlaceService.svc/SingleSearchParcel/{x}{y}?city=99''')
                yield f'''https://myplace.cuyahogacounty.us/MyPlaceService.svc/SingleSearchParcel/{str(x).zfill(3)}{str(y).zfill(2)}?city=99'''


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
        remove_quotation_marks = response.text[1:][:-1]
        remove_slashes = str(remove_quotation_marks).replace('\\', '')
        response_json = json.loads(remove_slashes)

        for item in response_json[0]:
            item_number = item['returndata'].split('|')[0][:-1]
            property_item, created = models.Property.objects.get_or_create(parcel_number=item_number,
                                                                           county=self.cuyahoga_county_object)
            property_item.save()
