# -*- coding: utf-8 -*-
import datetime

import scrapy
from scrapy import Request, FormRequest
from propertyrecords import utils, models

HEADERS = {
            "Info": "Request made as part of an Eye on Ohio Journalism project.",
            "Questions": "With questions, contact Lucia Walinchus at lucia@eyeonohio.com.",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, "
                          "like Gecko) Chrome/70.0.3538.102 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "X-MicrosoftAjax": "Delta=true"
            }


temp_var_address_search = 6150660

class WarrenSpider(scrapy.Spider):
    name = 'warren'
    allowed_domains = ['co.warren.oh.us']
    start_urls = [f'''http://www.co.warren.oh.us/property_search/summary.aspx?account_nbr={temp_var_address_search}''']
    # 611341
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
        self.new_property = models.Property()
        self.new_property.parcel_number = response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryParcelID']/text()").extract()[0]
        self.new_property.legal_acres = utils.convert_acres_to_integer(response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryLegalDesc']/text()").extract()[1])
        self.new_property.legal_description = response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryLegalDesc']/text()").extract()[0][0]
        self.new_property.owner = response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryCurrentOwner']/text()").extract()[0]
        self.new_property.date_sold = datetime.datetime.strptime(response.xpath("//span[@id='ContentPlaceHolderContent_lblSingleResSaleDate']/text()").extract()[0], '%m/%d/%Y')
        # -- date_of_LLC_name_change = response.xpath("/text()").extract()
        # -- date_of_mortgage = response.xpath("/text()").extract()
        # -- mortgage_amount = response.xpath("/text()").extract()
        self.new_property.property_class = response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryStateUseCode']/text()").extract()[0]
        self.new_property.land_use = response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryStateUseCode']/text()").extract()[0]
        self.new_property.tax_district = response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryTaxDistrict']/text()").extract()[0]
        self.new_property.school_district = response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryOhioSchoolDistNumber']/text()").extract()[0]
        # --  tax_lien = response.xpath("/text()").extract()
        # -- cauv_property = response.xpath("/text()").extract()
        # --  rental_registration = response.xpath("/text()").extract()
        self.new_property.current_market_value = response.xpath("//span[@id='ContentPlaceHolderContent_lblValSumTotalTrue']/text()").extract()[0]
        self.new_property.taxable_value = utils.convert_taxable_value_string_to_integer(response.xpath("//span[@id='ContentPlaceHolderContent_lblValSumTotalAssessed']/text()").extract()[0])
        self.new_property.year_2017_taxes = response.xpath("//span[@id='ContentPlaceHolderContent_lblTaxSumTotChargeNetTax']/text()").extract()[0]
        # tax_address = response.xpath("/text()").extract() RETRIEVED BELOW
        # -- owner_address = response.xpath("/text()").extract()

        self.new_property.property_address = response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryPropAddress']/text()").extract()[0]

        print('!!! HERE OUR PROPERTY INFO: !!!!!!!!!!!', self.new_property.owner, self.new_property.property_address, self.new_property.parcel_number,
              '?!?!?!?!', self.new_property.legal_acres, '#######',
            self.new_property.legal_description,
            self.new_property.date_sold,
            self.new_property.land_use,
            self.new_property.property_class,
            self.new_property.tax_district,
            self.new_property.school_district,
            self.new_property.current_market_value,
            self.new_property.taxable_value,
            self.new_property.year_2017_taxes
            )

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
        self.new_property.address = parsed_address
        self.new_property.save()
        print("!!!!!! BELOW WE CAN ACCESS: ", self.new_property)
        print(f'''!!!!! PARSED: {parsed_address} ''')

        # parse agents (TODO: yield items instead of printing)
        # for agent in response.xpath('//a[@class="regtext"]/text()'):
        #     print
        #     agent.extract()

