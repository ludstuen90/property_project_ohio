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
        rel_path = "../../parcel_data/montgomery/taxroll/taxroll.csv" # <-- Look two directores up for relevant CSV files
        abs_file_path = os.path.join(script_dir, rel_path)
        print("Montgomery initial loading process initiated.")
        with open(abs_file_path, encoding="ISO-8859-1") as csvfile:
            reader = csv.DictReader(csvfile)
            for number, row in enumerate(reader):
                parcel_id = row['PARCELID      ']
                montgomery_county_property_item, created = models.Property.objects.get_or_create(
                    parcel_number=parcel_id
                )

                try:
                    montgomery_county_property_item.legal_acres = Decimal(row["ACRES            "])
                except InvalidOperation:
                    montgomery_county_property_item.legal_acres = None
                montgomery_county_property_item.legal_description = \
                    f'''{row['LEGAL1                                                      '].strip()} 
                        {row['LEGAL2                                                      '].strip()} 
                        {row["LEGAL3                                                      "].strip()}'''
                montgomery_county_property_item.owner = f'''{row["OWNERNAME1                              "].strip()} {row['OWNERNAME2                              '].strip()}'''
                montgomery_county_property_item.property_class = row['CLS '].strip()
                montgomery_county_property_item.land_use = row['LUC '].strip()
                montgomery_county_property_item.tax_district = row['TXDST'].strip()
                montgomery_county_property_item.school_district_name = row['SCHOOL DISTRICT                                   '].strip()
                montgomery_county_property_item.rental_registration = utils.convert_y_n_to_boolean(row['RENTALREG'].strip())
                montgomery_county_property_item.county = montgomery_county

                # Property address:
                parcel_property_address, created = models.PropertyAddress.objects.get_or_create(
                    property=montgomery_county_property_item,
                    city=row["CITY/TOWNSHIP                                     "].strip(),
                    zipcode=row["PARCEL LOCATION ZIP           "].strip(),
                    primary_address_line=row["PARCELLOCATION                          "].strip(),
                )

                try:
                    final_address_parse = utils.parse_city_state_and_zip_from_line(row["PADDR3                                                                                                                     "].strip(), True)
                except LookupError:
                    final_address_parse = {
                        'city' : '',
                        'state': '',
                        'zipcode': ''
                    }
                # Tax Address
                tax_address, created = models.TaxAddress.objects.get_or_create(
                    name=row['MAILINGNAME1                            '].strip(),
                    secondary_name=row['MAILINGNAME2                            '].strip(),
                    primary_address_line=row['PADDR1                                                                                                                   '].strip(),
                    secondary_address_line=row['PADDR2                                                                          '].strip(),

                    city=final_address_parse['city'],
                    state=final_address_parse['state'],
                    zipcode=final_address_parse['zipcode']
                )


                montgomery_county_property_item.save()
                if row['PARCELID      ']:
                    montgomery_county_property_item.save()
                # #
                if number % 1000 == 0:
                    print('We have processed the following number of records: ', number)

        print("Montgomery initial loading process completed.")
