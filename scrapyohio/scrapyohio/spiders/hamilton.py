# -*- coding: utf-8 -*-
import datetime

import scrapy
from bs4 import BeautifulSoup
from scrapy import Request, FormRequest

from ohio import settings
from propertyrecords import utils, models


class HamiltonSpider(scrapy.Spider):
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, "
                      "like Gecko) Chrome/70.0.3538.102 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "X-MicrosoftAjax": "Delta=true"
    }

    name = 'hamilton'
    allowed_domains = ['wedge.hcauditor.org']

    def retrieve_all_hamilton_county_urls(self):
        self.hamilton_county_object, created = models.County.objects.get_or_create(name="Hamilton")
        self.parse_these_items = models.Property.objects.filter(county=self.hamilton_county_object)

        for item in self.parse_these_items:
            property_parameters = {'url': f'''https://wedge.hcauditor.org/view/re/{item.parcel_number}/2018/summary''',
                   'parcel_number': item.parcel_number
                   }
            yield property_parameters

    def __init__(self):
        self.HEADERS.update(settings.CONTACT_INFO_HEADINGS)
        self.logged_out = False

    def start_requests(self):
       # Ensure we have a county in the database
        self.hamilton_county_object, created = models.County.objects.get_or_create(name="Hamilton")


        # We want to assign headers for each request triggered. Override the request object
        # sent over to include Lucia's contact information
        for parameter_dictionary in self.retrieve_all_hamilton_county_urls():
            yield Request(parameter_dictionary['url'], dont_filter=True,
                        headers=self.HEADERS,
                        meta = {'parcel_id': parameter_dictionary['parcel_number']
                                },
                        )

    def parse(self, response):
        """

        :param response:
        :return:
        """
        soup = BeautifulSoup(response.body, 'html.parser')

        #
        # parcel_number
        # account_number
        # legal_acres = soup.find('table', summary='Appraisal Summary').find('td', text='Acreage').find_next_sibling('td').text
        # legal_description - PROP?
        # owner=  ON OWNER PAGE -- soup.find('table', summary='Related Names').find('td', text='Parcel Owner ').find_previous_sibling().text
        # date_sold = soup.find('table', summary='Appraisal Summary').find('td', text='Last Sale Date').find_next_sibling().text
        # date_of_LLC_name_change NA.
        # date_of_mortgage = V DIFF.
        # mortgage_amount = V DIFF.
        # property_class = NOT AVAIL?
        # property_rating = NOT AVAIL?
        # land_use = soup.find('table', id='property_information').find('tbody').find('div', text='Land Use').find_next_sibling('div').text
        tax_district = soup.find('table', id='property_information').find('tbody').find('div', text='Tax District').find_next_sibling('div').text
        school_district_name = soup.find('table', id='property_information').find('tbody').find('div', text='School District').find_next_sibling('div').text
        # school_district =
        # tax_delinquent =
        rental_reg_yes_no = soup.find('td', text='Rental Registration').find_next_sibling("td").text
        rental_registration = utils.convert_y_n_to_boolean(rental_reg_yes_no)
        # tax_lien =
        # tax_delinquent_year =
        # cauv_property = - CAUV AOUNT
        occ_yes_no = soup.find('td', text='Owner Occupancy Credit').find_next_sibling("td").text
        owner_occupancy_indicated = utils.convert_y_n_to_boolean(occ_yes_no)
        # last_scraped_one =
        # tax_address = models.ForeignKey( YES


















        # parsed_parcel_number = response.meta['parcel_id']
        # self.parsed_prop, created = models.Property.objects.get_or_create(parcel_number=parsed_parcel_number)
        # self.parsed_prop.county = self.warren_county_object
        # self.parsed_prop.legal_acres = utils.convert_acres_to_integer(response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryLegalDesc']/text()").extract()[1])
        # self.parsed_prop.legal_description = response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryLegalDesc']/text()").extract()[0]
        # self.parsed_prop.owner = response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryCurrentOwner']/text()").extract()[0]
        # self.parsed_prop.land_use = utils.parse_ohio_state_use_code(response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryStateUseCode']/text()").extract()[0])
        # self.parsed_prop.tax_district = response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryTaxDistrict']/text()").extract()[0]
        # self.parsed_prop.school_district = int(response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryOhioSchoolDistNumber']/text()").extract()[0])
        # self.parsed_prop.school_district_name = response.xpath("//span[@id='ContentPlaceHolderContent_lblSummarySchoolDistrict']/text()").extract()[0]
        #
        # self.parsed_prop.cauv_property = utils.cauv_parser(response.xpath("//span[@id='ContentPlaceHolderContent_lblValSumCAUVTrue']/text()").extract()[0])
        # try:
        #     self.parsed_prop.owner_occupancy_indicated = utils.convert_y_n_to_boolean(
        #         response.xpath("//span[@id='ContentPlaceHolderContent_lblSingleResOwnerOccupied']/text()").extract()[0])
        # except IndexError:
        #     # There are many reasons a property might not be owner occupied... if it's an office building,
        #     # for example. This field will be False unless we found an owner occupied indication or tax credit
        #     self.parsed_prop.owner_occupancy_indicated = False
        #
        # self.lookup_possibilities = [
        #         response.xpath("//span[@id='ContentPlaceHolderContent_lblSingleResSaleDate']/text()").extract(),
        #         response.xpath("//span[@id='ContentPlaceHolderContent_lblNoBldgLastSaleDate']/text()").extract(),
        # ]
        #
        # for lookup in self.lookup_possibilities:
        #     #     # We might be seeing a property with multiple buildings, and therefore sales data will not be
        #     #     # available on home page. In this case, we'll need to make a separate request.
        #     #     # See:  https://github.com/ludstuen90/ohio/issues/70
        #     try:
        #         parsed_lookup = datetime.datetime.strptime(lookup[0], '%m/%d/%Y')
        #         self.date_pulled_this_search = parsed_lookup.date()
        #         self.parsed_prop.date_sold = parsed_lookup.date()
        #         break
        #     except IndexError:
        #         continue
        #     except ValueError:
        #         continue


        self.parsed_prop.save()

        # # Tax values, will be changed to be stored in a new table below:
        # # Detect current year
        # current_year = response.xpath("//span[@id='ContentPlaceHolderContent_lblcurrvalue']/text()").extract()[0][-4:]
        # self.current_year_tax_values, created = models.TaxData.objects.update_or_create(
        #                                                             tax_year=current_year,
        #                                                             property_record_id = self.parsed_prop.id
        # )
        # self.current_year_tax_values.market_value = utils.convert_taxable_value_string_to_integer(response.xpath("//span[@id='ContentPlaceHolderContent_lblValSumTotalTrue']/text()").extract()[0])
        # self.current_year_tax_values.taxable_value = utils.convert_taxable_value_string_to_integer(response.xpath("//span[@id='ContentPlaceHolderContent_lblValSumTotalAssessed']/text()").extract()[0])
        # self.current_year_tax_values.taxes_paid = utils.convert_taxable_value_string_to_integer(response.xpath("//span[@id='ContentPlaceHolderContent_lblTaxSumTotChargeNetTax']/text()").extract()[0])
        # self.current_year_tax_values.save()
        # # End tax values
        #
        # # Parse pay next year tentative values
        # try:
        #     next_year = response.xpath("//p[contains(text(),'TENTATIVE VALUE AS OF 01-01-2018')]/text()").extract()[0][-4:]
        #     self.next_year_tax_values, created = models.TaxData.objects.update_or_create(
        #                                                                 tax_year=next_year,
        #                                                                 property_record_id = self.parsed_prop.id
        #     )
        #     self.next_year_tax_values.market_value = utils.convert_taxable_value_string_to_integer(response.xpath("//span[@id='ContentPlaceHolderContent_lblTentValSumTotalTrue']/text()").extract()[0])
        #     self.next_year_tax_values.taxable_value = utils.convert_taxable_value_string_to_integer(response.xpath("//span[@id='ContentPlaceHolderContent_lblTentValSumTotalAssessed']/text()").extract()[0])
        #     self.next_year_tax_values.save()
        # except IndexError:
        #     pass
        # # End next year
        #
        # # Declare screen values so that we can parse other views if needed.
        # self.data = {}
        # self.data['ctl00$ToolkitScriptManager1'] = 'ctl00$UpdatePanel1|ctl00$ContentPlaceHolderContent$lbTaxInfo'
        # self.data['__EVENTTARGET'] = "ctl00$ContentPlaceHolderContent$lbTaxInfo"
        # self.data['__EVENTARGUMENT'] = ""
        # self.data['__LASTFOCUS'] = ""
        # self.data['__VIEWSTATE'] = response.css('input#__VIEWSTATE::attr(value)').extract_first(),
        # self.data['__EVENTVALIDATION'] = response.css('input#__EVENTVALIDATION::attr(value)').extract_first(),
        # self.data['ctl00$ContentPlaceHolderContent$ddlTaxYear'] = '2017',
        # self.data['__ASYNCPOST'] = 'true',
        # yield FormRequest(
        #         url=response.request.url,
        #         method='POST',
        #         callback=self.parse_tax,
        #         formdata=self.data,
        #         meta={'page': 1, 'parcel_id': response.meta['parcel_id']},
        #         dont_filter=True,
        #         headers=self.HEADERS,
        #     )
        #
        # # If at this point we still haven't been able to download the last property sale
        # # date, let's go explicitly to the sales page and parse it from there.
        # # If we can parse it earlier on, skipping this step will allow our scrapes
        # # to go faster
        #
        # if not hasattr(self, 'date_pulled_this_search'):
        #     self.parsed_data = {}
        #     self.parsed_data['ctl00$ToolkitScriptManager1'] = 'ctl00$UpdatePanel1|ctl00$ContentPlaceHolderContent$lbSalesHistory'
        #     self.parsed_data['__EVENTTARGET'] = "ctl00$ContentPlaceHolderContent$lbSalesHistory"
        #     self.parsed_data['__EVENTARGUMENT'] = ""
        #     self.parsed_data['__LASTFOCUS'] = ""
        #     self.parsed_data['__VIEWSTATE'] = response.css('input#__VIEWSTATE::attr(value)').extract_first(),
        #     self.parsed_data['__EVENTVALIDATION'] = response.css('input#__EVENTVALIDATION::attr(value)').extract_first(),
        #     self.parsed_data['ctl00$ContentPlaceHolderContent$ddlTaxYear'] = '2017',
        #     self.parsed_data['__ASYNCPOST'] = 'true',
        #
        #     yield scrapy.FormRequest(
        #             url=response.request.url,
        #             method='POST',
        #             callback=self.parse_sale,
        #             formdata=self.parsed_data,
        #             meta={'page': 1, 'parcel_id': response.meta['parcel_id']},
        #             dont_filter=True,
        #             headers=self.HEADERS,
        #         )

    # def parse_tax(self, response):
    #     self.parsed_prop = models.Property.objects.get(parcel_number=response.meta['parcel_id'])
    #     returned_tax_address = response.css("div.wrapper div.rightContent:nth-child(4) div:nth-child(1) fieldset::text").extract()
    #     parsed_address = utils.parse_tax_address_from_css(returned_tax_address)
    #     # FIND IF TAX ADDRESS EXISTS, IF NOT CREATE
    #     if len(parsed_address) == 1:
    #         try:
    #             tax_record = models.TaxAddress.objects.get(name=parsed_address[0])
    #         except models.TaxAddress.DoesNotExist:
    #             tax_record = models.TaxAddress(tax_address=parsed_address)
    #             tax_record.save()
    #     else:
    #         try:
    #             # Pass the parsed address through our name parser (in Tax Address model), to see
    #             # what it would look like. Then, compare with existing records to see if we have
    #             # one that matches.
    #             # If so, get the record. Otherwise, create it.
    #             self.dummy_obj = models.TaxAddress(tax_address=parsed_address)
    #             tax_record = models.TaxAddress.objects.get(primary_address_line=self.dummy_obj.primary_address_line)
    #         except models.TaxAddress.DoesNotExist:
    #             tax_record = models.TaxAddress(tax_address=parsed_address)
    #             tax_record.save()
    #     self.parsed_prop.tax_address = tax_record
    #     self.parsed_prop.save()
    #
    #     # Do the work to also create a property address. Must come after property record is saved because
    #     # We need the ID to be able to access the property record
    #
    #     address_to_parse = utils.parse_address(response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryPropAddress']/text()").extract(), False)
    #     self.property_address, self.was_prp_address_created = models.PropertyAddress.objects.get_or_create(property_id=self.parsed_prop.id)
    #     self.property_address.primary_address_line = address_to_parse['primary_address_line']
    #     self.property_address.city = address_to_parse['city']
    #     self.property_address.zipcode = address_to_parse['zipcode']
    #     self.property_address.state = address_to_parse['state']
    #     try:
    #         if self.parsed_prop.secondary_address_line:
    #             self.property_address.secondary_address_line = self.parsed_prop.property_address['secondary_address_line']
    #     except AttributeError:
    #         pass
    #
    #     self.property_address.save()
    #
    #
    # def parse_sale(self, response):
    #     """
    #         Buildings with multiple buildings will require loading the 'last sale' page in order to
    #         verify when the buildings were last sold. This page loads if this is required.
    #
    #         If we can't find sale information on the home page, we'll always load this page so that way
    #         we can keep tabs on any sales that might happen.
    #     :return:
    #     """
    #     try:
    #         parsed_parcel_number = response.meta['parcel_id']
    #         property_to_save = models.Property.objects.get(parcel_number=parsed_parcel_number)
    #         soup = BeautifulSoup(response.body, 'html.parser')
    #         sale_date = soup.find('th').find_next('td').contents[0]
    #         property_to_save.date_sold = datetime.datetime.strptime(sale_date, "%m-%d-%Y")
    #         property_to_save.save()
    #     except AttributeError:
    #         # It's possible there might not be any last sale dates saved. Account for this!
    #         pass

