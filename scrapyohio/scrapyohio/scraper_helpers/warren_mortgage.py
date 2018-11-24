import json

import requests

from ohio import settings
from propertyrecords import models


class WarrenMortgageInfo:
    """
    Loop through all of the items in the database and scrape them.
    Make a new class for each scrape attempt? that seems wasteful

    Just do a method call? tha seems ... unsavory.

    Class with an active connection

    """
    access_token = ''
    WARREN_MORTGAGE_SITE = settings.WARREN_MORTGAGE_SITE
    WARREN_TOKEN_SITE = f'''{WARREN_MORTGAGE_SITE}/token'''
    WARREN_INITIAL_SEARCH = f'''{WARREN_MORTGAGE_SITE}/breeze/breeze/Search'''
    WARREN_DOCUMENT_DETAIL = f'''{WARREN_MORTGAGE_SITE}/breeze/breeze/DocumentDetail'''

    HEADERS = {
    'Content-Type': "application/json;charset=UTF-8",
    'Host': "oh3laredo.fidlar.com",
    'Origin': "https://oh3laredo.fidlar.com",
    'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36",
    'cache-control': "no-cache",
    }
    # Add in the journalism program contact information
    HEADERS.update(settings.CONTACT_INFO_HEADINGS)

    def __init__(self):
        # Warren county should exist here because it would have been created earlier in
        # warren.py
        self.warren_county_object = models.County.objects.get(name='Warren')
        self.warren_county_items = models.Property.objects.all().filter(county=self.warren_county_object)
        # self.access_token = self.retrieve_access_token()
        self.access_token = '12334'

    @classmethod
    def retrieve_access_token(cls, explicit_request=False):
        """
        This method is responsible for going out to retrieve an access token
        from the mortgage site and returns it.
        :return: A token with which to query the mortgage site
        """
        if len(cls.access_token) == 0 or explicit_request:
            payload = "grant_type=password&username=anonymous&password=&undefined="
            headers = {
                'Content-Type': "application/x-www-form-urlencoded",
                'cache-control': "no-cache",
            }

            response = requests.request("POST", cls.WARREN_TOKEN_SITE, data=payload, headers=headers)

            response_json = response.json()
            cls.access_token = response_json['access_token']
            access_token_dict = {'Authorization': f'''Bearer {cls.access_token}''', }
            cls.HEADERS.update(access_token_dict)
            return cls.access_token

    @classmethod
    def download_list_of_recorder_data_items(cls, parcel_number):
        """
        This method is in charge of going out to download mortgage i
        :param parcel_number:
        :return:
        """

        payload = json.dumps({"lastBusinessName":"","firstName":"","startDate":"","endDate":"","documentName":"",
                              "documentType":"","documentTypeName":"","book":"","page":"","subdivisionName":"",
                              "subdivisionLot":"","subdivisionBlock":"","municipalityName":"","tractSection":"",
                              "tractTownship":"","tractRange":"","tractQuarter":"","tractQuarterQuarter":"",
                              "addressHouseNo":"","addressStreet":"","addressCity":"","addressZip":"","parcelNumber":
                                  parcel_number,"referenceNumber":""})
        response = requests.request("POST", cls.WARREN_INITIAL_SEARCH, data=payload, headers=cls.HEADERS)


    def download_mortgage_info(self):
        """
        When this method is triggered, a process of downloading all
        mortgage information for Warren county properties in the database begins.
        :return: True or False indicating whether the process was able to complete
        successfully.

        """
        # Call access token to ensure that if we haven't downloaded a token yet, we will have one
        we_got = self.retrieve_access_token()

        for prop_to_parse in self.warren_county_items:
            self.download_list_of_recorder_data_items(prop_to_parse.parcel_number)




        # What is the desired behavior we want?
        # IF no access token, get one.
        # If access token expired, get a new one.
        # Otherwise, keep using an existing access token.
        # Where should access token be stored?
        # We could pretty much store it in this class....
        # I was requesting access tokens earlier and it didn't seen to be a problem.
