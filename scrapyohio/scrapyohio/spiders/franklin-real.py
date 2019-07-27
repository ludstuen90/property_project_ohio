import csv
import datetime
import os

import pytz
import scrapy
from bs4 import BeautifulSoup

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

    name = 'franklin-real'
    allowed_domains = ['countyfusion5.kofiletech.us']
    start_urls = ['https://countyfusion5.kofiletech.us/countyweb/login.do']

    def __init__(self):
        self.HEADERS.update(settings.CONTACT_INFO_HEADINGS)
        self.logged_out = False

    def start_requests(self):
        self.franklin_county_object, created = models.County.objects.get_or_create(name="Franklin")

        scrape_apts_and_hotels_from_list = True

        if scrape_apts_and_hotels_from_list:
            list_of_parcel_ids = []
            script_dir = os.path.dirname(__file__)  # <-- absolute dir this current script is in
            rel_path = "../scraper_data_drops/franklin-apts-hotels.csv"  # <-- Look two directories up for relevant CSV files
            abs_file_path = os.path.join(script_dir, rel_path)

            with open(abs_file_path, encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile, delimiter=',')
                for number, row in enumerate(reader):
                    striped_parc_num = row['Parcel Number'].split('-')
                    list_of_parcel_ids.append(f'''{striped_parc_num[0]}{striped_parc_num[1]}''')
                    # list_of_parcel_ids.append(row['Parcel Number'])

            self.please_parse_these_items = models.Property.objects.filter(county=self.franklin_county_object,
                                                                     parcel_number__in=list_of_parcel_ids,
                                                                       last_scraped_two__isnull=True
                                                                     ).order_by('?')
        else:
            self.please_parse_these_items = models.Property.objects.filter(county=self.franklin_county_object,
                                                                           last_scraped_two__isnull=True)

        for number, property_to_parse in enumerate(self.please_parse_these_items):
            yield scrapy.FormRequest(
                url='https://countyfusion5.kofiletech.us/countyweb/login.do',
                headers= {
                    "Origin": "https://countyfusion5.kofiletech.us",
                    "Upgrade-Insecure-Requests": "1",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
                },
                formdata={
                    "CountyFusionForceNewSession": "true",
                    "apptype": "",
                        "cmd":"login",
                        "countyname": "Franklin",
                        "datasource": "",
                        "fraudsleuth": "false",
                        "guest": "true",
                        "password": "",
                        "public": "false",
                        "scriptsupport": "yes",
                        "startPage": "",
                        "userdatasource": "",
                        "username": "",
                },
                callback=self.parse,
                dont_filter=True,
                meta={'property_django_id': property_to_parse.id, 'cookiejar': number},
            )


    def save_mortgage_value(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        result_number = soup.find('span', text='Consideration:').find_next('td').text
        amount_to_save = result_number.strip()
        decimal_converted_amount = utils.convert_taxable_value_string_to_integer(amount_to_save)
        property_to_save = models.Property.objects.get(id=response.meta['property_django_id'])
        property_to_save.mortgage_amount = decimal_converted_amount
        property_to_save.last_scraped_two = datetime.datetime.now(pytz.utc)
        property_to_save.save()

    def open_function(self, response):
        instid = utils.franklin_real_value_finder(response.text, 'instId')
        instnum = utils.franklin_real_value_finder(response.text, 'instNum')
        insttype = utils.franklin_real_value_finder(response.text, 'instType')
        for number, property_record in enumerate(insttype):
            if property_record == 'MORTGAGE':
                property_record = {
                    'instid': instid[number],
                    'instnum': instnum[number],
                    'insttype': insttype[number]
                }

                yield scrapy.Request(
                    url=f'''https://countyfusion5.kofiletech.us/countyweb/search/displayDocument.do?searchSessionId=searchJobMain&instId={instid[number]}&instNum={instnum[number]}&instType={insttype[number]}&assocDoc=undefined&assocParentNum=undefined&parcelNum=undefined&assocType=undefined&onloadAction=parent.documentLoaded();''',
                    method='GET',
                    callback=self.save_mortgage_value,
                    meta={'parcel_info': property_record,
                          'property_django_id': response.meta['property_django_id'],
                          'cookiejar': response.meta['cookiejar']
                          },
                    dont_filter=True,
                    headers=self.HEADERS
                )
                break

    def request_results_page(self, response):

        yield scrapy.Request(
            url=f'''https://countyfusion5.kofiletech.us/countyweb/search/Franklin/docs_SearchResultList.jsp?scrollPos=0&searchSessionId=searchJobMain''',
            method='GET',
            callback=self.open_function,
            meta={'property_django_id': response.meta['property_django_id'], 'cookiejar': response.meta['cookiejar']},
            dont_filter=True,
            headers=self.HEADERS,
        )

    def parse(self, response):
        """

        :param response:
        :return:
        """
        parse_prop = self.please_parse_these_items = models.Property.objects.get(id=response.meta['property_django_id'])
        yield scrapy.FormRequest(
            url='https://countyfusion5.kofiletech.us/countyweb/search/searchExecute.do?assessor=false',
            headers={
                "Origin": "https://countyfusion5.kofiletech.us",
                "Upgrade-Insecure-Requests": "1",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            },
            formdata={
                "ALLNAMES": "",
                   "CASETYPE": "",
                   "DATERANGE": '[{"name": "TODATE", "value": "User Defined"}]',
                   "FROMDATE": "",
                   "INSTTYPE": "ADLC,ADMO,AMAR,AMLC,AMMO,AC,AR,ASVL,ASSUM,LC,MMO,MDAR,MDLC,MDMO,MO,RFMO,RRADLC,RRADMO,"
                               "RRAMAR,RRAMLC,RRAMMO,RRAC,RRAR,RRASSUM,RRLC,RRMDAR,RRMDLC,RRMDMO,RRMO,RRFRMO,RRSUAR,"
                               "RRSULC,RRSUMO,RRSUVL,RRTR,RRWPLC,RRWPMO,RRWPVL,SUAR,SULC,SUMO,SUVL,WPLC,WPMO,WPVL",
                   "INSTTYPEALL": "false",
                   "MAXPRICE": "",
                   "MINPRICE": "",
                   "ORDERBY_LIST": "",
                    "PARCELNUM": f'''{parse_prop.parcel_number[0:3]}-{parse_prop.parcel_number[3:]}''',
                   "PARTY": "both",
                   "PLATS": "",
                   "QUARTER": "",
                   "RECSPERPAGE": "15",
                   "REMOVECHARACTERS": "true",
                   "SEARCHTYPE": "allNames",
                   "SELECTEDNAMES": "",
                   "TODATE": "",
                   "daterange_TODATE": "User Defined",
                   "searchCategory": "ADVANCED",
                   "searchSessionId": "searchJobMain",
                   "userRefCode": ""
            },
            callback=self.request_results_page,
            dont_filter=True,
            meta={'property_django_id': response.meta['property_django_id'], 'cookiejar': response.meta['cookiejar']},
        )

