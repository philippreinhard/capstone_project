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
import time


# from IPython.display import clear_output
start_time = time.time()

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def find_it(key, lists):
    for index, sublist in enumerate(lists):
        if sublist[0] == key:
            return index
    return None


def switch_locale():
    if locale.getlocale()[0] == 'de_DE':
        locale.setlocale(locale.LC_ALL, 'en_US')
    elif locale.getlocale()[0] == 'en_US':
        locale.setlocale(locale.LC_ALL, 'de_DE')


def get_localed_and_sanitized_number(value: str) -> float:  # deprecated
    keepcharacters = (',', '.', '-') # for company name sanitizing
    temp = value
    temp = "".join(c for c in temp if c.isalnum() or c in keepcharacters).strip()
    # if string is negatvie number expressed with trailing minus, like '50.000-'
    if temp[-1:] == '-':
        temp = '-' + temp[:-1]

    try:
        # current locale
        temp = locale.atof(temp, decimal.Decimal)
        temp = float(temp)
    except Exception as error1:
        try:
            switch_locale()
            temp = locale.atof(temp, decimal.Decimal)
            temp = float(temp)
        except Exception as error2:
            if debug_prints:
                print(item, 'error in conversion function for:', value)
            switch_locale()
            raise ValueError

    return temp


def get_sanitized_number(value: str) -> float:
    keepcharacters = ('-') # for company name sanitizing
    temp = value
    temp = "".join(c for c in temp if c.isalnum() or c in keepcharacters).strip()
    # if string is negatvie number expressed with trailing minus, like '50.000-'
    if temp[-1:] == '-':
        temp = '-' + temp[:-1]

    # add Comma before last two digits of number
    temp = temp[:-2] + ',' + temp[-2:]

    try:
        temp = locale.atof(temp, decimal.Decimal)
        temp = float(temp)
    except Exception as error1:
        if debug_prints:
            print(item, 'error in conversion function for:', value)
        raise ValueError

    return temp


# get company data from file
filepath_merged_companies = 'company_timestamps.json'
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

document_list = ['Rohe GmbH  Co. KG_22.01.2020.html']
# with open('output/test.csv', newline='', encoding='utf8') as f:
#     reader = csv.reader(f)
#     document_list = [item for sublist in reader for item in sublist]
debug_prints = True
# debug_prints = False

abort_execution = False
skip_item = False

# regexes here:
re_AEigenkapital = re.compile(r'A\. Eigenkapital', re.IGNORECASE)
re_Eigenkapital = re.compile('Eigenkapital', re.IGNORECASE)
re_Fehlbetrag = re.compile('Fehlbetrag', re.IGNORECASE)
re_DateDDMMYYYY = re.compile(r'\d{2}\.\d{2}\.\d{4}', re.IGNORECASE)
re_Rueckstellungen = re.compile(r'Rückstellungen', re.IGNORECASE)
re_eingefordertesKapital = re.compile(r'eingefordertes[\s\S]*Kapital', re.IGNORECASE)
re_nichtgedeckterFehlbetrag = re.compile(r'nicht[\s\S]*gedeckter[\s\S]*(Fehlbetrag|Verlustanteil)', re.IGNORECASE)
re_davonnichtgedeckt = re.compile(r'davon[\s\S]*nicht[\s\S]*gedeckt', re.IGNORECASE)
re_Jahresfehlbetrag = re.compile(r'Jahresfehlbetrag', re.IGNORECASE)
re_Jahresueberschuss = re.compile(r'Jahresüberschuss', re.IGNORECASE)
re_Verlustvortrag = re.compile(r'^(?!.*Gewinn.*).*Verlustvortrag.*$', re.IGNORECASE)
re_Jahresfehlbetrag_not_Jahresueberschuss = re.compile(r'^(?!.*Jahresüberschuss.*).*Jahresfehlbetrag.*$', re.IGNORECASE)
re_Bilanzverlust = re.compile(r'^(?!.*Bilanzgewinn.*).*Bilanzverlust.*$', re.IGNORECASE)
re_eigeneAnteile = re.compile(r'eigene[\s\S]*Anteile', re.IGNORECASE)
re_Umsatzerlos = re.compile('Umsatzerlös', re.IGNORECASE)
re_Kommanditkapital = re.compile(r'^(?!.*eingefordert.*).*Kommanditkapital.*$', re.IGNORECASE)
re_buchmaessigesEK = re.compile(r'buchmäßiges[\s\S]*Eigenkapital', re.IGNORECASE)
re_SummeEK = re.compile(r'Summe[\s\S]*Eigenkapital', re.IGNORECASE)
re_Verbindlichkeiten = re.compile(r'Verbindlichkeiten', re.IGNORECASE)

