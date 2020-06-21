import scrapy
import logging
import csv
import os
import json

company_attributes = []
with open('output.json', 'r') as file:
    company_attributes = json.load(file)

company_names = []
for company_attribute in company_attributes:
    company_names.append(company_attribute[0])

class Reviews(scrapy.Spider):
    name = "reviews"

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

        url_list = []
        with open('urls_merged_Dienst.json', 'r') as file:
            url_list = json.load(file)

        for url in url_list[3000:]:
            print(url)
            comments_url = url + "/kommentare"
            yield scrapy.Request(comments_url, self.parse_company_reviews)
            
    # Mitarbeiter: 60 Umsatz: 52018; Mitarbeiter: 200 Umsatz: 201922225; response.css('strong::text').get() kann None sein

    '''
    def parse_company_size(self, response):

        # else: In: response.css('strong::text').get() Out: 'Diese Firma hat leider noch keine Informationen hinterlegt.'
        if len(response.css('strong::text')) > 1:
            #sales = response.css('strong::text').get().split(" ")[0]
            #sales = [int(s) for s in response.css('strong::text').get().split() if s.isdigit()][0]
            #employees = response.css('strong::text')[1].get().replace(" ", "").replace("\n", "")
            sales = "".join([s for s in response.css('strong::text').get() if s.isdigit()])
            employees = "".join([s for s in response.css('strong::text')[1].get() if s.isdigit()])

            # Nur kleine und mittlere Unternehmen werden betrachtet
            # Quellen:  https://www.gesetze-im-internet.de/hgb/__267.html
            #           https://www.gesetze-im-internet.de/hgb/__267a.html
            if employees and sales and (int(employees) >= 10 and int(employees) < 250) and (float(sales) >= 0.7 and float(sales) < 40):
                print("Diese Firma ist klein oder mittelgroß: Anzahl Mitarbeiter: " + employees + " Umsatz: " + sales)
                comments_url = response.url + "/kommentare"
                yield scrapy.Request(url=comments_url, callback=self.parse_company_reviews)
                
            else: print("Rausgeflogen: Anzahl Mitarbeiter: " + employees + " Umsatz: " + sales)
            
        else: print(response.css('strong::text').get().replace("\n", ""))'''


    def parse_company_reviews(self, response):

        companyname_raw = response.css('header.index__profileHeader___LB66 span::text').get()
        print(companyname_raw)
        companyname = self.changed_name(companyname_raw)
        employees = None
        sales = None
        # Problem:  1. Es gibt oder 4 wo ich händisch noch was abgeschnitten hab (wo in Klammern noch was Stand)
        #           2. Was bringt das Filtern per dnb, wenn wir jetzt alle durchlassen^^ Die zu großen sollten wir wahrscheinlich kicken... Oder alles von kununu nehmen
        if companyname not in company_names: # or "AKKA" in companyname:
            print("Company was not in the result file")
            return None
        else:
            for company_attribute in company_attributes:
                # If the name is within the result file, but it has only one attribute and that is out of SME range, kick the company
                if company_attribute[0] == companyname:
                    if (company_attribute[1] == "missing" or company_attribute[2] == "missing") and ((company_attribute[1] != "missing" and (int(company_attribute[1]) >= 250 or int(company_attribute[1]) < 10)) or (company_attribute[2] != "missing" and (float(company_attribute[2]) >= 40 or float(company_attribute[2]) < 0.7))):
                        print("Company had one wrong attribute")
                        return None
                    else:
                        employees = company_attribute[1]
                        sales = company_attribute[2]

        # Auf der Unternehmensseite/kommentare
        review_list = response.css('article.index__contentBlock__7vKo-')

        for review in review_list[2:]:

            Anstellung = review.css('span.index__position__mCyeO::text')[0].get()
            if len(review.css('span.index__position__mCyeO::text')) > 1:
                Anstellung = Anstellung + review.css("span.index__position__mCyeO::text")[1].get()
            Bereich = ""
            if "Bereich" in review.css('div.index__employmentInfoBlock__27ro4').get():
                Bereich = review.css('div.index__employmentInfoBlock__27ro4').get()
                Bereich = Bereich.split('Bereich ')[1]
                Bereich = Bereich.split(' bei')[0]

            Dict = {'Unternehmen': companyname, 'Mitarbeiter': employees, 'Umsatz': sales, 'Datum': review.css('time::attr(datetime)').get(),
                    'ReviewRating': review.css('span.index__score__16yy9::text').get(), 'Anstellung': Anstellung,
                    'Bereich': Bereich, 'ReviewTitel': review.css('h3.index__title__2uQec::text').get().replace(";", ".").replace(" - ", ",")}

            fieldnames = ['Unternehmen', 'Mitarbeiter', 'Umsatz', 'Datum', 'ReviewRating', 'Anstellung', 'Bereich', 'ReviewTitel',
                          'Was macht dein Arbeitgeber in Corona-Zeiten gut?', 'Was macht dein Arbeitgeber in Corona-Zeiten nicht gut?', 'Was sollte dein Unternehmen in Corona-Zeiten (anders) machen?',
                          'Wofür möchtest du deinen Arbeitgeber im Umgang mit der Corona-Situation loben?', 'Was macht dein Arbeitgeber im Umgang mit der Corona-Situation nicht gut?',
                          'Wo siehst du Chancen für deinen Arbeitgeber mit der Corona-Situation besser umzugehen?', 'Wie kann dich dein Arbeitgeber im Umgang mit der Corona-Situation noch besser unterstützen?',
                          'Gut am Arbeitgeber finde ich', 'Schlecht am Arbeitgeber finde ich', 'Verbesserungsvorschläge', 'Arbeitsatmosphäre_s',
                          'Arbeitsatmosphäre', 'Image_s', 'Image', 'Work-Life-Balance_s', 'Work-Life-Balance', 'Karriere/Weiterbildung_s',
                          'Karriere/Weiterbildung', 'Gehalt/Sozialleistungen_s', 'Gehalt/Sozialleistungen', 'Umwelt-/Sozialbewusstsein_s',
                          'Umwelt-/Sozialbewusstsein', 'Kollegenzusammenhalt_s', 'Kollegenzusammenhalt', 'Umgang mit älteren Kollegen_s',
                          'Umgang mit älteren Kollegen', 'Vorgesetztenverhalten_s', 'Vorgesetztenverhalten', 'Arbeitsbedingungen_s',
                          'Arbeitsbedingungen', 'Kommunikation_s', 'Kommunikation', 'Gleichberechtigung_s', 'Gleichberechtigung',
                          'Interessante Aufgaben_s', 'Interessante Aufgaben']

            factor_list = review.css('div.index__factor__3Z15R')

            for i in range(0, len(factor_list)):
                factor_str = factor_list[i].get()
                factor = review.css('div.index__factor__3Z15R')[i]
                title = factor.css('h4.index__title__W4hOp::text').get()
                
                if title in fieldnames:
                    score = ""
                    answer = ""
                    if "data-score" in factor_str:
                        score = factor_str.split("data-score=\"")[1]
                        score = score.split("\"><")[0]
                        scoreTitle = title + '_s'
                        Dict[scoreTitle] = score
                    if factor.css('p.index__plainText__lgNCM'):
                        for i in range(0, len(factor.css('p.index__plainText__lgNCM::text'))):
                            # answer = answer + unicode(factor.css('p.index__plainText__lgNCM::text')[i].get(), "utf-8", errors="ignore")
                            # answer = answer + str(factor.css('p.index__plainText__lgNCM::text')[i].get().encode('ascii', 'ignore'))
                            answer = answer + factor.css('p.index__plainText__lgNCM::text')[i].get()
                        Dict[title] = answer.replace(";", ".").replace(" - ", ",")
                else: print('ACHTUNG ACHTUNG ACHTUNG ACHTUNG ACHTUNG ACHTUNG ACHTUNG ACHTUNG ACHTUNG ACHTUNG ACHTUNG ACHTUNG ACHTUNG ACHTUNG ACHTUNG ACHTUNG: Faktor ist nicht in der Spaltenliste drin. Er heißt: ' + title)

            # Write all the collected data in a new row in the csv file 'reviews.csv'
            with open('reviews.csv', 'a', newline='') as f:
                theWriter = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
                if os.stat('reviews.csv').st_size == 0:
                    theWriter.writeheader()
                theWriter.writerow(Dict)

        button = response.css("span.index__buttonContent__3Ds7B")

        if button:
            row = response.css("div.row")
            next_page_url = 'https://www.kununu.com/' + row.css("a::attr(href)")[-1].extract()
            #self.log(next_page_url)
            #if(next_page_url[-1] != '2'): #Erstmal nur die ersten 15 Seiten angucken
            yield scrapy.Request(url=next_page_url, callback=self.parse_company_reviews)
        else:
            self.log('');
            self.log('Last page reached: ' + response.url)
            self.log('Last page contained {} item(s)'.format(len(review_list)))
            self.log('');


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