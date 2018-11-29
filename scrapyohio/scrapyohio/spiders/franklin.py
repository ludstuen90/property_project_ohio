# -*- coding: utf-8 -*-
import datetime

import scrapy
from scrapy import Request, FormRequest, signals

from ohio import settings
from propertyrecords import utils, models
import json

from scrapyohio.scraper_helpers import warren_mortgage

HEADERS = {
            # "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, "
            #               "like Gecko) Chrome/70.0.3538.102 Safari/537.36",
            "X-MicrosoftAjax": "Delta=true",
                # 'Cookie': '_ga=GA1.2.155547435.1542057267; _gid=GA1.2.805851616.1543355211; ASP.NET_SessionId=dg5vzlamjnwqytemhmmqwez4; _gat=1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'es-AR,es;q=0.9,en-US;q=0.8,en;q=0.7,es-419;q=0.6',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            # 'Content-Length': '3055',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'property.franklincountyauditor.com',
            'Origin': 'http://property.franklincountyauditor.com',
            'Referer': 'http://property.franklincountyauditor.com/_web/search/advancedsearch.aspx?mode=advanced',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
            }

HEADERS.update(settings.CONTACT_INFO_HEADINGS)


class FranklinSpider(scrapy.Spider):
    name = 'franklin'
    allowed_domains = ['property.franklincountyauditor.com', ]

    # def retrieve_all_warren_county_urls(self):
    #     self.warren_county_object, created = models.County.objects.get_or_create(name="Warren")
    #
    #     self.please_parse_these_items = models.Property.objects.filter(county=self.warren_county_object)[:10]
    #
    #     for item in self.please_parse_these_items:
    #         url = f'''http://www.co.warren.oh.us/property_search/summary.aspx?account_nbr={item.account_number}'''
    #         yield url

    start_urls = ['http://property.franklincountyauditor.com/_web/search/advancedsearch.aspx?mode=advanced']

    # 1407775 - cauv
    # 6150660 - jas jenn smith
    # 551305 - settlers walk
    # 551865 -tatco dev tax
    # 552375 - tanglewood creek assoc
    # 551577 - LGHOA
    # 551571 - OWNERS IN COMMON

    def __init__(self):
        self.logged_out = False

    def start_requests(self):
       # Ensure we have a county in the database
        self.warren_county_object, created = models.County.objects.get_or_create(name="Franklin")

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
        print("HEADERS: ", HEADERS)

        print(response.css('input::attr(value)').extract())

        self.data = {}
        self.data['__EVENTTARGET'] = 'null'
        self.data['__EVENTARGUMENT'] = 'null'
        self.data['__VIEWSTATE'] = response.css('input#__VIEWSTATE::attr(value)').extract_first(),
        self.data['__VIEWSTATEGENERATOR'] = response.css("input#__VIEWSTATEGENERATOR::attr(value)").extract_first()
        self.data['__EVENTVALIDATION'] = response.css("input#__EVENTVALIDATION::attr(value)").extract_first()
        self.data['PageNum'] = 'null'
        self.data['PageSize'] = response.css("input#PageSize::attr(value)").extract_first()
        self.data['hdTaxYear']= 'null'
        self.data['hdAction'] = 'null'
        self.data['hdCriteriaLov'] = 'null'
        self.data['hdCriteriaTypes'] = 'N|C|N|N|C|C|C|C|N|C|D|N|C|C|C|C|C|N|N|N|C'
        self.data['hdReset'] = 'null'
        self.data['hdName'] = 'null'
        self.data['mode'] = 'null'
        self.data['hdListType'] = 'null'
        self.data['hdIndex'] = 'null'
        self.data['hdSelected'] = 'null'
        self.data['hdCriteriaGroup'] = 'null'
        # this should be boolean, false, but is stored as None... why?
        self.data['hdSelectAllChecked'] = 'false'
        self.data['sCriteria'] = '20'
        self.data['inpDistinct'] = 'on'
        self.data['ctl01$cal1'] = 'null'
        self.data['txtCrit'] = '1999'
        self.data['ctl01$cal2'] = ''
        self.data['ctl01$cal2$dateInput'] = 'null'
        self.data['SortBy']= response.css("input#SortBy::attr(value)").extract_first()
        self.data['SortDir']= response.css("input#SortDir::attr(value)").extract_first()
        self.data['PageSize']= response.css("input#PageSize::attr(value)").extract_first()
        self.data['hdCriteria'] = 'yrblt|1999~2000'
        self.data['hdLastState'] = response.css("input#hdLastState::attr(value)").extract_first()
        self.data['hdSelectedQuery'] = response.css("input#hdSelectedQuery::attr(value)").extract_first()
        self.data['hdSearchType'] = 'AdvSearch'
        self.data['hdCriterias'] = response.css('input#hdCriterias::attr(value)').extract_first()
        self.data['ctl01$dlGroups'] = '4'
        self.data['ctl01_cal1_dateInput_ClientState'] = response.css("input#ctl01_cal1_dateInput_ClientState::attr(value)").extract()
        self.data['ctl01_cal1_calendar_SD'] = response.css("input#ctl01_cal1_calendar_SD::attr(value)").extract_first()
        self.data['ctl01_cal1_calendar_AD'] = response.css("input#ctl01_cal1_calendar_AD::attr(value)").extract_first()
        self.data['ctl01$cal1$dateInput'] = 'null'
        self.data['ctl01_cal1_ClientState'] = response.css("input#ctl01_cal1_ClientState::attr(value)").extract()
        self.data['ctl01_cal2_dateInput_ClientState'] = response.css("input#ctl01_cal2_dateInput_ClientState::attr(value)").extract()
        self.data['ctl01_cal2_calendar_SD'] = response.css("input#ctl01_cal2_calendar_SD::attr(value)").extract()
        self.data['ctl01_cal2_calendar_AD'] = response.css("input#ctl01_cal2_calendar_AD::attr(value)").extract()
        self.data['ctl01_cal2_ClientState'] = response.css("input#ctl01_cal2_ClientState::attr(value)").extract()
        self.data['txtCrit2'] = response.css("input#txtCrit2::attr(value)").extract()
        self.data['txCriterias'] = response.css("input#txCriterias::attr(value)").extract()
        self.data['selSortBy'] = response.css("input#selSortBy::attr(value)").extract()
        self.data['selSortDir'] = response.css("input#selSortDir::attr(value)").extract()
        self.data['selPageSize'] = response.css("input#selPageSize::attr(value)").extract()
        self.data['searchOptions$hdBeta'] = 'null'

        # print("DID THIS PULL CORRECTLY: ", self.data['hdCriterias'] )
        print("self.data: ", self.data)
        yield FormRequest(
                url='http://property.franklincountyauditor.com/_web/search/advancedsearch.aspx?mode=advanced',
                method='POST',
                callback=self.parse_property_ids,
                formdata=self.data,
                meta={'page': 1},
                dont_filter=True,
                headers=HEADERS,
            )

    def parse_property_ids(self, response):
        """

        :return:
        """

        print("MADE It hERE: ", )
        from scrapy.utils.response import open_in_browser

        open_in_browser(response)
        # a = response.css("body.normalpage:nth-child(2) div.center:nth-child(7) div.contentpanel table:nth-child(2) tbody:nth-child(1) tr.SearchResults:nth-child(3) td:nth-child(3) > div:nth-child(1)::attr(value)").extract_first()
        a = response.xpath("/html[1]/body[1]/div[1]/div[3]/section[1]/div[1]/form[1]/table[1]/tbody[1]/tr[1]/td[1]/div[1]/div[1]/table[2]/tbody[1]/tr[1]/td[1]/table[1]/tbody[1]/tr[3]/td[1]/center[1]/table[2]/tbody[1]/tr[3]/td[3]/div[1]").extract()
        print("CAN WE GET A: ", a)
        print("REsponse status: ", response.status)
        print("REsponse is: ", response.body)