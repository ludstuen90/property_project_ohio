# -*- coding: utf-8 -*-

import scrapy
from bs4 import BeautifulSoup
from scrapy.utils.response import open_in_browser

from ohio import settings
from propertyrecords import utils, models


class MontgomerySpider(scrapy.Spider):
    handle_httpstatus_all = True
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, "
                      "like Gecko) Chrome/70.0.3538.102 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "X-MicrosoftAjax": "Delta=true"
    }

    name = 'montgomerycourts'
    allowed_domains = ['clerk.co.montgomery.oh.us']

    def retrieve_all_montgomery_county_urls(self):

        self.montgomery_county_object, created = models.County.objects.get_or_create(name="Montgomery")
        #self.please_parse_these_items = models.Property.objects.filter(county=self.montgomery_county_object).all()
        self.please_parse_these_items = models.Property.objects.filter(id=1103731)

        for item in self.please_parse_these_items:
            yield item.parcel_number

    def __init__(self):
        self.HEADERS.update(settings.CONTACT_INFO_HEADINGS)
        self.logged_out = False

    def start_requests(self):
        for enumerator, item in enumerate(self.retrieve_all_montgomery_county_urls()):
            print("looking at parcel number: ", item)

            yield scrapy.Request(
                url=f'''http://www.clerk.co.montgomery.oh.us/pro/''',
                method='GET',
                callback=self.parse,
                meta={'dont_redirect': False, "parc_id": item,
                      'spider_num': enumerator, 'cookiejar': enumerator},
                dont_filter=True,
                headers=self.HEADERS
                )

    def parse(self, response):
        """
        This is the main scraping function that downloads information
        :param response:
        :return:
        """

        open_in_browser(response)

    #     property_object = models.Property.objects.get(parcel_number = response.meta['parc_id'])
    #     county_object = models.County.objects.get(name='Montgomery')
    #     soup = BeautifulSoup(response.body, 'html.parser')
    #     property_object.legal_acres = soup.find('td', text='Acres').find_next('td').text
    #     property_object.legal_description = f'''{soup.find('td', text='Legal Description').find_next('td').text}{soup.find('td', text='Legal Description').find_next('tr').find_next('td').find_next('td').text}'''
    #     property_object.owner = soup.find('table', id='Owner').find('tr').find_next('tr').find('td').text
    #     property_object.date_sold = soup.find('table', id="Sales").find('tr').find_next('tr').find('td').text
    #
    #     property_object.tax_district = soup.find('table', id='Legal').find('tr').find_next('tr').find_next('tr').find_next('tr').find_next('tr').find_next('tr').find_next('tr').find('td').find_next('td').text
    #     property_object.county = county_object
    #
    #     first = soup.find('table', id='Mailing').find('td', text='Name').find_next('td').text
    #     second = soup.find('table', id='Mailing').find('td', text='Name').find_next('tr').find('td').find_next('td').text
    #     city_state =  soup.find('table', id='Mailing').find('td', text='City, State, Zip').find_next('td').text
    #     tax_address = models.TaxAddress.objects.get_or_create(
    #         primary_address_line= first,
    #         secondary_address_line= second,
    #         city= city_state['city'],
    #         state= city_state['state'],
    #         zipcode= city_state['zipcode']
    #     )
    #     property_object.tax_address = tax_address
    #     property_object.save()
    #     yield scrapy.Request(
    #         url=f'''https://www.mcrealestate.org/Datalets/Datalet.aspx?mode=sales&UseSearch=no&pin={response.meta['parc_id'][0:3]}%20{response.meta['parc_id'][3:8]}%20{response.meta['parc_id'][8:]}&LMparent=20''',
    #         method='GET',
    #         callback=self.parse_transfer_information,
    #         meta={'parcel_number': response.meta['parcel_number']},
    #         dont_filter=True,
    #         headers=self.HEADERS
    #     )
    #
    # def parse_transfer_information(self, response):
    #     parsed_parcel_number = response.meta['parc_id']
    #     property_object, created = models.Property.objects.get_or_create(parcel_number=parsed_parcel_number)
    #
    #     # Clear property objects
    #     # Delete existing property transfer records so that we can be sure our database reflects information
    #     # on the site.
    #     soup = BeautifulSoup(response.body, 'html.parser')
    #     models.PropertyTransfer.objects.filter(property=property_object).delete()
    #     rows_in_table = soup.find('table', id='Sales').find_all('tr')
    #
    #     for row in rows_in_table:
    #         date_sold = row.find_next('td').text
    #         sale_price = row.find_next('td').find_next('td').text
    #         deed_ref = row.find_next('td').find_next('td').find_next('td').text
    #         seller = row.find_next('td').find_next('td').find_next('td').find_next('td').text
    #         buyer = row.find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').text
    #
    #         print(date_sold, sale_price, deed_ref, seller, buyer)
    #         sale_record_object = models.PropertyTransfer.objects.create(
    #             guarantor = seller,
    #             guarantee = buyer,
    #             conveyance_number= deed_ref,
    #             sale_amount = utils.convert_taxable_value_string_to_integer(sale_price),
    #             transfer_date= date_sold,
    #             property=property_object
    #         )
    #         sale_record_object.save()
