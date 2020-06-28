import csv

review_counter = []
for i in range(2000):
    review_counter.append(0)

with open('reviews.csv', 'r', newline='') as f:

    theReader = csv.reader(f, delimiter=";")
    company = ""
    counter = 0

    for row in theReader:
        if row[0] == company:
            counter += 1
        else:
            if counter != 0:
                old_counter = review_counter[counter]
                old_counter += 1
                review_counter[counter] = old_counter
            company = row[0]
            counter = 1

sum = 0
index = 0
amount = 0
for count in review_counter:
    print(str(sum) + " + " + str(count) + " * " + str(index))
    sum = sum + count * index
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

mean = sum / amount

print(review_counter)
print("Durchschnitt: " + str(mean))
print("Median: " + str(median))



