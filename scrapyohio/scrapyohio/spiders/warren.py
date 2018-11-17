# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request, FormRequest
from propertyrecords import utils


HEADERS = {
            "Info": "Request made as part of an Eye on Ohio Journalism project.",
            "Questions": "With questions, contact Lucia Walinchus at lucia@eyeonohio.com.",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, "
                          "like Gecko) Chrome/70.0.3538.102 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "X-MicrosoftAjax": "Delta=true"
            }


class WarrenSpider(scrapy.Spider):
    name = 'warren'
    allowed_domains = ['co.warren.oh.us']
    start_urls = ['http://www.co.warren.oh.us/property_search/summary.aspx?account_nbr=6150660']

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
        parcel_number = response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryParcelID']/text()").extract()
        legal_acres = response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryLegalDesc']/text()").extract()
        legal_description = response.xpath("/text()").extract()
        owner = response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryCurrentOwner']/text()").extract()
        date_sold = response.xpath("//span[@id='ContentPlaceHolderContent_lblSingleResSaleDate']/text()").extract()
        # date_of_LLC_name_change = response.xpath("/text()").extract()
        # date_of_mortgage = response.xpath("/text()").extract()
        # mortgage_amount = response.xpath("/text()").extract()
        property_class = response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryStateUseCode']/text()").extract()
        # land_use = response.xpath("/text()").extract()
        tax_district = response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryTaxDistrict']/text()").extract()
        school_district = response.xpath("//span[@id='ContentPlaceHolderContent_lblSummarySchoolDistrict']/text()").extract()
        # tax_lien = response.xpath("/text()").extract()
        # cauv_property = response.xpath("/text()").extract()
        # rental_registration = response.xpath("/text()").extract()
        current_market_value = response.xpath("//span[@id='ContentPlaceHolderContent_lblValSumTotalTrue']/text()").extract()
        taxable_value = response.xpath("//span[@id='ContentPlaceHolderContent_lblValSumTotalAssessed']/text()").extract()
        year_2017_taxes = response.xpath("//span[@id='ContentPlaceHolderContent_lblTaxSumTotChargeNetTax']/text()").extract()
        # tax_address = response.xpath("/text()").extract()
        # owner_address = response.xpath("/text()").extract()

        property_address = response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryPropAddress']/text()").extract()

        print('!!! HERE OUR PROPERTY INFO: !!!!!!!!!!!', owner, property_address, parcel_number, legal_acres,
            legal_description,
            date_sold,
            property_class,
            tax_district,
            school_district,
            current_market_value,
            taxable_value,
            year_2017_taxes
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
                url='http://www.co.warren.oh.us/property_search/summary.aspx?account_nbr=6150660',
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
        print("RETURNED TAX: ", returned_tax_address)
        utils.parse_tax_address_from_css(returned_tax_address)

        # parse agents (TODO: yield items instead of printing)
        # for agent in response.xpath('//a[@class="regtext"]/text()'):
        #     print
        #     agent.extract()

