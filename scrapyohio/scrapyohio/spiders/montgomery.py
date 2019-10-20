# -*- coding: utf-8 -*-
import datetime
import decimal

import scrapy
from bs4 import BeautifulSoup
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

    name = 'montgomery'
    allowed_domains = ['mcrealestate.org']

    def retrieve_all_montgomery_county_urls(self):
        # Excludes any properties that have been scraped before... in this way, we can scrape faster.
        rescrape = False
        # Ensure we have a county in the database
        self.montgomery_county_object, created = models.County.objects.get_or_create(name="Montgomery")

        if rescrape:
            self.please_parse_these_items = models.Property.objects.all().filter(county=self.montgomery_county_object,
                                                                                 )
        else:
            self.please_parse_these_items = models.Property.objects.all().filter(county=self.montgomery_county_object,
                                                                             last_scraped_one__isnull=True
                                                                             )




        # # Ensure we have a property record for all items
        # for property in list_of_parcel_ids:
        #     created_property, created = models.Property.objects.get_or_create(parcel_number=property,
        #                                                               county=self.montgomery_county_object)
        #     created_property.save()
        #
        # self.please_parse_these_items = models.Property.objects.filter(county=self.montgomery_county_object,
        #                                                          parcel_number__in=list_of_parcel_ids
        #                                                          ).order_by('?')
        # else:
        #self.please_parse_these_items = models.Property.objects.filter(county=self.montgomery_county_object)
        # If we are not running a rescrape, take out properties that have already been scraped
        # if rescrape is False:
        #     self.please_parse_these_items_noscrape = self.please_parse_these_items.filter(last_scraped_one__isnull=True)
        #     for item in self.please_parse_these_items_noscrape:
        #         yield item.parcel_number
        #
        # else:
        for item in self.please_parse_these_items:
            yield item.parcel_number

    def __init__(self):
        self.HEADERS.update(settings.CONTACT_INFO_HEADINGS)
        self.logged_out = False

    def start_requests(self):
        for enumerator, item in enumerate(self.retrieve_all_montgomery_county_urls()):
            yield scrapy.Request(
                url=f'''https://www.mcrealestate.org/Datalets/Datalet.aspx?mode=PROFILEALL&UseSearch=no&pin={item[0:3]}%20{item[3:8]}%20{item[8:]}&LMparent=20''',
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
        property_object = models.Property.objects.get(parcel_number = response.meta['parc_id'])
        county_object = models.County.objects.get(name='Montgomery')
        soup = BeautifulSoup(response.body, 'html.parser')

        if not soup.find('table', class_='WidgetBar').find('b', text='-- No Data --'):
            try:
                property_object.legal_acres = decimal.Decimal(soup.find('td', text='Acres').find_next('td').text)
            except (decimal.InvalidOperation, AttributeError):
                pass

            property_object.legal_description = f'''{soup.find('td', text='Legal Description').find_next('td').text}{soup.find('td', text='Legal Description').find_next('tr').find_next('td').find_next('td').text}'''
            property_object.owner = soup.find('table', id='Owner').find('tr').find_next('tr').find('td').text
            try:
                property_object.date_sold = utils.datetime_to_date_string_parser(soup.find('table', id="Sales").find('tr').find_next('tr').find('td').text, '%d-%b-%y')
            except AttributeError:
                pass
            property_object.tax_district = soup.find('table', id='Legal').find('tr').find_next('tr').find_next('tr').find_next('tr').find_next('tr').find_next('tr').find_next('tr').find('td').find_next('td').text
            property_object.county = county_object
            property_object.last_scraped_one = datetime.datetime.now()
            first = soup.find('table', id='Mailing').find('td', text='Name').find_next('td').text
            second = soup.find('table', id='Mailing').find('td', text='Name').find_next('tr').find('td').find_next('td').text
            first_line = soup.find('table', id='Mailing').find('td', text='Mailing Address').find_next('td').text
            second_line = soup.find('table', id='Mailing').find('td', text='Mailing Address').find_next('tr').find('td').find_next('td').text
            city_state = soup.find('table', id='Mailing').find('td', text='City, State, Zip').find_next('td').text
            city_state_parsed = utils.parse_city_state_and_zip_from_line(city_state, True)
            tax_address, created = models.TaxAddress.objects.get_or_create(
                name= first,
                secondary_name= second,
                primary_address_line=first_line,
                secondary_address_line=second_line,
                city=city_state_parsed['city'],
                state=city_state_parsed['state'],
                zipcode=city_state_parsed['zipcode']
            )
            property_object.tax_address = tax_address
            property_object.save()
            yield scrapy.Request(
                url=f'''https://www.mcrealestate.org/Datalets/Datalet.aspx?mode=sales&UseSearch=no&pin={response.meta['parc_id'][0:3]}%20{response.meta['parc_id'][3:8]}%20{response.meta['parc_id'][8:]}&LMparent=20''',
                method='GET',
                callback=self.parse_transfer_information,
                meta={'parc_id': response.meta['parc_id']},
                dont_filter=True,
                headers=self.HEADERS
            )

    def parse_transfer_information(self, response):
        parsed_parcel_number = response.meta['parc_id']
        property_object, created = models.Property.objects.get_or_create(parcel_number=parsed_parcel_number)

        # Clear property objects
        # Delete existing property transfer records so that we can be sure our database reflects information
        # on the site.
        soup = BeautifulSoup(response.body, 'html.parser')
        try:
            if not soup.find('table', class_='WidgetBar').find('font', text='GET_DATA_FAILED:sales'):
                models.PropertyTransfer.objects.filter(property=property_object).delete()
                rows_in_table = soup.find('table', id='Sales').find_all('tr')

                for count, row in enumerate(rows_in_table):
                    if count != 0:
                        date_sold = row.find_next('td').text
                        attempt_sale_price = row.find_next('td').find_next('td').text

                        seller = row.find_next('td').find_next('td').find_next('td').find_next('td').text
                        buyer = row.find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').text
                        if seller != '' and buyer != '':
                            if len(attempt_sale_price) > 3:
                                converted_sale_price = utils.convert_taxable_value_string_to_integer(attempt_sale_price)
                            else:
                                converted_sale_price = 0
                            deed_ref = row.find_next('td').find_next('td').find_next('td').text
                            sale_record_object = models.PropertyTransfer.objects.create(
                                guarantor=seller,
                                guarantee=buyer,
                                conveyance_number=deed_ref,
                                sale_amount=converted_sale_price,
                                transfer_date=utils.datetime_to_date_string_parser(date_sold, '%d-%b-%y'),
                                property=property_object
                            )
                            sale_record_object.save()

            else:
                print('skipping due to flag, don-t destroy data')
        except AttributeError:
            pass