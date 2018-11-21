# from django.test import TestCase
import os
from decimal import Decimal

import pytest

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


def test_parse_city_state_and_zip_from_line():
    one = 'LEBANON OH           45036'
    two = 'RANCHO CUCA MONGA CA          98662'
    three = 'ST. PAUL MN            55445'
    four = 'SAINT IGNACIUS             77228'

    result_one = utils.parse_city_state_and_zip_from_line(one, True)
    result_two = utils.parse_city_state_and_zip_from_line(two, True)
    result_three = utils.parse_city_state_and_zip_from_line(three, True)
    result_four = utils.parse_city_state_and_zip_from_line(four, False)

    assert result_one == {
        'city': 'LEBANON',
        'state': 'OH',
        'zipcode': '45036'
    }

    assert result_two == {
        'city': 'RANCHO CUCA MONGA',
        'state': 'CA',
        'zipcode': '98662'
    }

    assert result_three == {
        'city': 'ST. PAUL',
        'state': 'MN',
        'zipcode': '55445'
    }

    assert result_four == {
        'city': 'SAINT IGNACIUS',
        'zipcode': '77228'
    }


def test_convert_acres_to_integer():

    result = utils.convert_acres_to_integer('0.258 ACRES')

    assert result == Decimal('0.258')


def test_convert_taxable_value_string_to_integer():

    result_no_decimals = utils.convert_taxable_value_string_to_integer('$123,456')
    result_with_decimals = utils.convert_taxable_value_string_to_integer('$123,456.97')

    assert result_no_decimals == Decimal('123456')
    assert result_with_decimals == Decimal('123456.97')

    with pytest.raises(ValueError):
        utils.convert_taxable_value_string_to_integer('$123.456.789')


def test_parse_ohio_state_use_code():

    result = utils.parse_ohio_state_use_code('0510 - SINGLE FAMILY DWG (PLATTED)	')

    assert result == 510


def test_convert_y_n_to_boolean():

    result_y = utils.convert_y_n_to_boolean('Y')
    result_n = utils.convert_y_n_to_boolean('N')

    assert result_y is True
    assert result_n is False


def test_cauv_parser():

    result_y = utils.cauv_parser('$999')
    result_n = utils.cauv_parser('$0')

    assert result_y is True
    assert result_n is False