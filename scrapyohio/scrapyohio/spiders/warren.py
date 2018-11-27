# -*- coding: utf-8 -*-
import datetime

import scrapy
from scrapy import Request, FormRequest, signals

from ohio import settings
from propertyrecords import utils, models

from scrapyohio.scraper_helpers import warren_mortgage


class WarrenSpider(scrapy.Spider):
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, "
                      "like Gecko) Chrome/70.0.3538.102 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "X-MicrosoftAjax": "Delta=true"
    }



    name = 'warren'
    allowed_domains = ['co.warren.oh.us', 'oh3laredo.fidlar.com']
    start_urls = [
        # 'http://www.co.warren.oh.us/property_search/summary.aspx?account_nbr=551571',
        # 'http://www.co.warren.oh.us/property_search/summary.aspx?account_nbr=1407775',
        'http://www.co.warren.oh.us/property_search/summary.aspx?account_nbr=551305',
        # 'http://www.co.warren.oh.us/property_search/summary.aspx?account_nbr=551865',
        # 'http://www.co.warren.oh.us/property_search/summary.aspx?account_nbr=552375',
        # 'http://www.co.warren.oh.us/property_search/summary.aspx?account_nbr=551577',
        # 'http://www.co.warren.oh.us/property_search/summary.aspx?account_nbr=551571',
        # 'http://www.co.warren.oh.us/property_search/summary.aspx?account_nbr=6150660',
    ]
    # 1407775 - cauv
    # 6150660 - jas jenn smith
    # 551305 - settlers walk
    # 551865 -tatco dev tax
    # 552375 - tanglewood creek assoc
    # 551577 - LGHOA
    # 551571 - OWNERS IN COMMON

    def __init__(self):
        self.HEADERS.update(settings.CONTACT_INFO_HEADINGS)
        self.logged_out = False

    def start_requests(self):

       # Ensure we have a county in the database
        self.warren_county_object, created = models.County.objects.get_or_create(name="Warren")

        # We want to assign headers for each request triggered. Override the request object
        # sent over to include Lucia's contact information
        for url in self.start_urls:
            yield Request(url, dont_filter=True,
                          headers=self.HEADERS
                          )

    def parse(self, response):
        """

        :param response:
        :return:
        """
        parsed_parcel_number = response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryParcelID']/text()").extract()[0]
        self.parsed_prop, created = models.Property.objects.get_or_create(parcel_number=parsed_parcel_number)
        self.parsed_prop.county = self.warren_county_object
        self.parsed_prop.parcel_number = parsed_parcel_number
        self.parsed_prop.legal_acres = utils.convert_acres_to_integer(response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryLegalDesc']/text()").extract()[1])
        self.parsed_prop.legal_description = response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryLegalDesc']/text()").extract()[0]
        self.parsed_prop.owner = response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryCurrentOwner']/text()").extract()[0]
        self.parsed_prop.land_use = utils.parse_ohio_state_use_code(response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryStateUseCode']/text()").extract()[0])
        self.parsed_prop.tax_district = response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryTaxDistrict']/text()").extract()[0]
        self.parsed_prop.school_district = int(response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryOhioSchoolDistNumber']/text()").extract()[0])
        self.parsed_prop.school_district_name = response.xpath("//span[@id='ContentPlaceHolderContent_lblSummarySchoolDistrict']/text()").extract()[0]

        self.parsed_prop.cauv_property = utils.cauv_parser(response.xpath("//span[@id='ContentPlaceHolderContent_lblValSumCAUVTrue']/text()").extract()[0])
        try:
            self.parsed_prop.owner_occupancy_indicated = utils.convert_y_n_to_boolean(
                response.xpath("//span[@id='ContentPlaceHolderContent_lblSingleResOwnerOccupied']/text()").extract()[0])
        except IndexError:
            # There are many reasons a property might not be owner occupied... if it's an office building,
            # for example. This field will be False unless we found an owner occupied indication or tax credit
            self.parsed_prop.owner_occupancy_indicated = False




        self.lookup_possibilities = [
                response.xpath("//span[@id='ContentPlaceHolderContent_lblSingleResSaleDate']/text()").extract(),
                response.xpath("//span[@id='ContentPlaceHolderContent_lblNoBldgLastSaleDate']/text()").extract(),
        ]

        for lookup in self.lookup_possibilities:
            #     # We might be seeing a property with multiple buildings, and therefore sales data will not be
            #     # available on home page. In this case, we'll need to make a separate request.
            #     # See:  https://github.com/ludstuen90/ohio/issues/70
            try:
                parsed_lookup = datetime.datetime.strptime(lookup[0], '%m/%d/%Y')
                self.parsed_prop.date_sold = parsed_lookup
                break
            except IndexError:
                continue

        self.parsed_prop.save()

        # Tax values, will be changed to be stored in a new table below:
        # Detect current year
        current_year = response.xpath("//span[@id='ContentPlaceHolderContent_lblcurrvalue']/text()").extract()[0][-4:]
        self.current_year_tax_values, created = models.TaxData.objects.update_or_create(
                                                                    tax_year=current_year,
                                                                    property_record_id = self.parsed_prop.id
        )
        self.current_year_tax_values.market_value = utils.convert_taxable_value_string_to_integer(response.xpath("//span[@id='ContentPlaceHolderContent_lblValSumTotalTrue']/text()").extract()[0])
        self.current_year_tax_values.taxable_value = utils.convert_taxable_value_string_to_integer(response.xpath("//span[@id='ContentPlaceHolderContent_lblValSumTotalAssessed']/text()").extract()[0])
        self.current_year_tax_values.taxes_paid = utils.convert_taxable_value_string_to_integer(response.xpath("//span[@id='ContentPlaceHolderContent_lblTaxSumTotChargeNetTax']/text()").extract()[0])
        self.current_year_tax_values.save()
        # End tax values

        # Parse pay next year tentative values
        next_year = response.xpath("//p[contains(text(),'TENTATIVE VALUE AS OF 01-01-2018')]/text()").extract()[0][-4:]
        self.next_year_tax_values, created = models.TaxData.objects.update_or_create(
                                                                    tax_year=next_year,
                                                                    property_record_id = self.parsed_prop.id
        )
        self.next_year_tax_values.market_value = utils.convert_taxable_value_string_to_integer(response.xpath("//span[@id='ContentPlaceHolderContent_lblTentValSumTotalTrue']/text()").extract()[0])
        self.next_year_tax_values.taxable_value = utils.convert_taxable_value_string_to_integer(response.xpath("//span[@id='ContentPlaceHolderContent_lblTentValSumTotalAssessed']/text()").extract()[0])
        self.next_year_tax_values.save()
        # End next year

        # Declare screen values so that we can parse other views if needed.
        self.data = {}
        self.data['ctl00$ToolkitScriptManager1'] = 'ctl00$UpdatePanel1|ctl00$ContentPlaceHolderContent$lbTaxInfo'
        self.data['__EVENTTARGET'] = "ctl00$ContentPlaceHolderContent$lbTaxInfo"
        self.data['__EVENTARGUMENT'] = ""
        self.data['__LASTFOCUS'] = ""
        self.data['__VIEWSTATE'] = response.css('input#__VIEWSTATE::attr(value)').extract_first(),
        self.data['__EVENTVALIDATION'] = response.css('input#__EVENTVALIDATION::attr(value)').extract_first(),
        self.data['ctl00$ContentPlaceHolderContent$ddlTaxYear'] = '2017',
        self.data['__ASYNCPOST'] = 'true',
        yield FormRequest(
                url=response.request.url,
                method='POST',
                callback=self.parse_tax,
                formdata=self.data,
                meta={'page': 1},
                dont_filter=True,
                headers=self.HEADERS,
            )

        # If at this point we still haven't been able to download the last property sale
        # date, let's go explicitly to the sales page and parse it from there.
        # If we can parse it earlier on, skipping this step will allow our scrapes
        # to go faster

        # if not self.parsed_prop.date_sold:
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
        #             meta={'page': 1},
        #             dont_filter=True,
        #             headers=self.HEADERS,
        #         )

    def parse_tax(self, response):
        self.parsed_prop = models.Property.objects.get(parcel_number=response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryParcelID']/text()").extract()[0])
        returned_tax_address = response.css("div.wrapper div.rightContent:nth-child(4) div:nth-child(1) fieldset::text").extract()
        parsed_address = utils.parse_tax_address_from_css(returned_tax_address)

        # FIND IF TAX ADDRESS EXISTS, IF NOT CREATE
        if len(parsed_address) == 1:
            try:
                tax_record = models.TaxAddress.objects.get(name=parsed_address[0])
            except models.TaxAddress.DoesNotExist:
                tax_record = models.TaxAddress(tax_address=parsed_address)
                tax_record.save()
        else:
            try:
                # Pass the parsed address through our name parser (in Tax Address model), to see
                # what it would look like. Then, compare with existing records to see if we have
                # one that matches.
                # If so, get the record. Otherwise, create it.
                self.dummy_obj = models.TaxAddress(tax_address=parsed_address)
                tax_record = models.TaxAddress.objects.get(primary_address_line=self.dummy_obj.primary_address_line)
            except models.TaxAddress.DoesNotExist:
                tax_record = models.TaxAddress(tax_address=parsed_address)
                tax_record.save()
        self.parsed_prop.tax_address = tax_record
        self.parsed_prop.save()

        # Do the work to also create a property address. Must come after property record is saved because
        # We need the ID to be able to access the property record

        address_to_parse = utils.parse_address(response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryPropAddress']/text()").extract(), False)
        self.property_address, self.was_prp_address_created = models.PropertyAddress.objects.get_or_create(property_id=self.parsed_prop.id)
        self.property_address.primary_address_line = address_to_parse['primary_address_line']
        self.property_address.city = address_to_parse['city']
        self.property_address.zipcode = address_to_parse['zipcode']
        self.property_address.state = address_to_parse['state']
        try:
            if self.parsed_prop.secondary_address_line:
                self.property_address.secondary_address_line = self.parsed_prop.property_address['secondary_address_line']
        except AttributeError:
            pass

        self.property_address.save()


    def parse_sale(self, response):
        """

        :return:
        """
        self.sale_date = print("DIR: ", dir(response))
        print("response::: ", response.body)
        self.sale_date = response.xpath("/html[1]/body[1]/form[1]/div[6]/div[1]/div[1]/div[2]/div[1]/div[1]/table[1]/tbody[1]/tr[2]/td[1]/text()").extract()
        print("!!!!SALE DATE: ", self.sale_date)
        for x in self.sale_date:
            print(x)
        print("type: ", type(self.sale_date))
        print("DIRTYPE: ", dir(self.sale_date))


        self.crawler.signals.connect(self.spider_idle, signal=signals.spider_idle)

    def spider_idle(self):
        # Wait until all records have downloaded, then trigger the mortgage download process
        if not self.logged_out:
            self.logged_out = True
            # a = warren_mortgage.WarrenMortgageInfo()
            # a.download_mortgage_info()
