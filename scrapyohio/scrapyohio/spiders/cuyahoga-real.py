# -*- coding: utf-8 -*-
import csv
import datetime
import os
import sys
from decimal import Decimal

import scrapy
from scrapy import FormRequest
from scrapy.exceptions import CloseSpider

from ohio import settings
from propertyrecords import models, utils
from bs4 import BeautifulSoup


HEADERS = {
    'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    'Accept-Encoding': "gzip, deflate, br",
    'Accept-Language': "es-AR,es;q=0.9,en-US;q=0.8,en;q=0.7,es-419;q=0.6",
    'Cache-Control': "max-age=0",
    'Connection': "keep-alive",
    'Content-Type': "application/x-www-form-urlencoded",
    'Host': "recorder.cuyahogacounty.us",
    'Origin': "https://recorder.cuyahogacounty.us",
    'Referer': "https://recorder.cuyahogacounty.us/searchs/parcelsearchs.aspx",
    'Upgrade-Insecure-Requests': "1",
    'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36",
    'cache-control': "no-cache",
            }

HEADERS.update(settings.CONTACT_INFO_HEADINGS)

payload = "__EVENTTARGET=&__EVENTARGUMENT=&__VIEWSTATE=%2FwEPDwUKLTQ3NzIzMzE3NA9kFgICAw9kFgYCAQ8WAh4EVGV4dGVkAgMPPCsADQEMFCsABQUPMDowLDA6MSwwOjIsMDozFCsAAhYGHwAFBEhvbWUeBVZhbHVlBQExHgtOYXZpZ2F0ZVVybAUCfi9kFCsAAhYGHwAFD1NlYXJjaCBEYXRhYmFzZR8BBQEyHwIFHX4vc2VhcmNocy9nZW5lcmFsc2VhcmNocy5hc3B4FCsABAULMDowLDA6MSwwOjIUKwACFgYfAAUOR2VuZXJhbCBTZWFyY2gfAQUBMx8CBR1%2BL3NlYXJjaHMvZ2VuZXJhbHNlYXJjaHMuYXNweGQUKwACFgYfAAUNUGFyY2VsIFNlYXJjaB8BBQE0HwIFHH4vc2VhcmNocy9wYXJjZWxzZWFyY2hzLmFzcHhkFCsAAhYGHwAFFFZldGVyYW4gR3JhdmUgU2VhcmNoHwEFAjY2HwIFOmh0dHA6Ly9yZWNvcmRlci5jdXlhaG9nYWNvdW50eS51cy92ZXRlcmFuL0dyYXZlU2VhcmNoLmFzcHhkFCsAAhYGHwAFDlByb3BlcnR5IEFsZXJ0HwEFAjYxHwIFNH4vL01lbWJlcnMvTG9naW4uYXNweD9SZXR1cm5Vcmw9JTJmbWVtYmVycyUyZm5vdGlmaWMUKwACBQMwOjAUKwACFgYfAAUOUHJvcGVydHkgQWxlcnQfAQUCNjIfAgVkaHR0cDovL3JlY29yZGVyLmN1eWFob2dhY291bnR5LnVzL01lbWJlcnMvTG9naW4uYXNweD9SZXR1cm5Vcmw9JTJmbWVtYmVycyUyZm5vdGlmaWNhdGlvbm1hbmFnZXIuYXNweGQUKwACFgYfAAUNRmlzY2FsIE9mZmljZR8BBQI3Mh8CBSZodHRwOi8vZmlzY2Fsb2ZmaWNlci5jdXlhaG9nYWNvdW50eS51c2RkAg8PFgIfAAUZDQoJCTxjZW50ZXI%2BwqA8L2NlbnRlcj4NCmRkf9vKGL1V%2B%2FKL93FohlCdJQAAAAA%3D&__VIEWSTATEGENERATOR=B99DED13&__EVENTVALIDATION=%2FwEWBgKXtO2JDQLn5fPPBALa8JHqAgKS0KzHDQK72KCUAgLCqo%2BIBEh%2FUvTvj3m26LhHjPat6rAAAAAA&txtRecStart=12%2F4%2F1800&txtRecEnd=12%2F4%2F2018&ParcelID=00338375&lstQuery=1&ValidateButton=Begin%20Search&undefined="
form_data = {'__EVENTTARGET': '',
             '__EVENTARGUMENT': '',
             '__VIEWSTATE': '/wEPDwUKLTQ3NzIzMzE3NA9kFgICAw9kFgYCAQ8WAh4EVGV4dGVkAgMPPCsADQEMFCsABQUPMDowLDA6MSwwOjIsMDozFCsAAhYGHwAFBEhvbWUeBVZhbHVlBQExHgtOYXZpZ2F0ZVVybAUCfi9kFCsAAhYGHwAFD1NlYXJjaCBEYXRhYmFzZR8BBQEyHwIFHX4vc2VhcmNocy9nZW5lcmFsc2VhcmNocy5hc3B4FCsABAULMDowLDA6MSwwOjIUKwACFgYfAAUOR2VuZXJhbCBTZWFyY2gfAQUBMx8CBR1+L3NlYXJjaHMvZ2VuZXJhbHNlYXJjaHMuYXNweGQUKwACFgYfAAUNUGFyY2VsIFNlYXJjaB8BBQE0HwIFHH4vc2VhcmNocy9wYXJjZWxzZWFyY2hzLmFzcHhkFCsAAhYGHwAFFFZldGVyYW4gR3JhdmUgU2VhcmNoHwEFAjY2HwIFOmh0dHA6Ly9yZWNvcmRlci5jdXlhaG9nYWNvdW50eS51cy92ZXRlcmFuL0dyYXZlU2VhcmNoLmFzcHhkFCsAAhYGHwAFDlByb3BlcnR5IEFsZXJ0HwEFAjYxHwIFNH4vL01lbWJlcnMvTG9naW4uYXNweD9SZXR1cm5Vcmw9JTJmbWVtYmVycyUyZm5vdGlmaWMUKwACBQMwOjAUKwACFgYfAAUOUHJvcGVydHkgQWxlcnQfAQUCNjIfAgVkaHR0cDovL3JlY29yZGVyLmN1eWFob2dhY291bnR5LnVzL01lbWJlcnMvTG9naW4uYXNweD9SZXR1cm5Vcmw9JTJmbWVtYmVycyUyZm5vdGlmaWNhdGlvbm1hbmFnZXIuYXNweGQUKwACFgYfAAUNRmlzY2FsIE9mZmljZR8BBQI3Mh8CBSZodHRwOi8vZmlzY2Fsb2ZmaWNlci5jdXlhaG9nYWNvdW50eS51c2RkAg8PFgIfAAUZDQoJCTxjZW50ZXI+wqA8L2NlbnRlcj4NCmRkf9vKGL1V+/KL93FohlCdJQAAAAA=',
             '__VIEWSTATEGENERATOR': 'B99DED13',
             '__EVENTVALIDATION': '/wEWBgKXtO2JDQLn5fPPBALa8JHqAgKS0KzHDQK72KCUAgLCqo+IBEh/UvTvj3m26LhHjPat6rAAAAAA',
             'txtRecStart': '12/4/1800',
             'txtRecEnd': datetime.datetime.now().strftime('%m/%d/%Y'),
             'lstQuery': '1',
             'ValidateButton': 'Begin Search',
    }

