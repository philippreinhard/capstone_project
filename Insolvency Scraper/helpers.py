import requests
from bs4 import BeautifulSoup
import time
import progressbar


def scrape_insolvency_court():
    """
    Returns all selectable regions and courts from homepage www.insolvenzbekanntmachungen.de in a dictionary.

    :return (dict): keys - regions
                    value - courts
    """

    URL = 'https://www.insolvenzbekanntmachungen.de/cgi-bin/bl_suche.pl'
    matchesperpage = 100

    # get all insolvency court:
    insolvency_court = {}

    # get all regions
    with requests.Session() as s:
        s.headers = {"User-Agent": "Mozilla/5.0"}
        s.headers.update({'Content-Type': 'application/x-www-form-urlencoded'})

        res = s.post(URL)
        soup = BeautifulSoup(res.text, "lxml")

    items = soup.find("select", {"name": "Bundesland"}).findAll("option")
    regions = values = [item.get('value') for item in items][1:]

    for region in regions:
        with requests.Session() as s:
            s.headers = {"User-Agent": "Mozilla/5.0"}
            s.headers.update({'Content-Type': 'application/x-www-form-urlencoded'})
            payload = 'Suchfunktion=uneingeschr&Absenden=Suche+starten&' + \
                      'Bundesland=' + region + \
                      '&Gericht=--+Alle+Insolvenzgerichte+--&' \
                      'Datum1=&Datum2=' \
                      '&Name=' + \
                      '&Sitz=' + \
                      '&Abteilungsnr=' + \
                      '&Registerzeichen=--&Lfdnr=' + \
                      '&Jahreszahl=--' + \
                      '&Registerart=--+keine+Angabe+--' + \
                      '&select_registergericht=' + \
                      '&Registergericht=--+keine+Angabe+--' + \
                      '&Registernummer=' + \
                      '&Gegenstand=--+Alle+Bekanntmachungen+innerhalb+des+Verfahrens+--' + \
                      '&matchesperpage=' + str(matchesperpage) + \
                      '&page=1' + \
                      '&sortedby=Datum'
            res = s.post(URL, data=payload)
            soup = BeautifulSoup(res.text, "lxml")

            items = soup.find("select", {"name": "Gericht"}).findAll("option")
            insolvency_court[region] = [item.get('value') for item in items][1:]

    return insolvency_court


