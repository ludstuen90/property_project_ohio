import csv
import datetime
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError, MultipleObjectsReturned
from django.core.management.base import BaseCommand
import os

from propertyrecords import models, utils


class Command(BaseCommand):
    help = 'Command for querying parcel IDs'

    def file_reader_generator(self, specific_file_name):
        with open(specific_file_name, encoding="ISO-8859-1") as csvfile:
            reader = csv.DictReader(csvfile)
            # row_count = sum(1 for row in reader)
            for number, row in enumerate(reader):
                yield row

    def handle(self, *args, **options):
        montgomery_county, created = models.County.objects.get_or_create(name='Montgomery')
        # took out 2017 and 2018
        available_years = ['2002', '2001']
        # year = '2017'

        for year in available_years:
            script_dir = os.path.dirname(__file__)  # <-- absolute dir this current script is in
            rel_path = f'''../../parcel_data/montgomery/sales/{year}''' # <-- Look two directores up for relevant CSV files
            abs_path = os.path.join(script_dir, rel_path)
            files_in_dir = os.listdir(abs_path)
            print("Montgomery initial loading process initiated.")
            for file_name in files_in_dir:
                specific_file_name = os.path.join(abs_path, file_name)
                with open(specific_file_name, encoding="ISO-8859-1") as csvfile:
                    print(specific_file_name)
                    readerfiles = csv.DictReader(csvfile)
                    for row in self.file_reader_generator(specific_file_name):

                        # reader = csv.DictReader(csvfile)
                        parcel_id_no_space = row['PARID'].replace(' ', '')
                        if len(parcel_id_no_space) > 5:
                            # print(parcel_id_no_space)
                            montgomery_county_property_item, created = models.Property.objects.get_or_create(
                                parcel_number=parcel_id_no_space,
                                county=montgomery_county
                            )

                            try:
                                property_transfer, created = models.PropertyTransfer.objects.get_or_create(
                                guarantor= row['OLDOWN'].strip(),
                                guarantee =row['OWNERNAME1'].strip(),
                                sale_amount=row['PRICE'].strip(),
                                conveyance_number=row['CONVNUM'].strip(),
                                transfer_date=datetime.datetime.strptime(row['SALEDTE'], '%d-%b-%y'),
                                property=montgomery_county_property_item
                                )
                                montgomery_county_property_item.save()
                                property_transfer.save()
                            except (ValueError, ValidationError):
                                property_transfer, created = models.PropertyTransfer.objects.get_or_create(
                                guarantor= row['OLDOWN'].strip(),
                                guarantee =row['OWNERNAME1'].strip(),
                                conveyance_number=row['CONVNUM'].strip(),
                                property=montgomery_county_property_item
                                )
                                montgomery_county_property_item.save()
                                property_transfer.save()

                            except KeyError:
                                # Some files don't have conveyance number - continue on!
                                try:
                                    property_transfer, created = models.PropertyTransfer.objects.get_or_create(
                                    guarantor= row['OLDOWN'].strip(),
                                    guarantee =row['OWNERNAME1'].strip(),
                                    property=montgomery_county_property_item
                                    )
                                    montgomery_county_property_item.save()
                                    property_transfer.save()
                                except MultipleObjectsReturned as e:
                                    # If we get more than one result, overwrite the first.
                                    # Doesn't appear to happen often
                                    print("EXCEPTION raised: ", e)
                                    property_transfer = models.PropertyTransfer.objects.filter(
                                        guarantor=row['OLDOWN'].strip(),
                                        guarantee=row['OWNERNAME1'].strip(),
                                        property=montgomery_county_property_item
                                    ).first()
                                    montgomery_county_property_item.save()
                                    property_transfer.save()

