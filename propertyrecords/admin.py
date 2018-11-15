from django.contrib import admin
from propertyrecords import models

# Register your models here.


class AddressInline(admin.StackedInline):
    model = models.PropertyAddress


class PropertyAdmin(admin.ModelAdmin):
    inlines = (AddressInline,)
    list_display = ('parcel_number', 'mortgage_amount', 'tax_lien', 'rental_registration', 'current_market_value',
                    'display_address')


admin.site.register(models.Property, PropertyAdmin)
admin.site.register(models.TaxAddress)
admin.site.register(models.OwnerAddress)
admin.site.register(models.County)
admin.site.register(models.DatabaseProgram)