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
