from datetime import timezone

from django.shortcuts import render
from django.views.generic import list

from propertyrecords import models

# Create your views here.


class CountyListView(list.ListView):

    model = models.Property

    warren_county = models.County.objects.get(name='Warren')
    paginate_by = 100  # if pagination is desired

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_list'] = models.Property.objects.filter(county=self.warren_county)
        context['num_county_prop'] = len(models.Property.objects.filter(county=self.warren_county))
        context['mort_info'] = len(models.Property.objects.filter(county=self.warren_county,
                                                                  ).exclude(mortgage_amount__isnull=True
                                                                            ))


        context['scanned_for_mort'] = len(models.Property.objects.filter(county=self.warren_county
                                                                     ).exclude(last_scraped_one__isnull=True))

        context['pcrt_scanned'] = "{:.0%}".format(context['scanned_for_mort']/context['num_county_prop'])
        context['prct_w_mort'] = "{:.0%}".format(context['mort_info']/context['num_county_prop'])
        # context['now'] = timezone.now()
        return context
