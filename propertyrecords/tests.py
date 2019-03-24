# from django.test import TestCase
import os
import re
from datetime import datetime
from decimal import Decimal

import bs4
import pytest

import pickle

from bs4 import BeautifulSoup

from propertyrecords import utils
from propertyrecords.test_data import parse_tax_address_from_csv, select_most_recent_mtg_item


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
    result_yes = utils.convert_y_n_to_boolean('yes')
    result_n = utils.convert_y_n_to_boolean('N')
    result_no = utils.convert_y_n_to_boolean('no')

    assert result_y is True
    assert result_yes is True
    assert result_n is False
    assert result_no is False


def test_cauv_parser():

    result_y = utils.cauv_parser('$999')
    result_n = utils.cauv_parser('$0')

    assert result_y is True
    assert result_n is False


def test_select_most_recent_mtg_item():

    test_data = select_most_recent_mtg_item.results
    parsed_result = utils.select_most_recent_mtg_item(test_data,'%m/%d/%Y %H:%M:%S %p')
    expected_result = {'Id': 6323317, 'DocumentName': '2018-032687', 'DocumentType': 'MTG', 'RecordedDateTime': '11/14/2018 8:01:03 AM', 'Party1': 'SMITH, JASON E', 'Party2': 'FIFTH THIRD BANK', 'LegalSummary': ''}

    assert parsed_result == expected_result


def test_base64_string_convert():

    converted_string = utils.convert_string_to_base64_bytes_object('Parcel')

    assert 'UGFyY2Vs' == converted_string

def test_cuyahoga_addr_splitter():

    dirname, filename = os.path.split(os.path.abspath(__file__))
    pickle_path1 = os.path.join(dirname, 'test_data/cuyahoga_address1.p')

    addr1 = pickle.load(open(pickle_path1, "rb"))
    first_result = utils.cuyahoga_addr_splitter(addr1)

    assert first_result == {'primary_address': '13461 LORAIN AVE', 'city': 'CLEVELAND',
                            'zipcode': '44111', 'state': 'OH'}

    pickle_path2 = os.path.join(dirname, 'test_data/cuyahoga_address2.p')
    addr2 = pickle.load(open(pickle_path2, "rb"))
    second_result = utils.cuyahoga_addr_splitter(addr2)

    assert second_result == {'primary_address': '633 FALLS RD', 'city': 'CHAGRIN FALLS TWP',
                            'zipcode': '44022', 'state': 'OH'}

    pickle_path3 = os.path.join(dirname, 'test_data/cuyahoga_address3.p')
    addr3 = pickle.load(open(pickle_path3, "rb"))
    third_result = utils.cuyahoga_addr_splitter(addr3)

    assert third_result == {'primary_address': '1951 W 26', 'city': 'CLEVELAND',
                            'zipcode': '44113', 'state': 'OH'}

    pickle_path4 = os.path.join(dirname, 'test_data/cuyahoga_address4.p')
    addr4 = pickle.load(open(pickle_path4, "rb"))
    fourth_result = utils.cuyahoga_addr_splitter(addr4)

    assert fourth_result == {'primary_address': '', 'city': '',
                            'zipcode': '0', 'state': ''}




def test_cuyahoga_tax_address_storer():
    dirname, filename = os.path.split(os.path.abspath(__file__))
    pickle_path1 = os.path.join(dirname, 'test_data/cuyahoga_address_tax1.p')

    addr1 = pickle.load(open(pickle_path1, "rb"))
    first_result = utils.cuyahoga_tax_address_parser(addr1)

    assert first_result == {'primary_address_line': 'SCOTT MADIS', 'secondary_address_line':
        '950 W LIBERTY', 'city': 'MEDINA', 'state': 'OH', 'zipcode': '44256'}

    pickle_path2 = os.path.join(dirname, 'test_data/cuyahoga_address_tax2.p')

    addr2 = pickle.load(open(pickle_path2, "rb"))
    second_result = utils.cuyahoga_tax_address_parser(addr2)

    assert second_result == {'primary_address_line': 'MARY COYNE NOGUERAS', 'secondary_address_line':
        'P O  BOX  110324', 'city': 'CLEVELAND', 'state': 'OH', 'zipcode': '44111'}



    pickle_path3 = os.path.join(dirname, 'test_data/cuyahoga_address_tax3.p')

    addr3 = pickle.load(open(pickle_path3, "rb"))
    third_result = utils.cuyahoga_tax_address_parser(addr3)

    assert third_result == {'primary_address_line': 'WELLS FARGO MORTGAGE RE TAX SERVICE', 'secondary_address_line':
        '1 HOME CAMPUS   MAC X2502-011', 'city': 'DES MOINES', 'state': 'IA', 'zipcode': '50328'}


    pickle_path4 = os.path.join(dirname, 'test_data/cuyahoga_address_tax4.p')

    addr4 = pickle.load(open(pickle_path4, "rb"))
    fourth_result = utils.cuyahoga_tax_address_parser(addr4)

    assert fourth_result == {'primary_address_line': 'CMHA', 'secondary_address_line': 'PO BOX 94967', 'city':
        'CLEVELAND', 'state': 'OH', 'zipcode': '44101'}


