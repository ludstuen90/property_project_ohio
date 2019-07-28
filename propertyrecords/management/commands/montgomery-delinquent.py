import csv
from decimal import Decimal, InvalidOperation

from django.core.management.base import BaseCommand
import os

from propertyrecords import models, utils


class Command(BaseCommand):
    help = 'Command for querying parcel IDs'

    def handle(self, *args, **options):
        montgomery_county, created = models.County.objects.get_or_create(name='Montgomery')
        script_dir = os.path.dirname(__file__)  # <-- absolute dir this current script is in
        rel_path = "../../parcel_data/montgomery/delinquent/delinquent.csv" # <-- Look two directores up for relevant CSV files
        abs_file_path = os.path.join(script_dir, rel_path)
        print("Montgomery initial loading process initiated.")
        with open(abs_file_path, encoding="ISO-8859-1") as csvfile:
            reader = csv.DictReader(csvfile)
            for number, row in enumerate(reader):
                parcel_id = row['PARCELID      ']
                parcel_id_no_space = row['PARCELID      '].replace(' ', '')
                montgomery_county_property_item, created = models.Property.objects.get_or_create(
                    parcel_number=parcel_id_no_space,
                    county = montgomery_county
                )
                montgomery_county_property_item.save()
                montgomery_county_property_item.tax_delinquent = True
                montgomery_county_property_item.save()
                if number % 1000 == 0:
                    print('We have processed the following number of records: ', number)

        print("Montgomery initial loading process completed.")
