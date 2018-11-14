from django.core.management.base import BaseCommand, CommandError
import csv
import os


class Command(BaseCommand):
    help = 'Command for querying parcel IDs'

    def handle(self, *args, **options):

        script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
        rel_path = "../../parcel_data/warren.csv"
        abs_file_path = os.path.join(script_dir, rel_path)

        with open(abs_file_path,  encoding="utf-8") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    print(f'''Account Number: {row[0]},Year: {row[1]} .''')
                    line_count += 1
                else:
                    print(f'''Account Number: {row[0]},Year: {row[1]} .''')
                    line_count += 1
            print(f'Processed {line_count} lines.')