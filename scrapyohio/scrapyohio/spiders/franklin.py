# -*- coding: utf-8 -*-
import datetime
import pickle

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
        # self.please_parse_these_items = models.Property.objects.filter(county=self.franklin_county_object).all()
        self.please_parse_these_items = models.Property.objects.filter(id__in=[3354426]).all()
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
                        meta={'dont_redirect': False, "parc_id": item['inpParid']},
                        dont_filter=True,
                        headers=self.HEADERS,
                    )

    def commercial_check(self, response):

        pickle_out = open("commercial.pickle", "wb")
        pickle.dump(response.body, pickle_out)
        pickle_out.close()

    def retrieve_info_to_parse(self, response):
        print("HI")
        # open_in_browser(response)

        # pickle_out = open("vaugn2tax.pickle", "wb")
        # pickle.dump(response.body, pickle_out)
        # pickle_out.close()
        #
        # soup = BeautifulSoup(response.body, 'html.parser')
        # table = soup.find('table', id="Owner")
        # rows = table.find_all('tr', recursive=False)
        # for row in rows:
        #     if (row.text.find("Calculated Acres") > -1):
        #         cell = row.findAll('td')[1]
        #         property_acres =  cell.get_text()
        #
        #
        # print("Looking at: ", response.xpath("//td[contains(text(),'ParcelID')]/text()"), " and expected: ", response.meta['parc_id'])
        # ITEMS THAT REMAIN!!!!
        # date_of_LLC_name_change
        # date_of_mortgage - NOT EASILY PARSED
        # mortgage_amount - NOT EASILY PARSED
        # property_rating - AVAILABLE FOR SOME COMMERCIAL PROPS

    # def land_parse(self, response):
    #     soup = BeautifulSoup(response.body, 'html.parser')
    #     table = soup.find('table', id="Land Characteristics")
    #     rows = table.find_all('tr', recursive=False)
    #     print("ROWS: ", type(rows))
    #     total_acreage = utils.calculate_total_number_of_acres(rows)
    #     print("ARRAY OF ACRES AL FINAL: ", total_acreage)

    def parse_transfer_data(self, response):
        # open_in_browser(response)
        # print("HI")
        parcel_number = response.meta['parcel_number']
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
                    print("Transfer Date: ", row_array[0], "Grantee: ", row_array[1], "conveyance_number", row_array[2],
                          "sale amount: ", row_array[5])
                except IndexError:
                    pass

        # pickle_out = open("transferdata.pickle", "wb")
        # pickle.dump(response.body, pickle_out)
        # pickle_out.close()


    def parse(self, response):
        """

        :param response:
        :return:
        """

        yield Request("http://property.franklincountyauditor.com/_web/Datalets/Datalet.aspx?sIndex=0&idx=1", dont_filter=True,
                      headers=self.HEADERS,
                      meta={"parc_id": response.meta['parc_id']
                            },
                      callback=self.retrieve_info_to_parse,
                      )

        yield Request("http://property.franklincountyauditor.com/_web/datalets/datalet.aspx?mode=sales_summary&sIndex=1&idx=1&LMparent=20",
                      dont_filter=True,
                      headers=self.HEADERS,
                      meta={"parc_id": response.meta['parc_id']
                            },
                      callback=self.parse_transfer_data,
                      )

        yield Request(
            "http://property.franklincountyauditor.com/_web/datalets/datalet.aspx?mode=commercial&sIndex=5&idx=18&LMparent=20",
            dont_filter=True,
            headers=self.HEADERS,
            meta={"parc_id": response.meta['parc_id']
                  },
            callback=self.commercial_check,
            )

        # yield Request("http://property.franklincountyauditor.com/_web/datalets/datalet.aspx?mode=land_summary&sIndex=0&idx=1&LMparent=20", dont_filter=True,
        #               headers=self.HEADERS,
        #               meta={"parc_id": response.meta['parc_id']
        #                     },
        #               callback=self.land_parse,
        #
        #               )
