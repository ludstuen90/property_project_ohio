# -*- coding: utf-8 -*-
import datetime

import scrapy
from scrapy import Request, FormRequest, signals

from ohio import settings
from propertyrecords import utils, models
import json

from scrapyohio.scraper_helpers import warren_mortgage

HEADERS = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, "
                          "like Gecko) Chrome/70.0.3538.102 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "X-MicrosoftAjax": "Delta=true",
            'Content-Type': 'multipart/form-data'
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

        print('response: ', response.body)
        print(response.css('input::attr(value)').extract())
        self.data = {}
        self.data['__EVENTTARGET']= ''
        self.data['__EVENTARGUMENT']= ''
        self.data['__VIEWSTATE'] = response.css('input#__VIEWSTATE::attr(value)').extract_first(),
        self.data['__VIEWSTATEGENERATOR']= response.css("input#__VIEWSTATEGENERATOR::attr(value)").extract_first()
        self.data['__EVENTVALIDATION'] = response.css("input#__EVENTVALIDATION::attr(value)").extract_first()
        self.data['PageNum']= ''
        self.data['SortBy']= response.css("input#SortBy::attr(value)").extract_first()
        self.data['SortDir']= response.css("input#SortDir::attr(value)").extract_first()
        self.data['PageSize']= response.css("input#PageSize::attr(value)").extract_first()
        self.data['hdCriteria'] = 'yrblt|1999~2000'
        self.data['hdLastState'] = response.css("input#hdLastState::attr(value)").extract_first()
        self.data['hdSelectedQuery'] = response.css("input#hdSelectedQuery::attr(value)").extract_first()
        self.data['hdSearchType'] = response.css("input#hdSearchType::attr(value)").extract_first()
        self.data['hdCriterias'] = response.css('input#hdCriterias::attr(value)').extract_first()
        self.data['ctl01$dlGroups'] = '4'
        self.data['ctl01_cal1_dateInput_ClientState'] = json.dumps({"minDateStr":"1900-01-01-00-00-00","maxDateStr":"2099-12-31-00-00-00"})
        self.data['ctl01_cal1_calendar_SD'] = response.css("input#ctl01_cal1_calendar_SD::attr(value)").extract_first()
        self.data['ctl01_cal1_calendar_AD'] = json.dumps([['1900', '1', '1'], ['2099', '12', '30'], ['2018', '11', '27']])
        self.data['ctl01_cal1_ClientState'] = json.dumps({"minDateStr": "1900-01-01-00-00-00", "maxDateStr": "2099-12-31-00-00-00"})
        self.data['ctl01_cal2_dateInput_ClientState'] = json.dumps({"enabled":True,"emptyMessage":"","validationText":"","valueAsString":"","minDateStr":"1900-01-01-00-00-00","maxDateStr":"2099-12-31-00-00-00","lastSetTextBoxValue":""})
        self.data['ctl01_cal2_calendar_SD'] = response.css("input#ctl01_cal2_calendar_SD::attr(value)").extract_first()
        self.data['ctl01_cal2_calendar_AD'] = json.dumps([['1900', '1', '1'], ['2099', '12', '30'], ['2018', '11', '27']])
        self.data['ctl01_cal2_ClientState']= json.dumps({"minDateStr": "1900-01-01-00-00-00", "maxDateStr": "2099-12-31-00-00-00"})

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
        # print("REsponse is: ", response.body)