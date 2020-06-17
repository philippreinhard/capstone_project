import urllib
from bs4 import BeautifulSoup


#Data to Extract from HTML Files: Anzahl Mitarbeiter, Umsatz und Bilanzsumme

#Anzahl Mitarbeiter: Wenn vorhanden, meist in <p> Tag
#Umsatz: Wenn vorhanden, meist <p> oder <br> Tag
#Bilanzsumme: Vorhanden in <td> tags als Tabelle

with open("KUNUNU_CIBEK.csv_29.01.2020.html") as fp:
    soup = BeautifulSoup(fp)
    print(soup.find_all("td"))

with open("KUNUNU_GCE mbH.csv_11.03.2020.html") as fp:
    soup = BeautifulSoup(fp)
    print(soup.find_all("td"))

with open("KUNUNU_GCE mbH.csv_15.03.2019.html") as fp:
    soup = BeautifulSoup(fp)
    print(soup.find_all("td"))

with open("KUNUNU_GCE mbH.csv_17.10.2019.html") as fp:
    soup = BeautifulSoup(fp)
    print(soup.find_all("td"))

with open("KUNUNU_GCE mbH.csv_19.02.2020.html") as fp:
    soup = BeautifulSoup(fp)
    print(soup.find_all("td"))

with open("KUNUNU_GCE mbH.csv_19.11.2019.html") as fp:
    soup = BeautifulSoup(fp)
    print(soup.find_all("td"))

with open("KUNUNU_GCE mbH.csv_23.10.2019.html") as fp:
    soup = BeautifulSoup(fp)
    print(soup.find_all("td"))

with open("KUNUNU_GCE mbH.csv_25.09.2019.html") as fp:
    soup = BeautifulSoup(fp)
    print(soup.find_all("p"))

with open("KUNUNU_GCE mbH.csv_27.04.2020.html") as fp:
    soup = BeautifulSoup(fp)
    print(soup.find_all("td"))
    print(soup.find_all("p"))


with open("KUNUNU_EACG GmbH.csv_21.02.2020.html") as fp:
    soup = BeautifulSoup(fp)
    print(soup.find_all("td"))

with open("KUNUNU_MathWorks.csv_21.04.2020.html") as fp:
    soup = BeautifulSoup(fp)
    print(soup.find_all("td"))

with open("KUNUNU_MathWorks.csv_28.02.2020.html") as fp:
    soup = BeautifulSoup(fp)
    print(soup.find_all("td"))
    print(soup.find_all("p"))

with open("KUNUNU_NetUSE AG.csv_08.07.2019.html") as fp:
    soup = BeautifulSoup(fp)
    print(soup.find_all("p"))

with open("KUNUNU_NetUSE AG.csv_16.04.2019.html") as fp:
    soup = BeautifulSoup(fp)
    print(soup.find_all("p"))

with open("KUNUNU_NetUSE AG.csv_26.03.2020.html") as fp:
    soup = BeautifulSoup(fp)
    print(soup.find_all("p"))
    print(soup.find_all("td"))

with open("KUNUNU_Nodes GmbH.csv_05.08.2019.html") as fp:
    soup = BeautifulSoup(fp)
    print(soup.find_all("Nothing to Scrape"))

with open("KUNUNU_Nodes GmbH.csv_13.11.2019.html") as fp:
    soup = BeautifulSoup(fp)
    print(soup.find_all("Nothing to Scrape"))

with open("KUNUNU_Nodes GmbH.csv_14.01.2020.html") as fp:
    soup = BeautifulSoup(fp)
    print(soup.find_all("td"))

with open("KUNUNU_Nodes GmbH.csv_14.02.2020.html") as fp:
    soup = BeautifulSoup(fp)
    print(soup.find_all("td"))

with open("KUNUNU_Nodes GmbH.csv_17.01.2020.html") as fp:
    soup = BeautifulSoup(fp)
    print(soup.find_all("td"))

with open("KUNUNU_Nodes GmbH.csv_17.05.2019.html") as fp:
    soup = BeautifulSoup(fp)
    print("Noting to Scrape")

with open("KUNUNU_Nodes GmbH.csv_27.12.2019.html") as fp:
    soup = BeautifulSoup(fp)
    print(soup.find_all("td"))

with open("KUNUNU_webgo GmbH.csv_02.08.2019.html") as fp:
    soup = BeautifulSoup(fp)
    print(soup.find_all("td"))

with open("KUNUNU_webgo GmbH.csv_02.08.2019.html") as fp:
    soup = BeautifulSoup(fp)
    print(soup.find_all("td"))

with open("KUNUNU_FORCAM GmbH.csv_09.01.2020.html") as fp:
    soup = BeautifulSoup(fp)
    print(soup.find_all("td"))
    print(soup.find_all("p"))

with open("KUNUNU_Formitas AG.csv_23.09.2019.html") as fp:
    soup = BeautifulSoup(fp)
    print(soup.find_all("b"))
    print(soup.find_all("br"))
    print(soup.find_all("td"))

with open("KUNUNU_ORSOFT GmbH.csv_18.03.2020.html") as fp:
    soup = BeautifulSoup(fp)
    print(soup.find_all("td"))
    print(soup.find_all("p"))

with open("KUNUNU_feedback ag.csv_06.11.2019.html") as fp:
    soup = BeautifulSoup(fp)
    print(soup.find_all("td"))
    print(soup.find_all("p"))
    print(soup.find_all("br"))

with open("KUNUNU_kimeta GmbH.csv_19.12.2019.html") as fp:
    soup = BeautifulSoup(fp)
    print(soup.find_all("td"))
    print(soup.find_all("p"))
    print(soup.find_all("br"))

with open("KUNUNU_pitcup GmbH.csv_16.12.2019.html") as fp:
    soup = BeautifulSoup(fp)
    print(soup.find_all("td"))
    print(soup.find_all("p"))
    print(soup.find_all("br"))

with open("KUNUNU_MobiMedia AG.csv_09.10.2019.html") as fp:
    soup = BeautifulSoup(fp)
    print(soup.find_all("td"))

with open("KUNUNU_MobiMedia AG.csv_09.10.2019.html") as fp:
    soup = BeautifulSoup(fp)
    print(soup.find_all("td"))

with open("KUNUNU_innovas GmbH.csv_11.02.2020.html") as fp:
    soup = BeautifulSoup(fp)
    print(soup.find_all("td"))
    print(soup.find_all("p"))

with open("KUNUNU_innovas GmbH.csv_20.01.2020.html") as fp:
    soup = BeautifulSoup(fp)
    print(soup.find_all("td"))

with open("KUNUNU_oculavis GmbH.csv_25.03.2020.html") as fp:
    soup = BeautifulSoup(fp)
    print(soup.find_all("td"))