# -*- coding: utf-8 -*-
import datetime
import decimal
import re

import pytz
import scrapy
from bs4 import BeautifulSoup
from scrapy import FormRequest

from ohio import settings
from propertyrecords import utils, models


class FranklinSpider(scrapy.Spider):
    handle_httpstatus_all = True
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, "
                      "like Gecko) Chrome/70.0.3538.102 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "X-MicrosoftAjax": "Delta=true"
    }

    name = 'franklin'
    allowed_domains = ['recorder.franklincountyohio.gov/']
    start_urls = ['https://countyfusion5.kofiletech.us/countyweb/login.do?countyname=Franklin']

    def retrieve_all_franklin_county_urls(self):
        self.please_parse_these_items = models.Property.objects.filter(county=self.franklin_county_object).all()

        for item in self.please_parse_these_items:
            yield item.parcel_number

    def __init__(self):
        self.HEADERS.update(settings.CONTACT_INFO_HEADINGS)
        self.logged_out = False


    def log_in_function(self):
       result_of_form_request= FormRequest(url="https://countyfusion5.kofiletech.us/countyweb/login.do?countyname=Franklin",
                            formdata={
                                "cmd": "login",
                                "countyname": "Franklin",
                                "scriptsupport": "yes",
                                "apptype": "",
                                "datasource": "",
                                "userdatasource": "",
                                "fraudsleuth": "false",
                                "guest": "true",
                                "public": "false",
                                "startPage": "",
                                "CountyFusionForceNewSession": "true",
                                "username": "",
                                "password":""
                            },
                            )




    def start_requests(self):

        # LOG IN
        return scrapy.FormRequest.from_response(
            response,
            formdata={'username': 'john', 'password': 'secret'},
            callback=self.after_login
        )

        # LATER ON ASSERT CHECK


        # Ensure we have a county in the database
        self.franklin_county_object, created = models.County.objects.get_or_create(name="Franklin")
        # We want to assign headers for each request triggered. Override the request object
        # sent over to include Lucia's contact information
        # for parameter_dictionary in self.retrieve_all_franklin_county_urls():

        # Use the enumerator function to allow an individual cookie jar for each request
        # This is necessary to keep track of multiple view states
        for enumerator, item in enumerate(self.retrieve_all_franklin_county_urls()):
            return scrapy.FormRequest.from_response(
                url='https://countyfusion5.kofiletech.us/countyweb/login.do?countyname=Franklin',
                response,
                formdata={'username': 'john', 'password': 'secret'},
                callback=self.after_login
            )



            #     scrapy.Request(
            #     url='https://countyfusion5.kofiletech.us/countyweb/login.do?countyname=Franklin',
            #     method='GET',
            #     callback=self.parse,
            #     meta={'dont_redirect': False, "parc_id": item,
            #           'spider_num': enumerator, 'cookiejar': enumerator},
            #     dont_filter=True,
            #     headers=self.HEADERS
            # )

    # def retrieve_info_to_parse(self, response):
    #     print("PARSING: ", response.meta['parc_id'])
    #
    # def parse(self, response):
    #     """
    #
    #     :param response:
    #     :return:
    #     """
    #     yield FormRequest.from_response(
    #         response,
    #         formdata={
    #             'inpParid': response.meta['parc_id']},
    #             meta={"parc_id": response.meta['parc_id'],
    #                         'spider_num': response.meta['spider_num'], 'cookiejar': response.meta['spider_num']
    #                         },
    #                 dont_filter=True,
    #         callback=self.retrieve_info_to_parse,
    #     )
