# This function exists so that we can validate our Travis-CI instance works.
import csv


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


def parse_tax_address_from_css(parsed_tax_address):
    """
    This method removes a lot of junk from a parsed tax address. First, it removes
    the extra space that shows up in the result, and then it removes the spaces
    found in the actual address.
    :param result: A list of strings parsed from the DOM
    :return: A list containing the lines of the address.
    """
    parsed_tax_address = [x.replace("\r\n", "") for x in parsed_tax_address]
    parsed_tax_address = [x.strip() for x in parsed_tax_address if (len(x.strip()) != 0)]
    return parsed_tax_address

