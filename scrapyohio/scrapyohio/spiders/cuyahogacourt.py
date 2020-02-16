# -*- coding: utf-8 -*-
import os
import re
import csv
from urllib.parse import urljoin

import scrapy
from bs4 import BeautifulSoup
from scrapy import FormRequest
from scrapy.utils.python import to_native_str
from scrapy.utils.response import open_in_browser

from ohio import settings


class CuyahogaCourtsScraper(scrapy.Spider):
    handle_httpstatus_all = True
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
        "Accept": "*/*",
        "X-MicrosoftAjax": "Delta=true",
        "X-Requested-With": "XMLHttpRequest",
        "Cache-Control": "no-cache",
        "Origin": "https://cpdocket.cp.cuyahogacounty.us",
        "Info": "The Ohio Center for Investigative Journalism, Eye on Ohio, is requesting these public records for "
        "use in a journalism project, and to conserve valuable public funds and government employees' time "
        "instead of filing multiple freedom of information act requests.",
        "Questions": "If you have questions or concerns, please contact Lucia Walinchus at 646-397-7761 or "
         "Lucia[the at symbol}eyeonohio.com.",
    }

    name = 'cuyahogacourt'
    allowed_domains = ['cpdocket.cp.cuyahogacounty.us']

    def retrieve_all_cuyahoga_county_urls(self):
        script_dir = os.path.dirname(__file__)  # <-- absolute dir this current script is in
        rel_path = "../../all_bor_cases.txt"
        rel_path_script = "../../all_bor_cases_results.txt"
        "/home/lukas/codigo/property_project_ohio/scrapyohio/scrapyohio/scraper_data_drops/Cuyahoga Land Bank Transfers.CSV"
        """
        
        f= open("/home/lukas/codigo/property_project_ohio/scrapyohio/cuyahoga_court_results.txt","r")
        
        array_of_known_ids = []
        items = csv.reader(f, delimiter=";")   
        
        for x in items: 
            print(x[0])
            array_of_known_ids.append(x[0])
        
        
        not_found_array = []
        with open("/home/lukas/codigo/property_project_ohio/scrapyohio/scrapyohio/scraper_data_drops/Cuyahoga Land Bank Transfers.CSV", "r") as file:
            reader = csv.reader(file)
            for row in reader:
                if row[4] not in array_of_known_ids:
                    not_found_array.append(row[4])
                 
        """
        abs_file_path = os.path.join(script_dir, rel_path)

        list_of_ids_already_processed = []
        abs_file_cuyahoga_path = os.path.join(script_dir, rel_path_script)
        with open(abs_file_cuyahoga_path, "r") as file:
            reader = csv.reader(file, delimiter=";")
            for row in reader:
                list_of_ids_already_processed.append(row[0])

        complete_list_of_all_case_ids_to_process = []
        with open(abs_file_path, "r") as file:
            reader = csv.reader(file)
            for iteration, row in enumerate(list(reader)):
                if row[0].strip() not in list_of_ids_already_processed:
                    complete_list_of_all_case_ids_to_process.append(row[0].strip())

        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", len(complete_list_of_all_case_ids_to_process))
        temp_list_of_ids = ["BR-19-019323"]
        for item in complete_list_of_all_case_ids_to_process:
            yield {"parc_id": item[6:], "case_year": item[3:5]}
        #
        # for item in complete_list_of_all_case_ids_to_process:
        #     yield item

    def __init__(self):
        self.HEADERS.update(settings.CONTACT_INFO_HEADINGS)
        self.logged_out = False


    def start_requests(self):
        # We want to assign headers for each request triggered. Override the request object
        # sent over to include Lucia's contact information
        # for parameter_dictionary in self.retrieve_all_franklin_county_urls():

        # Use the enumerator function to allow an individual cookie jar for each request
        # This is necessary to keep track of multiple view states
        for enumerator, item in enumerate(self.retrieve_all_cuyahoga_county_urls()):
            yield scrapy.Request(
                url='https://cpdocket.cp.cuyahogacounty.us/tos.aspx',
                method='GET',
                callback=self.parse,
                meta={'dont_redirect': False, "parc_id": item["parc_id"],
                      "case_year": item["case_year"],
                      'spider_num': enumerator, 'cookiejar': enumerator},
                dont_filter=True,
                headers=self.HEADERS
            )

    def parse(self, response):
        with open("examined_parcels.txt", 'a') as out_file:
            out_file.write(f"""{response.meta['parc_id']}\n""")

        yield FormRequest.from_response(

            response,
            formdata={
                'ctl00$SheetContentPlaceHolder$btnYes': "Yes",
            },
            meta={"parc_id": response.meta['parc_id'],
                  'spider_num': response.meta['spider_num'], 'cookiejar': response.meta['spider_num'],
                  "case_year": response.meta["case_year"]
                  },
            dont_filter=True,
            callback=self.initial_search,
            )

    def initial_search(self, response):
        yield FormRequest.from_response(
            response,
            url="https://cpdocket.cp.cuyahogacounty.us/Search.aspx",
            formdata={
                "__EVENTTARGET": "ctl00$SheetContentPlaceHolder$rbCivilCase",
                "ctl00$SheetContentPlaceHolder$rbSearches": "cvcase",
                "__ASYNCPOST": "true",
                "ctl00$ScriptManager1": "ctl00$SheetContentPlaceHolder$UpdatePanel1|ctl00$SheetContentPlaceHolder$rbCivilCase"
            },
            meta={"parc_id": response.meta['parc_id'],
                  'spider_num': response.meta['spider_num'], 'cookiejar': response.meta['spider_num'],
                  "case_year": response.meta["case_year"]
                  },
            headers={"Origin": "https://cpdocket.cp.cuyahogacounty.us",
                        "Upgrade-Insecure-Requests": "1",
                        "Content-Type": "application/x-www-form-urlencoded",
                        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
                        "Sec-Fetch-User": "?1",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
        },
                                    dont_filter=True,
            callback=self.real_search_page,
        )

    def property_page_open(self, response):
        soup = BeautifulSoup(response.body, 'html.parser')
        parcel_id_is = soup.find("td", text=re.compile("Parcel:"), class_="tdtitle").find_next().text
        parcel_id_is_stripped = parcel_id_is.strip()

        print("We have found  prayer amount: ", response.meta["prayer_amount"], " and case_number ", response.meta["case_number"], " and case title",
              response.meta["case_title"], " which was filed on ", response.meta["filing_date"], " WITH PARCEL ID: ", parcel_id_is_stripped)


        with open("all_bor_cases_results.txt", 'a') as out_file:
            out_file.write(f"""{response.meta["case_number"]};{response.meta["prayer_amount"]};{response.meta["filing_date"]};{parcel_id_is_stripped};{response.meta["case_title"]}\n""")

    def results_page(self, response):
        print("Real Results PARCEL ID IS: ", response.meta["parc_id"])
        soup = BeautifulSoup(response.body, 'html.parser')
        prayer_amount = soup.find("td", text=re.compile("Prayer Amount:"), class_="tdtitle").find_next().text
        stripped_amount = prayer_amount.strip()
        case_number = soup.find("td", text=re.compile("Case Number:"), class_="tdtitle").find_next().text
        case_stripped = case_number.strip()

        case_title = soup.find("td", text=re.compile("Case Title"), class_="tdtitle").find_next().text
        case_title_stripped = case_title.strip()

        filing_date = soup.find("td", text=re.compile("Filing Date:"), class_="tdtitle").find_next().text
        filing_date_stripped = filing_date.strip()

        matched = soup.select('#__VIEWSTATE')
        if matched:
            viewstate_value = matched[0].get('value')

        vsg = soup.select('#__VIEWSTATEGENERATOR')
        if vsg:
            viewstategenerator_value = vsg[0].get('value')

        evg = soup.select('#__EVENTVALIDATION')
        if evg:
            eventvalidation_value = evg[0].get('value')

        yield FormRequest.from_response(
            response,
            formdata={
                '__EVENTTARGET': "ctl00$SheetContentPlaceHolder$caseHeader$lbProperty",
                "__EVENTARGUMENT": "",
                "__EVENTVALIDATION": eventvalidation_value,
                "__VIEWSTATE": viewstate_value,
                "__VIEWSTATEGENERATOR": viewstategenerator_value
            },
            meta={"parc_id": response.meta['parc_id'],
                  'spider_num': response.meta['spider_num'], 'cookiejar': response.meta['spider_num'],
                    "prayer_amount": stripped_amount,
                    "case_number": case_stripped,
                     "case_title": case_title_stripped,
                    "filing_date": filing_date_stripped
                  },
            dont_filter=True,
            callback=self.property_page_open,
        )


        #
        # print("Let's try stripping to see what we get:", stripped_amount, "!!!")
        # with open('cuyahoga_court_results.txt', 'a') as file:
        #     file.write(f"""{response.meta['parc_id']};{case_stripped};{filing_date_stripped};{stripped_amount}\n""")

    def real_results(self, response):
        yield scrapy.Request(
            url='https://cpdocket.cp.cuyahogacounty.us/CaseSearchList.aspx',
            headers={"Sec-Fetch-Mode": "navigate",
                        "Sec-Fetch-Site": "none",
                    "Sec-Fetch-User": "?1",
                     "Upgrade-Insecure-Requests": "1"
                        },
            method='GET',
            callback=self.results_page,
            meta={"parc_id": response.meta['parc_id'],
                  'spider_num': response.meta['spider_num'], 'cookiejar': response.meta['spider_num'],
                  "case_year": response.meta["case_year"]},
            dont_filter=True,
        )

    def data_check_page(self, response):

        yield scrapy.Request(
            url='https://cpdocket.cp.cuyahogacounty.us/Check.aspx',
            headers={"Sec-Fetch-Mode": "navigate",
                        "Sec-Fetch-Site": "none",
                    "Sec-Fetch-User": "?1",
                     "Upgrade-Insecure-Requests": "1"
                        },
            method='GET',
            callback=self.real_results,
            meta={"parc_id": response.meta['parc_id'],
                  'spider_num': response.meta['spider_num'], 'cookiejar': response.meta['spider_num'],
                  "case_year": response.meta["case_year"],
                  },
            dont_filter=True,
        )

    def real_search_page(self, response):

        yield FormRequest(
            "https://cpdocket.cp.cuyahogacounty.us/Search.aspx",
            formdata={
                "__ASYNCPOST": "true",
                "__EVENTARGUMENT": "",
                "__EVENTTARGET": "",
                "__EVENTVALIDATION": "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",
                "__LASTFOCUS": "",
                "__VIEWSTATE": "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OAUEMTk1OGcQBQQxOTU3BQQxOTU3ZxAFBDE5NTYFBDE5NTZnEAUEMTk1NQUEMTk1NWcQBQQxOTU0BQQxOTU0ZxAFBDE5NTMFBDE5NTNnEAUEMTk1MgUEMTk1MmcQBQQxOTUxBQQxOTUxZxAFBDE5NTAFBDE5NTBnZGQCCw8PZBYCHwMFRGRpc3BsYXlQb3B1cCgnaF9DYXNlWWVhci5hc3B4JywnbXlXaW5kb3cnLDM3MCwyMjAsJ25vJyk7cmV0dXJuIGZhbHNlZAIPDw8WAh4JTWF4TGVuZ3RoZmRkAhEPFhQeIEN1bHR1cmVDdXJyZW5jeVN5bWJvbFBsYWNlaG9sZGVyBQEkHhZDdWx0dXJlVGltZVBsYWNlaG9sZGVyBQE6HhtDdWx0dXJlVGhvdXNhbmRzUGxhY2Vob2xkZXIFASweE092ZXJyaWRlUGFnZUN1bHR1cmVoHhFDdWx0dXJlRGF0ZUZvcm1hdAUDTURZHgtDdWx0dXJlTmFtZQUFZW4tVVMeFkN1bHR1cmVEYXRlUGxhY2Vob2xkZXIFAS8eFkN1bHR1cmVBTVBNUGxhY2Vob2xkZXIFBUFNO1BNHgpBY2NlcHRBbVBtaB4ZQ3VsdHVyZURlY2ltYWxQbGFjZWhvbGRlcgUBLmQCEw8PZBYCHwMFRmRpc3BsYXlQb3B1cCgnaF9DYXNlTnVtYmVyLmFzcHgnLCdteVdpbmRvdycsMzcwLDIyMCwnbm8nKTtyZXR1cm4gZmFsc2VkAhcPZBYCZg9kFggCAw8QZGQWAQIBZAIbDxAPFgYeDURhdGFUZXh0RmllbGQFC2Rlc2NyaXB0aW9uHg5EYXRhVmFsdWVGaWVsZAUNcGFydHlfcm9sZV9jZB4LXyFEYXRhQm91bmRnZBAVFQhbU0VMRUNUXQ1BQlNFTlQgUEFSRU5UDENPTU1JU1NJT05FUghDUkVESVRPUgZERUJUT1IJREVGRU5EQU5UCUdBUk5JU0hFRRtHQVJOSVNIRUUgLSBCRUlORyBHQVJOSVNIRUQRR1VBUkRJQU4gQUQgTElURU0VSU5URVJWRU5JTkcgUExBSU5USUZGCU5PTiBQQVJUWRJQQVJFTlQgQ09PUkRJTkFUT1IKUEVUSVRJT05FUglQTEFJTlRJRkYUUFJJVkFURSBQQVJUWSBTRUxMRVIIUkVDRUlWRVIH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BDIwMDYFBDIwMDZnEAUEMjAwNQUEMjAwNWcQBQQyMDA0BQQyMDA0ZxAFBDIwMDMFBDIwMDNnEAUEMjAwMgUEMjAwMmcQBQQyMDAxBQQyMDAxZxAFBDIwMDAFBDIwMDBnEAUEMTk5OQUEMTk5OWcQBQQxOTk4BQQxOTk4ZxAFBDE5OTcFBDE5OTdnEAUEMTk5NgUEMTk5NmcQBQQxOTk1BQQxOTk1ZxAFBDE5OTQFBDE5OTRnEAUEMTk5MwUEMTk5M2cQBQQxOTkyBQQxOTkyZxAFBDE5OTEFBDE5OTFnEAUEMTk5MAUEMTk5MGcQBQQxOTg5BQQxOTg5ZxAFBDE5ODgFBDE5ODhnEAUEMTk4NwUEMTk4N2cQBQQxOTg2BQQxOTg2ZxAFBDE5ODUFBDE5ODVnEAUEMTk4NAUEMTk4NGcQBQQxOTgzBQQxOTgzZxAFBDE5ODIFBDE5ODJnEAUEMTk4MQUEMTk4MWcQBQQxOTgwBQQxOTgwZxAFBDE5NzkFBDE5NzlnEAUEMTk3OAUEMTk3OGcQBQQxOTc3BQQxOTc3ZxAFBDE5NzYFBDE5NzZnEAUEMTk3NQUEMTk3NWcQBQQxOTc0BQQxOTc0ZxAFBDE5NzMFBDE5NzNnEAUEMTk3MgUEMTk3MmcQBQQxOTcxBQQxOTcxZxAFBDE5NzAFBDE5NzBnEAUEMTk2OQUEMTk2OWcQBQQxOTY4BQQxOTY4ZxAFBDE5NjcFBDE5NjdnEAUEMTk2NgUEMTk2NmcQBQQxOTY1BQQxOTY1ZxAFBDE5NjQFBDE5NjRnEAUEMTk2MwUEMTk2M2cQBQQxOTYyBQQxOTYyZxAFBDE5NjEFBDE5NjFnEAUEMTk2MAUEMTk2MGcQBQQxOTU5BQQxOTU5ZxAFBDE5NTgFBDE5NThnEAUEMTk1NwUEMTk1N2cQBQQxOTU2BQQxOTU2ZxAFBDE5NTUFBDE5NTVnEAUEMTk1NAUEMTk1NGcQBQQxOTUzBQQxOTUzZxAFBDE5NTIFBDE5NTJnEAUEMTk1MQUEMTk1MWcQBQQxOTUwBQQxOTUwZxAFBDE5NDkFBDE5NDlnEAUEMTk0OAUEMTk0OGcQBQQxOTQ3BQQxOTQ3ZxAFBDE5NDYFBDE5NDZnEAUEMTk0NQUEMTk0NWcQBQQxOTQ0BQQxOTQ0ZxAFBDE5NDMFBDE5NDNnEAUEMTk0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dCBjYXNlIG51bWJlci48YnIgLz4NCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAzLiBDbGljayBvbiB0aGUgc3VibWl0IGJ1dHRvbiB0byBwZXJmb3JtIHRoZSBkZXNpcmVkIHF1ZXJ5LjxiciAvPmQCCw8PZBYCHwMFGmphdmFzY3JpcHQ6d2luZG93LnByaW50KCk7ZAIPDw9kFgIfAwUiamF2YXNjcmlwdDpvbkNsaWNrPXdpbmRvdy5jbG9zZSgpO2QCEw8PZBYCHwMFRmRpc3BsYXlQb3B1cCgnaF9EaXNjbGFpbWVyLmFzcHgnLCdteVdpbmRvdycsMzcwLDMwMCwnbm8nKTtyZXR1cm4gZmFsc2VkAhcPZBYCZg8PFgIeC05hdmlnYXRlVXJsBRYvU2VhcmNoLmFzcHg/aXNwcmludD1ZZGQCGQ8PZBYCHwMFRWRpc3BsYXlQb3B1cCgnaF9RdWVzdGlvbnMuYXNweCcsJ215V2luZG93JywzNzAsNDc1LCdubycpO3JldHVybiBmYWxzZWQCGw8WAh8ABQcxLjEuMjMyZBgBBR5fX0NvbnRyb2xzUmVxdWlyZVBvc3RCYWNrS2V5X18WEAUpY3RsMDAkU2hlZXRDb250ZW50UGxhY2VIb2xkZXIkcmJDaXZpbENhc2UFKWN0bDAwJFNoZWV0Q29udGVudFBsYWNlSG9sZGVyJHJiQ2l2aWxOYW1lBSljdGwwMCRTaGVldENvbnRlbnRQbGFjZUhvbGRlciRyYkNpdmlsTmFtZQUwY3RsMDAkU2hlZXRDb250ZW50UGxhY2VIb2xkZXIkcmJDaXZpbEZvcmVjbG9zdXJlBTBjdGwwMCRTaGVldENvbnRlbnRQbGFjZUhvbGRlciRyYkNpdmlsRm9yZWNsb3N1cmUFJmN0bDAwJFNoZWV0Q29udGVudFBsYWNlSG9sZGVyJHJiQ3JDYXNlBSZjdGwwMCRTaGVldENvbnRlbnRQbGFjZUhvbGRlciRyYkNyQ2FzZQUmY3RsMDAkU2hlZXRDb250ZW50UGxhY2VIb2xkZXIkcmJDck5hbWUFJmN0bDAwJFNoZWV0Q29udGVudFBsYWNlSG9sZGVyJHJiQ3JOYW1lBSdjdGwwMCRTaGVldENvbnRlbnRQbGFjZUhvbGRlciRyYkNvYUNhc2UFJ2N0bDAwJFNoZWV0Q29udGVudFBsYWNlSG9sZGVyJHJiQ29hQ2FzZQUnY3RsMDAkU2hlZXRDb250ZW50UGxhY2VIb2xkZXIkcmJDb2FOYW1lBSdjdGwwMCRTaGVldENvbnRlbnRQbGFjZUhvbGRlciRyYkNvYU5hbWUFOGN0bDAwJFNoZWV0Q29udGVudFBsYWNlSG9sZGVyJGNpdmlsQ2FzZVNlYXJjaCRpbWdidG5UeXBlBThjdGwwMCRTaGVldENvbnRlbnRQbGFjZUhvbGRlciRjaXZpbENhc2VTZWFyY2gkaW1nYnRuWWVhcgU6Y3RsMDAkU2hlZXRDb250ZW50UGxhY2VIb2xkZXIkY2l2aWxDYXNlU2VhcmNoJGltZ2J0bk51bWJlcvHYNe2q0kTuT+hR3km1hJD0gmRhTmFehS+T8Vft3Gyt",
                "__VIEWSTATEGENERATOR": "BBBC20B8",
                "ctl00$ScriptManager1": "ctl00$SheetContentPlaceHolder$UpdatePanel1|ctl00$SheetContentPlaceHolder$civilCaseSearch$btnSubmitCase",
                "ctl00$SheetContentPlaceHolder$civilCaseSearch$btnSubmitCase": "Submit Search",
                "ctl00$SheetContentPlaceHolder$civilCaseSearch$ddlCaseType": "BR",
                "ctl00$SheetContentPlaceHolder$civilCaseSearch$ddlCaseYear": f"""20{response.meta["case_year"]}""",
                "ctl00$SheetContentPlaceHolder$civilCaseSearch$meeCaseNum_ClientState": "",
                "ctl00$SheetContentPlaceHolder$civilCaseSearch$txtCaseNum": response.meta["parc_id"],
                "ctl00$SheetContentPlaceHolder$rbSearches": "cvcase"
            },
            meta={"parc_id": response.meta['parc_id'],
                  'spider_num': response.meta['spider_num'], 'cookiejar': response.meta['spider_num'],
                  "case_year": response.meta["case_year"],
                  'dont_redirect': True, 'handle_httpstatus_list': [302]
                  },
            dont_filter=True,
            headers=self.HEADERS,
            callback=self.data_check_page,
        )