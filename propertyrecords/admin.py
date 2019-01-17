from django.contrib import admin
from propertyrecords import models

# Register your models here.


class AddressInline(admin.StackedInline):
    model = models.PropertyAddress
    can_delete = False

class TaxDataInline(admin.StackedInline):
    model = models.TaxData
    extra = 0
    can_delete = False

class PropertyTransferInline(admin.TabularInline):
    model = models.PropertyTransfer
    extra = 0
    can_delete = False

class PropertyAdmin(admin.ModelAdmin):
    inlines = (AddressInline, TaxDataInline, PropertyTransferInline)
    list_display = ('parcel_number', 'mortgage_amount', 'tax_lien', 'owner_occupancy_indicated',
                    'display_address', 'last_scraped_one')
    readonly_fields = ['tax_address']
    list_filter = ['county']
    search_fields = ['parcel_number']


admin.site.register(models.Property, PropertyAdmin)
admin.site.register(models.TaxAddress)
admin.site.register(models.County)
admin.site.register(models.DatabaseProgram)
admin.site.register(models.TaxData)