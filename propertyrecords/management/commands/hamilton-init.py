import csv
import datetime

from django.core.management.base import BaseCommand
import os

from propertyrecords import models, utils


class Command(BaseCommand):
    help = 'Command for querying parcel IDs'

    def handle(self, *args, **options):
        # a = input('Is the Hamilton County parcel data to import saved inside of the '
        #           'propertyrecords/parcel_data/hamilton folder? Enter Y if so, or N if not. ')
        a = 'Y'
        if a.upper() == 'Y':
            print("Hamilton County initial loading process initiated.")

            hamilton_county, created = models.County.objects.get_or_create(name='Hamilton') # Create county object if doesn't exist
            script_dir = os.path.dirname(__file__)  # <-- absolute dir this current script is in
            rel_path = "../../parcel_data/hamilton" # <-- Look two directories up for relevant CSV files
            hamilton_directory_path = os.path.join(script_dir, rel_path)
            for filename in os.listdir(hamilton_directory_path):
                if filename.endswith(".csv"):
                    print(os.path.join(hamilton_directory_path, filename))
                    abs_file_path = os.path.join(hamilton_directory_path, filename)
                    with open(abs_file_path, encoding="ISO-8859-1") as csvfile:
                        reader = csv.DictReader(csvfile)
                        for number, row in enumerate(reader):
                            parcel_number = row['Parcel Number'].replace('-', '')
                            name = row['Name']
                            address = row['Address']
                            raw_sale_date = row['Sale Date']
                            try:
                                sale_date = datetime.datetime.strptime(raw_sale_date, "%m/%d/%Y").date()
                            except ValueError:
                                sale_date = None
                            hamilton_county_property_item, created = models.Property.objects.get_or_create(
                                parcel_number=parcel_number
                            )
                            hamilton_county_property_item.owner = name
                            hamilton_county_property_item.date_sold = sale_date
                            hamilton_county_property_item.county = hamilton_county
                            hamilton_county_property_item.save()
                            hamilton_county_address_item, created = models.PropertyAddress.objects.get_or_create(
                                property_id=hamilton_county_property_item.id
                            )
                            hamilton_county_address_item.primary_address_line = address
                            hamilton_county_address_item.save()

                            if number % 1000 == 0:
                                print('We have processed the following number of records: ', number)
                        continue
                else:
                    continue
