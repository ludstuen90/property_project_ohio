import csv

from django.core.management.base import BaseCommand
import os

from propertyrecords import models


class Command(BaseCommand):
    help = 'Command for querying parcel IDs'

    def handle(self, *args, **options):
        # a = input('Is the Montgomery County parcel data to import saved inside of the '
        #           'propertyrecords/parcel_data folder, named montgomery.csv? Enter Y if so, or N if not. ')
        # if a.upper() == 'Y':
        montgomery_county, created = models.County.objects.get_or_create(name='Montgomery')
        script_dir = os.path.dirname(__file__)  # <-- absolute dir this current script is in
        rel_path = "../../parcel_data/montgomery.csv" # <-- Look two directores up for relevant CSV files
        abs_file_path = os.path.join(script_dir, rel_path)
        print("Franklin initial loading process initiated.")
        with open(abs_file_path, encoding="ISO-8859-1") as csvfile:
            reader = csv.DictReader(csvfile)
            for number, row in enumerate(reader):
                parcel_id = row['PARCELID      ']
                print("Parcel ID: ", parcel_id)
                # account_number = account_number.replace('-', '')
                montgomery_county_property_item, created = models.Property.objects.get_or_create(
                    parcel_number=parcel_id
                )
                montgomery_county_property_item.county = montgomery_county
                if row['PARCELID      ']:
                    montgomery_county_property_item.save()
                # #
                if number % 1000 == 0:
                    print('We have processed the following number of records: ', number)

        print("Montgomery initial loading process completed.")
        # else:
        #     print("Script not confirmed to be in place. Exiting scrape.")