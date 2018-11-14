from django.core.management.base import BaseCommand, CommandError
from propertyrecords import utils
import os


class Command(BaseCommand):
    help = 'Command for querying parcel IDs'

    def handle(self, *args, **options):
        script_dir = os.path.dirname(__file__)  # <-- absolute dir this current script is in
        rel_path = "../../parcel_data/warren.csv" # <-- Look two directores up for relevant CSV files
        abs_file_path = os.path.join(script_dir, rel_path)

        list_of_arrays = utils.loop_through_csv_file_and_return_array_of_account_ids(abs_file_path)
        print('?!?!?', list_of_arrays)