import csv

from django.core.management.base import BaseCommand
import os

from scrapyohio.scrapyohio.scraper_helpers import warren_mortgage


class Command(BaseCommand):
    help = 'Command for querying parcel IDs'

    def handle(self, *args, **options):
        a = warren_mortgage.WarrenMortgageInfo()
        a.download_mortgage_info()