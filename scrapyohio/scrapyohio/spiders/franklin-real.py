# -*- coding: utf-8 -*-

import requests
import scrapy
from bs4 import BeautifulSoup
from scrapy import FormRequest
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

    name = 'franklin-real'
    allowed_domains = ['countyfusion5.kofiletech.us']
    start_urls = ['https://countyfusion5.kofiletech.us/countyweb/login.do']

    def retrieve_all_franklin_county_urls(self):
        self.please_parse_these_items = models.Property.objects.filter(county=self.franklin_county_object).all()[:1]

        for item in self.please_parse_these_items:
            yield item.parcel_number

    def __init__(self):
        self.HEADERS.update(settings.CONTACT_INFO_HEADINGS)
        self.logged_out = False

    # def log_in_function(self):
    #     """
    #     The purpose of this method is to return a token with a JSESSIONID that we can use in the site.
    #     :return: JSESSIONID token for the Franklin Real Estate site.
    #     """
    #     session = requests.Session()
    #     formdata = {
    #         "Origin": "https://countyfusion5.kofiletech.us",
    #         "Upgrade-Insecure-Requests": "1",
    #         "Content-Type": "application/x-www-form-urlencoded",
    #         "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
    #         "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
    #     }
    #
    #     r = session.post('https://countyfusion5.kofiletech.us/countyweb/login.do', data=formdata)
    #     return session

    def start_requests(self):
        # LOG IN
        # self.token = self.log_in_function()


        yield scrapy.FormRequest(
            url='https://countyfusion5.kofiletech.us/countyweb/login.do',
            formdata={
            "Origin": "https://countyfusion5.kofiletech.us",
            "Upgrade-Insecure-Requests": "1",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            },
            callback=self.parse
        )


        # LATER ON ASSERT CHECK
        #
        # # Ensure we have a county in the database
        # self.franklin_county_object, created = models.County.objects.get_or_create(name="Franklin")
        # # We want to assign headers for each request triggered. Override the request object
        # # sent over to include Lucia's contact information
        # # for parameter_dictionary in self.retrieve_all_franklin_county_urls():
        #
        # # Use the enumerator function to allow an individual cookie jar for each request
        # # This is necessary to keep track of multiple view states
        # # print("SELF TOKEN: ", self.token)
        # for enumerator, item in enumerate(self.retrieve_all_franklin_county_urls()):
        #     # session = self.log_in_function()
        #     # print("Session: ", session)
        #     # print("Session: ", type(session))
        #
        #     yield scrapy.FormRequest(url="https://countyfusion5.kofiletech.us/countyweb/search/searchExecute.do?assessor=false",
        #                              formdata={
        #                                 "ALLNAMES": "bile",
        #                                 "CASETYPE":"",
        #                                 "DATERANGE":'[{"name": "TODATE", "value": "User Defined"}]',
        #                                 "FROMDATE":"",
        #                         "INSTTYPE": "AS,ASAC,ASAL,ASAR,ASLC,ASMO,ASTR,RRAS,RRASAC,RRASAR,RRASLC,RRASMO,RRASTR,"
        #                                     "RRASVL,RRVET,VET,AF,AG,AMEA,AMZO,ANNEX,ASEA,AD,CTRL,CT,COND,CCCE,CE,DECL,DE,"
        #                                     "DISC,DA,EA,FA,MERGE,MDAG,PREA,REDECL,REEA,RRAF,RRAG,RRAMZO,RRANNEX,RRASEA,"
        #                                     "RRAD,RRCT,RRCONDO,RRCCCE,RRCE,RRDECL,RRDE,RRDISC,RRDA,RREA,RRFA,RRMERGE,"
        #                                     "RRDMAG,RRPREA,RRREDECL,RRREEA,RRSD,RRSUAG,RRSUEA,RRVAAL,RRZO,SD,SUAG,SUEA,TR,"
        #                                     "VA,VAAL,VAEA,ZO,AMFT,CCFT,FT,PRFT,RFFT,REFT,RVREFT,RRCCFT,RRFT,RRPRFT,RRREFT,WDFT,"
        #                                     "ADLE,AMLE,ASLE,CCLE,LE,MDLE,PRAL,PRLE,REAL,RELE,RRADLE,RRAMLE,RRASAL,RRAL,"
        #                                     "RRCCLE,RRLE,RRMDLE,RRPRAL,RRPRLE,RRREAL,RRRELE,RRSULE,RRWPLE,SULE,WPLE,AFO,"
        #                                     "AMFS2RP,AMML,ASFS2RP,ASLN,ASML,ASTLC,BE,BW,CSL,COBE,COBW,COFS2RP,CALN,CCBE,"
        #                                     "CCBW,CCFS2RP,CCLN,CCML,CCPP,EXTLC,FLN,FS2RP,LN,ML,MFLN,NOCS,PRBE,PRBW,PRFLN,"
        #                                     "PRFS2RP,PRLN,PRML,PRPP,PP,RB,RFTLC,RFBE,REBE,REBW,RECALN,REFS2RP,RELN,REML,"
        #                                     "REMFLN,REPP,RERB,RTLC,RRAFO,RRAMFS2RP,RRASFS2RP,RRASLN,RRASML,RRASTLC,RRBE,"
        #                                     "RRBW,RRCSL,RRCOBE,RRCOBW,RRCOFS2RP,RRCALN,RRCCBE,RRCCBW,RRCCFS2RP,RRCCLN,"
        #                                     "RRCCML,RRCCPP,RRFS2RP,RRLN,RRML,RRMFLN,RRCN,RRNOCS,RRTLC,RRPRBE,RRPRBW,"
        #                                     "RRPR2FSRP,RRPRLN,RRPRML,RRPRPP,RRPP,RRRB,RRRFBE,RRRFFT,RRREBE,RRREBW,"
        #                                     "RRRECALN,RRREFS2RP,RRRELN,RRREML,RRREMFLN,RRREPP,RRRERB,RRSUBE,RRSUFT,"
        #                                     "RRSUFS2RP,RRSULN,RRSUML,RRSUPP,RRTRMFS2RP,RRVL,RRWPLN,RRWPML,SUBE,SUFT,"
        #                                     "SUFS2RP,SULN,SUML,SUPP,TLC,TRMFS2RP,VL,WPLN,WPML,WP/VL,CTTRAINING,MISC,"
        #                                     "NO,CN,NPPTP,NPPTR,NOTIF,NLD,OP,OOC,PC,REOP,RRMISC,RRNO,RRNLD,RROP,RRPC,"
        #                                     "RRVA,RRVAEA,test,TC,UNKNOWN,VOID,ADLC,ADMO,AMAR,AMLC,AMMO,AC,AR,ASVL,ASSUM,"
        #                                     "LC,MMO,MDAR,MDLC,MDMO,MO,RFMO,RRADLC,RRADMO,RRAMAR,RRAMLC,RRAMMO,RRAC,RRAR,"
        #                                     "RRASSUM,RRLC,RRMDAR,RRMDLC,RRMDMO,RRMO,RRFRMO,RRSUAR,RRSULC,RRSUMO,RRSUVL,"
        #                                     "RRTR,RRWPLC,RRWPMO,RRWPVL,SUAR,SULC,SUMO,SUVL,WPLC,WPMO,WPVL,PT,REPT,RRPT,"
        #                                     "RRREPT,CB,CF,CONDOPLAT,CR,DB,IB,LB,MB,OR,PB,PLAT,RRCONDOPLT,RRPLAT,ZB,LWS,"
        #                                     "PO,HC,RELWS,REPO,REHC,RRLWS,RRPO,RRHC,RRRELWS,RRREPO,RRREHC,CTLC,CC,CCAR,"
        #                                     "CCLC,CCMO,CCVL,PR,PRAS,PRAC,PRAR,PRLC,PRMO,PRVL,RE,READMO,REAS,REAC,REAR,"
        #                                     "RECSL,REFLN,RELC,REMO,RETR,REVL,REMDMO,RRCC,RRCCAR,RRCCLC,RRCCMO,RRCCVL,"
        #                                     "RRPR,RRPRAS,RRPRAC,RRPRAR,RRPRLC,RRPRMO,RRPRVL,RRRE,RRRECSL,RRREAS,RRREAC,"
        #                                     "RRREAR,RRRELC,RRREMO,RRREOP,RRRETR,RRREVL,SPB,ADFS,ADFSRP,AMFS,AMFSRP,"
        #                                     "AMFS RP,ASFS,ASFSRP,ASFS RP,BWFS,COBWFS,COFS,COFSRP,COFS RP,CCBWFS,CCFSRP,"
        #                                     "CCFS RP,FS,FSRP,FS RP,FSCSRP,MDFS,MDFSRP,PRBWFS,PRFS,PRFSRP,PRFS RP,REBWFS,"
        #                                     "REFS,REFSRP,REFS RP,RRFSR1,RRAMFS,RRAMFSRP,RRASFS,RRASFSRP,RRBWFS,RRCOBWFS,"
        #                                     "RRCOFS,RRCOFSRP,RRCCBWFS,RRCCFSRP,RRFS,RRFSRP,RRFS RP,RRPRBWFS,RRPRFS,"
        #                                     "RRPRFSRP,RRREBWFS,RRREFS,RRREFSRP,RRSUFS,RRSUFSRP,RRTRMFS,RRTRMFSRP,SUFS,"
        #                                     "SUFSRP,TRMFS,TRMFSRP",
        #                     "INSTTYPEALL": "true",
        #                     "MAXPRICE": "",
        #                     "MINPRICE": "",
        #                     "ORDERBY_LIST": "",
        #                     "PARTY": "both",
        #                     "PLATS": "",
        #                     "QUARTER": "",
        #                     "RECSPERPAGE": "15",
        #                     "REMOVECHARACTERS": "true",
        #                     "SEARCHTYPE": "allNames",
        #                     "SELECTEDNAMES": "",
        #                     "TODATE": "",
        #                     "daterange_TODATE": "User Defined",
        #                     "searchCategory": "ADVANCED",
        #                     "searchSessionId": "searchJobMain",
        #                     "userRefCode": ""
        #                              },
        #                          headers={
        #                           'Cookie':'JSESSIONID={}'.format(self.token),
        #                           'origin': "https://countyfusion5.kofiletech.us",
        #                           'upgrade-insecure-requests': "1",
        #                           'content-type': "application/x-www-form-urlencoded",
        #                           'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
        #                           'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        #                           'cache-control': "no-cache",
        #                         },
        #                              cookies={'JSESSIONID': self.token},
        #                     callback=self.parse
        #                 )
            # return scrapy.FormRequest.from_response(
            #     url='https://countyfusion5.kofiletech.us/countyweb/login.do?countyname=Franklin',
            #     response,
            #     formdata={'username': 'john', 'password': 'secret'},
            #     callback=self.after_login
            # )

            #     scrapy.Request(
            #     url='https://countyfusion5.kofiletech.us/countyweb/login.do?countyname=Franklin',
            #     method='GET',
            #     callback=self.parse,
            #     meta={'dont_redirect': False, "parc_id": item,
            #           'spider_num': enumerator, 'cookiejar': enumerator},
            #     dont_filter=True,
            #     headers=self.HEADERS
            # )


    def open_function(self, response):
        open_in_browser(response)


    def parse(self, response):
        """

        :param response:
        :return:
        """
        print("Made it here")
        url = "https://countyfusion5.kofiletech.us/countyweb/search/searchExecute.do"

        querystring = {"assessor": "false"}

        payload = ""
        headers = {
            'Cookie': 'JSESSIONID=F6D19600E930E1191251627B21B9B4B8',
            'origin': "https://countyfusion5.kofiletech.us",
            'upgrade-insecure-requests': "1",
            'content-type': "application/x-www-form-urlencoded",
            'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
            'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            'cache-control': "no-cache",
            'postman-token': "09211b63-8281-7594-502f-f905df689e46"
        }

        yield  requests.request("POST", url, data=payload, headers=headers, params=querystring)

        print(response.text)
        #
        # yield scrapy.Request(url="https://countyfusion5.kofiletech.us/countyweb/search/searchExecute.do?assessor=false",
        #                    body=json.dumps({
        #                        "ALLNAMES": "bile",
        #                        "CASETYPE": "",
        #                        "DATERANGE": '[{"name": "TODATE", "value": "User Defined"}]',
        #                        "FROMDATE": "",
        #                        "INSTTYPE": "AS,ASAC,ASAL,ASAR,ASLC,ASMO,ASTR,RRAS,RRASAC,RRASAR,RRASLC,RRASMO,RRASTR,"
        #                                    "RRASVL,RRVET,VET,AF,AG,AMEA,AMZO,ANNEX,ASEA,AD,CTRL,CT,COND,CCCE,CE,DECL,DE,"
        #                                    "DISC,DA,EA,FA,MERGE,MDAG,PREA,REDECL,REEA,RRAF,RRAG,RRAMZO,RRANNEX,RRASEA,"
        #                                    "RRAD,RRCT,RRCONDO,RRCCCE,RRCE,RRDECL,RRDE,RRDISC,RRDA,RREA,RRFA,RRMERGE,"
        #                                    "RRDMAG,RRPREA,RRREDECL,RRREEA,RRSD,RRSUAG,RRSUEA,RRVAAL,RRZO,SD,SUAG,SUEA,TR,"
        #                                    "VA,VAAL,VAEA,ZO,AMFT,CCFT,FT,PRFT,RFFT,REFT,RVREFT,RRCCFT,RRFT,RRPRFT,RRREFT,WDFT,"
        #                                    "ADLE,AMLE,ASLE,CCLE,LE,MDLE,PRAL,PRLE,REAL,RELE,RRADLE,RRAMLE,RRASAL,RRAL,"
        #                                    "RRCCLE,RRLE,RRMDLE,RRPRAL,RRPRLE,RRREAL,RRRELE,RRSULE,RRWPLE,SULE,WPLE,AFO,"
        #                                    "AMFS2RP,AMML,ASFS2RP,ASLN,ASML,ASTLC,BE,BW,CSL,COBE,COBW,COFS2RP,CALN,CCBE,"
        #                                    "CCBW,CCFS2RP,CCLN,CCML,CCPP,EXTLC,FLN,FS2RP,LN,ML,MFLN,NOCS,PRBE,PRBW,PRFLN,"
        #                                    "PRFS2RP,PRLN,PRML,PRPP,PP,RB,RFTLC,RFBE,REBE,REBW,RECALN,REFS2RP,RELN,REML,"
        #                                    "REMFLN,REPP,RERB,RTLC,RRAFO,RRAMFS2RP,RRASFS2RP,RRASLN,RRASML,RRASTLC,RRBE,"
        #                                    "RRBW,RRCSL,RRCOBE,RRCOBW,RRCOFS2RP,RRCALN,RRCCBE,RRCCBW,RRCCFS2RP,RRCCLN,"
        #                                    "RRCCML,RRCCPP,RRFS2RP,RRLN,RRML,RRMFLN,RRCN,RRNOCS,RRTLC,RRPRBE,RRPRBW,"
        #                                    "RRPR2FSRP,RRPRLN,RRPRML,RRPRPP,RRPP,RRRB,RRRFBE,RRRFFT,RRREBE,RRREBW,"
        #                                    "RRRECALN,RRREFS2RP,RRRELN,RRREML,RRREMFLN,RRREPP,RRRERB,RRSUBE,RRSUFT,"
        #                                    "RRSUFS2RP,RRSULN,RRSUML,RRSUPP,RRTRMFS2RP,RRVL,RRWPLN,RRWPML,SUBE,SUFT,"
        #                                    "SUFS2RP,SULN,SUML,SUPP,TLC,TRMFS2RP,VL,WPLN,WPML,WP/VL,CTTRAINING,MISC,"
        #                                    "NO,CN,NPPTP,NPPTR,NOTIF,NLD,OP,OOC,PC,REOP,RRMISC,RRNO,RRNLD,RROP,RRPC,"
        #                                    "RRVA,RRVAEA,test,TC,UNKNOWN,VOID,ADLC,ADMO,AMAR,AMLC,AMMO,AC,AR,ASVL,ASSUM,"
        #                                    "LC,MMO,MDAR,MDLC,MDMO,MO,RFMO,RRADLC,RRADMO,RRAMAR,RRAMLC,RRAMMO,RRAC,RRAR,"
        #                                    "RRASSUM,RRLC,RRMDAR,RRMDLC,RRMDMO,RRMO,RRFRMO,RRSUAR,RRSULC,RRSUMO,RRSUVL,"
        #                                    "RRTR,RRWPLC,RRWPMO,RRWPVL,SUAR,SULC,SUMO,SUVL,WPLC,WPMO,WPVL,PT,REPT,RRPT,"
        #                                    "RRREPT,CB,CF,CONDOPLAT,CR,DB,IB,LB,MB,OR,PB,PLAT,RRCONDOPLT,RRPLAT,ZB,LWS,"
        #                                    "PO,HC,RELWS,REPO,REHC,RRLWS,RRPO,RRHC,RRRELWS,RRREPO,RRREHC,CTLC,CC,CCAR,"
        #                                    "CCLC,CCMO,CCVL,PR,PRAS,PRAC,PRAR,PRLC,PRMO,PRVL,RE,READMO,REAS,REAC,REAR,"
        #                                    "RECSL,REFLN,RELC,REMO,RETR,REVL,REMDMO,RRCC,RRCCAR,RRCCLC,RRCCMO,RRCCVL,"
        #                                    "RRPR,RRPRAS,RRPRAC,RRPRAR,RRPRLC,RRPRMO,RRPRVL,RRRE,RRRECSL,RRREAS,RRREAC,"
        #                                    "RRREAR,RRRELC,RRREMO,RRREOP,RRRETR,RRREVL,SPB,ADFS,ADFSRP,AMFS,AMFSRP,"
        #                                    "AMFS RP,ASFS,ASFSRP,ASFS RP,BWFS,COBWFS,COFS,COFSRP,COFS RP,CCBWFS,CCFSRP,"
        #                                    "CCFS RP,FS,FSRP,FS RP,FSCSRP,MDFS,MDFSRP,PRBWFS,PRFS,PRFSRP,PRFS RP,REBWFS,"
        #                                    "REFS,REFSRP,REFS RP,RRFSR1,RRAMFS,RRAMFSRP,RRASFS,RRASFSRP,RRBWFS,RRCOBWFS,"
        #                                    "RRCOFS,RRCOFSRP,RRCCBWFS,RRCCFSRP,RRFS,RRFSRP,RRFS RP,RRPRBWFS,RRPRFS,"
        #                                    "RRPRFSRP,RRREBWFS,RRREFS,RRREFSRP,RRSUFS,RRSUFSRP,RRTRMFS,RRTRMFSRP,SUFS,"
        #                                    "SUFSRP,TRMFS,TRMFSRP",
        #                        "INSTTYPEALL": "true",
        #                        "MAXPRICE": "",
        #                        "MINPRICE": "",
        #                        "ORDERBY_LIST": "",
        #                        "PARTY": "both",
        #                        "PLATS": "",
        #                        "QUARTER": "",
        #                        "RECSPERPAGE": "15",
        #                        "REMOVECHARACTERS": "true",
        #                        "SEARCHTYPE": "allNames",
        #                        "SELECTEDNAMES": "",
        #                        "TODATE": "",
        #                        "daterange_TODATE": "User Defined",
        #                        "searchCategory": "ADVANCED",
        #                        "searchSessionId": "searchJobMain",
        #                        "userRefCode": ""
        #                    }),
        #                    headers={
        #                        'origin': "https://countyfusion5.kofiletech.us",
        #                        'upgrade-insecure-requests': "1",
        #                        'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
        #                        'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        #                        'cache-control': "no-cache",
        #                    },
        #                    callback=self.open_function)
