# -*- coding: utf-8 -*-
import datetime

import scrapy
from bs4 import BeautifulSoup
from scrapy import Request, FormRequest
from scrapy.utils.response import open_in_browser

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
            property_parameters = {'url': "http://property.franklincountyauditor.com/_web/search/CommonSearch.aspx?mode=PARID"}
            property_parameters['ScriptManager1_TSM'] = " ;;AjaxControlToolkit, Version=4.1.50731.0, Culture=neutral, PublicKeyToken=28f01b0e84b6d53e:en-US:f8fb2a65-e23a-483b-b20e-6db6ef539a22:ea597d4b:b25378d2;Telerik.Web.UI, Version=2013.1.403.45, Culture=neutral, PublicKeyToken=121fae78165ba3d4:en-US:66639117-cae4-4d6c-a3d7-81eea986263a:16e4e7cd:f7645509:24ee1bba:874f8ea2:19620875:f46195d3:490a9d4e"
            property_parameters['__EVENTTARGET']= ""
            property_parameters['__EVENTARGUMENT']= ""
            property_parameters['__VIEWSTATE']= "/wEPDwUKMTMyMjI2NDUyNA8UKwACZGcWAmYPZBYEAgcPZBYEAgEPDxYCHgdWaXNpYmxlaGQWAmYPZBYCZg9kFgQCAQ9kFgICAQ9kFgICAQ8QZGQWAGQCAw9kFgJmD2QWAmYPPCsADgIAFCsAAmQXAQUIUGFnZVNpemUCCgEWAhYLDwICFCsAAjwrAAUBBAUDSlVSPCsABQEEBQROQU1FZGUUKwAACyl5VGVsZXJpay5XZWIuVUkuR3JpZENoaWxkTG9hZE1vZGUsIFRlbGVyaWsuV2ViLlVJLCBWZXJzaW9uPTIwMTMuMS40MDMuNDUsIEN1bHR1cmU9bmV1dHJhbCwgUHVibGljS2V5VG9rZW49MTIxZmFlNzgxNjViYTNkNAE8KwAHAAspdFRlbGVyaWsuV2ViLlVJLkdyaWRFZGl0TW9kZSwgVGVsZXJpay5XZWIuVUksIFZlcnNpb249MjAxMy4xLjQwMy40NSwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj0xMjFmYWU3ODE2NWJhM2Q0AWRkZGRmZAIDDw8WAh8AaGRkAggPFCsAAw8WAh4XRW5hYmxlQWpheFNraW5SZW5kZXJpbmdoZGRkZBgBBR5fX0NvbnRyb2xzUmVxdWlyZVBvc3RCYWNrS2V5X18WAQUVUmFkV2luZG93X05hdmlnYXRlVXJs1WEjqavCVdlgjf6WnxLeWu1/AvMnxjPOZlGWSV007EA="
            property_parameters['__VIEWSTATEGENERATOR'] = "A01010D4"
            property_parameters['__EVENTVALIDATION']= "/wEdAAsQB2fqAqcqElbYSdl4hUOlimrMKsvipVqgAm6eeFqW4HJKYAFO6I0fqTxQsc4lhuw/VBgahKiSYWm0TH20tWytmzXzYHIa1dmXlvkbftBdgwslnNmVQBKtcUYebedL4DIIE4uP8nfiSzXQ9yZdaHxE13z69BI9GFFQ52nNWBw1jGE7wbUKBFGxkg1vsxgrWVeJ/gVz0FNuJTGXAWFWdI3aBWrIxCGTmNcpF4dAhdp4eeHY92y26Rn23YRfNQ8+AnitmDnVKm0plZ1CLN7mVoC8"
            property_parameters['PageNum'] = ""
            property_parameters['SortBy']= "ALT_ID"
            property_parameters['SortDir'] = "asc"
            property_parameters['PageSize'] = "25"
            property_parameters['hdAction'] = "Search"
            property_parameters['hdIndex'] = ""
            property_parameters['sIndex'] = "-1"
            property_parameters['hdListType'] = "PA"
            property_parameters['hdJur'] = ""
            property_parameters['hdSelectAllChecked'] = "false"
            property_parameters['inpParid']= item.parcel_number
            property_parameters['selSortBy'] = "ALT_ID"
            property_parameters['selSortDir'] =  "asc"
            property_parameters['selPageSize']= "25"
            property_parameters['searchOptions$hdBeta']= ""
            property_parameters['btSearch'] = ""
            property_parameters['RadWindow_NavigateUrl_ClientState'] = ""
            property_parameters['mode'] = "PARID"
            property_parameters['mask'] = ""
            property_parameters['param1'] = ""
            property_parameters['searchimmediate'] = ""

            yield property_parameters

    def __init__(self):
        self.HEADERS.update(settings.CONTACT_INFO_HEADINGS)
        self.logged_out = False

    def start_requests(self):
       # Ensure we have a county in the database
        self.franklin_county_object, created = models.County.objects.get_or_create(name="Franklin")
        # We want to assign headers for each request triggered. Override the request object
        # sent over to include Lucia's contact information
        # for parameter_dictionary in self.retrieve_all_franklin_county_urls():
        # print("!!!", parameter_dictionary)

       # for item in retrieve_all_franklin_county_urls.items():
        for item in self.retrieve_all_franklin_county_urls():
            yield scrapy.FormRequest(
                        url="http://property.franklincountyauditor.com/_web/search/CommonSearch.aspx?mode=PARID",
                        method='POST',
                        callback=self.parse,
                        formdata=item,
                        meta={'dont_redirect': False},
                        dont_filter=True,
                        headers=self.HEADERS,
                    )

    def open_in_browser(self, response):
        open_in_browser(response)

    def parse(self, response):
        """

        :param response:
        :return:
        """

        print('!!!!!!!!!!!!!!! response: ', response)
        print('!!!!!!!!!!!!!!! response: ', dir(response))
        print('!!!!!!!!!!!!!!! response STATUS: ', response.status)
        print('!!!!!!!!!!!!!!! response META: ', response.meta)
        print('!!!!!!!!!!!!!!! response FOLLOW: ', response.follow)
        print('!!!!!!!!!!!!!!! response: ', response.body)
        print('!!!?!?!?!?!??!?!! response: ', response.headers)

        print('!!!!!!!!!!!!!!! response: ', response.xpath("//table[@id='Owner']/tbody/tr[1]/td[2]/text()"))


        yield Request("http://property.franklincountyauditor.com/_web/Datalets/Datalet.aspx?sIndex=0&idx=1", dont_filter=True,
                      headers=self.HEADERS,
                      meta={
                            },
                      callback=self.open_in_browser,

                      )
        # parsed_parcel_number = response.meta['parcel_id']
        #     self.parsed_prop, created = models.Property.objects.get_or_create(parcel_number=parsed_parcel_number)
        #     self.parsed_prop.county = self.warren_county_object
        #     self.parsed_prop.legal_acres = utils.convert_acres_to_integer(response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryLegalDesc']/text()").extract()[1])
        #     self.parsed_prop.legal_description = response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryLegalDesc']/text()").extract()[0]
        #     self.parsed_prop.owner = response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryCurrentOwner']/text()").extract()[0]
        #     self.parsed_prop.land_use = utils.parse_ohio_state_use_code(response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryStateUseCode']/text()").extract()[0])
        #     self.parsed_prop.tax_district = response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryTaxDistrict']/text()").extract()[0]
        #     self.parsed_prop.school_district = int(response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryOhioSchoolDistNumber']/text()").extract()[0])
        #     self.parsed_prop.school_district_name = response.xpath("//span[@id='ContentPlaceHolderContent_lblSummarySchoolDistrict']/text()").extract()[0]
        #
        #     self.parsed_prop.cauv_property = utils.cauv_parser(response.xpath("//span[@id='ContentPlaceHolderContent_lblValSumCAUVTrue']/text()").extract()[0])
        #     try:
        #         self.parsed_prop.owner_occupancy_indicated = utils.convert_y_n_to_boolean(
        #             response.xpath("//span[@id='ContentPlaceHolderContent_lblSingleResOwnerOccupied']/text()").extract()[0])
        #     except IndexError:
        #         # There are many reasons a property might not be owner occupied... if it's an office building,
        #         # for example. This field will be False unless we found an owner occupied indication or tax credit
        #         self.parsed_prop.owner_occupancy_indicated = False
        #
        #     self.lookup_possibilities = [
        #             response.xpath("//span[@id='ContentPlaceHolderContent_lblSingleResSaleDate']/text()").extract(),
        #             response.xpath("//span[@id='ContentPlaceHolderContent_lblNoBldgLastSaleDate']/text()").extract(),
        #     ]
        #
        #     for lookup in self.lookup_possibilities:
        #         #     # We might be seeing a property with multiple buildings, and therefore sales data will not be
        #         #     # available on home page. In this case, we'll need to make a separate request.
        #         #     # See:  https://github.com/ludstuen90/ohio/issues/70
        #         try:
        #             parsed_lookup = datetime.datetime.strptime(lookup[0], '%m/%d/%Y')
        #             self.date_pulled_this_search = parsed_lookup.date()
        #             self.parsed_prop.date_sold = parsed_lookup.date()
        #             break
        #         except IndexError:
        #             continue
        #         except ValueError:
        #             continue
        #
        #
        #     self.parsed_prop.save()
        #
        #     # Tax values, will be changed to be stored in a new table below:
        #     # Detect current year
        #     current_year = response.xpath("//span[@id='ContentPlaceHolderContent_lblcurrvalue']/text()").extract()[0][-4:]
        #     self.current_year_tax_values, created = models.TaxData.objects.update_or_create(
        #                                                                 tax_year=current_year,
        #                                                                 property_record_id = self.parsed_prop.id
        #     )
        #     self.current_year_tax_values.market_value = utils.convert_taxable_value_string_to_integer(response.xpath("//span[@id='ContentPlaceHolderContent_lblValSumTotalTrue']/text()").extract()[0])
        #     self.current_year_tax_values.taxable_value = utils.convert_taxable_value_string_to_integer(response.xpath("//span[@id='ContentPlaceHolderContent_lblValSumTotalAssessed']/text()").extract()[0])
        #     self.current_year_tax_values.taxes_paid = utils.convert_taxable_value_string_to_integer(response.xpath("//span[@id='ContentPlaceHolderContent_lblTaxSumTotChargeNetTax']/text()").extract()[0])
        #     self.current_year_tax_values.save()
        #     # End tax values
        #
        #     # Parse pay next year tentative values
        #     try:
        #         next_year = response.xpath("//p[contains(text(),'TENTATIVE VALUE AS OF 01-01-2018')]/text()").extract()[0][-4:]
        #         self.next_year_tax_values, created = models.TaxData.objects.update_or_create(
        #                                                                     tax_year=next_year,
        #                                                                     property_record_id = self.parsed_prop.id
        #         )
        #         self.next_year_tax_values.market_value = utils.convert_taxable_value_string_to_integer(response.xpath("//span[@id='ContentPlaceHolderContent_lblTentValSumTotalTrue']/text()").extract()[0])
        #         self.next_year_tax_values.taxable_value = utils.convert_taxable_value_string_to_integer(response.xpath("//span[@id='ContentPlaceHolderContent_lblTentValSumTotalAssessed']/text()").extract()[0])
        #         self.next_year_tax_values.save()
        #     except IndexError:
        #         pass
        #     # End next year
        #
        #     # Declare screen values so that we can parse other views if needed.
        #     self.data = {}
        #     self.data['ctl00$ToolkitScriptManager1'] = 'ctl00$UpdatePanel1|ctl00$ContentPlaceHolderContent$lbTaxInfo'
        #     self.data['__EVENTTARGET'] = "ctl00$ContentPlaceHolderContent$lbTaxInfo"
        #     self.data['__EVENTARGUMENT'] = ""
        #     self.data['__LASTFOCUS'] = ""
        #     self.data['__VIEWSTATE'] = response.css('input#__VIEWSTATE::attr(value)').extract_first(),
        #     self.data['__EVENTVALIDATION'] = response.css('input#__EVENTVALIDATION::attr(value)').extract_first(),
        #     self.data['ctl00$ContentPlaceHolderContent$ddlTaxYear'] = '2017',
        #     self.data['__ASYNCPOST'] = 'true',
        #     yield FormRequest(
        #             url=response.request.url,
        #             method='POST',
        #             callback=self.parse_tax,
        #             formdata=self.data,
        #             meta={'page': 1, 'parcel_id': response.meta['parcel_id']},
        #             dont_filter=True,
        #             headers=self.HEADERS,
        #         )
        #
        #     # If at this point we still haven't been able to download the last property sale
        #     # date, let's go explicitly to the sales page and parse it from there.
        #     # If we can parse it earlier on, skipping this step will allow our scrapes
        #     # to go faster
        #
        #     if not hasattr(self, 'date_pulled_this_search'):
        #         self.parsed_data = {}
        #         self.parsed_data['ctl00$ToolkitScriptManager1'] = 'ctl00$UpdatePanel1|ctl00$ContentPlaceHolderContent$lbSalesHistory'
        #         self.parsed_data['__EVENTTARGET'] = "ctl00$ContentPlaceHolderContent$lbSalesHistory"
        #         self.parsed_data['__EVENTARGUMENT'] = ""
        #         self.parsed_data['__LASTFOCUS'] = ""
        #         self.parsed_data['__VIEWSTATE'] = response.css('input#__VIEWSTATE::attr(value)').extract_first(),
        #         self.parsed_data['__EVENTVALIDATION'] = response.css('input#__EVENTVALIDATION::attr(value)').extract_first(),
        #         self.parsed_data['ctl00$ContentPlaceHolderContent$ddlTaxYear'] = '2017',
        #         self.parsed_data['__ASYNCPOST'] = 'true',
        #
        #         yield scrapy.FormRequest(
        #                 url=response.request.url,
        #                 method='POST',
        #                 callback=self.parse_sale,
        #                 formdata=self.parsed_data,
        #                 meta={'page': 1, 'parcel_id': response.meta['parcel_id']},
        #                 dont_filter=True,
        #                 headers=self.HEADERS,
        #             )
        #
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
        #
