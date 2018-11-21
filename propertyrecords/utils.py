# This function exists so that we can validate our Travis-CI instance works.
import csv
from datetime import datetime
from decimal import Decimal


def loop_through_csv_file_and_return_array_of_account_ids(absolute_csv_file_path):
    """
    Given a CSV file, this item will return the first item in the list. This is useful for storing the Account IDs
    in systems such as that of Warren County
    :param absolute_csv_file_path: absolute file path to CSV
    :return: a Python list of all items in the first row of each
    """
    list_of_parcel_ids = []

    with open(absolute_csv_file_path, encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                list_of_parcel_ids.append(row[0])
                line_count += 1
    return list_of_parcel_ids


def parse_white_space_from_each_line_of_address(address_to_parse):
    """
    Given an address, this method will return a version of the same address,
    but without white space.
    :param address: A list including address parameters
    :return: The same list but with extra spaces stripped out
    """

    parsed_addr = [x.strip() for x in address_to_parse if (len(x.strip()) != 0)]
    return parsed_addr


def parse_tax_address_from_css(parsed_tax_address):
    """
    This method removes a lot of junk from a parsed tax address. First, it removes
    the extra space that shows up in the result, and then it removes the spaces
    found in the actual address.
    :param result: A list of strings parsed from the DOM
    :return: A list containing the lines of the address.
    """
    parsed_tax_address = [x.replace("\r\n", "") for x in parsed_tax_address]
    parsed_tax_address = parse_white_space_from_each_line_of_address(parsed_tax_address)
    return parsed_tax_address


def parse_city_state_and_zip_from_line(address_line, state):
    """
    Given a string representing the last lines of an address block, this method will return the city,
    state and zip in an object
    :param address_line: 'RANCHO CUCA MONGA CA            98772'
    :param state: True or false, indicating whether the address includes a state.
    :return: {city: 'RANCHO CUCA MONGA', state: 'CA', zip: 98872}
    """
    last_line_length = len(address_line)
    zip_code = address_line[(last_line_length - 5):last_line_length]

    if address_line[(last_line_length - 6)] != ' ':
        raise LookupError("Unable to parse address. Zip code not in expected format.")

    if state:
        # We count back from the zip code, and look for a pattern that looks like a state abbreviation.
        # We hope to find a pattern like: 'Space space space two letters space space'
        for x in range(last_line_length - 6, 0, -1):
            if (
                    address_line[x].isalpha() == False and
                    address_line[x + 1].isalpha() == True and
                    address_line[x + 2].isalpha() == True and
                    address_line[x + 4].isalpha() == False
            ):
                state_name = f'''{address_line[x+1]}{address_line[x+2]}'''
                city_name = address_line[0:x]
        return {
            'city': str(city_name),
            'state': state_name,
            'zipcode': zip_code
        }
    else:
        # We count back from the zip code, and look for a pattern that looks like a state abbreviation.
        # We hope to find a pattern like: 'Space space space two letters space space'
        zipcode = address_line[-5:]
        for x in range(last_line_length - 6, 0, -1):
            if address_line[x].isalpha():
                city_name = address_line[:(x+1)]
                break
        return {
            'city': str(city_name),
            'zipcode': zipcode
        }


def convert_acres_to_integer(acres_string):
    """
    Accepts a string like '0.258 ACRES' and returns decimal of acres
    :param acres_string: '0.258 ACRES'
    :return: Number (decimal) of number of acres in the property
    """
    if acres_string[-6:] != ' ACRES':
        raise ValueError("Unexpected Acres format introduced")

    for number, character in enumerate(acres_string):
        if character == ' ':
            return Decimal(acres_string[:number])


def convert_taxable_value_string_to_integer(taxable_value_string):
    """
    Given a string that resembles a currency value, convert this value to
    an integer.
    Note, this will only work for integers, and not decimals.
    :param taxable_value_string:
    :return:
    """
    remove_currency_artifacts = taxable_value_string.replace("$", '').replace(",", "")
    if '.' in remove_currency_artifacts:
        if remove_currency_artifacts[-3:-2] != '.':
            raise ValueError("Input contains an unexpected decimal point.")

    return Decimal(remove_currency_artifacts)


def parse_ohio_state_use_code(use_string):
    """
    Given a string, this method will return the numerical value of the Ohio State Use Code
    :param use_string: A string containing a street value
    :return: numerical value of state use code
    """
    for number, character in enumerate(use_string):
        if character.isdigit():
            pass
        elif character == ' ':
            if use_string[0] == '0':
                return int(use_string[1:number])
            else:
                return int(use_string[:number])


def parse_address(address_block, state):
    """
    This method works to parse property addresses from Warren County. Keep this in mind as we expand.
    :param address_block:
    :param state:
    :return:
    """
    parsed_white_space = parse_white_space_from_each_line_of_address(address_block)
    length = len(address_block) - 1
    final_line_dict = parse_city_state_and_zip_from_line(parsed_white_space[length], state)
    primary_address_line = parsed_white_space[0]

    if length == 2:
        secondary_address_line = parsed_white_space[1]

    dict_return = {
        'primary_address_line': primary_address_line,
        'city': final_line_dict['city'],
        'zipcode': final_line_dict['zipcode']
    }

    try:
        if secondary_address_line:
            dict_return['secondary_address_line'] = secondary_address_line
    except UnboundLocalError:
        pass

    if state:
        dict_return['state']: final_line_dict['state']
    else:
        dict_return['state'] = 'OH'

    return dict_return

