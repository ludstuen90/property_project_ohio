from datetime import timezone

from django.shortcuts import render
from django.views.generic import list

import propertyrecords
from propertyrecords import models

# Create your views here.


class CountyListView(list.ListView):

    model = models.Property

    # warren_county = models.County.objects.get(name='Warren')
    paginate_by = 100  # if pagination is desired

    def get_context_data(self, **kwargs):
        county = self.kwargs.get('county')
        context = super().get_context_data(**kwargs)
        context['all_counties'] = models.County.objects.all()
        try:
            self.county_object = models.County.objects.get(name__iexact=county)

            context['object_list'] = models.Property.objects.filter(county=self.county_object)
            context['num_county_prop'] = len(models.Property.objects.filter(county=self.county_object))
            context['mort_info'] = len(models.Property.objects.filter(county=self.county_object,
                                                                      ).exclude(mortgage_amount__isnull=True
                                                                                ))

            context['scanned_for_mort'] = len(models.Property.objects.filter(county=self.county_object
                                                                         ).exclude(last_scraped_one__isnull=True))

            context['pcrt_scanned'] = "{:.0%}".format(context['scanned_for_mort']/context['num_county_prop'])
            context['prct_w_mort'] = "{:.0%}".format(context['mort_info']/context['num_county_prop'])

            context['county_name'] = self.kwargs.get('county')
            context['parsed_county'] = True

        except:
            pass
        return context
