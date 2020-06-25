import json

### This method takes two input lists as produced by the DNB scrapers and merges them
### while overriding missing values
with open('input/input1.json', 'r') as input1:
    list1 = json.load(input1)

with open('input/input2.json', 'r') as input2:
    list2 = json.load(input2)

output_list = []


for company1 in list1:
    found = False
    print('Company1: ' + str(company1))
    for company2 in list2:
        if company1 == company2:
            print('Company2: ' +str(company2))
            output_list.append(company1)
            found = True
            break
        if company1[0] == company2[0]:
            temp_list = []
            temp_list.append(company1[0])

            if company1[1] == 'missing' and company2[1] != 'missing':
                temp_list.append(company2[1])
            else:
                temp_list.append(company1[1])

            if company1[2] == 'missing' and company2[2] != 'missing':
                temp_list.append(company2[2])
            else:
                temp_list.append(company1[2])

            if company1[3] == 'missing' and company2[3] != 'missing':
                temp_list.append(company2[3])
            else:
                temp_list.append(company1[3])

            if company1[4] == 'missing' and company2[4] != 'missing':
                temp_list.append(company2[4])
            else:
                temp_list.append(company1[4])

            if company1[5] == 'missing' and company2[5] != 'missing':
                temp_list.append(company2[5])
            else:
                temp_list.append(company1[5])
            print('TempCompany Output: ' +str(temp_list))
            output_list.append(temp_list)
            found = True

    ## list2 does not contain company from list1
    if not found:
        print('Not found in company2, adding to output:' + str(company1))
        output_list.append(company1)


## now add all elements that are only in list2 to the output list

def contains(alist, elem):
    for l in alist:
        if l[0] == elem[0]:
            return True
    return False


for company2 in list2:
    if not contains(output_list, company2):
        output_list.append(company2)
        print(company2)


with open('input/output.json', 'w') as f:
    json.dump(output_list, f)
