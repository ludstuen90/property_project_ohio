from django.contrib import admin
from propertyrecords import models

# Register your models here.


class AddressInline(admin.StackedInline):
    model = models.PropertyAddress


class TaxDataInline(admin.StackedInline):
    model = models.TaxData
    extra = 0


class PropertyAdmin(admin.ModelAdmin):
    inlines = (AddressInline, TaxDataInline)
    list_display = ('parcel_number', 'mortgage_amount', 'tax_lien', 'owner_occupancy_indicated',
                    'display_address')
    list_filter = ['county']
    search_fields = ['parcel_number']


admin.site.register(models.Property, PropertyAdmin)
admin.site.register(models.TaxAddress)
admin.site.register(models.County)
admin.site.register(models.DatabaseProgram)
admin.site.register(models.TaxData)