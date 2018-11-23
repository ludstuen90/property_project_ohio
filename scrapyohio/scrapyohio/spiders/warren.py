# -*- coding: utf-8 -*-

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


temp_var_address_search = 551571
#f'''http://www.co.warren.oh.us/property_search/summary.aspx?account_nbr={temp_var_address_search}'''


class WarrenSpider(scrapy.Spider):
    name = 'warren'
    allowed_domains = ['co.warren.oh.us']
    start_urls = [
        'http://www.co.warren.oh.us/property_search/summary.aspx?account_nbr=551571',
        'http://www.co.warren.oh.us/property_search/summary.aspx?account_nbr=1407775',
        'http://www.co.warren.oh.us/property_search/summary.aspx?account_nbr=551305',
        'http://www.co.warren.oh.us/property_search/summary.aspx?account_nbr=551865',
        'http://www.co.warren.oh.us/property_search/summary.aspx?account_nbr=552375',
        'http://www.co.warren.oh.us/property_search/summary.aspx?account_nbr=551577',
        'http://www.co.warren.oh.us/property_search/summary.aspx?account_nbr=551571',
        # 'http://www.co.warren.oh.us/property_search/summary.aspx?account_nbr=6150660',
    ]
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
        parsed_parcel_number = response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryParcelID']/text()").extract()[0]
        self.parsed_prop, created = models.Property.objects.get_or_create(parcel_number=parsed_parcel_number)

        self.parsed_prop.parcel_number = parsed_parcel_number
        self.parsed_prop.legal_acres = utils.convert_acres_to_integer(response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryLegalDesc']/text()").extract()[1])
        self.parsed_prop.legal_description = response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryLegalDesc']/text()").extract()[0]
        self.parsed_prop.owner = response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryCurrentOwner']/text()").extract()[0]
        self.parsed_prop.land_use = utils.parse_ohio_state_use_code(response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryStateUseCode']/text()").extract()[0])
        self.parsed_prop.tax_district = response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryTaxDistrict']/text()").extract()[0]
        self.parsed_prop.school_district = int(response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryOhioSchoolDistNumber']/text()").extract()[0])
        self.parsed_prop.school_district_name = response.xpath("//span[@id='ContentPlaceHolderContent_lblSummarySchoolDistrict']/text()").extract()[0]
        self.parsed_prop.mortgage_amount = utils.convert_taxable_value_string_to_integer('$1,999,999')

        self.parsed_prop.cauv_property = utils.cauv_parser(response.xpath("//span[@id='ContentPlaceHolderContent_lblValSumCAUVTrue']/text()").extract()[0])
        try:
            self.parsed_prop.owner_occupancy_indicated = utils.convert_y_n_to_boolean(
                response.xpath("//span[@id='ContentPlaceHolderContent_lblSingleResOwnerOccupied']/text()").extract()[0])
        except IndexError:
            # There are many reasons a property might not be owner occupied... if it's an office building,
            # for example. This field will be False unless we found an owner occupied indication or tax credit
            self.parsed_prop.owner_occupancy_indicated = False


        self.parsed_prop.date_sold = datetime.datetime.strptime(
            response.xpath("//span[@id='ContentPlaceHolderContent_lblSingleResSaleDate']/text()").extract()[0],
            '%m/%d/%Y')


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

        # #     self.new_property.date_of_mortgage = datetime.datetime.strptime(
        # #         response.xpath("//span[@id='ContentPlaceHolderContent_lblSingleResSaleDate']/text()").extract()[0],
        # #         '%m/%d/%Y')


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
                callback=self.parse_page,
                formdata=self.data,
                meta={'page': 1},
                dont_filter=True,
                headers=HEADERS,
            )

    def parse_page(self, response):

        self.parsed_prop = models.Property.objects.get(parcel_number=response.xpath("//span[@id='ContentPlaceHolderContent_lblSummaryParcelID']/text()").extract()[0])
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