def unlimited_search(name='', region='--+Alle+Bundesl%E4nder+--', court='--+Alle+Insolvenzgerichte+--&',
                     matchesperpage=100, verbose=False):
    """
    Get all the available insolvencies from the homepage 'www.insolvenzbekanntmachungen.de' from the last 2 weeks.

    :param name (str): name of the firm or real person who has initiated an insolvency process.
    :param region (str): region of the insolvency process
    :param court (str): court of the insolvency
    :param matchesperpage (int): number of max
    :param verbose (bool): print additional information

    :return (list): list of all available insolvencies.
    """

    URL = 'https://www.insolvenzbekanntmachungen.de/cgi-bin/bl_suche.pl'

    # 1. find max number of pages
    with requests.Session() as s:
        s.headers = {"User-Agent": "Mozilla/5.0"}
        s.headers.update({'Content-Type': 'application/x-www-form-urlencoded'})
        payload = 'Suchfunktion=uneingeschr&Absenden=Suche+starten&' + \
                  'Bundesland=' + region + \
                  '&Gericht=' + court + \
                  'Datum1=&Datum2=' \
                  '&Name=' + name + \
                  '&Sitz=' + \
                  '&Abteilungsnr=' + \
                  '&Registerzeichen=--&Lfdnr=' + \
                  '&Jahreszahl=--' + \
                  '&Registerart=--+keine+Angabe+--' + \
                  '&select_registergericht=' + \
                  '&Registergericht=--+keine+Angabe+--' + \
                  '&Registernummer=' + \
                  '&Gegenstand=--+Alle+Bekanntmachungen+innerhalb+des+Verfahrens+--' + \
                  '&matchesperpage=' + str(matchesperpage) + \
                  '&page=1' + \
                  '&sortedby=Datum'
        res = s.post(URL, data=payload)
        soup = BeautifulSoup(res.text, "lxml")
        t = soup.select('center a')[-1].attrs['href']
        start_nr = t.find('&page=')
        end_nr = t.find('#Ergebnis')
        result_page_nr = int(t[start_nr + 6:end_nr])

        # 2. go through all pages and get data
        start_time = time.time()

        insolvency = []

    with requests.Session() as s:
        s.headers = {"User-Agent": "Mozilla/5.0"}
        s.headers.update({'Content-Type': 'application/x-www-form-urlencoded'})

        for page in range(1, result_page_nr):

            # for region in regions:
            payload = 'Suchfunktion=uneingeschr&Absenden=Suche+starten&' + \
                      'Bundesland=' + region + \
                      '&Gericht=' + court + \
                      'Datum1=&Datum2=' \
                      '&Name=' + name + \
                      '&Sitz=' + \
                      '&Abteilungsnr=' + \
                      '&Registerzeichen=--&Lfdnr=' + \
                      '&Jahreszahl=--' + \
                      '&Registerart=--+keine+Angabe+--' + \
                      '&select_registergericht=' + \
                      '&Registergericht=--+keine+Angabe+--' + \
                      '&Registernummer=' + \
                      '&Gegenstand=--+Alle+Bekanntmachungen+innerhalb+des+Verfahrens+--' + \
                      '&matchesperpage=' + str(matchesperpage) + \
                      '&page=' + str(page) + \
                      '&sortedby=Datum'
            res = s.post(URL, data=payload)
            soup = BeautifulSoup(res.text, "lxml")

            for item in soup.select("b li a"):
                insolvency.append(item.get_text(strip=True))
    if verbose:
        print("--- %s minutes ---" % ((time.time() - start_time) / 60))
        print(len(insolvency))

    return insolvency


def detail_search(name='', region='', court='', residence='', verbose=False):
    """
    Get insolvencies which are older than 2 weeks and could not be found within the unlimited_search() function.

    :param name (str): name of the firm or real person who has initiated an insolvency process.
    :param region (str): region of the insolvency process
    :param court (str): court of the insolvency
    :param residence (str): residence of the debtor
    :param verbose (bool): print additional information
    :return (list): list of all available insolvencies.
    """

    URL = 'https://www.insolvenzbekanntmachungen.de/cgi-bin/bl_suche.pl'
    matchesperpage = 100

    start_time = time.time()

    insolvency = []

    # if court is a dict from function scrape_insolvency_court()
    if type(court) == dict:
        for region, all_courts in court.items():
            for court in all_courts:
                with requests.Session() as s:
                    s.headers = {"User-Agent": "Mozilla/5.0"}
                    s.headers.update({'Content-Type': 'application/x-www-form-urlencoded'})

                    # for region in regions:
                    payload = 'Suchfunktion=detail&Absenden=Suche+starten&' + \
                              'Bundesland=' + region + \
                              '&Gericht=' + court + \
                              '&Datum1=&Datum2=' \
                              '&Name=' + name + \
                              '&Sitz=' + residence + \
                              '&Abteilungsnr=' + \
                              '&Registerzeichen=--&Lfdnr=' + \
                              '&Jahreszahl=--' + \
                              '&Registerart=--+keine+Angabe+--' + \
                              '&select_registergericht=' + \
                              '&Registergericht=--+keine+Angabe+--' + \
                              '&Registernummer=' + \
                              '&Gegenstand=--+Alle+Bekanntmachungen+innerhalb+des+Verfahrens+--' + \
                              '&matchesperpage=' + str(matchesperpage) + \
                              '&page=100' + \
                              '&sortedby=Datum'
                    res = s.post(URL, data=payload)
                    soup = BeautifulSoup(res.text, "lxml")

                    for item in soup.select("b li a"):
                        insolvency.append(item.get_text(strip=True))

    # if court is a str
    else:
        with requests.Session() as s:
            s.headers = {"User-Agent": "Mozilla/5.0"}
            s.headers.update({'Content-Type': 'application/x-www-form-urlencoded'})

            # for region in regions:
            payload = 'Suchfunktion=detail&Absenden=Suche+starten&' + \
                      'Bundesland=' + region + \
                      '&Gericht=' + court + \
                      '&Datum1=&Datum2=' \
                      '&Name=' + name + \
                      '&Sitz=' + residence + \
                      '&Abteilungsnr=' + \
                      '&Registerzeichen=--&Lfdnr=' + \
                      '&Jahreszahl=--' + \
                      '&Registerart=--+keine+Angabe+--' + \
                      '&select_registergericht=' + \
                      '&Registergericht=--+keine+Angabe+--' + \
                      '&Registernummer=' + \
                      '&Gegenstand=--+Alle+Bekanntmachungen+innerhalb+des+Verfahrens+--' + \
                      '&matchesperpage=' + str(matchesperpage) + \
                      '&page=100' + \
                      '&sortedby=Datum'
            res = s.post(URL, data=payload)
            soup = BeautifulSoup(res.text, "lxml")

            for item in soup.select("b li a"):
                insolvency.append(item.get_text(strip=True))
    if verbose:
        print("--- %s seconds ---" % ((time.time() - start_time)))
        print("Number of results: " + str(len(insolvency)))

    return insolvency


