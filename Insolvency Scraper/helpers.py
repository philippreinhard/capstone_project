import requests
from bs4 import BeautifulSoup
import time


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


def scrape_court_and_insolvency(company_attributes, insolvency_court, verbose=False):
    """
    Search for insolvency for a company using the name and postcode + city of the headquarter and returns insolvencies
    in a dict. If there is any error during the process, the company name is saved in an error-list.

    :param company_attributes (list): list of a list of information [name, employee, sales Mio. €, postcode, city]
    :param insolvency_court (dict): dict of regions and courts from scrape_insolvency_court()
    :param verbose (bool): print additional information
    :return: insolvenz_data_dict (dict), errors (list)
    """
    # https://www.gerichtsverzeichnis.de/verzeichnis.php
    URL = 'https://www.gerichtsverzeichnis.de/verzeichnis.php'
    # payload = 'suchen=suchen&suchfeld=65817 eppstein'

    insolvenz_data_dict = {}
    errors = []

    for i in range(len(company_attributes)):
        name = company_attributes[i][0]
        plz = company_attributes[i][3]
        city = company_attributes[i][4].title()
        if verbose:
            print(name)
            print(plz)
            print(city)

        # filtering nonsense data
        if name.lower() == 'frau' or name.lower() == 'herr':
            continue

        # change german char into compatible char<
        german_char = ['ä', 'ö', 'ü']
        new_char = ['ae', 'oe', 'ue']

        for i_char in range(len(german_char)):
            name = name.replace(german_char[i_char], new_char[i_char])
            city = city.replace(german_char[i_char], new_char[i_char])

        payload = 'suchen=suchen&suchfeld=' + plz + city

        with requests.Session() as s:
            s.headers = {"User-Agent": "Mozilla/5.0"}
            s.headers.update({'Content-Type': 'application/x-www-form-urlencoded'})

            res = s.post(URL, data=payload)
            soup = BeautifulSoup(res.text, "lxml")

        try:
            insolvency_court_raw = soup.find("div", {"class": "gerichtstyp"},
                                             text="Insolvenzverfahren").nextSibling.text[12:]

        # workaround if court could not be found but city name is in insolvency_court
        except:
            if city[1:] in insolvency_court:
                insolvency_court_raw = city[1:]
            else:
                errors.append(name + ' ' + plz + ' ' + city)
                if verbose:
                    print('Error!')
                    print(name + ' ' + plz + ' ' + city)

                continue

        # finally insolvency data
        for region in insolvency_court:
            for city in insolvency_court[region]:
                if city in insolvency_court_raw:
                    data = detail_search(name=name, region=region, court=city)
                    if len(data) > 0:
                        insolvenz_data_dict[name] = data
                        if verbose:
                            print('Treffer: ' + name + ': ' + str(len(data)))
                            print(str(i) + '/' + str(len(company_attributes)))

    return insolvenz_data_dict, errors
