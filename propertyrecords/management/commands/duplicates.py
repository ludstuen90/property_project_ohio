from django.core.management.base import BaseCommand, CommandError
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

        for x in range(0, 20):
            created_property = models.Property.objects.create(
                parcel_number=self.random_int_maker(5),
                legal_acres=self.random_int_maker(3),
                legal_description=self.random_string_maker(100),
                owner=self.random_string_maker(60),
                date_sold=datetime.datetime.now(),
                date_of_LLC_name_change=datetime.datetime.now(),
                date_of_mortgage=datetime.datetime.now(),
                mortgage_amount=self.random_int_maker(4),
                property_class=self.random_string_maker(2),
                land_use=self.random_string_maker(2),
                tax_district=self.random_string_maker(38),
                school_district=self.random_string_maker(38),
                tax_lien=True,
                cauv_property=False,
                rental_registration=False,
                current_market_value=self.random_int_maker(9),
                taxable_value=self.random_int_maker(8),
                year_2017_taxes=self.random_int_maker(9),
                tax_address_id=int(1),
                owner_address_id=int(4),
            )

            # Earlier big db is 1, 2
            models.PropertyAddress.objects.create(
                property_id=created_property.id,
                street_number=self.random_int_maker(4),
                street_name=self.random_string_maker(20),
                street_direction=self.random_string_maker(3),
                street_type=self.random_string_maker(4),
                secondary_address_line=self.random_string_maker(10),
                city=self.random_string_maker(20),
                state='OH',
                zipcode=self.random_int_maker(5)
            )

            if x%1000 == 0:
                print(x)


