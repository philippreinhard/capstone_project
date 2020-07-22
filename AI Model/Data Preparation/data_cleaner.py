import json
import numpy as np
import pandas as pd


## This script shows the companies sorted by reviews and can throw the ones with the most reviews out
data_path = "model_data/"


df = pd.read_csv(data_path + "reviews_merged.csv")
# df = df[["Unternehmen", "Datum", "ReviewRating","Arbeitsatmosphäre_s", "Image_s", "Work-Life-Balance_s", "Karriere/Weiterbildung_s", "Gehalt/Sozialleistungen_s","Umwelt-/Sozialbewusstsein_s","Kollegenzusammenhalt_s", "Umgang mit älteren Kollegen_s","Vorgesetztenverhalten_s","Arbeitsbedingungen_s","Kommunikation_s", "Gleichberechtigung_s", "Interessante Aufgaben_s"]]
pd.set_option('display.max_rows', 4000)
pd.set_option('display.max_colwidth', -1)
print(len(df["Unternehmen"].value_counts()[0:100000000]))
print(df["Unternehmen"].value_counts()[0:100])
elimlist = df["Unternehmen"].value_counts()[0:100].index.tolist()


#for elim in elimlist:
#    df = df[df.Unternehmen != elim]

print(len(df["Unternehmen"].value_counts()[0:10000]))
#df.to_csv(data_path+"reviews_merged_filtered.csv")