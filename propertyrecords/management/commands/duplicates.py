from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError

from propertyrecords import models

import string
import random

import datetime


class Command(BaseCommand):
    help = 'Command for querying parcel IDs'

    @staticmethod
    def random_string_maker(length):
        our_string = ''

        for letter in range(0, length):
            our_string += random.choice(string.ascii_letters)

        return our_string

    @staticmethod
    def random_int_maker(length):
        our_string = ''

        for letter in range(0, length):
            our_string += random.choice(string.digits)

        return int(our_string)

    def handle(self, *args, **options):

        junk_county, created = models.County.objects.get_or_create(name="junk")

        for x in range(0, 2874672):
            try:
                created_property = models.Property.objects.create(
                    parcel_number=self.random_int_maker(12),
                    legal_acres=self.random_int_maker(3),
                    legal_description=self.random_string_maker(100),
                    owner=self.random_string_maker(60),
                    date_sold=datetime.datetime.now(),
                    date_of_LLC_name_change=datetime.datetime.now(),
                    date_of_mortgage=datetime.datetime.now(),
                    mortgage_amount=self.random_int_maker(4),
                    property_class=self.random_int_maker(2),
                    land_use=self.random_int_maker(2),
                    tax_district=self.random_string_maker(38),
                    school_district_name=self.random_string_maker(38),
                    school_district=self.random_int_maker(4),
                    tax_lien=True,
                    cauv_property=False,
                    # current_market_value=self.random_int_maker(9),
                    # taxable_value=self.random_int_maker(8),
                    # year_2017_taxes=self.random_int_maker(9),
                    tax_address_id=int(1),
                    # owner_address_id=int(4),
                    county=junk_county,
                )

                # Earlier big db is 1, 2
                models.PropertyAddress.objects.create(
                    property_id=created_property.id,
                    primary_address_line=self.random_string_maker(25),
                    secondary_address_line=self.random_string_maker(20),
                    city=self.random_string_maker(20),
                    state='OH',
                    zipcode=self.random_int_maker(5)
                )
            except IntegrityError:
                pass

            if x%1000 == 0:
                print(x)


