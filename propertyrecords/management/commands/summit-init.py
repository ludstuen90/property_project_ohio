import csv

from django.core.management.base import BaseCommand
import os

from propertyrecords import models


class Command(BaseCommand):
    help = 'Command for querying parcel IDs'

    def handle(self, *args, **options):
        summit_county, created = models.County.objects.get_or_create(name='Summit')
        script_dir = os.path.dirname(__file__)  # <-- absolute dir this current script is in
        rel_path = "../../parcel_data/summit.csv" # <-- Look two directores up for relevant CSV files
        abs_file_path = os.path.join(script_dir, rel_path)
        print("Warren initial loading process initiated.")
        with open(abs_file_path, encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for number, row in enumerate(reader):
                # print("Parcel: ", row['PARID'], "addr ", row['ADDR'], "OWN1: ", row['OWN1'], "OWN 2: ", row['OWN2'], 'CLASS ', row['CLASS'], " ACRES: ", " CALCAC", row['CALCARES'] )
                #own addr 3 must be more than 1 in length to count
                # print(row['OWNADDR1'],'#####', row['OWNADDR2'], '#####', row['OWNADDR3'], )
                #
                # WE can mostly count on the city and state but will be blank in case of out of country
                if len(row['OWNADDR3']) < 2:
                    print("!", row['OWNADDR1'], '\n', '?', row['OWNADDR2'], '\n', "CITY: ", row['CITYNAME'], row['STATECODE'], row['OWNZIP1'], '\n')

                print(row['OWNZIP1'], row['OWNZIP2'])

                # if len(row['OWNADDR3']) > 1:
                #     print(row['OWNADDR1'], row['OWNADDR2'], "CITYNAME: ", row['CITYNAME'], 'STATECODE', row['STATECODE'], '?!?!', row['OWNADDR2'], row['OWNADDR3'])
                #     print(row['COUNTRY'], '##', row['OWNADDR3'])
                #     print("len: ", len(row['OWNADDR3']), "OwnAddr1: ", row['OWNADDR1'], " 2 --- ", row['OWNADDR2'], ' - and 3 ', row['OWNADDR3'])


                # summit_county_property_item, created = models.Property.objects.get_or_create(parcel_number=row['PARID'])
                # summit_county_property_item.account_number = row['Account Number']
                # summit_county_property_item.county = summit_county
                # if row['Account Number']:
                #     summit_county_property_item.save()
                #
                # if number % 1000 == 0:
                #     print('We have processed the following number of reecords: ', number)

        print("Summit initial loading process completed.")

