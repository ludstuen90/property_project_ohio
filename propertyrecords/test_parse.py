import os
import pickle
import re

from ..propertyrecords import utils

from bs4 import BeautifulSoup

script_dir = os.path.dirname(__file__)
# relative_path_to_file = "dict.pickle"
relative_path_to_file = "no2own.pickle"
abs_file_path = os.path.join(script_dir, relative_path_to_file)
pickle_in = open(abs_file_path, "rb")
dummy_response = pickle.load(pickle_in)

soup = BeautifulSoup(dummy_response, 'html.parser')
table = soup.find('table', id="Owner")
rows = table.find_all('tr', recursive=False)

# FIND ACRES
for row in rows:
    if (row.text.find("Calculated Acres") > -1):
        cell = row.findAll('td')[1]
        property_acres = cell.get_text()
        # print("!!", property_acres)

# FIND ADDRESS
tds = soup.find_all('td', class_="DataletHeaderBottom")
address = tds[1].get_text()

#LEGAL DESCRIPTION
land_use = soup.find('td', text="Land Use")
use = land_use.next_sibling.get_text()
# print("USE: ", use)

#OWNER
table = soup.find('table', id='Owner')
owner_cell = table.find('td', text="Owner")
next_cell = owner_cell.next_sibling
owner_name = next_cell.get_text()

next_row = owner_cell.parent.next_sibling
cells = next_row.find_all('td')
secondary_owner_attempt = cells[1].get_text()
names = utils.name_parser_and_joiner(owner_name, secondary_owner_attempt)
print(names)

# next_row = owner_cell.parent.next_sibling.encode('utf-8').strip()
# print("NEXT ROW: ", next_row)
        #PropertyAddress
        # legal_acres - DOWNLAODED
        # legal_description
        # owner
        # date_sold
        # date_of_LLC_name_change
        # date_of_mortgage
        # mortgage_amount
        # property_class
        # property_rating
        # land_use
        # tax_district
        # school_district_name
        # school_district
        # tax_lien
        # tax_lien_information_source
        # cauv_property
        # owner_occupancy_indicated
        # county
        # tax_address
        # TaxData
        # PropertyTransfer
        # PROPERTY ADDRESS = DOWNLAODED