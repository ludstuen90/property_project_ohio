# -*- coding: utf-8 -*-
import datetime
import decimal
import re

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
    allowed_domains = ['property.franklincountyauditor.com']

    def retrieve_all_franklin_county_urls(self):
        self.please_parse_these_items = models.Property.objects.filter(county=self.franklin_county_object).all()

        for item in self.please_parse_these_items:
            yield item.parcel_number

    def __init__(self):
        self.HEADERS.update(settings.CONTACT_INFO_HEADINGS)
        self.logged_out = False

    def start_requests(self):
       # Ensure we have a county in the database
        self.franklin_county_object, created = models.County.objects.get_or_create(name="Franklin")
        # We want to assign headers for each request triggered. Override the request object
        # sent over to include Lucia's contact information
        # for parameter_dictionary in self.retrieve_all_franklin_county_urls():

        # Use the enumerator function to allow an individual cookie jar for each request
        # This is necessary to keep track of multiple view states
        for enumerator, item in enumerate(self.retrieve_all_franklin_county_urls()):
            yield scrapy.Request(
                url='http://property.franklincountyauditor.com/_web/search/commonsearch.aspx?mode=parid',
                method='GET',
                callback=self.parse,
                meta={'dont_redirect': False, "parc_id": item,
                      'spider_num': enumerator, 'cookiejar': enumerator},
                dont_filter=True,
                headers=self.HEADERS
            )

    def retrieve_info_to_parse(self, response):
        print("PARSING: ", response.meta['parc_id'])
        parsed_parcel_number = response.meta['parc_id']
        self.parsed_prop, created = models.Property.objects.get_or_create(parcel_number=parsed_parcel_number)

        soup = BeautifulSoup(response.body, 'html.parser')

        # FIND ADDRESS
        try:
            tds = soup.find_all('td', class_="DataletHeaderBottom")
            address = tds[1].get_text()
            city = utils.franklin_row_name_returner(soup, re.compile("Tax Status"), "City/Village")
            zip = utils.franklin_row_name_returner(soup, re.compile("Tax Status"), "Zip Code")

            self.property_address, self.was_prp_address_created = models.PropertyAddress.objects.get_or_create(
                property_id=self.parsed_prop.id)
            self.property_address.primary_address_line = address
            self.property_address.city = city
            self.property_address.zipcode = zip
            self.property_address.save()
        except UnicodeEncodeError:
            pass

        # LEGAL DESCRIPTION
        legal_desc_text_1 = utils.franklin_row_name_returner(soup, "Owner", "Legal Description")
        legal_desc_cell_1 = utils.franklin_row_name_returner(soup, "Owner", "Legal Description", cell_value=True)

        legal_desc_text_2 = utils.find_td_cell_value_beneath_current_bssoup(legal_desc_cell_1)
        legal_desc_cell_2 = utils.find_td_cell_value_beneath_current_bssoup(legal_desc_cell_1, True)

        legal_desc_text_3 = utils.find_td_cell_value_beneath_current_bssoup(legal_desc_cell_2)

        self.parsed_prop.legal_description = f'''{legal_desc_text_1} {legal_desc_text_2} {legal_desc_text_3}'''

        # Land Use
        self.parsed_prop.land_use = utils.franklin_row_name_returner(soup, re.compile("Tax Status"), "Land Use")

        # OWNER
        owner_name = utils.franklin_row_name_returner(soup, "Owner", "Owner")
        owner_cell = utils.franklin_row_name_returner(soup, "Owner", "Owner", cell_value=True)
        secondary_owner_attempt = utils.find_td_cell_value_beneath_current_bssoup(owner_cell)
        names = utils.name_parser_and_joiner(owner_name, secondary_owner_attempt)
        self.parsed_prop.owner = names

        # LAST SALE DATE
        string_date_sold = utils.franklin_row_name_returner(soup, "Most Recent Transfer", "Transfer Date")
        self.parsed_prop.date_sold = utils.datetime_to_date_string_parser(string_date_sold, '%b-%d-%Y')

        # CAUV PROPERTY
        cauv_yn = utils.franklin_row_name_returner(soup, re.compile("Tax Status"), "CAUV Property")
        self.parsed_prop.cauv_property = utils.convert_y_n_to_boolean(cauv_yn)

        # TAX LIEN
        tax_lien_yn = utils.franklin_row_name_returner(soup, re.compile("Tax Status"), "Tax Lien")
        self.parsed_prop.tax_lien = utils.convert_y_n_to_boolean(tax_lien_yn)

        # PROPERTY CLASS
        self.parsed_prop.property_class = utils.franklin_row_name_returner(soup, re.compile("Tax Status"), "Property Class")

        # OWNER OCC CREDIT
        text_occ_indicated = utils.franklin_row_name_returner(soup, re.compile("Tax Status"), "Owner Occ. Credit")
        self.parsed_prop.owner_occupancy_indicated = utils.franklin_county_credit_parser(text_occ_indicated)

        # Rental Registration
        rental_registration_yn = utils.franklin_row_name_returner(soup, re.compile("Tax Status"), "Rental Registration")
        self.parsed_prop.rental_registration = utils.convert_y_n_to_boolean(rental_registration_yn)

        # Land Use:
        land_use_string = utils.franklin_row_name_returner(soup, re.compile("Tax Status"), "Land Use")
        land_use_number = land_use_string.split(' ')[0]
        self.parsed_prop.land_use = int(land_use_number)

        # Tax District:
        self.parsed_prop.tax_district = utils.franklin_row_name_returner(soup, re.compile("Tax Status"), "Tax District")

        # school_district
        sd = utils.franklin_row_name_returner(soup, re.compile("Tax Status"), "School District")
        try:
            # Remove extra spaces, just to be nice
            if sd.split('-', 1)[0][-1:] == " ":
                self.parsed_prop.school_district = sd.split('-', 1)[0][:-1]
            else:
                self.parsed_prop.school_district = sd.split('-', 1)[0]

            if sd.split('-', 1)[1][:1] == " ":
                self.parsed_prop.school_district_name = sd.split('-', 1)[1][1:]
            else:
                self.parsed_prop.school_district_name = sd.split('-', 1)[1]

        except IndexError:
            pass

        # FIND ACRES
        self.parsed_prop.legal_acres = utils.franklin_row_name_returner(soup, "Owner", "Calculated Acres")

        # FIND TAX ADDRESS
        returned_tax_line = utils.franklin_county_tax_address_getter(soup)
        length_tax_line = len(returned_tax_line)

        # FIND IF TAX ADDRESS EXISTS, IF NOT CREATE
        if len(returned_tax_line) >= 1:
            try:
                tax_record = models.TaxAddress.objects.get(name=returned_tax_line[0], primary_address_line=returned_tax_line[length_tax_line-2])
                #IF NAME AND ADDRESS IS THE SAME, PULL EXISTING RECORD

            except models.TaxAddress.DoesNotExist:
                tax_record = models.TaxAddress(tax_address=returned_tax_line)
                tax_record.save()
                self.parsed_prop.tax_address = tax_record

        try:
            self.parsed_prop.tax_address = tax_record
        except UnboundLocalError:
            # No tax address available, keep scraping
            pass

        self.parsed_prop.last_scraped_one = datetime.datetime.now()
        self.parsed_prop.save()

        # ---------- PARSE TAX DATA INFO
        # Find property data if applicable
        try:
            tax_year_row = soup.find('td', text=re.compile("Current Market Value")).get_text()
            tax_year = tax_year_row.split(' ')[0]
            market_value = utils.franklin_row_name_returner(soup, re.compile("Current Market Value"), "Total",
                                                            cell_column_number=3)
            taxable_value = utils.franklin_row_name_returner(soup, re.compile("Taxable Value"), "Total",
                                                             cell_column_number=3)
            table = soup.find('table', id=f'''{tax_year} Taxes''')
            rows = table.find_all('tr', recursive=False)
            specific_row = rows[1]
            for iteration, cell in enumerate(specific_row):
                # find the cell underneath "Total Paid," and grab its value
                if iteration == 1:
                    taxes_paid = cell.get_text()
            self.tax_record, created = models.TaxData.objects.get_or_create(property_record=self.parsed_prop,
                                                                            tax_year=tax_year)

            self.tax_record.market_value = utils.decimal_converter(market_value)
            self.tax_record.taxable_value = utils.decimal_converter(taxable_value)
            self.tax_record.taxes_paid = utils.decimal_converter(taxes_paid)
            self.tax_record.save()
        except AttributeError:
            # No tax info available, keep scraping as possible.
            pass

    def parse_transfer_data(self, response):
        parcel_number = response.meta['parc_id']
        property_object = models.Property.objects.get(parcel_number=parcel_number)

        # Delete existing property transfer records so that we can be sure our database reflects information
        # on the site.
        models.PropertyTransfer.objects.filter(property=property_object).delete()

        soup = BeautifulSoup(response.body, 'html.parser')

        table = soup.find('table', id="Sales Summary")
        rows = table.find_all('tr', recursive=False)

        for iteration, row in enumerate(rows):
            if iteration == 0:
                pass
            else:
                try:
                    row_array = [x.get_text() for x in row.children]
                    models.PropertyTransfer.objects.create(
                        property=property_object,
                        guarantor='',
                        guarantee=row_array[1],
                        sale_amount=utils.convert_taxable_value_string_to_integer(row_array[5]),
                        conveyance_fee=decimal.Decimal('-999'),
                        conveyance_number=row_array[2],
                        transfer_date=utils.datetime_to_date_string_parser(row_array[0], '%b-%d-%Y')
                    )
                except IndexError:
                    pass

    def parse(self, response):
        """

        :param response:
        :return:
        """
        yield FormRequest.from_response(
            response,
            formdata={
                'inpParid': response.meta['parc_id']},
                meta={"parc_id": response.meta['parc_id'],
                            'spider_num': response.meta['spider_num'], 'cookiejar': response.meta['spider_num']
                            },
                    dont_filter=True,
            callback=self.retrieve_info_to_parse,
        )

        yield FormRequest.from_response(
            response,
            url="http://property.franklincountyauditor.com/_web/datalets/datalet.aspx?mode=sales_summary&sIndex=1&idx=1&LMparent=20",
                      meta={"parc_id": response.meta['parc_id'],
                            'spider_num': response.meta['spider_num'], 'cookiejar': response.meta['spider_num']
                            },
                      callback=self.parse_transfer_data,
                    dont_filter=True
                      )

