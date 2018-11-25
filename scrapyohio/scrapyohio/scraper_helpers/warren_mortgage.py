import datetime
import json

import requests

from ohio import settings
from propertyrecords import models, utils


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
    DATE_FORMAT = '%m/%d/%Y %H:%M:%S %p'

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
        self.access_token = ''

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
        response_json = response.json()
        return response_json

    def retrieve_document_details(self, property_id_item):
        """

        :param property_id_item:
        :return:
        """
        # response = requests.request("POST", cls.WARREN_TOKEN_SITE, data=payload, headers=headers)

        payload = json.dumps({'id':property_id_item})

        response = requests.request("POST", self.WARREN_DOCUMENT_DETAIL, data=payload, headers=self.HEADERS )
        response_json = response.json()

        return response_json['DocumentDetail']['ConsiderationAmount']

    def download_mortgage_detail(self, property_dictionary):
        """
        This method expects a dictionary with the key as a Property django item and the value of
        a dictionary referring to recorder data in Warren County.

        To get the information we care about, the mortgage amount, we'll need to make one last call.
        Once we have this, we'll need to send another query to get more information on it
        :param property_dictionary: Dictionary {django_property_item:dictionary_of_recorder_data}
        :return: Information which has been saved to database
        """

        for django_item, mortgage_info in property_dictionary.items():
            mortgage_amount = self.retrieve_document_details(mortgage_info['Id'])
            django_item.mortgage_amount = mortgage_amount
            django_item.save()

    def identify_most_recent_mortage_for_each(self):
        property_items = {}

        for prop_to_parse in self.warren_county_items:
            recorder_data = self.download_list_of_recorder_data_items(f'''0{prop_to_parse.parcel_number}''')

            # Select the most recent mortgage item, and return it
            most_recent_item = utils.select_most_recent_mtg_item(recorder_data, self.DATE_FORMAT)
            if most_recent_item:
                # If no mortgage detected, do nothing.
                mortgage_date = datetime.datetime.strptime(most_recent_item['RecordedDateTime'], self.DATE_FORMAT)
                try:
                    if not prop_to_parse.date_sold <= datetime.datetime.date(mortgage_date):
                        pass
                    else:
                        property_items[prop_to_parse] = most_recent_item
                        prop_to_parse.date_of_mortgage = mortgage_date
                        prop_to_parse.save()
                except TypeError:
                    # In the case of us not having any date sold in our system, we shouldn't store mortgage.
                    pass
        return property_items

    def download_mortgage_info(self):
        """
        When this method is triggered, a process of downloading all
        mortgage information for Warren county properties in the database begins.
        :return: True or False indicating whether the process was able to complete
        successfully.

        """
        self.retrieve_access_token()

        results_dict = self.identify_most_recent_mortage_for_each()
        self.download_mortgage_detail(results_dict)

