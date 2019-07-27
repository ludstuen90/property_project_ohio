# This function exists so that we can validate our Travis-CI instance works.
import base64
import csv
import datetime
import re
from decimal import Decimal
from bs4 import BeautifulSoup


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


def cuyahoga_addr_splitter(input_address_string):
    """
    This method converts addresses as they are returned from
    Cuyahoga's Property management system into a a format we can
    store in our database.

    It handles city names that are one to many words long, as well
    as addresses that are not stored. (IE: Records that say just ','
    :param address_string:
    :return: Dictionary of all relevant properties
    """
    address_string = input_address_string.split('\n')
    list = []

    try:
        for item in address_string:
            list.append(item.strip())
        city_line = list[2].split(' ')


        if len(city_line) == 1:
            primary_address = f'''{list[1]}'''
        else:
            primary_address = f'''{list[1]} {city_line[0]}'''

        normalized_primary_address = " ".join(primary_address.split()).upper()
        list_len = len(list)
        zip_code = list[list_len-2]

        if len(zip_code) == 0:
            zip_code = '0'

        city_state_split = city_line[-1].split(',')

        first_city_name = ''
        for item in city_line[1:-1]:
            first_city_name += f'''{item.upper()} '''

        city_name = f'''{first_city_name}{city_state_split[0].upper() }'''
        state = city_state_split[1]

        return {
            'primary_address': normalized_primary_address,
            'city': city_name,
            'zipcode': zip_code,
            'state': state
        }
    except IndexError:
        return {
            'primary_address': address_string,
            'city': '',
            'zipcode': '0',
            'state': ''

        }
    # Then to get the city, we will just ['', '633   Falls', 'RD Chagrin Falls Twp,OH', '44022']
    # split the space split on the comma,and add in all the not-street-Rd thing as city,
    # and the right side of the equation becomes the state
    # zip is standard
    #then we can delete all the mess above.
    # be sure to handle when things are not real addresses!


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
    new_zip_format = False
    space_before_zipcode = 6

    if address_line[(last_line_length - 5)] == ' ':
        listed = list(address_line)
        listed[(last_line_length-5)] = '-'
        address_line = "".join(listed)


    if address_line[(last_line_length - 5)] == '-' and address_line[(last_line_length - 11)] == ' ':
        new_zip_format = True

    elif address_line[(last_line_length - 6)] != ' ':
        raise LookupError("Unable to parse address. Zip code not in expected format.")

    # Logic to set out how to parse city/state and zipcode patterns from end of line, according to flags raised
    if new_zip_format and state:
        space_before_zipcode = 11
        zip_code = address_line[(last_line_length - 10):last_line_length]
    elif state:
        # state yes, trad
        zip_code = address_line[(last_line_length - 5):last_line_length]
    elif new_zip_format:
        zip_code = address_line[(last_line_length - 10):last_line_length]
    else:
        # state no, trad
        zip_code = address_line[-5:]

    if state:
        # We count back from the zip code, and look for a pattern that looks like a state abbreviation.
        # We hope to find a pattern like: 'Space space space two letters space space'
        for x in range(last_line_length - space_before_zipcode, 0, -1):
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

        for x in range(last_line_length - space_before_zipcode, 0, -1):
            if address_line[x].isalpha():
                city_name = address_line[:(x+1)]
                break
        return {
            'city': str(city_name),
            'zipcode': zip_code
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


def decimal_converter(input_number):
    """
    This method strips a string of its commas, and converts the resulting integer into a decimal object. This is used
    in Franklin County
    :param input_number: A string, in the form of something like "72,192.02"
    :return: the same number, but in the format of a Decimal type
    """

    input_number_no_comma = input_number.replace(',', '')
    return Decimal(input_number_no_comma)



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


def convert_y_n_to_boolean(response_string):
    """
    Given a string value, will return True
    if string value is equal to "Y"
    :param response_string:
    :return:
    """
    if response_string.upper() == 'Y' or response_string.upper() == 'YES':
        return True
    else:
        return False


def cauv_parser(cauv_value):
    """

    :param cauv_value:
    :return:
    """
    if cauv_value != '$0':
        return True
    else:
        return False


def select_most_recent_mtg_item(recorder_data_dict, date_format):
    most_recent_result_found = {}

    try:
        mtg_items = [item for item in recorder_data_dict['DocResults']
                     if item['DocumentType'] == 'MTG' or
                     item['DocumentType'] == 'LC']

    except KeyError:
        # This indicates we have not found any meeting type documents in this record.
        return False

    if len(mtg_items) == 0:
        return False

    for memo in mtg_items:
        if most_recent_result_found == {}:
            most_recent_result_found = memo
        else:
            if datetime.datetime.strptime(memo['RecordedDateTime'], date_format) > datetime.datetime.strptime(most_recent_result_found['RecordedDateTime'], date_format):
                most_recent_result_found = memo

    return most_recent_result_found


def find_property_information_by_name(soup, td_name):
    """
    Given a property name, this will return the value of the item 2 elements down. (Elements defined in Beautiful Soup
    :param td_name:
    :return: Value of TD item two elements down
    """

    item_returned = soup.body.find(text=re.compile(f'''^{td_name}'''))
    return item_returned.next_element.next_element.contents[0].contents[0]


def cuyahoga_county_name_street_parser(string1, string2):
    """

        #Split name from earlier line
    # LOOK FOR PO BOX OR ADDRESS NUMBER
    # start back from end of first line and look for where the LAST NUMBER ends
    # but also be able to capture the last single letter if it's a cardinal number

    """
    name_line_length = (len(string1) -1)

    in_first_line_we_have_encountered_a_digit = False

    for character_num in range(name_line_length, 0, -1):
        if string1[character_num].isdigit():
            in_first_line_we_have_encountered_a_digit = True
        elif string1[character_num].isspace() and in_first_line_we_have_encountered_a_digit:
            primary_line = string1[:character_num]
            secondary_line = f'''{string1[character_num+1:]} {string2}'''
            return {
                'primary_line': primary_line,
                'secondary_line': secondary_line
            }

            # parse digits we have encountered so far as the address number, return that

    # Check for cardinal direction in the last spot
    cardinal_directions = ['n', 'e', 's', 'w']
    if string1[-1:].lower() in cardinal_directions and string1[-2:].isspace():
        return {
            'primary_line': string1[:-2],
            'secondary_line': f'''{string1[-2:]} {string2}'''
        }

    #  Check for PO BOX listed in the first line
    if 'PO BOX' in string1[-8:].upper():
        for character_num in range(name_line_length, 0, -1):
            if ' PO BOX' in string1[character_num:]:
                primary_line = string1[:character_num]
                secondary_line = f'''{string1[character_num+1:]} {string2}'''
                return {
                    'primary_line': primary_line,
                    'secondary_line': secondary_line
                }

    # Else just return what we have as the first and second lines, our algorithm is unable to parse
    else:
        return{
            'primary_line': string1,
            'secondary_line': string2
        }


def cuyahoga_tax_address_parser(input_string):
    """
    Given a tax address string as seen on Cuyahoga County's website (https://myplace.cuyahogacounty.us/),
    this function parses out the name and address of the tax payer

    :param string:  Richard M Mucci 1281 W \n 89 ST  \n CLEVELAND, OH 44102
    :return: {'primary_address_line': 'Richard M Mucci', 'secondary_address_line': '1281 W 89 ST',
     city': 'CLEVELAND', 'state': 'OH', 'zipcode': '44114'
    """

    address_list = input_string.split('\n')
    our_list = []

    for item in address_list:
        our_list.append(item.strip())

    first_lines_parsed = cuyahoga_county_name_street_parser(our_list[1], our_list[2])

    # Split last line
    comma_split = our_list[-2].split(',')
    city = comma_split[0]
    space_split = comma_split[1].split(' ')

    zipcode =space_split[-1]
    state = space_split[-2]

    return {
        'primary_address_line': first_lines_parsed['primary_line'].upper(),
        'secondary_address_line': first_lines_parsed['secondary_line'].upper(),
        'city': city.upper(),
        'state': state.upper(),
        'zipcode': zipcode
    }


def convert_string_to_base64_bytes_object(string):
    converted_string = base64.b64encode(string.encode("utf-8"))
    return converted_string.decode("utf-8")


def name_cleaner(name):
    """
    Given a name, this method will remove periods, commas, and white space, returning it
    squeaky clean to wherever it came from.
    :param name:
    :return:
    """

    punct_free_name = name.replace(',', '').replace('.', '')
    split_name = punct_free_name.split()
    string_to_return = ''

    for name in split_name:
        string_to_return += f'''{name} '''
    return string_to_return[:-1].upper()


def parse_recorder_items(soup, primary_owner_name, type_of_parse):

    if type_of_parse == 'DEED':
        search_terms = 'DECT|DEED|DESH|DEAF'
    elif type_of_parse == 'MORT':
        search_terms = 'MORT'
    else:
        raise TypeError("Unrecognized input passed into parse_recorder_items")

    # Find the last transfer of the appropriate type (MORT or DEED)
    # Confirm doc type is still at column 2
    cols = [header.string for header in soup.find_all('th')]

    try:

        cols.index('Doc. Type')
        rows = soup.find('table', id='ctl00_ContentPlaceHolder1_GridView1').find_all('tr')
        rows_length = len(rows) - 1

        # Here, we loop through all of the table rows starting from the bottom. As soon as we find
        # a document type matching the type of search we're doing, we'll analyze it.
        # If it matches, we return the date it was filed; if not, we return None.
        for i in range(rows_length, 0, -1):
            if rows[i].find_all('td')[2].contents[0] in search_terms:
                if type_of_parse == 'DEED':
                    if name_cleaner(rows[i].find_all('td')[4].contents[0]).upper() in name_cleaner(primary_owner_name):
                        return rows[i].find_all('td')[5].contents[0]
                    else:
                        return None

                elif type_of_parse == 'MORT':
                    if name_cleaner(rows[i].find_all('td')[3].contents[0]) in name_cleaner(primary_owner_name):
                        return rows[i].find_all('td')[5].contents[0]
                    else:
                        return None
    except ValueError:
        # We found no reuslts in our search of the recorder site
        return None

def convert_to_string_and_drop_final_zero(integer):
    return str(integer)[:-1]


def datetime_to_date_string_parser(datetime_string, format):
    """
    Given a datetime string, like '10/7/1977 12:00:00 AM' and a format of of the date,
    this method will return a a datetime object.
    :param datetime_string: '10/7/1977 12:00:00 AM'
    :param format: %M/%D/%Y
    :return: datetime_object(10/7/1977)
    """

    date_string = datetime_string.split(' ')[0]
    dt_object = datetime.datetime.strptime(date_string, format)
    return dt_object


def calculate_total_number_of_acres(rows):
    array_of_acres = []
    for counter, row in enumerate(rows):
        if counter != 0:
            try:
                contents = row.findAll('td')[4].contents
                array_of_acres.append(contents[0])
            except IndexError:
                pass
    converted_to_num = [float(x) for x in array_of_acres]
    total_acreage = 0
    for num in converted_to_num:
        total_acreage += num
    return total_acreage


def name_parser_and_joiner(name_one, name_two):
    """
    Given two names, this method returns the two names with an & sign in the middle, if a secondary owner exists
    :param name_one: Primary Owner Name
    :param name_two: Secondary Owner Name (or empty string if not possible)
    :return: Primary owner name, or - if two names, names joined by & symbol
    """
    if len(name_two) > 0:
        return f'''{name_one} & {name_two}'''
    else:
        return name_one


def franklin_row_name_returner(soup, table_id, row_term, **kwargs):
    table = soup.find('table', id=table_id)
    rows = table.find_all('tr', recursive=False)
    cell_column_number = 1
    if kwargs.get("cell_column_number", False):
        cell_column_number = kwargs.get("cell_column_number")
    # FIND ACRES
    for row in rows:
        if row.text.find(row_term) == 0:
            cell = row.findAll('td')[cell_column_number]
            # print("kwargs is: ", kwargs, " table id: ", table_id, " cell: ", cell)
            if kwargs.get('cell_value', False):
                # If args passed, return the value of the cell, rather than the text
                # so that we can continue to perform other data manipulation
                return cell
            else:
                found_value = cell.get_text()
                return found_value


def find_td_cell_value_beneath_current_bssoup(cell, *args):
    next_row = cell.parent.next_sibling
    cells = next_row.find_all('td')
    if len(args) >= 1:
        return cells[1]
    else:
        underneath_td_cell = cells[1].get_text()
        return underneath_td_cell



def franklin_county_tax_address_getter(soup):
    primary_owner_text = franklin_row_name_returner(soup, "Owner", "Tax Bill Mailing")
    primary_owner_text_cell = franklin_row_name_returner(soup, "Owner", "Tax Bill Mailing", cell_value=True)

    secondary_owner_text = find_td_cell_value_beneath_current_bssoup(primary_owner_text_cell)
    secondary_owner_cell = find_td_cell_value_beneath_current_bssoup(primary_owner_text_cell, True)


    first_address_line_text = find_td_cell_value_beneath_current_bssoup(secondary_owner_cell)
    first_address_line_cell = find_td_cell_value_beneath_current_bssoup(secondary_owner_cell, True)

    secondary_address_line_text = find_td_cell_value_beneath_current_bssoup(first_address_line_cell)

    names_with_white_space = [primary_owner_text, secondary_owner_text, first_address_line_text, secondary_address_line_text]
    names_without_white_space = parse_white_space_from_each_line_of_address(names_with_white_space)
    return names_without_white_space


def franklin_real_value_finder(input_text, type_to_find):
    array_of_matches = re.findall(f'''documentRowInfo\[[0-9]*\].{type_to_find} *	*= .*''', input_text)
    parsed_array = []
    for x in array_of_matches:
        match = re.search('".*"', x)
        parsed_array.append(match.group(0).replace('"', ""))

    return parsed_array


def franklin_county_credit_parser(parsed_value):
    """
    This method is coded to handle string values in the form of "2018: Yes 2019: Yes", which is how
    the system was returning values at the time of parsing. Unknown if values will change to "Yes" at some point
    in the middle of the year, though ideally this method is built to handle such a change.
    :param parsed_value:
    :return: The true-false value of whether the property received a credit at the closest-to-present timeframe.
    """
    final_value = parsed_value[-3:]
    if final_value.upper() == 'YES':
        return convert_y_n_to_boolean(final_value)
    elif final_value[-2:].upper() == 'NO':
        return convert_y_n_to_boolean(final_value[-2:])


