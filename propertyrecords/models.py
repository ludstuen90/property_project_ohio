from django.db import models


class Property(models.Model):
    parcel_number = models.BigIntegerField()
    legal_acres = models.DecimalField(max_digits=6, decimal_places=3)
    legal_description = models.CharField(max_length=120)
    owner = models.CharField(max_length=84)
    date_sold = models.DateField()
    date_of_LLC_name_change = models.DateField()
    date_of_mortgage = models.DateField()
    mortgage_amount = models.DecimalField(max_digits=12, decimal_places=2)
    property_class = models.CharField(max_length=3)
    land_use = models.CharField(max_length=3)
    tax_district = models.CharField(max_length=42)
    school_district = models.CharField(max_length=42)
    tax_lien = models.BooleanField()
    cauv_property = models.BooleanField()
    rental_registration = models.BooleanField()
    current_market_value = models.DecimalField(max_digits=12, decimal_places=2)
    taxable_value = models.DecimalField(max_digits=12, decimal_places=2)
    year_2017_taxes = models.DecimalField(max_digits=12, decimal_places=2)
    tax_address = models.ForeignKey(
        'TaxAddress',
        on_delete=models.CASCADE,
    )
    owner_address = models.ForeignKey(
        'OwnerAddress',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        """
        :return:
        """
        return f'''{self.parcel_number}'''

    class Meta:
        verbose_name_plural = "properties"

    @property
    def display_address(self):
        address = PropertyAddress.objects.get(property=self.id)
        return address


class AddressProperties(models.Model):
    """
    Here, we declare what sorts of things to expect in an address. Then, we inherit these properties
    later on, so as to keep our code neat and tidy.
    """

    street_number = models.IntegerField()
    street_name = models.CharField(max_length=24)
    street_direction = models.CharField(max_length=4, blank=True)
    street_type = models.CharField(max_length=6)
    secondary_address_line = models.CharField(max_length=16, blank=True, help_text="Apartment, Floor, Etc. ")
    city = models.CharField(max_length=24)
    state = models.CharField(max_length=2)
    zipcode = models.IntegerField()

    def __str__(self):
        self.address_string = f''' {self.street_number} {self.street_direction} { self.street_name}
            {self.street_type} {self.city}, {self.state} {self.zipcode}'''
        try:
            if self.name:
                return f'''{self.name}: {self.address_string}'''
            else:
                return self.address_string

        except AttributeError or TypeError:
            return self.address_string

    def save(self, *args, **kwargs):
        """
        Override default save mechanism so that state names are always saved in upper case
        """
        self.state = self.state.upper()
        return super(AddressProperties, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "address properties"


class PropertyAddress(AddressProperties):
    """
    Addresses listed of individual properties
    One to one relationship with properties
    """

    property = models.OneToOneField(
        Property,
        on_delete=models.CASCADE,
        primary_key=True,
    )

    class Meta:
        verbose_name_plural = "property addresses"


class TaxAddress(AddressProperties):
    """
    Addresses listed as taxable addresses on properties
    One to many relationship with properties
    """
    name = models.CharField(max_length=24, blank=True)

    class Meta:
        verbose_name_plural = "tax addresses"


class OwnerAddress(AddressProperties):
    """
    Addresses listed as property owners
    One to many relationship with properties

    """
    name = models.CharField(max_length=24, blank=True)

    class Meta:
        verbose_name_plural = "owner addresses"


class DatabaseProgram(models.Model):
    name = models.CharField(max_length=24)
    primary_url = models.CharField(max_length=82)
    parcel_download_url = models.CharField(max_length=82)
    type_of_key = models.CharField(max_length=12, help_text='Indicate what type of key we search with; i.e. parcel id? '
                                                            'account number?')

    def __str__(self):
        return self.name


class County(models.Model):
    name = models.CharField(max_length=18)
    database_type = models.ForeignKey(DatabaseProgram, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "counties"