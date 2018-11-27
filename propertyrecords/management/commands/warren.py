import csv

from django.core.management.base import BaseCommand
import os

from propertyrecords import models


class Command(BaseCommand):
    help = 'Command for querying parcel IDs'

    def handle(self, *args, **options):
        warren_county = models.County.objects.get(name='Warren')
        script_dir = os.path.dirname(__file__)  # <-- absolute dir this current script is in
        rel_path = "../../parcel_data/warren.csv" # <-- Look two directores up for relevant CSV files
        abs_file_path = os.path.join(script_dir, rel_path)

        with open(abs_file_path, encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                warren_county_property_item, created = models.Property.objects.get_or_create(parcel_number=row['Parcel Number'])
                warren_county_property_item.county = warren_county
                warren_county_property_item.save()



