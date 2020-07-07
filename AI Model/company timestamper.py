import json
import numpy as np
import pandas as pd
from sys import *
import os

data_path = "Data Preparation/model_data/"


with open(data_path + 'new_company_attributes_merged.json', 'r') as file:
    company_list = json.load(file)

df = pd.read_csv(data_path + "reviews_merged.csv")

df = df[["Unternehmen", "Datum", "ReviewRating", "Arbeitsatmosphäre_s", "Image_s", "Work-Life-Balance_s",
         "Karriere/Weiterbildung_s", "Gehalt/Sozialleistungen_s", "Umwelt-/Sozialbewusstsein_s",
         "Kollegenzusammenhalt_s", "Umgang mit älteren Kollegen_s", "Vorgesetztenverhalten_s", "Arbeitsbedingungen_s",
         "Kommunikation_s", "Gleichberechtigung_s", "Interessante Aufgaben_s"]]

company_list_unique = []
for company in company_list:
    if company in company_list_unique:
        continue
    else:
        company_list_unique.append(company)
company_list = company_list_unique

def get_dates(dates):
    # takes the timestamps and extracts the years

    years = []
    half_years = []
    for date in dates:
        year, month = date.split("-")[:2]
        years.append(int(year))
    return years

def get_outter_timestamps(comp_reviews):
    # get largest and smallest years of the datasample

    max_timestamp = comp_reviews["Year"].max()
    min_timestamp = comp_reviews["Year"].min()

    # we do not consider 2020, so reduce it to 2019
    if max_timestamp >= 2020:
        max_timestamp = 2019

    if min_timestamp >= 2020:
        min_timestamp = 2019

    return max_timestamp, min_timestamp

new_company_list = []
index = 0
for company in company_list:

    if (index % 100 == 0):
        print(str(index) + "/" + str(len(company_list)))

    new_company = []
    old_name = company[0]
    n_employees = company[2]
    n_sales = company[3]
    plz = company[4]
    location = company[5]


    # filter big companies, continue if company is too big
    if n_employees == "missing" and n_sales == "missing":
        None
    elif (n_employees == "missing" and float(n_sales.replace(",", "")) >= 40) or (
            n_sales == "missing" and int(n_employees.replace(",", "")) >= 250) or (
            n_employees != "missing" and n_sales != "missing" and float(n_sales.replace(",", "")) >= 40 and int(
        n_employees.replace(",", "")) >= 250):
        continue

    comp_reviews = df.loc[df['Unternehmen'] == old_name]

    years = get_dates(comp_reviews["Datum"])
    comp_reviews = comp_reviews.assign(Year=years)

    # extract first and last timestamps of Series
    last_timestamp, first_timestamp = get_outter_timestamps(comp_reviews)
    if str(first_timestamp) == 'nan' and str(last_timestamp) == 'nan':
        continue

    new_company.append(old_name)
    new_company.append(str(first_timestamp))
    new_company.append(str(last_timestamp))

    new_company.append(plz)
    new_company.append(location)
    new_company_list.append(new_company)

    index+=1

with open('company_timestamps.json', 'w') as f:
    json.dump(new_company_list, f)