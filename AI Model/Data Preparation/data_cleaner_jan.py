
import pandas as pd


## This script shows the companies sorted by reviews and can throw the ones with the most reviews out
data_path = "model_data/"


df = pd.read_csv(data_path + "reviews_merged.csv")
new_df = df
# df = df[["Unternehmen", "Datum", "ReviewRating","Arbeitsatmosphäre_s", "Image_s", "Work-Life-Balance_s", "Karriere/Weiterbildung_s", "Gehalt/Sozialleistungen_s","Umwelt-/Sozialbewusstsein_s","Kollegenzusammenhalt_s", "Umgang mit älteren Kollegen_s","Vorgesetztenverhalten_s","Arbeitsbedingungen_s","Kommunikation_s", "Gleichberechtigung_s", "Interessante Aufgaben_s"]]
pd.set_option('display.max_rows', 4000)
pd.set_option('display.max_colwidth', -1)

new_df = new_df.set_index("Unternehmen")

print("test")
print(len(df["Unternehmen"].value_counts()[0:100000000]))
#print(df["Unternehmen"].value_counts()[0:100])
elimlist = df["Unternehmen"].value_counts()[0:49].index.tolist()
list= {"etventure GmbH", "tts GmbH", "Quadient", "ACP IT Solutions GmbH", "Allgeier IT Solutions GmbH", "Celonis SE", "cronos Unternehmensberatung GmbH", "Campana & Schott", "Worldline", "Bureau Veritas Germany", "CONET Technologies Holding GmbH", "Jung von Matt", "Buchbinder Rent-a-Car", "Interseroh", "Schwarz IT KG", "Studioline Photography",  "SIG Sales GmbH & Co. KG", "Berlin Brands Group", "Atlas Titan", "1st solution consulting gmbh", "Software AG Deutschland", "Kienbaum Consultants International", "Invitel GmbH"}
print(elimlist)
print(len(new_df.index))
for comp in elimlist:
    print("removed: "+comp)
    new_df = new_df.drop(comp, axis=0)

for comp in list:
    print("removed: "+comp)
    new_df = new_df.drop(comp, axis=0)

print(len(new_df.index))
print(new_df)
new_df = new_df.reset_index()
new_df = new_df.drop("Unnamed: 0", axis=1)
print(new_df)

new_df.to_csv("reviews_merged_clean.csv", index=False, encoding='utf8')

#for elim in elimlist:
#    df = df[df.Unternehmen != elim]

#print(len(df["Unternehmen"].value_counts()[0:10000]))
#df.to_csv(data_path+"reviews_merged_filtered.csv")