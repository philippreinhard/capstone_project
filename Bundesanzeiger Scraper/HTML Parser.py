# for html parsing:
from bs4 import BeautifulSoup, NavigableString, Tag
# for file importing and exporting:
import csv
import pandas as pd
# import json
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


def scan_htmls(print_title):
    global debug_prints

    # get list of all files in folder 'scraped_data'
    document_list = []
    for root, dirs, files in os.walk('scraped_data'):
        document_list.extend(files)
        break

    # document_list = ['KUNUNU_KH Software GmbH  Co.KG.csv_03.09.2019.html']
    # document_list = ['KUNUNU_MathWorks.csv_28.02.2020.html', 'KUNUNU_con terra GmbH.csv_05.02.2019.html']
    # document_list = ['KUNUNU_MathWorks.csv_28.02.2020.html', 'KUNUNU_KH Software GmbH  Co.KG.csv_03.09.2019.html', 'KUNUNU_areto consulting gmbh.csv_21.02.2020.html']
    # document_list = ['KUNUNU_BDS Systemberatung für Organisation  Methodik GmbH.csv_07.04.2020.html']

    abort_execution = False
    skip_item = False

    # for company name sanitizing
    keepcharacters = (' ', '.', '_', '-')
    employee_desc = ['Arbeitnehmer', 'Mitarbeiter']

    locale.setlocale(locale.LC_ALL, 'de_DE')
    count_of_htmls = len([item for item in document_list if item.endswith('.html')])
    html_counter = 1
    export_counter = 0
    company_data = pd.DataFrame(
        columns=['Unternehmen', 'Dokumentendatum', 'Dokumententyp', 'JA_von', 'JA_bis', 'Anzahl_MA', 'Eigenkapital',
                 'Bilanzsumme', 'EK-Quote', 'Umsatzerlöse', 'Bilanz_Aktiva', 'Bilanz_Passiva', 'Dateiname'])
    regexDates = re.compile(r'vom (\d{2}\.\d{2}\.\d{4}) bis zum (\d{2}\.\d{2}\.\d{4})')

    for item in document_list:
        if document_list.index(item) < 10:

            #clear_output(wait=True)
            clear()
            print(print_title)
            print("> scanning document:", html_counter, "/", count_of_htmls, "--", item)

            temp_unternehmen = ""
            temp_dokumententyp = ""
            temp_JA_von = ""
            temp_JA_bis = ""
            temp_datum = ""
            temp_anzahl_MA = ""
            temp_umsatz = ""
            temp_bilanzaktiva = ""
            temp_bilanzpassiva = ""
            temp_guv = ""
            temp_dateiname = ""

            if item.endswith('.html'):
                try:
                    with open('scraped_data/' + item, encoding='utf-8') as file:
                        soup = BeautifulSoup(file, 'lxml')
                    skip_item = False
                except Exception as EError:
                    print("An Error occured!", repr(EError))
                    skip_item = True
            else:
                print('> file is no html, will be skipped...')
                skip_item = True

            if not skip_item:
                if html_counter < count_of_htmls:
                    html_counter = html_counter + 1

                # do some magic here

                temp_unternehmen = soup.find("h3", class_="z_titel").get_text(separator=" ")
                # for sanitizing the company name, sometimes there are tabs and shit
                # temp_Unternehmen = "".join(c for c in temp_Unternehmen if c.isalnum() or c in keepcharacters).rstrip()
                temp_unternehmen = " ".join(temp_unternehmen.split())
                temp_dokumententyp = soup.find("td", class_="info").get_text().split()[0]
                temp_datum = soup.find("td", class_="date").get_text(separator=" ")
                temp_JA_von = regexDates.findall(soup.find("td", class_="info").get_text())[0][0]
                temp_JA_bis = regexDates.findall(soup.find("td", class_="info").get_text())[0][1]
                temp_dateiname = item

                ############# find aktiva and passiva tables
                start = soup.find("h3", id=re.compile("^jp_Bilanz", re.IGNORECASE))
                temp_bilanz = []
                if start:
                    for elem in start.next_siblings:
                        if elem.name == 'h3':
                            # print("found an h3:", elem.text)
                            break
                        if elem.name != 'table':
                            continue
                        # it's a <table> tag before the next <h3>
                        temp_bilanz.append(elem)
                else:
                    print("no jp_Bilanz found")

                if len(temp_bilanz) > 1:
                    # Aktiva:
                    keys = []
                    values = []
                    for temp_bilanz_tr in temp_bilanz[0].find_all('tr'):
                        if len(temp_bilanz_tr.find_all('td')) > 1:
                            elem = temp_bilanz_tr.find_all('td')[0].get_text(strip=True)
                            keys.append(" ".join(elem.split()))
                            elem = temp_bilanz_tr.find_all('td')[1].get_text(strip=True)
                            try:
                                values.append(float(locale.atof(elem, decimal.Decimal)))
                            except Exception as e:
                                if debug_prints:
                                    print("error in getting trs of bilanz")
                                values.append(elem)
                    temp_bilanzaktiva = dict(zip(keys, values))
                    # Passiva:
                    keys = []
                    values = []
                    for temp_bilanz_tr in temp_bilanz[1].find_all('tr'):
                        if len(temp_bilanz_tr.find_all('td')) > 1:
                            elem = temp_bilanz_tr.find_all('td')[0].get_text(strip=True)
                            keys.append(" ".join(elem.split()))
                            elem = temp_bilanz_tr.find_all('td')[1].get_text(strip=True)
                            try:
                                values.append(float(locale.atof(elem, decimal.Decimal)))
                            except Exception as e:
                                if debug_prints:
                                    print("error in getting trs of bilanz")
                                values.append(elem)
                    temp_bilanzpassiva = dict(zip(keys, values))
                if len(temp_bilanz) > 2:  # there was a third table for GuV
                    print("GuV found!")
                    temp_guv = temp_bilanz[2]

                ############# find EK and Bilanzsumme
                if temp_bilanz:
                    # get Bilanzsumme
                    # first, get last table row
                    bilanzsumme_tr = temp_bilanz[0].find_all('tr')[-1]
                    temp_bilanzsumme = ""
                    if len(bilanzsumme_tr.find_all('td')) >= 3:
                        temp_bilanzsumme = bilanzsumme_tr.find_all('td')[-2].get_text().strip()
                    elif len(bilanzsumme_tr.find_all('td')) == 2:
                        temp_bilanzsumme = bilanzsumme_tr.find_all('td')[-1].get_text().strip()
                    else:
                        print("no bilanzsumme found")
                    # convert to float with german locale
                    try:
                        temp_bilanzsumme = locale.atof(temp_bilanzsumme, decimal.Decimal)
                    except Exception as e:
                        if debug_prints:
                            print("error in converting temp_bilanzsumme to float!")
                            temp_bilanzsumme = 0.0

                    if debug_prints:
                        print('Bilanzsumme:', temp_bilanzsumme)

                    # get EK
                    ek_td = soup.find('td', string=re.compile('A. Eigenkapital', re.IGNORECASE))
                    if ek_td is None:
                        ek_td = soup.find('td', string=re.compile('Eigenkapital', re.IGNORECASE))
                        if ek_td is not None and re.search('Fehlbetrag', ek_td.text, re.IGNORECASE):
                            ek_td = ek_td.find_next('td', string=re.compile('Eigenkapital', re.IGNORECASE))
                            print('re found Fehlbetrag')
                    # print(ek_td.text)
                    if ek_td is not None:
                        ek_tr = ek_td.parent
                        temp_ek = 0.0
                        # Value of EK is stated in adjacent table cell
                        if ek_td.next_sibling.next_sibling.get_text().strip() != "":
                            if debug_prints:
                                print('Value of EK is stated in adjacent table cell')

                            temp_ek = ek_td.next_sibling.next_sibling.get_text()
                            if debug_prints:
                                print('temp_EK raw:', temp_ek.encode('raw_unicode_escape'))
                            temp_ek = locale.atof(temp_ek, decimal.Decimal)
                        # Value of EK has to be summed up
                        else:
                            ek_zwischensumme = []
                            if debug_prints:
                                print('Value of EK has to be summed up')

                            for elem in ek_tr.next_siblings:
                                if elem.name == 'tr':
                                    if debug_prints:
                                        print("found an tr:", " ".join(elem.text.split()))
                                    ek_tds = elem.find_all('td')
                                    ek_td0 = ek_tds[0].get_text().strip()
                                    if ek_td0.startswith(('I.', 'II.', 'III.', 'IV.', 'V.')):
                                        if debug_prints:
                                            print('EK tr found:', ek_tds)
                                        # walk right until value is found
                                        for elem2 in ek_tds[0].next_siblings:
                                            if not (elem2 and isinstance(elem2, NavigableString)):
                                                if elem2.text.strip() != "":
                                                    ek_zwischensumme.append(elem2.text)
                                                    break
                                    elif ek_td0.startswith(('B.', 'C.', 'D.')):
                                        break
                            if debug_prints:
                                print('EK_zwischensumme:', ek_zwischensumme)
                            for elem in ek_zwischensumme:
                                temp_ek = temp_ek + float(locale.atof(elem, decimal.Decimal))
                        if debug_prints:
                            print('EK und Bilanzsumme:', temp_ek, temp_bilanzsumme)
                        try:
                            temp_ekquote = float(temp_ek) / float(temp_bilanzsumme)
                        except ZeroDivisionError as e:
                            print('ZeroDivisionError bei temp_EKquote')
                            temp_ekquote = 0.0

                ############# find Umsatzerlöse
                try:
                    umsatz_td = soup.find_all('td', string=re.compile('Umsatzerlös', re.IGNORECASE))[-1]

                    for elem in umsatz_td.next_siblings:
                        if not (elem and isinstance(elem, NavigableString)):
                            if elem.text.strip() != "":
                                try:
                                    temp_umsatz = float(locale.atof(elem.text, decimal.Decimal))
                                except Exception as e:
                                    if debug_prints:
                                        print("error in converting temp_umsatz to float!")
                                    temp_umsatz = elem.text
                                if debug_prints:
                                    print('umsatz:', temp_umsatz)
                                break
                except Exception as e:
                    if debug_prints:
                        print("error in finding td Umsatzerlöse")

                ############# find count of employees
                ma_sentence_found = False
                search_element = soup.find_all('p')
                for elem in search_element:
                    # if elem.text contains a string out of employee_desc
                    if any(x in elem.text for x in employee_desc):
                        # if there are any br tag children
                        # https://stackoverflow.com/questions/5275359/using-beautifulsoup-to-extract-text-between-line-breaks-e-g-br-tags
                        for br in elem.find_all('br'):
                            next_s = br.next_sibling
                            if not (next_s and isinstance(next_s, NavigableString)):
                                continue
                            next2_s = next_s.next_sibling
                            if next2_s and isinstance(next2_s, Tag) and next2_s.name == 'br':
                                text = str(next_s)
                                if any(x in text for x in employee_desc):
                                    if debug_prints:
                                        print("MA found ins brs:", " ".join(text.split()))
                                        print("MA found ins brs:", " ".join(text.split()))
                                    temp_anzahl_MA = " ".join(text.split())
                                    ma_sentence_found = True
                                    break
                        if not ma_sentence_found:
                            if debug_prints:
                                print("MA not found in brs, but directly in p tag:", " ".join(elem.text.split()))
                            temp_anzahl_MA = " ".join(elem.text.split())

                        break

                # print(temp_anzahl_MA)

                # temp_ek = 0
                # temp_bilanzsumme = 0
                # temp_ekquote = 0

                test = [temp_unternehmen, temp_datum, temp_dokumententyp, temp_JA_von, temp_JA_bis,
                        temp_anzahl_MA, temp_ek, temp_bilanzsumme, temp_ekquote, temp_umsatz, temp_bilanzaktiva,
                        temp_bilanzpassiva, temp_dateiname]
                # print(test)
                # company_data.append(test, ignore_index=True)
                company_data.loc[len(company_data)] = test
                export_counter = export_counter + 1

                temp_unternehmen = ""
                temp_datum = ""
                temp_dokumententyp = ""
                temp_JA_von = ""
                temp_JA_bis = ""
                temp_anzahl_MA = ""
                temp_ek = ""
                temp_bilanzsumme = ""
                temp_ekquote = ""
                temp_umsatz = ""
                temp_bilanzaktiva = ""
                temp_bilanzpassiva = ""
                temp_dateiname = ""

                # print(company_data.describe())
                # print(company_data)
                # company_data.to_pickle('output/company_attributes.pkl')
                # print(company_data.loc[0,'Anzahl_MA'])

    try:
        company_data.to_csv('output/company_attributes.csv', index=False, encoding='utf-8', sep=';',
                            quoting=csv.QUOTE_ALL)
    except PermissionError as e:
        print("could not export file because of PermissionError, please try again!!")
    print("Done!")
    print("Found and exported values out of", export_counter, "html files.")


scan_htmls("=== Parse HTML files for Jahresabschlüsse ===")
