import datetime
import json
import requests

from ohio import settings
from propertyrecords import models, utils


class WarrenMortgageInfo:
    """
    Loop through all of the Warren County
    properties items in the database and scrape the
    mortgage date and amount if possible.
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

        self.warren_county_items = models.Property.objects.filter(county=self.warren_county_object).order_by('?')

    def retrieve_access_token(self):
        """
        This method is responsible for going out to retrieve an access token
        from the mortgage site and returns it.
        :return: A token with which to query the mortgage site
        """
        payload = "grant_type=password&username=anonymous&password=&undefined="
        headers = {
            'Content-Type': "application/x-www-form-urlencoded",
            'cache-control': "no-cache",
        }

        response = requests.request("POST", self.WARREN_TOKEN_SITE, data=payload, headers=headers)

        response_json = response.json()
        self.access_token = response_json['access_token']
        access_token_dict = {'Authorization': f'''Bearer {self.access_token}''', }
        self.HEADERS.update(access_token_dict)
        return self.access_token

    def download_list_of_recorder_data_items(self, parcel_number, **kwargs):
        """
        This method is in charge of going out to download mortgage information.
        :param parcel_number:
        :return:
        """

        payload = json.dumps({"lastBusinessName":"","firstName":"","startDate":"","endDate":"","documentName":"",
                              "documentType": "","documentTypeName":"","book":"","page":"","subdivisionName":"",
                              "subdivisionLot": "","subdivisionBlock":"","municipalityName":"","tractSection":"",
                              "tractTownship": "","tractRange":"","tractQuarter":"","tractQuarterQuarter":"",
                              "addressHouseNo": "","addressStreet":"","addressCity":"","addressZip": "", "parcelNumber":
                                  parcel_number, "referenceNumber": ""})

        response = requests.request("POST", self.WARREN_INITIAL_SEARCH, data=payload, headers=self.HEADERS)
        response_json = response.json()

        if response_json.get('Msg', '') == 'Session is invalid':
            if kwargs.get('second_attempt', ''):
                raise ConnectionError()
            else:
                self.retrieve_access_token()
                return self.download_list_of_recorder_data_items(parcel_number, second_attempt=True)
        return response_json

    def retrieve_document_details(self, property_id_item):
        """

        :param property_id_item:
        :return:
        """
        payload = json.dumps({'id': property_id_item})

        response = requests.request("POST", self.WARREN_DOCUMENT_DETAIL, data=payload, headers=self.HEADERS)
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
            try:
                mortgage_amount = self.retrieve_document_details(mortgage_info['Id'])
                django_item.mortgage_amount = mortgage_amount
                print("Found mortgage date of $", mortgage_amount, " date ", django_item.date_of_mortgage,
                      " on account number: ", django_item.account_number)
                django_item.save()
            except KeyError:
                # For some reason, we couldn't return the details we wanted. Keep strong, and carry on .
                pass

    def identify_most_recent_mortage_for_each(self):
        property_items = {}

        for prop_to_parse in self.warren_county_items:
            trimmed_parcel_number = utils.convert_to_string_and_drop_final_zero(prop_to_parse.parcel_number)
            recorder_data = self.download_list_of_recorder_data_items(trimmed_parcel_number)
            # Select the most recent mortgage item, and return it
            most_recent_item = utils.select_most_recent_mtg_item(recorder_data, self.DATE_FORMAT)
            if most_recent_item:
                # If no mortgage detected, do nothing.
                mortgage_date = datetime.datetime.strptime(most_recent_item['RecordedDateTime'], self.DATE_FORMAT)
                try:
                    if not prop_to_parse.date_sold <= datetime.datetime.date(mortgage_date):
                        print("No mortgage identified on account number: ", prop_to_parse.account_number)
                        pass
                    else:
                        property_items[prop_to_parse] = most_recent_item
                        prop_to_parse.date_of_mortgage = mortgage_date
                        prop_to_parse.save()
                        self.download_mortgage_detail({prop_to_parse: most_recent_item})

                except TypeError:
                    # In the case of us not having any date sold in our system, we should store the data. The first owners
                    # would have a mortgage.
                    property_items[prop_to_parse] = most_recent_item
                    prop_to_parse.date_of_mortgage = mortgage_date
                    prop_to_parse.save()
                    self.download_mortgage_detail({prop_to_parse: most_recent_item})

        return property_items

    def download_mortgage_info(self):
        """
        When this method is triggered, a process of downloading all
        mortgage information for Warren county properties in the database begins.
        :return: True or False indicating whether the process was able to complete
        successfully.

        """
        self.retrieve_access_token()
        self.identify_most_recent_mortage_for_each()
        print("The script has finished successfully.")
