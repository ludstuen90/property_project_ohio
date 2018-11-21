# -*- coding: utf-8 -*-
import datetime

import scrapy
from scrapy import Request, FormRequest
from propertyrecords import utils, models

HEADERS = {
            "Info": "The Ohio Center for Investigative Journalism, Eye on Ohio, is requesting these public records for "
                    "use in a journalism project, and to conserve valuable public funds and government employees' time "
                    "instead of filing multiple freedom of information act requests.",
            "Questions": "If you have questions or concerns, please contact Lucia Walinchus at 646-397-7761 or "
                         "Lucia[the at symbol}eyeonohio.com.",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, "
                          "like Gecko) Chrome/70.0.3538.102 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "X-MicrosoftAjax": "Delta=true"
            }


temp_var_address_search = 6150660
#f'''http://www.co.warren.oh.us/property_search/summary.aspx?account_nbr={temp_var_address_search}'''


class WarrenSpider(scrapy.Spider):
    name = 'warren'
    allowed_domains = ['co.warren.oh.us']
    start_urls = [f'''http://www.co.warren.oh.us/property_search/summary.aspx?account_nbr={temp_var_address_search}''']
    # 1407775 - cauv
    # 6150660 - jas jenn smith
    # 551305 - settlers walk
    # 551865 -tatco dev tax
    # 552375 - tanglewood creek assoc
    # 551577 - LGHOA
    # 551571 - OWNERS IN COMMON

    def start_requests(self):
        # We want to assign headers for each request triggered. Override the request object
        # sent over to include Lucia's contact information
        for url in self.start_urls:
            yield Request(url, dont_filter=True,
                          headers=HEADERS
                          )

    def parse(self, response):
        """

        :param response:
        :return:
        """

        self.property, self.was_prp_created = models.Property.objects.update_or_create(parcel_number=response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryParcelID']/text()").extract()[0])
        self.property.legal_acres = utils.convert_acres_to_integer(response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryLegalDesc']/text()").extract()[1])
        self.property.legal_description = response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryLegalDesc']/text()").extract()[0][0]
        self.property.owner = response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryCurrentOwner']/text()").extract()[0]

        try:
            self.property.date_sold = datetime.datetime.strptime(response.xpath("//span[@id='ContentPlaceHolderContent_lblSingleResSaleDate']/text()").extract()[0], '%m/%d/%Y')

        except IndexError:
            pass

        self.property.land_use = utils.parse_ohio_state_use_code(response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryStateUseCode']/text()").extract()[0])
        self.property.tax_district = response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryTaxDistrict']/text()").extract()[0]
        self.property.school_district = int(response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryOhioSchoolDistNumber']/text()").extract()[0])
        self.property.school_district_name = response.xpath("//span[@id='ContentPlaceHolderContent_lblSummarySchoolDistrict']/text()").extract()[0]
        self.property.current_market_value = utils.convert_taxable_value_string_to_integer(response.xpath("//span[@id='ContentPlaceHolderContent_lblValSumTotalTrue']/text()").extract()[0])
        self.property.taxable_value = utils.convert_taxable_value_string_to_integer(response.xpath("//span[@id='ContentPlaceHolderContent_lblValSumTotalAssessed']/text()").extract()[0])
        self.property.year_2017_taxes = utils.convert_taxable_value_string_to_integer(response.xpath("//span[@id='ContentPlaceHolderContent_lblTaxSumTotChargeNetTax']/text()").extract()[0])
        self.property.property_address = utils.parse_address(response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryPropAddress']/text()").extract(), False)


        # TEMPROARILY SET UNKNOWN VALUES:
        # --  tax_lien = respon     se.xpath("/text()").extract()
        self.property.tax_lien = True
        # -- cauv_property = response.xpath("/text()").extract()

        self.property.cauv_property = utils.cauv_parser(response.xpath("//span[@id='ContentPlaceHolderContent_lblValSumCAUVTrue']/text()").extract()[0])
        # self.property.cauv_property = True

        try:
            self.property.owner_occupancy_indicated = utils.convert_y_n_to_boolean(response.xpath("//span[@id='ContentPlaceHolderContent_lblSingleResOwnerOccupied']/text()").extract()[0])
        except IndexError:
            # There are many reasons a property might not be owner occupied... if it's an office building,
            # for example. This field will be False unless we found an owner occupied indication or tax credit
            self.property.owner_occupancy_indicated = False

        # -- owner_address = response.xpath("/text()").extract()
        self.property.owner_address_id = 2
        # -- date_of_LLC_name_change = response.xpath("/text()").extract()

        # try:
        #     self.new_property.date_of_LLC_name_change = datetime.datetime.strptime(
        #         response.xpath("//span[@id='ContentPlaceHolderContent_lblSingleResSaleDate']/text()").extract()[0],
        #         '%m/%d/%Y')
        #     # -- date_of_mortgage = response.xpath("/text()").extract()
        #     self.new_property.date_of_mortgage = datetime.datetime.strptime(
        #         response.xpath("//span[@id='ContentPlaceHolderContent_lblSingleResSaleDate']/text()").extract()[0],
        #         '%m/%d/%Y')
        # except IndexError:
        #     pass
        # -- mortgage_amount = response.xpath("/text()").extract()
        self.property.mortgage_amount = utils.convert_taxable_value_string_to_integer('$1,999,999')
        # ?? self.new_property.property_class = response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryStateUseCode']/text()").extract()[0]
        self.property.property_class = 3



        self.data = {}
        self.data['ctl00$ToolkitScriptManager1'] = 'ctl00$UpdatePanel1|ctl00$ContentPlaceHolderContent$lbTaxInfo'
        self.data['__EVENTTARGET'] = "ctl00$ContentPlaceHolderContent$lbTaxInfo"
        self.data['__EVENTARGUMENT'] = ""
        self.data['__LASTFOCUS'] = ""
        self.data['__VIEWSTATE'] = response.css('input#__VIEWSTATE::attr(value)').extract_first(),
        self.data['__EVENTVALIDATION'] = response.css('input#__EVENTVALIDATION::attr(value)').extract_first(),
        self.data['ctl00$ContentPlaceHolderContent$ddlTaxYear'] = '2017',
        self.data['__ASYNCPOST'] = 'true',

        return FormRequest(
                url=f'''http://www.co.warren.oh.us/property_search/summary.aspx?account_nbr={temp_var_address_search}''',
                method='POST',
                callback=self.parse_page,
                formdata=self.data,
                meta={'page': 1},
                dont_filter=True,
                headers=HEADERS
            )

    def parse_page(self, response):

        # current_page = response.meta['page'] + 1
        returned_tax_address = response.css("div.wrapper div.rightContent:nth-child(4) div:nth-child(1) fieldset::text").extract()
        parsed_address = utils.parse_tax_address_from_css(returned_tax_address)
        # FIND IF TAX ADDRESS EXISTS, IF NOT CREATE
        if len(parsed_address) == 1:
            try:
                tax_record = models.TaxAddress.objects.get(primary_address_line=parsed_address[0])
            except models.TaxAddress.DoesNotExist:
                tax_record = models.TaxAddress(tax_address=parsed_address)
                tax_record.save()
        else:
            try:
                tax_record = models.TaxAddress.objects.get(primary_address_line=parsed_address[1])
            except models.TaxAddress.DoesNotExist:
                tax_record = models.TaxAddress(tax_address=parsed_address)
                tax_record.save()
        self.property.tax_address = tax_record
        self.property.save()

        # Do the work to also create a property address. Must come after property record is saved because
        # We need the ID to be able to access the property record

        self.property_address, self.was_prp_address_created = models.PropertyAddress.objects.get_or_create(property_id=self.property.id)
        self.property_address.primary_address_line = self.property.property_address['primary_address_line']
        self.property_address.city = self.property.property_address['city']
        self.property_address.zipcode = self.property.property_address['zipcode']
        self.property_address.state = self.property.property_address['state']
        try:
            if self.property.secondary_address_line:
                self.property_address.secondary_address_line = self.property.property_address['secondary_address_line']
        except AttributeError:
            pass
        self.property_address.save()

        # parse agents (TODO: yield items instead of printing)
        # for agent in response.xpath('//a[@class="regtext"]/text()'):
        #     print
        #     agent.extract()