current_locale = 'de_DE'
employee_desc = ['Arbeitnehmer', 'Mitarbeiter']

locale.setlocale(locale.LC_ALL, 'de_DE')

count_of_documentlist = len(document_list)
count_of_htmls = len([item for item in document_list if item.endswith('.html')])

html_counter = 1
overall_counter = 1
export_counter = 0

# output dataframe
company_data = pd.DataFrame(
    columns=['Dateiname', 'Unternehmensname_given', 'Ort_given', 'Unternehmensname_infile', 'Ort_infile', 'Dokumentendatum',
             'Dokumententyp', 'JA_von', 'JA_bis', 'Anzahl_MA', 'Eigenkapital',
             'Bilanzsumme', 'Bilanzgewinn/verlust', 'EK-Quote', 'Nicht gedeckter Fehlbetrag', 'Umsatzerlöse', 'Bilanz_Aktiva', 'Bilanz_Passiva'])
regexDates = re.compile(r'vom (\d{2}\.\d{2}\.\d{4}) bis zum (\d{2}\.\d{2}\.\d{4})')

# loop through all files in folder 'scraped_data'
for item in document_list:
    if document_list.index(item) < 100000:  # manually set limit for testing/debugging purposes

        # clear_output(wait=True)
        # clear()

        # print(print_title)
        if document_list.index(item) % 100 == 0:
            print('> scanning document:', overall_counter, "/", count_of_documentlist, "--", item)

        if overall_counter < count_of_documentlist:
            overall_counter = overall_counter + 1

        unternehmensname_infile = ''
        dokumententyp = ''
        JA_von = ''
        ek_td = ''
        JA_bis = ''
        datum = ''
        anzahl_MA = ''
        umsatz = ''
        bilanzaktiva = ''
        bilanzpassiva = ''
        bilanzsumme = ''
        bilanzsumme_vorjahr = ''
        break_out = False
        guv = ''
        nicht_gedeckter_fehlbetrag = ''

        if item.endswith('.html'):
            try:
                with open('scraped_data/' + item, encoding='utf-8') as file:
                    soup = BeautifulSoup(file, 'lxml')
                skip_item = False
            except Exception as e:
                print('An Error occured reading the html!', item, repr(e))
                skip_item = True
        else:
            if debug_prints:
                print('> file is no html, will be skipped...')
            skip_item = True

        if not skip_item:
            if html_counter < count_of_htmls:
                html_counter = html_counter + 1

            if debug_prints:
                print('> scanning document:', overall_counter, "/", count_of_documentlist, "--", item)

            # do some magic here

            ############# find Unternehmensname_infile
            try:
                if soup.find("h3", class_="z_titel") is not None:
                    unternehmensname_infile = soup.find("h3", class_="z_titel").get_text(separator=" ")
                    unternehmensname_infile = " ".join(unternehmensname_infile.split())
                elif soup.find("h3") is not None:
                    unternehmensname_infile = soup.find("h3").get_text(separator=" ")
                    unternehmensname_infile = " ".join(unternehmensname_infile.split())
            except AttributeError as e:
                print(item, 'An error occured while searching for unternehmensname_infile!', item, repr(e))
                unternehmen_infile = ''

            ############# find Ort_infile
            try:
                if soup.find("h4", class_="z_titel") is not None:
                    ort_infile = soup.find("h4", class_="z_titel").get_text(separator=" ")
                    ort_infile = " ".join(ort_infile.split())
                elif soup.find("h4") is not None:
                    ort_infile = soup.find("h4").get_text(separator=" ")
                    ort_infile = " ".join(ort_infile.split())
                else:
                    ort_infile = '#VALUE!'
            except AttributeError as e:
                print(item, 'An error occured while searching for ort_infile!', item, repr(e))
                ort_infile = ''

            ############# find Unternehmensname_given and Ort_given
            company_index = find_it(item[0:-16], company_names)
            if company_index is not None:
                unternehmensname_given = company_names[company_index][0]
                ort_given = company_names[company_index][4]
            else:
                unternehmensname_given = ''
                ort_given = ''
                company_index = None

            ############# find other information
            if re.search('Ergänzung', soup.find("td", class_="info").get_text(), re.IGNORECASE):
                dokumententyp = 'Ergänzung der Veröffentlichung'
            else:
                dokumententyp = soup.find("td", class_="info").get_text().split()[0]
            datum = soup.find("td", class_="date").get_text(separator=" ")
            try:
                JA_von = regexDates.findall(soup.find("td", class_="info").get_text())[0][0]
            except IndexError as IE:
                print(item, 'IndexError while doing regex for JA_von!')
            try:
                JA_bis = regexDates.findall(soup.find("td", class_="info").get_text())[0][1]
            except IndexError as IE:
                print(item, 'IndexError while doing regex for JA_bis!')

            ############# find aktiva and passiva tables
            start = soup.find("h3", id=re.compile("^jp_Bilanz", re.IGNORECASE))
            bilanz = []
            if start:
                for elem in start.next_siblings:
                    if elem.name == 'h3' and (elem.text == "Aktiva" or elem.text == "Passiva"):
                        pass
                    elif elem.name == 'h3':
                        break
                    if elem.name != 'table':
                        continue
                    # it's a <table> tag before the next <h3>
                    bilanz.append(elem)
            else:
                if debug_prints:
                    print("no element with id jp_Bilanz found")

            # construct json strings for aktiva and passiva
            if len(bilanz) == 1:  # 1 big table which holds both aktiva and passiva
                # Aktiva and Passiva:
                keys = []
                values = []
                passiva_found = False
                for bilanz_tr in bilanz[0].find_all('tr'):
                    if re.search('Passiv', bilanz_tr.find_all('td')[0].get_text(strip=True), re.IGNORECASE) and not passiva_found:
                        bilanzaktiva = dict(zip(keys, values))
                        keys = []
                        values = []
                        passiva_found = True
                    elif len(bilanz_tr.find_all('td')) > 1:
                        elem = bilanz_tr.find_all('td')[0].get_text(strip=True)
                        keys.append(" ".join(elem.split()))
                        elem = bilanz_tr.find_all('td')[1].get_text(strip=True)
                        try:
                            if re_DateDDMMYYYY.search(elem) or elem.strip() == '':  # if value is date
                                values.append(elem)
                            else:
                                values.append(get_sanitized_number(elem))
                        except Exception as e:
                            if debug_prints:
                                print("error in getting bilanz tr value!", keys[-1], elem, repr(e))
                            values.append(elem)
                bilanzpassiva = dict(zip(keys, values))

            elif len(bilanz) > 1:  # 1 table for Aktiva, 1 for Passiva
                # Aktiva:
                keys = []
                values = []
                for bilanz_tr in bilanz[0].find_all('tr'):
                    if len(bilanz_tr.find_all('td')) > 1:
                        elem = bilanz_tr.find_all('td')[0].get_text(strip=True)
                        keys.append(" ".join(elem.split()))
                        elem = bilanz_tr.find_all('td')[1].get_text(strip=True)
                        try:
                            if re_DateDDMMYYYY.search(elem) or elem.strip() == '':  # if value is date
                                values.append(elem)
                            else:
                                values.append(get_sanitized_number(elem))
                        except Exception as e:
                            if debug_prints:
                                print("error in getting bilanz tr value!", keys[-1], elem, repr(e))
                            values.append(elem)

                bilanzaktiva = dict(zip(keys, values))
                # Passiva:
                keys = []
                values = []
                for bilanz_tr in bilanz[1].find_all('tr'):
                    if len(bilanz_tr.find_all('td')) > 1:
                        elem = bilanz_tr.find_all('td')[0].get_text(strip=True)
                        keys.append(" ".join(elem.split()))
                        elem = bilanz_tr.find_all('td')[1].get_text(strip=True)
                        try:
                            if re_DateDDMMYYYY.search(elem) or elem.strip() == '':  # if value is date
                                values.append(elem)
                            else:
                                values.append(get_sanitized_number(elem))
                        except Exception as e:
                            if debug_prints:
                                print("error in getting bilanz tr value!", keys[-1], elem, repr(e))
                            values.append(elem)
                bilanzpassiva = dict(zip(keys, values))
            if len(bilanz) > 2:  # there was a third table for GuV
                if debug_prints:
                    print("GuV found!")
                guv = bilanz[2]

            ############# find EK and Bilanzsumme
            if bilanz:
                # get Bilanzsumme
                # first, get last table row
                bilanzsumme_tr = bilanz[0].find_all('tr')[-1]
                bilanz_tds = bilanzsumme_tr.find_all('td')
                # walk right until value is found
                bilanzsumme_found = False
                for elem2 in bilanz_tds[0].next_siblings:
                    if not (elem2 and isinstance(elem2, NavigableString)):
                        if elem2.text.strip() != "":
                            if not bilanzsumme_found:
                                bilanzsumme_found = True
                                bilanzsumme = elem2.text.strip()
                            else:
                                bilanzsumme_vorjahr = elem2.text.strip()
                                break
                    else:
                        pass

                if not bilanzsumme:
                    # get Bilanzsumme
                    # first, get last table row
                    if not re.search('Summe', bilanz_tds[0].get_text(), re.IGNORECASE):  # für den Ausnahmefall dass die letzte Zeile leer ist, vorletzte wird genommen
                        bilanzsumme_tr = bilanz[0].find_all('tr')[-2]
                    bilanz_tds = bilanzsumme_tr.find_all('td')
                    # walk right until value is found
                    bilanzsumme_found = False
                    for elem2 in bilanz_tds[0].next_siblings:
                        if not (elem2 and isinstance(elem2, NavigableString)):
                            if elem2.text.strip() != "":
                                if not bilanzsumme_found:
                                    bilanzsumme_found = True
                                    bilanzsumme = elem2.text.strip()
                                else:
                                    bilanzsumme_vorjahr = elem2.text.strip()
                                    break
                        else:
                            pass

                # convert to float with german locale
                try:
                    bilanzsumme = get_sanitized_number(bilanzsumme)
                except Exception as e:
                    if debug_prints:
                        print(item, "error in converting bilanzsumme to float!")

                try:
                    bilanzsumme_vorjahr = get_sanitized_number(bilanzsumme_vorjahr)
                except Exception as e:
                    if debug_prints:
                        print(item, "error in converting bilanzsumme_vorjahr to float!")

                if debug_prints:
                    print('bilanzsumme:', bilanzsumme)
                    print('Bilanzsumme_vorjahr:', bilanzsumme_vorjahr)

                # get EK
                if len(bilanz) >= 1:
                    ek_td = bilanz[0].find('td', string=re_AEigenkapital)
                if ek_td is None and len(bilanz) > 1:
                    ek_td = bilanz[1].find('td', string=re_AEigenkapital)
                if ek_td is None:
                    ek_td = soup.find('td', string=re_Eigenkapital)
                    if ek_td is not None and re_Fehlbetrag.search(ek_td.text):  # Um Aktiva-Posten 'nicht durch Eigenkapital abgedeckter Fehlbetrag' abzufangen
                        ek_td = ek_td.find_next('td', string=re_Eigenkapital)
                        if debug_prints:
                            print(item, 're found Fehlbetrag')

                if ek_td is None:  # find tds that have a <b> (or any other element) in them that has the "EK" inside
                    ek_tds = bilanz[0].parent.find_all('td')
                    for temp_var in ek_tds:
                        if temp_var.find(string=re_Eigenkapital):
                            if temp_var.find(string=re_Fehlbetrag):
                                continue
                            else:
                                if temp_var.find(string=re_AEigenkapital):
                                    # elem.extend(temp_var)
                                    ek_td = temp_var
                                    break
                    # ek_td = elem[-1]


                if ek_td is not None:
                    ek_tr = ek_td.parent
                    eigenkapital = 0.0
                    ek_has_to_be_summed_up = True

                    # Value of EK is stated in adjacent table cell
                    # walk right until value is found
                    ek_tds = ek_tr.find_all('td')
                    for elem2 in ek_tds[0].next_siblings:
                        if not (elem2 and isinstance(elem2, NavigableString)):
                            if elem2.text.strip() != "" and elem2.text.strip() != "0,00":
                                eigenkapital = elem2.text.strip()
                                if debug_prints:
                                    print('Value of EK is stated in adjacent table cell')
                                    print('eigenkapital raw:', eigenkapital.encode('raw_unicode_escape'))
                                try:
                                    eigenkapital = get_sanitized_number(eigenkapital)
                                except Exception as e:
                                    if debug_prints:
                                        print(item, "error in converting eigenkapital to float!")
                                ek_has_to_be_summed_up = False
                                break
                            elif elem2.text.strip() == "0,00":
                                ek_has_to_be_summed_up = True
                                break
                            else:
                                pass
                        else:
                            pass

                    if ek_has_to_be_summed_up:
                        ek_zwischensumme = []
                        ek_secondlevel_has_data = None
                        if debug_prints:
                            print('Value of EK has to be summed up')

                        for elem in ek_tr.next_siblings:
                            if elem.name == 'tr':
                                if debug_prints:
                                    print("found an tr:", " ".join(elem.text.split()))
                                ek_tds = elem.find_all('td')
                                ek_td0 = ek_tds[0].get_text().strip()
                                if ek_td0.startswith(('B.', 'C.', 'D.') or re_Rueckstellungen.search(ek_td0) or re_Verbindlichkeiten.search(ek_td0)):
                                    break
                                else:  # if ek_td0.startswith(('I.', 'II.', 'III.', 'IV.', 'V.')) or re.search(r'nicht[\s\S]*gedeckter[\s\S]*Fehlbetrag', ek_td0, re.IGNORECASE):
                                    if debug_prints:
                                        print('EK tr found')  # :', ek_tds)

                                    # skipping_values = ['davon', 'eingefordertes Kapital', 'Summe', 'Bilanzgewinn', 'Bilanzverlust']
                                    skipping_values = ['davon', 'eingefordertes Kapital', 'Summe']

                                    if ek_td0.startswith(('I.', 'II.', 'III.', 'IV.', 'V.')):
                                        ek_secondlevel = True
                                        ek_secondlevel_has_data = False
                                    else:
                                        ek_secondlevel = False

                                    # walk right until value is found
                                    if ek_secondlevel or (not ek_secondlevel and not ek_secondlevel_has_data):
                                        for elem2 in ek_tds[0].next_siblings:
                                            if not (elem2 and isinstance(elem2, NavigableString)):
                                                if elem2.text.strip() != "":
                                                    if re_buchmaessigesEK.search(ek_td0) or re_SummeEK.search(ek_td0):
                                                        ek_zwischensumme = []
                                                        eigenkapital = get_sanitized_number(elem2.text.strip().splitlines()[0])
                                                        break_out = True
                                                        break
                                                    elif (any(x in ek_td0 for x in skipping_values) or
                                                        re_eingefordertesKapital.search(ek_td0) or
                                                        re_Kommanditkapital.search(ek_td0)) and \
                                                            not re_davonnichtgedeckt.search(ek_td0):
                                                        pass
                                                    elif (re_nichtgedeckterFehlbetrag.search(ek_td0) or
                                                          re_Fehlbetrag.search(ek_td0) or
                                                          re_davonnichtgedeckt.search(ek_td0)) and not \
                                                            (re_Jahresfehlbetrag.search(ek_td0) or
                                                             re_Jahresueberschuss.search(ek_td0)) and \
                                                            elem2.text.strip() != '0,00':  # für Fehlbetrag
                                                        ek_zwischensumme.append(elem2.text.strip().splitlines()[0].replace('-', ''))
                                                        nicht_gedeckter_fehlbetrag = elem2.text.strip().splitlines()[0].replace('-', '')
                                                        if ek_secondlevel: ek_secondlevel_has_data = True
                                                    elif re_Verlustvortrag.search(ek_td0) or \
                                                            re_Jahresfehlbetrag_not_Jahresueberschuss.search(ek_td0) or \
                                                            re_Bilanzverlust.search(ek_td0) or \
                                                            re_eigeneAnteile.search(ek_td0):
                                                        if elem2.text.strip()[-1:] == '-' or elem2.text.strip()[:1] == '-':
                                                            ek_zwischensumme.append(elem2.text.strip().splitlines()[0])
                                                        else:
                                                            ek_zwischensumme.append('-' + elem2.text.strip().splitlines()[0])
                                                        if ek_secondlevel: ek_secondlevel_has_data = True
                                                    else:
                                                        ek_zwischensumme.append(elem2.text.strip().splitlines()[0])
                                                        if ek_secondlevel: ek_secondlevel_has_data = True
                                                    break
                                        if break_out:
                                            break


                        if debug_prints:
                            print('EK_zwischensumme:', ek_zwischensumme)
                        if ek_zwischensumme:
                            for elem in ek_zwischensumme:
                                if elem.strip() != '':
                                    try:
                                        temp_var = get_sanitized_number(elem)
                                        eigenkapital = eigenkapital + temp_var
                                    except Exception as e:
                                        if debug_prints:
                                            print(item, 'error adding ek_zwischensumme!', repr(e))
                            eigenkapital = round(eigenkapital, 2)

                    # Nicht gedeckter Fehlbetrag II:

                    fehlbetrag_tds = bilanz[0].parent.find_all('td')
                    fehlbetrag_td = None
                    for temp_var in fehlbetrag_tds:
                        if temp_var.find(string=re_nichtgedeckterFehlbetrag):
                            fehlbetrag_td = temp_var
                            break
                    if fehlbetrag_td is not None and isinstance(fehlbetrag_td, Tag):
                        fehlbetrag_tds = fehlbetrag_td.parent.find_all('td')
                        if fehlbetrag_tds:
                            for elem2 in fehlbetrag_tds[0].next_siblings:
                                if not (elem2 and isinstance(elem2, NavigableString)):
                                    if elem2.text.strip() != "":
                                        if nicht_gedeckter_fehlbetrag.strip() != elem2.text.strip():
                                            if nicht_gedeckter_fehlbetrag != '':
                                                if debug_prints:
                                                    print(item, 'nicht gedeckter Fehlbetrag unklar:', nicht_gedeckter_fehlbetrag, elem2.text.strip())
                                            try:
                                                temp_var = get_sanitized_number(elem2.text.strip().splitlines()[0].strip())
                                            except Exception as e:
                                                if debug_prints:
                                                    print('error converting nicht_gedeckter_fehlbetrag:', elem2.text.strip().splitlines()[0].strip())
                                            try:
                                                if temp_var > get_sanitized_number(nicht_gedeckter_fehlbetrag):
                                                    nicht_gedeckter_fehlbetrag = temp_var
                                                    if debug_prints:
                                                        print('nicht_gedeckterfehlbetrag nun:', nicht_gedeckter_fehlbetrag)
                                            except Exception as e:
                                                if debug_prints:
                                                    print('error comparing nicht_gedeckter_fehlbetrag, it is still ', nicht_gedeckter_fehlbetrag)
                                                nicht_gedeckter_fehlbetrag = temp_var
                                        break
                                else:
                                    pass

                    try:
                        if isinstance(nicht_gedeckter_fehlbetrag, str):
                            nicht_gedeckter_fehlbetrag = get_sanitized_number(nicht_gedeckter_fehlbetrag)
                    except Exception as e:
                        if debug_prints:
                            print(item, 'error finally converting nicht_gedeckter_fehlbetrag,', '"'+str(nicht_gedeckter_fehlbetrag)+'"')

                    try:
                        if nicht_gedeckter_fehlbetrag * (-1.0) == eigenkapital:
                            eigenkapital = 0
                        if nicht_gedeckter_fehlbetrag > 0:
                            eigenkapital = 0
                    except Exception as e:
                        pass

                    try:
                        if eigenkapital < 0:
                            nicht_gedeckter_fehlbetrag = eigenkapital
                            eigenkapital = 0
                    except Exception as e:
                        pass

                    # EK-Quote
                    try:
                        if not nicht_gedeckter_fehlbetrag:
                            eigenkapitalquote = float(eigenkapital) / float(bilanzsumme)
                        else:
                            eigenkapitalquote = float(nicht_gedeckter_fehlbetrag) / float(bilanzsumme)
                            if eigenkapitalquote > 0:
                                eigenkapitalquote = eigenkapitalquote * (-1.0)
                    except Exception as e:
                        if debug_prints:
                            print(item, 'error calculating eigenkapitalquote', repr(e))
                        eigenkapitalquote = 0.0

                    if debug_prints:
                        print('EK, Bilanzsumme, EK-Quote, Fehlbetrag:', eigenkapital, bilanzsumme, eigenkapitalquote, nicht_gedeckter_fehlbetrag)
                else:  # in case ek_td is none
                    eigenkapital = ''
                    eigenkapitalquote = ''
            else:  # in case bilanz is none
                eigenkapital = ''
                eigenkapitalquote = ''
                bilanzsumme = ''

            ############# find Umsatzerlöse
            try:
                umsatz_td = soup.find_all('td', string=re_Umsatzerlos)[-1]
                # walk right until value is found
                for elem in umsatz_td.next_siblings:
                    if not (elem and isinstance(elem, NavigableString)):
                        if elem.text.strip() != "":
                            try:
                                umsatz = get_sanitized_number(elem.text)
                            except Exception as e:
                                if debug_prints:
                                    print(item, "error in converting umsatz to float!")
                                umsatz = elem.text
                            if debug_prints:
                                print('umsatz:', umsatz)
                            break
                    else:
                        pass
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
                                    print("MA found ins br tags:", " ".join(text.split()))
                                anzahl_MA = " ".join(text.split())
                                ma_sentence_found = True
                                break
                    if not ma_sentence_found:
                        if debug_prints:
                            print("MA found in p tags:", " ".join(elem.text.split()))
                        anzahl_MA = " ".join(elem.text.split())

                    break

            if bilanzsumme != '' and bilanzsumme_vorjahr != '':
                try:
                    bilanzgewinn = float(bilanzsumme) - float(bilanzsumme_vorjahr)
                    bilanzgewinn = round(bilanzgewinn, 2)
                except Exception as e:
                    if debug_prints:
                        print(item, 'error calculating bilanzgewinn', repr(e))
                    bilanzgewinn = str(bilanzsumme) + "-" + str(bilanzsumme_vorjahr)
            else:
                bilanzgewinn = ''


            temporary_list = [item, unternehmensname_given, ort_given, unternehmensname_infile, ort_infile, datum,
                              dokumententyp, JA_von, JA_bis,
                              anzahl_MA, eigenkapital, bilanzsumme, bilanzgewinn, eigenkapitalquote, nicht_gedeckter_fehlbetrag, umsatz, '#N/A in this version',
                              '#N/A in this version']

            company_data.loc[len(company_data)] = temporary_list
            export_counter = export_counter + 1

            unternehmensname_infile = ''
            bilanz = ''
            datum = ''
            dokumententyp = ''
            JA_von = ''
            JA_bis = ''
            anzahl_MA = ''
            eigenkapital = ''
            bilanzsumme = ''
            eigenkapitalquote = ''
            umsatz = ''
            bilanzaktiva = ''
            bilanzpassiva = ''
            bilanzsumme_found = None
            bilanzsumme_tr = ''
            fehlbetrag_tds = ''
            fehlbetrag_td = ''
            nicht_gedeckter_fehlbetrag = ''
            ma_sentence_found = None
            elem = ''
            elem2 = ''
            ek_td = ''
            ek_tds = ''
            ek_tr = ''
            temporary_list = []
            locale.setlocale(locale.LC_ALL, 'de_DE')

        else:  # in the case skip_item = True
            pass

    else:  # in the case index >= limit
        break

try:
    # company_data.to_csv('output/company_attributes.csv', index=False, encoding='utf-8', sep=';', quoting=csv.QUOTE_ALL)
    company_data.to_csv('output/company_attributes2.csv', index=False, encoding='utf-8', sep=';' , quoting=csv.QUOTE_ALL)
except PermissionError as e:
    print("could not export file because of PermissionError, please try again!!")
print("Done!")
print("Found and exported values out of", export_counter, "html files.")
duration = (time.time() - start_time)
print(f'--- run time: {(duration/60):.0f} minutes, {(duration%60):.2f} seconds ---')
