# from django.test import TestCase
import os

from propertyrecords import utils
from propertyrecords.test_data import parse_tax_address_from_csv

# Test to see that we can appropriately read a CSV file


def test_csv_file_reading_ability():
    script_dir = os.path.dirname(__file__)  # <-- absolute dir this current script is in
    relative_path_to_csv_file = "test_data/loop_through_csv_file_and_return_array_of_account_ids.csv"  # <-- Look two directores up for relevant CSV files
    abs_file_path = os.path.join(script_dir, relative_path_to_csv_file)

    result = utils.loop_through_csv_file_and_return_array_of_account_ids(abs_file_path)
    assert result == ['531367', '531375', '531383', '531391', '531405', '531413', '531421', '531448',
                      '531456', '531464']


def test_parse_tax_address_from_csv():

    returned_address = parse_tax_address_from_csv.returned_address
    expected_return = ['SMITH  JASON E & JENNIFER', '265 LUDLOW CT', 'LEBANON OH           45036']
    parsed_address = utils.parse_tax_address_from_css(returned_address)
    assert parsed_address == expected_return