def scrape_court_and_insolvency(company_attributes, insolvency_court, time_out=0, verbose=False):
    """
    Search for insolvency for a company using the name and postcode + city of the headquarter and returns insolvencies
    in a dict. If there is any error during the process, the company name is saved in an error-list.

    :param company_attributes (list): list of a list of information [name (based on kununu), name (based on dnb), employee, sales Mio. €, postcode, city]
    :param insolvency_court (dict): dict of regions and courts from scrape_insolvency_court()
    :param time_out (int): time delay between scraping
    :param verbose (bool): print additional information
    :return: insolvenz_data_dict (dict), errors (list), company_attributes_insolvency (list)
    """
    # https://www.gerichtsverzeichnis.de/verzeichnis.php
    # payload = 'suchen=suchen&suchfeld=65817 eppstein'

    insolvenz_data_dict = {}
    errors = []
    company_attributes_insolvency = []

    # status bar 
    bar = progressbar.ProgressBar(maxval=len(company_attributes),
                                  widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()

    for i in range(len(company_attributes)):
        if len(company_attributes_insolvency) != i:
            print(i-1)
            print(company_attributes[i-1])
            break
        
        time.sleep(time_out)
        bar.update(i + 1)

        insolvency_court_raw = ""
        error_type = 0
        company_attribute_i = company_attributes[i].copy()

        name = company_attribute_i[1]
        plz = company_attribute_i[4]
        city = company_attribute_i[5][1:].replace('SS', 'ß')

        if verbose:
            print()
            print(str(i) + '. / ' + str(len(company_attributes)))
            print(name)
            print(plz)
            print(city)

        # filtering missing data & filtering nonsense data 
        if plz == 'missing' or city == 'missing' or name.lower() == 'frau' or name.lower() == 'herr':
            error_type = 1
            error_company_attributes = company_attribute_i
            error_company_attributes.append(error_type)
            errors.append(error_company_attributes)

            temp_company = company_attribute_i
            temp_company.append('')
            temp_company.append(-1)
            company_attributes_insolvency.append(temp_company)

            if verbose:
                print('Error!')
                print(error_company_attributes)
            continue
        
        # change german char into compatible char
        german_char = ['ä', 'ö', 'ü', 'ß']
        new_char = ['&auml;', '&ouml;', '&uuml;', '&szlig;']
        
        city_ger = city.lower()
        
        for i_char in range(len(german_char)):
            city_ger = city_ger.replace(german_char[i_char], new_char[i_char])

        payload = 'suchen=suchen&suchfeld=' + plz + ' ' + city_ger

        with requests.Session() as s:
            s.headers = {"User-Agent": "Mozilla/5.0"}
            s.headers.update({'Content-Type': 'application/x-www-form-urlencoded'})
            URL = 'https://www.gerichtsverzeichnis.de/verzeichnis.php'

            res = s.post(URL, data=payload)
            soup = BeautifulSoup(res.text, "lxml")

        try:
            temp_court = soup.find("div", {"class": "gerichtstyp"}, text="Insolvenzverfahren").nextSibling.text[12:]
            
            temp_city_court = ''
            for region_court in insolvency_court:
                for city_court in insolvency_court[region_court]:
                    if city_court.lower() == temp_court.lower():
                        insolvency_court_raw = city_court
                    elif city_court.lower() in temp_court.lower():
                        temp_city_court = city_court
            
            if insolvency_court_raw == '':
                insolvency_court_raw = temp_city_court
                
            if insolvency_court_raw == '':
                if temp_court != '':
                    error_type = 2
                raise Exception

        # workaround if court could not be found
        except:
            URL = 'https://gerichtsstand.net/suche/?plz=' + plz + '&ort=' + city

            try:
                with requests.Session() as s:
                    s.headers = {"User-Agent": "Mozilla/5.0"}
                    s.headers.update({'Content-Type': 'application/x-www-form-urlencoded'})

                    res = s.post(URL)
                    soup = BeautifulSoup(res.text, "lxml")
                    infos = soup.findAll('div')[12].find('div').find('div')
                    
                    info_list = infos.text.split('\n')
                    for info in info_list:
                        if 'Insolvenzverfahren: ' in info:
                            insolvency_court_raw = info[23:]
                            break
                    
                    if insolvency_court_raw == "":
                        raise Exception
            except:
            
                if insolvency_court_raw == '':
                    infos = soup.findAll('div')[12].find('a').text

                    temp_city_court = ''
                    for region_court in insolvency_court:
                        for city_court in insolvency_court[region_court]:
                            if city_court.lower() == infos.lower():
                                insolvency_court_raw = city_court
                            elif city_court.lower() in infos.lower():
                                temp_city_court = city_court

                    if insolvency_court_raw == '':
                        insolvency_court_raw = temp_city_court

                if insolvency_court_raw == "":
                    for region_court in insolvency_court:
                        for city_court in insolvency_court[region_court]:
                            if city_court.lower() in city.lower():
                                insolvency_court_raw = city_court                    
                            
        if insolvency_court_raw == "":
            if error_type == 0: 
                error_type = 3
            error_company_attributes = company_attribute_i
            error_company_attributes.append(error_type)
            errors.append(error_company_attributes)

            if verbose:
                print('Error!')
                print(error_company_attributes)

            temp_company = company_attribute_i
            temp_company.append('')
            temp_company.append(-1)
            company_attributes_insolvency.append(temp_company)
            
            continue

        # string modification e.g. shortcuts
        insolvency_court_raw = insolvency_court_raw.replace('a.d.', 'an der')

        # finally insolvency data
        temp_city_court = ''
        temp_region_court = ''
        city_court_selected = ''
        region_court_selected = ''
        
        for region_court in insolvency_court:
            for city_court in insolvency_court[region_court]:
                
                if city_court.lower() == insolvency_court_raw.lower():
                    city_court_selected = city_court
                    region_court_selected = region_court
                elif city_court.lower() in insolvency_court_raw.lower():
                    temp_city_court = city_court
                    temp_region_court = region_court

        if city_court_selected == '':
            city_court_selected = temp_city_court
            region_court_selected = temp_region_court
            
        if city_court_selected != '':
            if verbose:
                print('Court: ' + city_court_selected)

        data = detail_search(name=name, region=region_court_selected, court=city_court_selected)
        if len(data) > 0:
            temp_company = company_attribute_i
            temp_company.append(city_court_selected)
            temp_company.append(1)
            company_attributes_insolvency.append(temp_company)

            insolvenz_data_dict[name] = data
            if verbose:
                print('Insolvency: ' + name + ': ' + str(len(data)))
                print(str(i) + '/' + str(len(company_attributes)))
        else:
            temp_company = company_attribute_i
            temp_company.append(city_court_selected)
            temp_company.append(0)
            company_attributes_insolvency.append(temp_company)

    bar.finish()
    return insolvenz_data_dict, errors, company_attributes_insolvency
