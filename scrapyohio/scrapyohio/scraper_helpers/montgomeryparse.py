import re
import pdf2image
import pyocr
from PIL import Image

import os
cwd = os.getcwd()


def if_possible_remove_brackets(input_string):
    try:
        return input_string[0]
    except IndexError:
        if input_string == []:
            return ""
        else:
            return "ERRR!"

def file_parser(filename):
    print("Entering with filename of ", filename)
    actual_filepath = f"""/home/lukas/Descargas/dockets/{filename}"""
    a = pdf2image.convert_from_path(actual_filepath, 500)
    a[0].save(os.path.join(cwd, 'pictures/out0.jpg'), 'JPEG')
    a[1].save(os.path.join(cwd, 'pictures/out1.jpg'), 'JPEG')
    a[2].save(os.path.join(cwd, 'pictures/out2.jpg'), 'JPEG')
    tools = pyocr.get_available_tools()
    tool = tools[0]
    output_text0 = tool.image_to_string(Image.open(os.path.join(cwd, 'pictures/out0.jpg')),
                                        builder=pyocr.builders.TextBuilder())
    output_text1 = tool.image_to_string(Image.open(os.path.join(cwd, 'pictures/out1.jpg')),
                                        builder=pyocr.builders.TextBuilder())
    output_text2 = tool.image_to_string(Image.open(os.path.join(cwd, 'pictures/out2.jpg')),
                                        builder=pyocr.builders.TextBuilder())

    output_text = output_text0 + output_text1 + output_text2

    #print(output_text)

    unpaid_taxes_regex = r"which are currently due and unpaid, are (.*?) and are a first and best lien against"
    fair_market_value_regex = r"Plaintiff says that the fair market value of the parcel as determined by the\nAuditor of Montgomery County is (.*?).\n\n"
    unpaid_taxes = re.findall( unpaid_taxes_regex, output_text)
    fair_market_value = re.findall(fair_market_value_regex, output_text)
    # parcel_number = re.findall(r"Plaintiff says that delinquent real estate taxes stand charged against the real\nproperty with permanent parcel number (.*?).\n\n", output_text)
    parcel_number1 = re.findall(r"P. P. No. (.*?).\n", output_text)
    parcel_number2 = re.findall(r"P.P. No. (.*?).\n", output_text)
    parcel_number3 = re.findall(r"P .P. No. (.*?).\n", output_text)

    if len(parcel_number2) > len(parcel_number1):
        parcel_number = parcel_number2
    elif len(parcel_number3) > len(parcel_number2):
        parcel_number = parcel_number3
    else:
        parcel_number = parcel_number1

    if unpaid_taxes == [] or fair_market_value == []:
        a[3].save(os.path.join(cwd, 'pictures/out3.jpg'), 'JPEG')
        output_text3 = tool.image_to_string(Image.open(os.path.join(cwd, 'pictures/out3.jpg')),
                                            builder=pyocr.builders.TextBuilder())

        if unpaid_taxes == []:
            unpaid_taxes = re.findall(unpaid_taxes_regex, output_text3)
        if fair_market_value == []:
            fair_market_value = re.findall(fair_market_value_regex, output_text3)

    with open("output.txt", "a") as myfile:
        myfile.write(f"""{filename};{if_possible_remove_brackets(unpaid_taxes)};{if_possible_remove_brackets(fair_market_value)};{if_possible_remove_brackets(parcel_number)}\n""")
    print("#################")
    print("Unpaid taxes: ", unpaid_taxes)
    print("Fair Market Value: ", fair_market_value)
    print("Parcel Number: ", parcel_number)
    print(filename)
    print("#################")

[file_parser(x) for x in os.listdir("/home/lukas/Descargas/dockets")]
# file_parser("2019 BR 00005.pdf")
