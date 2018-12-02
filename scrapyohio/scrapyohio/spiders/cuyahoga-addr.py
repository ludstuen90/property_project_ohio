
import json
import re

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
    name = 'cuyahoga-addr'
    allowed_domains = ['treasurer.cuyahogacounty.us']

    def retrieve_all_warren_county_urls(self):
        self.cuyahoga_county_object, created = models.County.objects.get_or_create(name="Cuyahoga")
        # all_cuyahoga_properties = models.Property.objects.filter(county=self.cuyahoga_county_object).order_by('?')[:20]
        all_cuyahoga_properties = models.Property.objects.filter(parcel_number='00338375')
        # all_cuyahoga_properties = models.Property.objects.filter(parcel_number='67111244')

        for property in all_cuyahoga_properties:
            yield f'''https://myplace.cuyahogacounty.us/{utils.convert_string_to_base64_bytes_object(property.parcel_number)}?city={utils.convert_string_to_base64_bytes_object('99')}&searchBy={utils.convert_string_to_base64_bytes_object('Parcel')}&dataRequested={utils.convert_string_to_base64_bytes_object('Tax Bill')}'''


        # yield "https://treasurer.cuyahogacounty.us/payments/real_prop/parcel_data.asp?txtParcel=00522056&year=2017"
        #https://myplace.cuyahogacounty.us/MTAxMzcwMDE=?city=OTk=&searchBy=UGFyY2Vs&dataRequested=R2VuZXJhbCBJbmZvcm1hdGlvbg==
        #https://myplace.cuyahogacounty.us/MDAzMDI0MzM=?city=OTk=&searchBy=UGFyY2Vs&dataRequested=R2VuZXJhbCBJbmZvcm1hdGlvbg==
        #MDAzMDI0MzM=
        # SECONDARY OWNER PROPERTY -- general information page appears different
        #00302433


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

        :param response:
        :return:
        """
        # soup = BeautifulSoup(response.body, 'html.parser')
        #
        # property_number = response.xpath(
        #     "/html[1]/body[1]/div[1]/div[3]/div[2]/div[1]/div[1]/div[4]/div[1]/ul[1]/li[1]/text()").extract()[
        #     0].strip().replace('-', '')
        #
        # property = models.Property.objects.get(parcel_number=property_number)

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
        addr_strp = response.xpath("//div[@class='TaxBillSummaryHeadingTable']//div[2]//div[2]/text()").extract_first().strip()

        not_strp = response.xpath("//div[@class='TaxBillSummaryHeadingTable']//div[2]//div[2]/text()").extract_first()
        print("This  prop addr is: ", not_strp)

        import pickle
        pickle.dump(not_strp, open("save.p", "wb"))


        # for item in addr_strp:
        #     print(item)

        # print(utils.cuyahoga_county_prop_addr_parser(not_strp))

        # GENERAL PAGE
        # property.school_district_name = response.xpath('/html[1]/body[1]/div[1]/div[3]/div[2]/div[1]/div[1]/div[4]/div[2]/div[1]/div[2]/div[2]/text()').extract_first()
        # property.tax_district = response.xpath("/html[1]/body[1]/div[1]/div[3]/div[2]/div[1]/div[1]/div[4]/div[2]/div[1]/div[1]/div[4]/text()").extract_first()
        # property.land_use = utils.parse_ohio_state_use_code(response.xpath("/html[1]/body[1]/div[1]/div[3]/div[2]/div[1]/div[1]/div[4]/div[2]/div[1]/div[3]/div[2]/text()").extract_first())
        # property.legal_description = response.xpath("//div[@class='generalInfoValue col-lg-3']/text()").extract_first()
        # property.primary_owner = response.xpath("/html[1]/body[1]/div[1]/div[3]/div[2]/div[1]/div[1]/div[4]/div[1]/ul[1]/li[2]/text()").extract_first().strip()
        # property.save()

        # # Often will not exist, and will throw an IndexError if so
        # secondary_owner = response.xpath("//li[@class='liGreen']/text()").extract()[0].strip()
        #
        # # TAX BILL PAGE

        # yield scrapy.Request(
        #     url=f'''https://myplace.cuyahogacounty.us/{utils.convert_string_to_base64_bytes_object(property.parcel_number)}?city={utils.convert_string_to_base64_bytes_object('99')}&searchBy={utils.convert_string_to_base64_bytes_object('Parcel')}&dataRequested={utils.convert_string_to_base64_bytes_object('Tax Bill')}''',
        #     method='GET',
        #     callback=self.parse_tax_page_information,
        #     dont_filter=True,
        #     headers=HEADERS
        # )



    #### LAND PAGE
    #https://myplace.cuyahogacounty.us/MTAxMzcwMDE=?city=OTk=&searchBy=UGFyY2Vs&dataRequested=TGFuZA==
    # ACRES - response.xpath("/html[1]/body[1]/div[1]/div[3]/div[2]/div[1]/div[1]/div[4]/div[2]/div[2]/div[4]/div[4]/text()").extract()[0]
    #response.xpath("/html[1]/body[1]/div[1]/div[3]/div[2]/div[1]/div[1]/div[4]/div[2]/div[2]/div[4]/div[4]")


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



    # def parse_tax_page_information(self, response):
    #     """
    #
    #     :param request:
    #     :return:
    #     """
    #
    #     parcel_number = response.xpath(
    #         "/html[1]/body[1]/div[1]/div[3]/div[2]/div[1]/div[1]/div[4]/div[1]/div[1]/div[1]/div[6]/div[2]/text()").extract_first().replace(
    #         '-', '')
    #
    #     property = models.Property.objects.get(parcel_number=parcel_number)
    #
    #     property.property_class = response.xpath("/html[1]/body[1]/div[1]/div[3]/div[2]/div[1]/div[1]/div[4]/div[1]/div[1]/div[1]/div[5]/div[2]/text()").extract_first()
    #     property.owner_occupancy_credit = utils.convert_y_n_to_boolean(response.xpath("//div[@class='taxDataBody']/div[1]/div[1]/div[3]/table/tr[2]/td[2]/text()").extract_first())
    #     # property_address = response.xpath("//div[@class='TaxBillSummaryHeadingTable']//div[2]//div[2]/text()").extract()[0].strip()
    #     #
    #     # tax_address = response.xpath("//div[@class='TaxBillSummaryHeadingTable']//div[3]//div[2]/text()").extract()[0].strip()
    #     #
    #     # # TWO YEARS, IDEALLY:
    #     # tax_year = 2017# response.xpath("//div[@class='HeaderHighlight']/text()").extract()[0].split(' ')[0]
    #     # market_value = soup.body.find(text=re.compile('Market Values')).parent.parent.parent.findAll('tr')[3].findAll('td')[1].contents[0]
    #     # taxable_value = soup.body.find(text=re.compile('Assessed Values')).parent.parent.parent.findAll('tr')[3].findAll('td')[1].contents[0]
    #     # taxes_paid = response.xpath("//div[@class='row']//div[3]//div[2]//b[1]/text()").extract()[0]
    #     # property_record =  'a'  #LINK TO  PROP RECORD
    #     # # MARKET VALUES
    #     # Residential Condominium
    #     #
    #     #