def test_cuyahoga_recorder_parser():
    dirname, filename = os.path.split(os.path.abspath(__file__))
    pickle_path1 = os.path.join(dirname, 'test_data/cuyahoga_mort_deed_data1.p')
    pickle_path2 = os.path.join(dirname, 'test_data/cuyahoga_mort_deed_data2.p')

    html_response1 = pickle.load(open(pickle_path1, "rb"))
    soup1 = BeautifulSoup(html_response1, 'html.parser')

    html_response2 = pickle.load(open(pickle_path2, "rb"))
    html_response2 = html_response2.replace('\n', '')
    print("html", html_response2)
    soup2 = BeautifulSoup(html_response2, 'html.parser')

    deed_search_result = utils.parse_recorder_items(soup1, '2015 WEST 53RD LLC', 'DEED')
    mortgage_search_result = utils.parse_recorder_items(soup1, '2015 WEST 53RD LLC', 'MORT')
    lowercase_search_result = utils.parse_recorder_items(soup1, '2015 west 53rd llc', 'MORT')
    period_search_result = utils.parse_recorder_items(soup1, '2015 WEST, 53RD LLC.', 'MORT')
    extra_space_search_result = utils.parse_recorder_items(soup1, '2015 WEST, 53RD            LLC.', 'MORT')
    no_results_result = utils.parse_recorder_items(soup2, 'CASE # CV#16861346', 'DEED')

    assert deed_search_result == '3/26/2013'
    assert mortgage_search_result == '10/23/2013'
    assert lowercase_search_result == '10/23/2013'
    assert period_search_result == '10/23/2013'
    assert extra_space_search_result == '10/23/2013'
    assert no_results_result is None

    with pytest.raises(TypeError):
        utils.parse_recorder_items(soup1, '2015 WEST 53RD LLC', 'COFFEE')


def test_convert_to_string_and_drop_final_zero():

    string_result = utils.convert_to_string_and_drop_final_zero('12312000410')
    integer_result = utils.convert_to_string_and_drop_final_zero(16364510030)

    assert string_result == '1231200041'
    assert integer_result == '1636451003'


def test_datetime_to_date_string_parser():
    result_one = utils.datetime_to_date_string_parser('10/7/1977 12:00:00 AM', '%m/%d/%Y')

    result_two = utils.datetime_to_date_string_parser('10/07/1999 12:00:00 AM', '%m/%d/%Y')

    assert result_one == datetime(1977, 10, 7, 0, 0)

    assert result_two == datetime(1999, 10, 7, 0, 0)

def test_acreage_adder():
    script_dir = os.path.dirname(__file__)
    relative_path_to_file = "test_data/franklin_acre_data.pickle"
    abs_file_path = os.path.join(script_dir, relative_path_to_file)
    pickle_in = open(abs_file_path, "rb")
    dummy_response = pickle.load(pickle_in)
    soup = BeautifulSoup(dummy_response, 'html.parser')
    table = soup.find('table', id="Land Characteristics")
    rows = table.find_all('tr', recursive=False)
    result_one = utils.calculate_total_number_of_acres(rows)
    assert result_one == 2.02


def test_name_parser_and_joiner():

    test_one_name_one = "CITY OF NEW ALBANY"
    blank_string = ""

    test_two_name_one = 'VERST ROBERT E JR'
    test_two_name_two = 'VERST ROSEANNE I'

    result_one = utils.name_parser_and_joiner(test_one_name_one, blank_string)

    result_two = utils.name_parser_and_joiner(test_two_name_one, test_two_name_two)
    assert result_one == "CITY OF NEW ALBANY"
    assert result_two == "VERST ROBERT E JR & VERST ROSEANNE I"


def test_row_value_getter_franklin():
    script_dir = os.path.dirname(__file__)
    relative_path_to_file = "test_data/franklin_verst.pickle"
    abs_file_path = os.path.join(script_dir, relative_path_to_file)
    pickle_in = open(abs_file_path, "rb")
    dummy_response = pickle.load(pickle_in)
    soup = BeautifulSoup(dummy_response, 'html.parser')

    most_recent_transfer_date = utils.franklin_row_name_returner(soup, "Most Recent Transfer", "Transfer Date")
    calculated_acres = utils.franklin_row_name_returner(soup, "Owner", "Calculated Acres")
    prop_status = utils.franklin_row_name_returner(soup, re.compile("Tax Status"), "Property Class")
    raw_value = utils.franklin_row_name_returner(soup, re.compile("Tax Status"), "Property Class", True)

    assert 'SEP-27-2011' == most_recent_transfer_date
    assert '2.02' == calculated_acres
    assert 'R - Residential' == prop_status
    assert type(raw_value) == bs4.element.Tag

def test_find_td_cell_value_beneath_current_bssoup():
    script_dir = os.path.dirname(__file__)
    relative_path_to_file = "test_data/franklin_verst.pickle"
    abs_file_path = os.path.join(script_dir, relative_path_to_file)
    pickle_in = open(abs_file_path, "rb")
    dummy_response = pickle.load(pickle_in)
    soup = BeautifulSoup(dummy_response, 'html.parser')

    owner_cell = utils.franklin_row_name_returner(soup, "Owner", "Owner", True)
    secondary_owner_attempt = utils.find_td_cell_value_beneath_current_bssoup(owner_cell)

    assert "VERST ROSEANNE I" == secondary_owner_attempt



def test_franklin_county_credit_parser():

    occ = "2018: Yes 2019: Yes"
    hcc = "2018: No 2019: No"

    assert utils.franklin_county_credit_parser(occ) is True
    assert utils.franklin_county_credit_parser(hcc) is False