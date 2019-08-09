import csv

from django.core.management.base import BaseCommand
import os

from propertyrecords import models


class Command(BaseCommand):
    help = 'Command for querying parcel IDs'

    def handle(self, *args, **options):
        a = input('Is the Franklin County parcel data to import saved inside of the '
                  'propertyrecords/parcel_data folder, named franklin.csv? Enter Y if so, or N if not. ')
        if a.upper() == 'Y':
            franklin_county, created = models.County.objects.get_or_create(name='Franklin')
            script_dir = os.path.dirname(__file__)  # <-- absolute dir this current script is in
            rel_path = "../../parcel_data/franklin.csv" # <-- Look two directores up for relevant CSV files
            abs_file_path = os.path.join(script_dir, rel_path)
            print("Franklin initial loading process initiated.")
            with open(abs_file_path, encoding="ISO-8859-1") as csvfile:
                reader = csv.DictReader(csvfile)
                for number, row in enumerate(reader):
                    account_number = row['PID']
                    account_number = account_number.replace('-', '')
                    string_land_use_code = row['LANDUSE']
                    try:
                        land_use_code = int(string_land_use_code)
                    except ValueError:
                        pass

                    franklin_county_property_item, created = models.Property.objects.get_or_create(
                        parcel_number=account_number,
                    )
                    franklin_county_property_item.county = franklin_county
                    franklin_county_property_item.land_use = land_use_code
                    if row['PID']:
                        franklin_county_property_item.save()

                    if number % 1000 == 0:
                        print('We have processed the following number of reecords: ', number)

            print("Franklin initial loading process completed.")
        else:
            print("Script not confirmed to be in place. Exiting scrape.")