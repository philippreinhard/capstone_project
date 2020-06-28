import scrapy
import logging
import csv
import os
import json

urls_size_filtered = []

# [kununu-Name, dnb-Name, employees, sales, plz, city]
# 0: kununu-Name, 1: dnb-Name, 2: employees, 3: sales, 4: plz, 5: city
with open('company_attributes_Dienstleistungen_merged.json', 'r') as file:
    company_attributes = json.load(file)

company_names = []
for company_attribute in company_attributes:
    company_names.append(company_attribute[0])

url_list = []

kicked_by_dnb = 0
kicked_by_kununu = 0

class filter_size(scrapy.Spider):
    name = "filter_size"

    # Reduce Log-Level of some Loggers to avoid "spam" messages in Command line
    def __init__(self, *args, **kwargs):
        logger = logging.getLogger('scrapy.core.scraper')
        logger.setLevel(logging.INFO)
        logger2 = logging.getLogger('scrapy.core.engine')
        logger2.setLevel(logging.INFO)
        logger3 = logging.getLogger('scrapy.middleware')
        logger3.setLevel(logging.WARNING)
        logger4 = logging.getLogger('kununu')
        logger4.setLevel(logging.WARNING)
        super().__init__(*args, **kwargs)

    def start_requests(self):

        global url_list

        with open('urls_merged_Dienst.json', 'r') as file:
            url_list = json.load(file)

        for the_url in url_list[:1000]:
            print(the_url)
            yield scrapy.Request(the_url, self.parse_company_size)

    def changed_name(self, name):
        # Achtung: Muss exakt gleich sein, wie die Methode in correct_names.py
        if " beteiligung" in name:
            name = name.split(" beteiligung")[0]
        if " Beteiligung" in name:
            name = name.split(" Beteiligung")[0]
        if "gesellschaft mit beschr" in name:
            name = name.split("gesellschaft mit beschr")[0]
        if " (" in name:
            name = name.split(" (")[0]
        '''if " (haftungs" in name:
            name = name.split(" (haftungs")[0]
        if " (Haftungs" in name:
            name = name.split(" (Haftungs")[0]'''
        if " haftungs" in name:
            name = name.split(" haftungs")[0]
        return name

    # Umsatz: 52018; Umsatz: 201922225; response.css('strong::text').get() kann None sein
    def parse_company_size(self, response):

        global kicked_by_dnb
        global kicked_by_kununu

        # add in case an error occurs
        urls_size_filtered.append(response.url)

        companyname_raw = response.css('span.company-name::text').get()
        print(companyname_raw)
        companyname = self.changed_name(companyname_raw)
        employees = None
        sales = None

        # check size in scraped dnb infos -> kick url if company too big
        if companyname in company_names:
            for company_attribute in company_attributes:
                if company_attribute[0] == companyname:
                    if ((company_attribute[2] != "missing" and int(str(company_attribute[2]).replace(",", "")) >= 250) and (company_attribute[3] != "missing" and float(company_attribute[3]) >= 40)) or\
                            (company_attribute[3] == "missing" and company_attribute[2] != "missing" and int(str(company_attribute[2]).replace(",", "")) >= 250) or\
                            (company_attribute[2] == "missing" and company_attribute[3] != "missing" and float(company_attribute[3]) >= 40):
                        print("Company is too big according to dnb")
                        kicked_by_dnb += 1
                        del urls_size_filtered[-1]
                        return None

        # Check size in kununu -> kick url if info says company too big
        if response.css('strong::text').get() is not None and len(response.css('strong::text')) > 1:
            # sales = response.css('strong::text').get().split(" ")[0]
            # sales = "".join([s for s in response.css('strong::text').get() if s.isdigit()])
            sales = [int(s) for s in response.css('strong::text').get().split() if s.isdigit()][0]
            # employees = response.css('strong::text')[1].get().replace(" ", "").replace("\n", "")
            employees = "".join([s for s in response.css('strong::text')[1].get() if s.isdigit()])
            print("Kununu sales: " + str(sales))
            print("Kununu employees: " + str(employees))

            # in case sales are given in thousands
            if float(sales) > 3000:
                sales = float(sales) / 1000
                print("Kununu sales corrected: " + str(sales))

            # Nur kleine und mittlere Unternehmen werden betrachtet
            # Quellen:  https://www.gesetze-im-internet.de/hgb/__267.html
            #           https://www.gesetze-im-internet.de/hgb/__267a.html
            if (employees and int(employees) >= 250) and (sales and float(sales) >= 40):
                print("Company is too big according to kununu")
                del urls_size_filtered[-1]
                kicked_by_kununu += 1
                return None

        print(url_list.index(response.url))

        if url_list.index(response.url) > (len(url_list[:1000]) - 15):
            print("Ursprungsliste Länge: 1000") # + str(len(url_list)))
            print("Neue Liste: " + str(len(urls_size_filtered)))
            print("Kicked by dnb: " + str(kicked_by_dnb))
            print("Kicked by kununu: " + str(kicked_by_kununu))
            with open('urls_Dienst_without_big_companies.json', 'w') as f:
                json.dump(urls_size_filtered, f)