class WarrenSpider(scrapy.Spider):
    name = 'cuyahoga-real'
    allowed_domains = ['recorder.cuyahogacounty.us']

    def retrieve_all_warren_county_urls(self):

        scrape_apts_and_hotels_from_list = True
        continue_where_last_scrape_left_off = False
        seven_days_ago = datetime.datetime.today() - datetime.timedelta(days=7)

        self.cuyahoga_county_object, created = models.County.objects.get_or_create(name="Cuyahoga")

        if continue_where_last_scrape_left_off and scrape_apts_and_hotels_from_list:

            sys.exit("Both variables continue_where_last_scrape_left_off and scrape_apts_and_hotels_from_list cannot be"
                     "true at the same time.")

        if continue_where_last_scrape_left_off:
            self.all_cuyahoga_properties = models.Property.objects.filter(county=self.cuyahoga_county_object,
                                                                        ).exclude(
                                                                    last_scraped_two__gte=seven_days_ago
                                                                    ).order_by('?')

        elif scrape_apts_and_hotels_from_list:
            list_of_parcel_ids = []
            script_dir = os.path.dirname(__file__)  # <-- absolute dir this current script is in
            rel_path = "../scraper_data_drops/cuyahogareal.csv"  # <-- Look two directories up for relevant CSV files
            abs_file_path = os.path.join(script_dir, rel_path)
            with open(abs_file_path, encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile, delimiter=';')
                for number, row in enumerate(reader):
                    list_of_parcel_ids.append(row['PARCEL_ID'])

            self.all_cuyahoga_properties = models.Property.objects.filter(county=self.cuyahoga_county_object,
                                                                          parcel_number__in=list_of_parcel_ids
                                                                          ).order_by('?')
        else:
            self.all_cuyahoga_properties = models.Property.objects.filter(county=self.cuyahoga_county_object,
                                                                          ).order_by('?')
        for item in self.all_cuyahoga_properties:
            yield {'url': "https://recorder.cuyahogacounty.us/searchs/parcelsearchs.aspx", 'parcel_id':
                item.parcel_number}

    def __init__(self, *args, **kwargs):
        self.logged_out = False

    def start_requests(self):
       # Ensure we have a county in the database
        self.warren_county_object, created = models.County.objects.get_or_create(name="Cuyahoga")

        # We want to assign headers for each request triggered. Override the request object
        # sent over to include Lucia's contact information
        for enumerator, package in enumerate(self.retrieve_all_warren_county_urls()):
            form_data['ParcelID'] = package['parcel_id']

            yield FormRequest(
                    url=package['url'],
                    formdata=form_data,
                    method='POST',
                    meta={'page': 1, 'parcel_id': package['parcel_id'], 'cookiejar': enumerator},
                    dont_filter=True,
                    headers=HEADERS,
            )


    def mortgage_processor(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        result = soup.find('span', id='ctl00_ContentPlaceHolder1_label7').get_text()
        no_dollar_sign = result.replace('$', '')
        no_comma = no_dollar_sign.replace(',', '')
        property_object = models.Property.objects.get(parcel_number=response.meta['parcel_id'])
        property_object.mortgage_amount = Decimal(no_comma)
        property_object.save()

    def parse(self, response, *args, **kwargs):
        """

        :param response:
        :return:
        """
        if response.url == 'https://recorder.cuyahogacounty.us/LockedOut.aspx':
            # If we receive this page, it's because our IP address has been blocked!
            raise CloseSpider('ip_address_blocked')

        soup = BeautifulSoup(response.text, 'html.parser')
        property_object = models.Property.objects.get(parcel_number=response.meta['parcel_id'])
        primary_owner = property_object.owner
        try:
            deed_response = utils.parse_recorder_items(soup, primary_owner, 'DEED')
            deed_date = deed_response['date']
            property_object.date_sold = datetime.datetime.strptime(deed_date, '%m/%d/%Y')
        except TypeError:
            pass
        property_object.last_scraped_two = datetime.datetime.now()
        # if deed_date:
        try:
            mortgage_response = utils.parse_recorder_items(soup, primary_owner, 'MORT')
            mortgage_date = mortgage_response['date']
            property_object.date_of_mortgage = datetime.datetime.strptime(mortgage_date, '%m/%d/%Y')

        except TypeError:
            pass
        property_object.save()
        try:
            if mortgage_date is not None:
                    req_num = int(mortgage_response['row']) - 1
                    yield FormRequest.from_response(
                        response,
                        formname="aspnetForm",
                        formxpath="//form[@id='aspnetForm']",
                        formdata={
                                  '__EVENTARGUMENT': f'''Select${req_num}''',
                                  '__EVENTTARGET': 'ctl00$ContentPlaceHolder1$GridView1'},
                        dont_click=True,
                        dont_filter=True,
                        callback=self.mortgage_processor,
                        meta={'parcel_id': response.meta['parcel_id'], 'cookiejar': response.meta['cookiejar']}
                    )
        except UnboundLocalError:
            # No mortgage available
            pass
