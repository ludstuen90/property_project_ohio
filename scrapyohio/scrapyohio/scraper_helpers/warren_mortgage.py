import requests

from ohio import settings


class WarrenMortgageInfo:
    """
    Loop through all of the items in the database and scrape them.
    Make a new class for each scrape attempt? that seems wasteful

    Just do a method call? tha seems ... unsavory.

    Class with an active connection

    """

    WARREN_TOKEN_SITE = settings.WARREN_TOKEN_SITE

    def __init__(self):
        self.access_token = self.retrieve_access_token()
        print("SELF ACCESS TOKEN IS: ", self.access_token)

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

        headers.update(settings.CONTACT_INFO_HEADINGS)

        response = requests.request("POST", self.WARREN_TOKEN_SITE, data=payload, headers=headers)
        response_json = response.json()

        return response_json['access_token']


a = WarrenMortgageInfo()
