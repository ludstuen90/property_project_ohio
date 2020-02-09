# -*- coding: utf-8 -*-
import os
import re
import csv
from urllib.parse import urljoin

from scrapy.utils.python import to_native_str
from scrapy.utils.response import open_in_browser

import scrapy
from bs4 import BeautifulSoup
from scrapy import FormRequest

from ohio import settings

class CuyahogaCaseNumberScraper(scrapy.Spider):
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

    name = 'cuyahoga_case_num'
    allowed_domains = ['cpdocket.cp.cuyahogacounty.us']

    def start_requests(self):
        # We want to assign headers for each request triggered. Override the request object
        # sent over to include Lucia's contact information
        # for parameter_dictionary in self.retrieve_all_franklin_county_urls():

        # Use the enumerator function to allow an individual cookie jar for each request
        # This is necessary to keep track of multiple view states

        yield scrapy.Request(
            url='https://cpdocket.cp.cuyahogacounty.us/tos.aspx',
            method='GET',
            callback=self.accept_tos,
            meta={'dont_redirect': False,
                  "cookiejar": 1
                  },
            dont_filter=True,
            headers=self.HEADERS
        )

    def accept_tos(self, response):
        # with open("examined_parcels.txt", 'w') as out_file:
        #     out_file.write(f"""{response.meta['parc_id']}\n""")

        # Load the foreclosure  search thing

        yield FormRequest.from_response(

            response,
            formdata={
                'ctl00$SheetContentPlaceHolder$btnYes': "Yes",
            },
            meta={
                "cookiejar": 1
                  },
            dont_filter=True,
            callback=self.initial_search,
            )

    def initial_search(self, response):
        yield FormRequest.from_response(
            response,
            url="https://cpdocket.cp.cuyahogacounty.us/Search.aspx",
            formdata={
                "ctl00$ScriptManager1" : "ctl00$SheetContentPlaceHolder$UpdatePanel1|ctl00$SheetContentPlaceHolder$rbCivilName",
                "__EVENTTARGET": "ctl00$SheetContentPlaceHolder$rbCivilName",
                "__ASYNCPOST": "true",
                "ctl00$SheetContentPlaceHolder$rbSearches": "cvname",
            },
            meta={
                "cookiejar": 1
                  },
            headers={"Origin": "https://cpdocket.cp.cuyahogacounty.us",
                        "X-Requested-With": "XMLHttpRequest",
                        "Content-Type": "application/x-www-form-urlencoded",
                        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
                        "Sec-Fetch-User": "?1",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
        },
                                    dont_filter=True,
            callback=self.real_search_page,
        )

    def real_search_page(self, response):

        yield FormRequest(
            "https://cpdocket.cp.cuyahogacounty.us/Search.aspx",
            formdata={
                "__ASYNCPOST": "true",
                "__EVENTARGUMENT": "",
                "__EVENTTARGET": "",
                "__LASTFOCUS": "",
                "__EVENTVALIDATION": "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",
                "__LASTFOCUS": "",
                "__VIEWSTATE":"/wEPDwULLTEzMjA5Mjg3NzAPZBYCZg9kFgICAw9kFhQCAw9kFgICAQ9kFgQCAQ8WAh4EVGV4dAUPQ3V5YWhvZ2EgQ291bnR5ZAIDDxYCHwAFD0NsZXJrIG9mIENvdXJ0c2QCBQ8PFgIeB1Zpc2libGVoZGQCBw8PFgIfAWhkZAIJD2QWBAIDD2QWAgIBDxYCHwAFigI8Zm9udCBmYWNlPSJBcmlhbCIgc2l6ZT0iNCI+PGI+Tk9USUNFOjwvYj5QbGVhc2Ugbm90ZSB0aGF0IHRoZSBDbGVyayBvZiBDb3VydHMgV2ViZG9ja2V0IHB1YmxpYyBhY2Nlc3MgYW5kIEUtRmlsaW5nIHN5c3RlbXMgd2lsbCBiZSB1bmF2YWlsYWJsZSBvbiBTYXR1cmRheSwgRmVicnVhcnkgMTUgZnJvbSAxOjMwcG0gdGhyb3VnaCBTdW5kYXksIEZlYnJ1YXJ5IDE2IGF0IDExOjAwQU0gZm9yIGJ1aWxkaW5nIG1haW50ZW5hbmNlLjwvZm9udD48L1A+DQoNCg0KDQoNCmQCBQ9kFgJmD2QWFgIDDxYCHwFoZAIHDxAPFgIeB0NoZWNrZWRnZGRkZAIVD2QWAmYPZBYMAgMPEGQPFghmAgECAgIDAgQCBQIGAgcWCBAFCFtTRUxFQ1RdZWcQBRJCT0FSRCBPRiBSRVZJU0lPTlMFAkJSZxAFBUNJVklMBQJDVmcQBRJET01FU1RJQyBSRUxBVElPTlMFAkRSZxAFC0dBUk5JU0hNRU5UBQJHUmcQBQ1KVURHTUVOVCBMSUVOBQJKTGcQBRRNSVNDRUxMQU5FT1VTLUNMQUlNUwUCTVNnEAUOU1BFQ0lBTCBET0NLRVQFAlNEZxYBZmQCBQ8PZBYCHgdvbmNsaWNrBUhkaXNwbGF5UG9wdXAoJ2hfQ2FzZUNhdGVnb3J5LmFzcHgnLCdteVdpbmRvdycsMzcwLDIyMCwnbm8nKTtyZXR1cm4gZmFsc2VkAgkPEGQPFkhmAgECAgIDAgQCBQIGAgcCCAIJAgoCCwIMAg0CDgIPAhACEQISAhMCFAIVAhYCFwIYAhkCGgIbAhwCHQIeAh8CIAIhAiICIwIkAiUCJgInAigCKQIqAisCLAItAi4CLwIwAjECMgIzAjQCNQI2AjcCOAI5AjoCOwI8Aj0CPgI/AkACQQJCAkMCRAJFAkYCRxZIEAUIW1NFTEVDVF1lZxAFBDIwMjAFBDIwMjBnEAUEMjAxOQUEMjAxOWcQBQQyMDE4BQQyMDE4ZxAFBDIwMTcFBDIwMTdnEAUEMjAxNgUEMjAxNmcQBQQyMDE1BQQyMDE1ZxAFBDIwMTQFBDIwMTRnEAUEMjAxMwUEMjAxM2cQBQQyMDEyBQQyMDEyZxAFBDIwMTEFBDIwMTFnEAUEMjAxMAUEMjAxMGcQBQQyMDA5BQQyMDA5ZxAFBDIwMDgFBDIwMDhnEAUEMjAwNwUEMjAwN2cQBQQyMDA2BQQyMDA2ZxAFBDIwMDUFBDIwMDVnEAUEMjAwNAUEMjAwNGcQBQQyMDAzBQQyMDAzZxAFBDIwMDIFBDIwMDJnEAUEMjAwMQUEMjAwMWcQBQQyMDAwBQQyMDAwZxAFBDE5OTkFBDE5OTlnEAUEMTk5OAUEMTk5OGcQBQQxOTk3BQQxOTk3ZxAFBDE5OTYFBDE5OTZnEAUEMTk5NQUEMTk5NWcQBQQxOTk0BQQxOTk0ZxAFBDE5OTMFBDE5OTNnEAUEMTk5MgUEMTk5MmcQBQQxOTkxBQQxOTkxZxAFBDE5OTAFBDE5OTBnEAUEMTk4OQUEMTk4OWcQBQQxOTg4BQQxOTg4ZxAFBDE5ODcFBDE5ODdnEAUEMTk4NgUEMTk4NmcQBQQxOTg1BQQxOTg1ZxAFBDE5ODQFBDE5ODRnEAUEMTk4MwUEMTk4M2cQBQQxOTgyBQQxOTgyZxAFBDE5ODEFBDE5ODFnEAUEMTk4MAUEMTk4MGcQBQQxOTc5BQQxOTc5ZxAFBDE5NzgFBDE5NzhnEAUEMTk3NwUEMTk3N2cQBQQxOTc2BQQxOTc2ZxAFBDE5NzUFBDE5NzVnEAUEMTk3NAUEMTk3NGcQBQQxOTczBQQxOTczZxAFBDE5NzIFBDE5NzJnEAUEMTk3MQUEMTk3MWcQBQQxOTcwBQQxOTcwZxAFBDE5NjkFBDE5NjlnEAUEMTk2OAUEMTk2OGcQBQQxOTY3BQQxOTY3ZxAFBDE5NjYFBDE5NjZnEAUEMTk2NQUEMTk2NWcQBQQxOTY0BQQxOTY0ZxAFBDE5NjMFBDE5NjNnEAUEMTk2MgUEMTk2MmcQBQQxOTYxBQQxOTYxZxAFBDE5NjAFBDE5NjBnEAUEMTk1OQUEMTk1OWcQBQQxOTU4BQQxOTU4ZxAFBDE5NTcFBDE5NTdnEAUEMTk1NgUEMTk1NmcQBQQxOTU1BQQxOTU1ZxAFBDE5NTQFBDE5NTRnEAUEMTk1MwUEMTk1M2cQBQQxOTUyBQQxOTUyZxAFBDE5NTEFBDE5NTFnEAUEMTk1MAUEMTk1MGcWAWZkAgsPD2QWAh8DBURkaXNwbGF5UG9wdXAoJ2hfQ2FzZVllYXIuYXNweCcsJ215V2luZG93JywzNzAsMjIwLCdubycpO3JldHVybiBmYWxzZWQCDw8PFgIeCU1heExlbmd0aGZkZAITDw9kFgIfAwVGZGlzcGxheVBvcHVwKCdoX0Nhc2VOdW1iZXIuYXNweCcsJ215V2luZG93JywzNzAsMjIwLCdubycpO3JldHVybiBmYWxzZWQCFw8PFgIfAWdkFgJmD2QWBgIbDxAPFgYeDURhdGFUZXh0RmllbGQFC2Rlc2NyaXB0aW9uHg5EYXRhVmFsdWVGaWVsZAUNcGFydHlfcm9sZV9jZB4LXyFEYXRhQm91bmRnZBAVFQhbU0VMRUNUXQ1BQlNFTlQgUEFSRU5UDENPTU1JU1NJT05FUghDUkVESVRPUgZERUJUT1IJREVGRU5EQU5UCUdBUk5JU0hFRRtHQVJOSVNIRUUgLSBCRUlORyBHQVJOSVNIRUQRR1VBUkRJQU4gQUQgTElURU0VSU5URVJWRU5JTkcgUExBSU5USUZGCU5PTiBQQVJUWRJQQVJFTlQgQ09PUkRJTkFUT1IKUEVUSVRJT05FUglQTEFJTlRJRkYUUFJJVkFURSBQQVJUWSBTRUxMRVIIUkVDRUlWRVIHUkVMQVRPUgpSRVNQT05ERU5UFVRISVJEIFBBUlRZIEFQUEVMTEFOVBVUSElSRCBQQVJUWSBERUZFTkRBTlQVVEhJUkQgUEFSVFkgUExBSU5USUZGFRUAAkFQAkNNAUMCRFQBRAJHUgJCRwFHAklQAk5QAlBDAVQBUAJQUAFSAlJMAlJTAlRBAlREAlRQFCsDFWdnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2RkAh8PEA8WBh8FBQtkZXNjcmlwdGlvbh8GBRBjYXNlX2NhdGVnb3J5X2NkHwdnZBAVCAhbU0VMRUNUXRJCT0FSRCBPRiBSRVZJU0lPTlMFQ0lWSUwSRE9NRVNUSUMgUkVMQVRJT05TC0dBUk5J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OTg2BQQxOTg2ZxAFBDE5ODUFBDE5ODVnEAUEMTk4NAUEMTk4NGcQBQQxOTgzBQQxOTgzZxAFBDE5ODIFBDE5ODJnEAUEMTk4MQUEMTk4MWcQBQQxOTgwBQQxOTgwZxAFBDE5NzkFBDE5NzlnEAUEMTk3OAUEMTk3OGcQBQQxOTc3BQQxOTc3ZxAFBDE5NzYFBDE5NzZnEAUEMTk3NQUEMTk3NWcQBQQxOTc0BQQxOTc0ZxAFBDE5NzMFBDE5NzNnEAUEMTk3MgUEMTk3MmcQBQQxOTcxBQQxOTcxZxAFBDE5NzAFBDE5NzBnEAUEMTk2OQUEMTk2OWcQBQQxOTY4BQQxOTY4ZxAFBDE5NjcFBDE5NjdnEAUEMTk2NgUEMTk2NmcQBQQxOTY1BQQxOTY1ZxAFBDE5NjQFBDE5NjRnEAUEMTk2MwUEMTk2M2cQBQQxOTYyBQQxOTYyZxAFBDE5NjEFBDE5NjFnEAUEMTk2MAUEMTk2MGcQBQQxOTU5BQQxOTU5ZxAFBDE5NTgFBDE5NThnEAUEMTk1NwUEMTk1N2cQBQQxOTU2BQQxOTU2ZxAFBDE5NTUFBDE5NTVnEAUEMTk1NAUEMTk1NGcQBQQxOTUzBQQxOTUzZxAFBDE5NTIFBDE5NTJnEAUEMTk1MQUEMTk1MWcQBQQxOTUwBQQxOTUwZxAFBDE5NDkFBDE5NDlnEAUEMTk0OAUEMTk0OGcQBQQxOTQ3BQQxOTQ3ZxAFBDE5NDYFBDE5NDZnEAUEMTk0NQUEMTk0NWcQBQQxOTQ0BQQxOTQ0ZxAFBDE5NDMFBDE5NDNnEAUEMTk0MgUEMTk0MmcQBQQxOTQxBQQxOTQxZxAFBDE5NDAFBDE5NDBnEAUEMTkzOQUEMTkzOWcQBQQxOTM4BQQxOTM4ZxAFBDE5MzcFBDE5MzdnEAUEMTkzNgUEMTkzNmcQBQQxOTM1BQQxOTM1ZxAFBDE5MzQFBDE5MzRnEAUEMTkzMwUEMTkzM2cQBQQxOTMyBQQxOTMyZxAFBDE5MzEFBDE5MzFnEAUEMTkzMAUEMTkzMGcQBQQxOTI5BQQxOTI5ZxAFBDE5MjgFBDE5MjhnEAUEMTkyNwUEMTkyN2cQBQQxOTI2BQQxOTI2ZxAFBDE5MjUFBDE5MjVnEAUEMTkyNAUEMTkyNGcQBQQxOTIzBQQxOTIzZxAFBDE5MjIF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UGxhY2VIb2xkZXIkcmJDaXZpbENhc2UFKWN0bDAwJFNoZWV0Q29udGVudFBsYWNlSG9sZGVyJHJiQ2l2aWxOYW1lBTBjdGwwMCRTaGVldENvbnRlbnRQbGFjZUhvbGRlciRyYkNpdmlsRm9yZWNsb3N1cmUFMGN0bDAwJFNoZWV0Q29udGVudFBsYWNlSG9sZGVyJHJiQ2l2aWxGb3JlY2xvc3VyZQUmY3RsMDAkU2hlZXRDb250ZW50UGxhY2VIb2xkZXIkcmJDckNhc2UFJmN0bDAwJFNoZWV0Q29udGVudFBsYWNlSG9sZGVyJHJiQ3JDYXNlBSZjdGwwMCRTaGVldENvbnRlbnRQbGFjZUhvbGRlciRyYkNyTmFtZQUmY3RsMDAkU2hlZXRDb250ZW50UGxhY2VIb2xkZXIkcmJDck5hbWUFJ2N0bDAwJFNoZWV0Q29udGVudFBsYWNlSG9sZGVyJHJiQ29hQ2FzZQUnY3RsMDAkU2hlZXRDb250ZW50UGxhY2VIb2xkZXIkcmJDb2FDYXNlBSdjdGwwMCRTaGVldENvbnRlbnRQbGFjZUhvbGRlciRyYkNvYU5hbWUFJ2N0bDAwJFNoZWV0Q29udGVudFBsYWNlSG9sZGVyJHJiQ29hTmFtZQU1Y3RsMDAkU2hlZXRDb250ZW50UGxhY2VIb2xkZXIkY2l2aWxOYW1lU2VhcmNoJGNiQWxpYXMFNWN0bDAwJFNoZWV0Q29udGVudFBsYWNlSG9sZGVyJGNpdmlsTmFtZVNlYXJjaCRyYkFscGhhBThjdGwwMCRTaGVldENvbnRlbnRQbGFjZUhvbGRlciRjaXZpbE5hbWVTZWFyY2gkcmJQaG9uZXRpYwU4Y3RsMDAkU2hlZXRDb250ZW50UGxhY2VIb2xkZXIkY2l2aWxOYW1lU2VhcmNoJHJiUGhvbmV0aWMfoKD2kiAZ99qHGEjjH3qDykuheSZJ/m3IBMAGDCeUTw==",
               "__VIEWSTATEGENERATOR": "BBBC20B8",
                "ctl00$ScriptManager1": "ctl00$SheetContentPlaceHolder$UpdatePanel1|ctl00$SheetContentPlaceHolder$civilNameSearch$btnSubmitName",
                "ctl00$SheetContentPlaceHolder$civilNameSearch$btnSubmitName": "Submit Search",
                "ctl00$SheetContentPlaceHolder$civilNameSearch$ddlCaseCat": "BR",
                "ctl00$SheetContentPlaceHolder$civilNameSearch$ddlCaseYear": "2019",
                "ctl00$SheetContentPlaceHolder$civilNameSearch$ddlFormatResults": "20",
                "ctl00$SheetContentPlaceHolder$civilNameSearch$ddlPartyRole": "",
                "ctl00$SheetContentPlaceHolder$civilNameSearch$grpType": "rbAlpha",
                "ctl00$SheetContentPlaceHolder$civilNameSearch$txtCompName": "Treasurer",
                "ctl00$SheetContentPlaceHolder$civilNameSearch$txtFirstName": "",
                "ctl00$SheetContentPlaceHolder$civilNameSearch$txtLastName": "",
                "ctl00$SheetContentPlaceHolder$civilNameSearch$txtMiddleName": "",
                "ctl00$SheetContentPlaceHolder$rbSearches": "cvname"
            },
            meta={
                "cookiejar": 1,
                "dont_redirect": False,
                  },
            headers=self.HEADERS,
            callback=self.please_open,
        )

    def please_open(self, response):
        open_in_browser(response)
        yield scrapy.Request(
            url='https://cpdocket.cp.cuyahogacounty.us/Check.aspx',
            headers={
                        "Sec-Fetch-Site": "none",
                    "Sec-Fetch-User": "?1",
                     "Upgrade-Insecure-Requests": "1",
                     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
                        },
            method='GET',
            callback=self.get_real_results,
            meta={"cookiejar": 1},
            dont_filter=True
                )

    def get_real_results(self, response):
        yield scrapy.Request(
            url='https://cpdocket.cp.cuyahogacounty.us/NameSearchResults.aspx',
            headers={
                        "Sec-Fetch-Site": "none",
                    "Sec-Fetch-User": "?1",
                     "Upgrade-Insecure-Requests": "1",
                     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
                        },
            method='GET',
            callback=self.real_results,
            meta={"cookiejar": 1},
            dont_filter=True
                )

    def real_results(self, response):
        open_in_browser(response)
        soup = BeautifulSoup(response.body, 'html.parser')

        all_results = soup.find("table", id="SheetContentPlaceHolder_ctl00_gvNameResults").find_all("tr")

        for x in all_results:
            try:
                result = x.find("td", align="center").find("a").text
                with open("found_case_numbers.txt", 'a') as out_file:
                    out_file.write(f"""{result}\n""")
            except AttributeError:
                pass

        matched = soup.select('#__VIEWSTATE')
        if matched:
            viewstate_value = matched[0].get('value')

        vsg = soup.select('#__VIEWSTATEGENERATOR')
        if vsg:
            viewstategenerator_value = vsg[0].get('value')

        evg = soup.select('#__EVENTVALIDATION')
        if evg:
            eventvalidation_value = evg[0].get('value')
        yield FormRequest(
            "https://cpdocket.cp.cuyahogacounty.us/NameSearchResults.aspx",
            formdata={
                "__VIEWSTATE": viewstate_value,
                "__VIEWSTATEGENERATOR": viewstategenerator_value,
                    "__EVENTVALIDATION": eventvalidation_value,
                "__EVENTARGUMENT": f'''Page${2}''',
                "__EVENTTARGET": "ctl00$SheetContentPlaceHolder$ctl00$gvNameResults",
            },
            meta={ 'cookiejar': 1,
                   "pagenum": 3
                  },
            headers={"Origin": "https://cpdocket.cp.cuyahogacounty.us",
                     "Upgrade-Insecure-Requests": "1",
                     "Content-Type": "application/x-www-form-urlencoded",
                     "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
                     "Sec-Fetch-User": "?1",
                     "Upgrade-Insecure-Requests": "1",
                     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
                     },
            dont_filter=True,
            callback=self.next_page,
        )

    def next_page(self, response):
        open_in_browser(response)

        soup = BeautifulSoup(response.body, 'html.parser')

        all_results = soup.find("table", id="SheetContentPlaceHolder_ctl00_gvNameResults").find_all("tr")

        for x in all_results:
            try:
                result = x.find("td", align="center").find("a").text
                with open("found_case_numbers.txt", 'a') as out_file:
                    out_file.write(f"""{result}\n""")
            except AttributeError:
                pass

        print("PAGENUM IS : ", response.meta["pagenum"])
        print("THIS IS A TYPE OF: ", type(response.meta["pagenum"]))
        if int(response.meta["pagenum"]) < 77:
            pagenum = (response.meta["pagenum"]+1)
            print("KICKED OFF FUNCTION WITH NEXT PAGE NUM OF ", pagenum)
            matched = soup.select('#__VIEWSTATE')
            matched = soup.select('#__VIEWSTATE')
            if matched:
                viewstate_value = matched[0].get('value')

            vsg = soup.select('#__VIEWSTATEGENERATOR')
            if vsg:
                viewstategenerator_value = vsg[0].get('value')

            evg = soup.select('#__EVENTVALIDATION')
            if evg:
                eventvalidation_value = evg[0].get('value')

            yield FormRequest(
                "https://cpdocket.cp.cuyahogacounty.us/NameSearchResults.aspx",
                formdata={
                    "__VIEWSTATE": viewstate_value,
                    "__VIEWSTATEGENERATOR": viewstategenerator_value,
                        "__EVENTVALIDATION": eventvalidation_value,
                    "__EVENTARGUMENT": f'''Page${pagenum}''',
                    "__EVENTTARGET": "ctl00$SheetContentPlaceHolder$ctl00$gvNameResults",
                },
                meta={'cookiejar': 1,
                       "pagenum": pagenum
                      },
                headers={"Origin": "https://cpdocket.cp.cuyahogacounty.us",
                         "Upgrade-Insecure-Requests": "1",
                         "Content-Type": "application/x-www-form-urlencoded",
                         "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
                         "Sec-Fetch-User": "?1",
                         "Upgrade-Insecure-Requests": "1",
                         "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
                         },
                dont_filter=True,
                callback=self.next_page,
            )
        #
        # matched = soup.select('#__VIEWSTATE')
        # if matched:
        #     viewstate_value = matched[0].get('value')
        #
        # vsg = soup.select('#__VIEWSTATEGENERATOR')
        # if vsg:
        #     viewstategenerator_value = vsg[0].get('value')
        #
        # evg = soup.select('#__EVENTVALIDATION')
        # if evg:
        #     eventvalidation_value = evg[0].get('value')
        #
        # yield FormRequest(
        #     "https://cpdocket.cp.cuyahogacounty.us/NameSearchResults.aspx",
        #     formdata={
        #         "__VIEWSTATE": viewstate_value,
        #         "__VIEWSTATEGENERATOR": viewstategenerator_value,
        #             "__EVENTVALIDATION": eventvalidation_value,
        #         "__EVENTARGUMENT": "Page$2",
        #         "__EVENTTARGET": "ctl00$SheetContentPlaceHolder$ctl00$gvNameResults",
        #     },
        #     meta={ 'cookiejar': 1
        #           },
        #     headers={"Origin": "https://cpdocket.cp.cuyahogacounty.us",
        #              "Upgrade-Insecure-Requests": "1",
        #              "Content-Type": "application/x-www-form-urlencoded",
        #              "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
        #              "Sec-Fetch-User": "?1",
        #              "Upgrade-Insecure-Requests": "1",
        #              "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
        #              },
        #     dont_filter=True,
        #     callback=self.next_page,
        # )

# # REQUEST THE INFORMATION FOR THE SEARCH
# # LOOP THROUGH ALL THE RESULTS, EACH PAGE WRITING ALL OF THE INFORMATION TO A CSV FILE BECAUSE WE DON'T WANT TO
# # RISK THAT THE NUMBERS AT THE END ARE NOT STORED THAT WOULD BE HORRIBLÑE.
# soup.find("table", id="SheetContentPlaceHolder_ctl00_gvNameResults").find_all("tr")
#
# for x in a:
#     print(x)
#
# # Descargar todos los items en está pagina
# for number, item in enumerate(a):
#     try:
#         item.find("td", align="center").find("a").text
#     except AttributeError:
#         pass
#


# IN THE FILES THERE ARE 237 UNIQUE FROM 2019
# AND 236 UNIQUE FROM 2018

# # Do post back of the page number, increasing 1 by 1 up until 	76 pages -
#
# href="javascript:__doPostBack('ctl00$SheetContentPlaceHolder$ctl00$gvNameResults','Page$67')"
#
# # Calculate how many pages there would be