import json
import csv

'''with open('kununu/reviews_Beratung_sorted.csv', 'r', newline='', encoding='utf-8') as f:
    theReader = csv.reader(f, delimiter=";")

    scoreSum = 0
    index = 0
    for row in theReader:
        if index != 0:
            scoreSum += float(row[4].replace(',', '.'))
        index += 1

    average = scoreSum / index

print("Durchschnittsscore gesamt: " + str(average))'''

review_counter = []
for i in range(2000):
    review_counter.append(0)

fiveAndHigher = 0
tenAndHigher = 0
scoreSum = 0

with open('kununu/new_company_attributes_Dienstleistungen_merged.json', 'r') as file:
    company_attributes = json.load(file)

for company_attribute in company_attributes:

    if company_attribute[7] == 1:

        print("Name: " + str(company_attribute[0]))

        with open('kununu/reviews_Dienst_sorted.csv', 'r', newline='', encoding='utf-8') as f:
            theReader = csv.reader(f, delimiter=";")

            counter = 0
            score = 0
            for row in theReader:
                if row[0] == company_attribute[0]:
                    counter += 1
                    score += float(row[4].replace(',', '.'))
                elif counter != 0:
                    if counter > 4:
                        fiveAndHigher += 1
                        if counter > 9:
                            tenAndHigher += 1
                    scoreSum += score / counter
                    old_counter = review_counter[counter]
                    old_counter += 1
                    review_counter[counter] = old_counter
                    break
        print("Anzahl Reviews: " + str(counter))
        scoreDurchschnitt = 0
        if counter != 0:
            scoreDurchschnitt = score/counter
        print("Scoredurchschnitt: " + str(scoreDurchschnitt))

theSum = 0
index = 0
amount = 0
for count in review_counter:
    theSum = theSum + count * index
    amount = amount + count
    index += 1

median = 0
median1 = 0
median2 = 0
middleAmount1 = 0
middleAmount2 = 0

if amount % 2 == 0:
    middleAmount1 = amount / 2
    amountCounter = 0
    for i in range(len(review_counter)):
        amountCounter += review_counter[i]
        if amountCounter >= middleAmount1:
            median = i
            break
else:
    middleAmount1 = (amount - 1) / 2
    middleAmount2 = (amount + 1) / 2
    amountCounter = 0
    for i in range(len(review_counter)):
        amountCounter += review_counter[i]
        if amountCounter >= middleAmount1 and median1 == 0:
            median1 = i
        if amountCounter >= middleAmount2:
            median2 = i
            break
    median = (median1 + median2) / 2

mean = theSum / amount
avgScore = scoreSum / amount

print("Anzahl Unternehmen: " + str(amount))
print(review_counter)
print("Durchschnitt: " + str(mean))
print("Median: " + str(median))
print("Anzahl Reviews 5 & höher: " + str(fiveAndHigher))
print("Anzahl Reviews 10 & höher: " + str(tenAndHigher))
print("Scoredurchschnitt: " + str(avgScore))
