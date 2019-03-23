import os
import pickle
import re

import utils

from bs4 import BeautifulSoup

script_dir = os.path.dirname(__file__)
relative_path_to_file = "dict.pickle"
# relative_path_to_file = "no2own.pickle"
abs_file_path = os.path.join(script_dir, relative_path_to_file)
pickle_in = open(abs_file_path, "rb")
dummy_response = pickle.load(pickle_in)

soup = BeautifulSoup(dummy_response, 'html.parser')
#ACRES
print("ACRES: ", utils.franklin_row_name_returner(soup, "Owner", "Calculated Acres"))

# FIND ADDRESS
tds = soup.find_all('td', class_="DataletHeaderBottom")
address = tds[1].get_text()
city = utils.franklin_row_name_returner(soup, re.compile("Tax Status"), "City/Village")
zip = utils.franklin_row_name_returner(soup, re.compile("Tax Status"), "Zip Code")
print(address, city, zip)

#LEGAL DESCRIPTION
land_use = soup.find('td', text="Land Use")
use = land_use.next_sibling.get_text()

#OWNER
table = soup.find('table', id='Owner')
owner_cell = table.find('td', text="Owner")
next_cell = owner_cell.next_sibling
owner_name = next_cell.get_text()

next_row = owner_cell.parent.next_sibling
cells = next_row.find_all('td')
secondary_owner_attempt = cells[1].get_text()
names = utils.name_parser_and_joiner(owner_name, secondary_owner_attempt)

# LAST SALE DATE
utils.franklin_row_name_returner(soup, "Most Recent Transfer", "Transfer Date")

#CAUV PROPERTY
cauv_yn = utils.franklin_row_name_returner(soup, re.compile("Tax Status"), "CAUV Property")
cauv = utils.convert_y_n_to_boolean(cauv_yn)

# TAX LIEN
tax_lien_yn = utils.franklin_row_name_returner(soup, re.compile("Tax Status"), "Tax Lien")
tax_lien = utils.convert_y_n_to_boolean(tax_lien_yn)

# PROPERTY CLASS
property_class = utils.franklin_row_name_returner(soup, re.compile("Tax Status"), "Property Class")
#

# OWNER OCC CREDIT
occ = utils.franklin_row_name_returner(soup, re.compile("Tax Status"), "Owner Occ. Credit")

# Homestead Credit
hcc = utils.franklin_row_name_returner(soup, re.compile("Tax Status"), "Homestead Credit")

#Land Use:
lu = utils.franklin_row_name_returner(soup, re.compile("Tax Status"), "Land Use")

#Tax District:
td = utils.franklin_row_name_returner(soup, re.compile("Tax Status"), "Tax District")


#school_district
sd = utils.franklin_row_name_returner(soup, re.compile("Tax Status"), "School District")
try:
    # Remove extra spaces, just to be nice
    if sd.split('-', 1)[0][-1:] == " ":
        school_district_number =sd.split('-', 1)[0][:-1]
    else:
        school_district_number = sd.split('-', 1)[0]

    if sd.split('-', 1)[1][:1] == " ":
        school_district_name = sd.split('-', 1)[1][1:]
    else:
        school_district_name = sd.split('-', 1)[1]

except IndexError:
    pass




# next_row = owner_cell.parent.next_sibling.encode('utf-8').strip()
# print("NEXT ROW: ", next_row)
        # date_of_LLC_name_change
        # date_of_mortgage
        # mortgage_amount
        # property_class
        # property_rating
        # tax_address
        # TaxData
        # PropertyTransfer
        # PROPERTY ADDRESS = DOWNLAODED