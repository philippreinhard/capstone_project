# for html parsing:
from bs4 import BeautifulSoup, NavigableString, Tag
# for file importing and exporting:
import csv
import pandas as pd
import json
import os
# for german numbers
import decimal
import locale
# other:
import re  # regex
from IPython.display import clear_output

debug_prints = True


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def find_it(key, lists):
    for index, sublist in enumerate(lists):
        if sublist[0] == key:
            return index
    return None


filepath_merged_companies = 'company_timestamps.json'
# get company data from file
try:
    with open(filepath_merged_companies) as json_file:
        company_names = json.load(json_file)
        merged_companies_len = len(company_names)
except Exception as e:
    print("couldn't read JSON file!", repr(e))
    pass

# get list of all files in folder 'scraped_data'
document_list = []
for root, dirs, files in os.walk('scraped_data'):
    document_list.extend(files)
    break

count_of_documentlist = len(document_list)
count_of_htmls = len([item for item in document_list if item.endswith('.html')])

result_data = pd.DataFrame(
    columns=['Dateiname', 'Unternehmen_infile', 'Ort_infile', 'Unternehmen_given', 'Ort_given', 'match'])

# from_year=int(item[1]), company=item[0].strip(), place=item[4].strip(),
html_counter = 1
overall_counter = 1
company_index = 0

for item in document_list:
    if document_list.index(item) < 1000000:

        # clear_output(wait=True)
        # clear()
        # print("=== Parse HTML files for wrong company names ===")
        if document_list.index(item) % 100 == 0:
            print("> scanning document:", overall_counter, "/", count_of_documentlist, "--", item)

        if overall_counter < count_of_documentlist:
            overall_counter = overall_counter + 1

        if item.endswith('.html'):
            try:
                with open('scraped_data/' + item, encoding='utf-8') as file:
                    soup = BeautifulSoup(file, 'lxml')
                skip_item = False
            except Exception as e:
                print(item, "An Error occured reading the html!", repr(e))
                skip_item = True
        else:
            # print('> file is no html, will be skipped...')
            skip_item = True

        if not skip_item:
            # print("> scanning HTML:", html_counter, "/", count_of_htmls)
            if html_counter < count_of_htmls:
                html_counter = html_counter + 1

            try:
                if soup.find("h3", class_="z_titel") is not None:
                    unternehmen_infile = soup.find("h3", class_="z_titel").get_text(separator=" ")
                elif soup.find("h3") is not None:
                    unternehmen_infile = soup.find("h3").get_text(separator=" ")
                else:
                    unternehmen_infile = '#VALUE!'
            except AttributeError as e:
                print(item, 'An error occured while searching for h3!', repr(e))

            try:
                if soup.find("h4", class_="z_titel") is not None:
                    ort_infile = soup.find("h4", class_="z_titel").get_text(separator=" ")
                elif soup.find("h4") is not None:
                    ort_infile = soup.find("h4").get_text(separator=" ")
                else:
                    ort_infile = '#VALUE!'
            except AttributeError as e:
                print(item, 'An error occured while searching for h4!', repr(e))

            company_index = find_it(item[0:-16], company_names)
            if company_index is not None:
                unternehmen_given = company_names[company_index][0]
                ort_given = company_names[company_index][4]
            else:
                unternehmen_given = ''
                ort_given = ''

            temp_row = [item, unternehmen_infile, ort_infile, unternehmen_given, ort_given,
                        (unternehmen_given == unternehmen_infile)]
            result_data.loc[len(result_data)] = temp_row

            # print('> company name matches?', (unternehmen_given == unternehmen_infile))

        else:
            # ['Dateiname', 'Unternehmen_infile', 'Ort_infile', 'Unternehmen_given', 'Ort_given', 'match']
            temp_row = [item, '', '', '', '', '#N/A']
            result_data.loc[len(result_data)] = temp_row
    else:
        break

try:
    result_data.to_csv('output/wrong_company_names.csv', index=False, encoding='utf-8', sep=';',
                       quoting=csv.QUOTE_ALL)
except PermissionError as e:
    print("could not export file because of PermissionError, please try again!!")
print("Done!")
