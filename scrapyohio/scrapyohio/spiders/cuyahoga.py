import json
import re
from _decimal import InvalidOperation

import scrapy

from ohio import settings
from propertyrecords import models, utils
from bs4 import BeautifulSoup


HEADERS = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, "
                          "like Gecko) Chrome/70.0.3538.102 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "X-MicrosoftAjax": "Delta=true"
            }

HEADERS.update(settings.CONTACT_INFO_HEADINGS)


class WarrenSpider(scrapy.Spider):
    name = 'cuyahoga'
    allowed_domains = ['myplace.cuyahogacounty.us']

    def retrieve_all_warren_county_urls(self):
        self.cuyahoga_county_object, created = models.County.objects.get_or_create(name="Cuyahoga")
        all_cuyahoga_properties = models.Property.objects.filter(county=self.cuyahoga_county_object)

        for property in all_cuyahoga_properties:
            yield f'''https://myplace.cuyahogacounty.us/{utils.convert_string_to_base64_bytes_object(property.parcel_number)}?city={utils.convert_string_to_base64_bytes_object('99')}&searchBy={utils.convert_string_to_base64_bytes_object('Parcel')}&dataRequested={utils.convert_string_to_base64_bytes_object('General Information')}'''


    def __init__(self):
        self.logged_out = False

    def start_requests(self):
       # Ensure we have a county in the database
        self.warren_county_object, created = models.County.objects.get_or_create(name="Cuyahoga")

        # We want to assign headers for each request triggered. Override the request object
        # sent over to include Lucia's contact information
        for url in self.retrieve_all_warren_county_urls():
            yield scrapy.Request(url, dont_filter=True,
                          headers=HEADERS
                          )

    def parse(self, response):
        """
        This method is responsible for downloading information for Cuyahoga
        records from the myplace.cuyahogacounty.us site.
        :param response:
        :return:
        """

        property_number = response.xpath(
            "/html[1]/body[1]/div[1]/div[3]/div[2]/div[1]/div[1]/div[4]/div[1]/ul[1]/li[1]/text()").extract()[
            0].strip().replace('-', '')

        property = models.Property.objects.get(parcel_number=property_number)

        """
        *date_sold - can find, but not super accurate
        !date_of_LLC_name_change - 
        *date_of_mortgage -can find, other site 
        *mortgage_amount -can find, other site  
        school_district - could be other site
        *tax_lien - unknown for both 
        *tax_lien_information_source -- unknown for both  
        !cauv_property -- UNKNOWN 
        """

        # GENERAL PAGE
        property.school_district_name = response.xpath('/html[1]/body[1]/div[1]/div[3]/div[2]/div[1]/div[1]/div[4]/div[2]/div[1]/div[2]/div[2]/text()').extract_first()
        property.tax_district = response.xpath("/html[1]/body[1]/div[1]/div[3]/div[2]/div[1]/div[1]/div[4]/div[2]/div[1]/div[1]/div[4]/text()").extract_first()
        try:
            property.land_use = utils.parse_ohio_state_use_code(response.xpath("/html[1]/body[1]/div[1]/div[3]/div[2]/div[1]/div[1]/div[4]/div[2]/div[1]/div[3]/div[2]/text()").extract_first())
        except ValueError:
            property.land_user = response.xpath("/html[1]/body[1]/div[1]/div[3]/div[2]/div[1]/div[1]/div[4]/div[2]/div[1]/div[3]/div[2]/text()").extract_first()
        property.legal_description = response.xpath("//div[@class='generalInfoValue col-lg-3']/text()").extract_first()
        property.primary_owner = response.xpath("/html[1]/body[1]/div[1]/div[3]/div[2]/div[1]/div[1]/div[4]/div[1]/ul[1]/li[2]/text()").extract_first().strip()
        property.property_rating = response.xpath("/html[1]/body[1]/div[1]/div[3]/div[2]/div[1]/div[1]/div[4]/div[2]/div[1]/div[2]/div[4]/text()").extract_first()
        property.save()

        # # Often will not exist, and will throw an IndexError if so
        # secondary_owner = response.xpath("//li[@class='liGreen']/text()").extract()[0].strip()
        #
        # # TAX BILL PAGE

        yield scrapy.Request(
            url=f'''https://myplace.cuyahogacounty.us/{utils.convert_string_to_base64_bytes_object(property.parcel_number)}?city={utils.convert_string_to_base64_bytes_object('99')}&searchBy={utils.convert_string_to_base64_bytes_object('Parcel')}&dataRequested={utils.convert_string_to_base64_bytes_object('Tax Bill')}''',
            method='GET',
            callback=self.parse_tax_page_information,
            dont_filter=True,
            headers=HEADERS
        )

    #### LAND PAGE
    #https://myplace.cuyahogacounty.us/MTAxMzcwMDE=?city=OTk=&searchBy=UGFyY2Vs&dataRequested=TGFuZA==
    # ACRES - response.xpath("/html[1]/body[1]/div[1]/div[3]/div[2]/div[1]/div[1]/div[4]/div[2]/div[2]/div[4]/div[4]/text()").extract()[0]
    #response.xpath("/html[1]/body[1]/div[1]/div[3]/div[2]/div[1]/div[1]/div[4]/div[2]/div[2]/div[4]/div[4]")

        yield scrapy.Request(
            url=f'''https://myplace.cuyahogacounty.us/{utils.convert_string_to_base64_bytes_object(
                property.parcel_number)}?city={utils.convert_string_to_base64_bytes_object(
                '99')}&searchBy={utils.convert_string_to_base64_bytes_object(
                'Parcel')}&dataRequested={utils.convert_string_to_base64_bytes_object('Land')}''',
            method='GET',
            callback=self.parse_land_information,
            dont_filter=True,
            headers=HEADERS
        )

        # yield scrapy.Request(
        #     url='https://recorder.cuyahogacounty.us/searchs/parcelsearchs.aspx',
        #     method='GET',
        #     callback=self.mortgage_finder,
        #     dont_filter=True,
        #     headers=HEADERS,
        # )
        #MORTGAGE AMOUNTS WE CAN SEE HERE
        # date_of_mortgage
        # mortgage_amount
        # date_sold
            # https://recorder.cuyahogacounty.us/searchs/parcelsearchs.aspx

        # SCHOOL DISTRICT: (* Requires VPN access)
        #https://thefinder.tax.ohio.gov/StreamlineSalesTaxWeb/default_SchoolDistrict.aspx
        # school_district

        # TAX INFO (* Requires VPN access)
        # Ideally would look by address, but zip code could provide a starting point. (zip + 4 digits would be ideal)


        # HOW COULD WE STORE LLC NAMES?
        # Call back to earlier tax years, and look at the name each year... record different primary
        # owner names as they exist.
        # date_of_LLC_name_change


    def parse_tax_page_information(self, response):
        """

        :param request:
        :return:
        """

        parcel_number = response.xpath(
            "/html[1]/body[1]/div[1]/div[3]/div[2]/div[1]/div[1]/div[4]/div[1]/div[1]/div[1]/div[6]/div[2]/text()").extract_first().replace(
            '-', '')
        soup = BeautifulSoup(response.body, 'html.parser')


        our_property = models.Property.objects.get(parcel_number=parcel_number)

        our_property.property_class = response.xpath("/html[1]/body[1]/div[1]/div[3]/div[2]/div[1]/div[1]/div[4]/div[1]/div[1]/div[1]/div[5]/div[2]/text()").extract_first()
        # ooc_string = str(soup.body.find_all(text=re.compile('Owner Occupancy Credit'))[1].find_next('td').contents[0])
        # our_property.owner_occupancy_indicated = utils.convert_y_n_to_boolean(ooc_string)
        our_property.owner_occupancy_indicated = utils.convert_y_n_to_boolean(response.xpath("//div[@class='taxDataBody']/div[1]/div[1]/div[3]/table/tr[2]/td[2]/text()").extract_first())

        tax_year = response.xpath("//div[@class='HeaderHighlight']/text()").extract_first().split(' ')[0]

        tax_values_object, created = models.TaxData.objects.get_or_create(property_record=our_property,
                                                                          tax_year=tax_year)
        try:
            tax_values_object.market_value = utils.convert_taxable_value_string_to_integer(soup.body.find(text=re.compile('Market Values')).parent.parent.parent.findAll('tr')[3].findAll('td')[1].contents[0])
            tax_values_object.taxable_value = utils.convert_taxable_value_string_to_integer(soup.body.find(text=re.compile('Assessed Values')).parent.parent.parent.findAll('tr')[3].findAll('td')[1].contents[0])
            tax_values_object.taxes_paid = utils.convert_taxable_value_string_to_integer(response.xpath("//div[@class='row']//div[3]//div[2]//b[1]/text()").extract()[0])
        except InvalidOperation:
            # tax_values_object.market_value = soup.body.find(text=re.compile('Market Values')).parent.parent.parent.findAll('tr')[3].findAll('td')[1].contents[0]
            # tax_values_object.taxable_value = soup.body.find(text=re.compile('Assessed Values')).parent.parent.parent.findAll('tr')[3].findAll('td')[1].contents[0]
            # tax_values_object.taxes_paid = response.xpath("//div[@class='row']//div[3]//div[2]//b[1]/text()").extract()[0]
            pass
        tax_values_object.save()

        property_address, created = models.PropertyAddress.objects.get_or_create(property = our_property)
        property_address_dict = utils.cuyahoga_addr_splitter(response.xpath("//div[@class='TaxBillSummaryHeadingTable']//div[2]//div[2]/text()").extract_first())
        property_address.primary_address_line = property_address_dict['primary_address']
        property_address.city = property_address_dict['city']
        property_address.state = property_address_dict['state']
        property_address.zipcode = property_address_dict['zipcode']
        property_address.save()

        tax_addr = response.xpath("//div[@class='TaxBillSummaryHeadingTable']//div[3]//div[2]/text()").extract_first()

        parsed_tax_result = utils.cuyahoga_tax_address_parser(tax_addr)

        tax_object, created = models.TaxAddress.objects.get_or_create(name=parsed_tax_result['primary_address_line'])
        tax_object.primary_address_line = parsed_tax_result['secondary_address_line']
        tax_object.city = parsed_tax_result['city']
        tax_object.state = parsed_tax_result['state']
        tax_object.zipcode = parsed_tax_result['zipcode']
        tax_object.save()

        our_property.tax_address = tax_object
        our_property.owner = response.xpath("/html[1]/body[1]/div[1]/div[3]/div[2]/div[1]/div[1]/div[4]/div[1]/div[1]/div[1]/div[1]/div[2]/text()").extract_first()
        our_property.save()

    def parse_land_information(self, response):

        parcel_number = response.xpath("/html[1]/body[1]/div[1]/div[3]/div[2]/div[1]/div[1]/div[4]/div[1]/ul[1]/li[1]/text()").extract_first().strip().replace('-', '')

        property_object = models.Property.objects.get(parcel_number=parcel_number)

        property_object.legal_acres = response.xpath("/html[1]/body[1]/div[1]/div[3]/div[2]/div[1]/div[1]/div[4]/div[2]/div[2]/div[4]/div[4]/text()").extract_first()
        property_object.save()

    def parse_transfers_info(self, response):

        parcel_number = response.xpath("/html[1]/body[1]/div[1]/div[3]/div[2]/div[1]/div[1]/div[4]/div[1]/ul[1]/li[1]/text()").extract_first().strip().replace('-', '')
        property_object = models.Property.objects.get(parcel_number=parcel_number)

    def mortgage_finder(self, response):
        from scrapy.utils.response import open_in_browser
        open_in_browser(response)

        # print('response!: ', response.body)

        self.data = {}
        self.data['ctl00$ToolkitScriptManager1'] = 'ctl00$UpdatePanel1|ctl00$ContentPlaceHolderContent$lbTaxInfo'
        self.data['__EVENTTARGET'] = "ctl00$ContentPlaceHolderContent$lbTaxInfo"
        self.data['__EVENTARGUMENT'] = ""
        self.data['__LASTFOCUS'] = ""
        self.data['__VIEWSTATE'] = response.css('input#__VIEWSTATE::attr(value)').extract_first(),
        self.data['__EVENTVALIDATION'] = response.css('input#__EVENTVALIDATION::attr(value)').extract_first(),
        self.data['ctl00$ContentPlaceHolderContent$ddlTaxYear'] = '2017',
        self.data['__ASYNCPOST'] = 'true',
        return self.data