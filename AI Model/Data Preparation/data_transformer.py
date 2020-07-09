import json
import numpy as np
import pandas as pd
from sys import *
import os

data_path = "model_data/"
pd.set_option('display.width', 100)
pd.set_option('display.max_columns', 20)

print("Initializing...")

with open(data_path + 'new_company_attributes_merged.json', 'r') as file:
    company_list = json.load(file)

# remove duplicates in company_list
insolvencies = 0
company_list_unique = []
for company in company_list:
    if company[7] == int(1):
        insolvencies+=1
    if company in company_list_unique:
        continue;
    else:
        company_list_unique.append(company)
company_list = company_list_unique
#print(insolvencies)

df = pd.read_csv(data_path + "reviews_merged.csv")
df.head()
df = df[["Unternehmen", "Datum", "ReviewRating", "Arbeitsatmosphäre_s", "Image_s", "Work-Life-Balance_s",
         "Karriere/Weiterbildung_s", "Gehalt/Sozialleistungen_s", "Umwelt-/Sozialbewusstsein_s",
         "Kollegenzusammenhalt_s", "Umgang mit älteren Kollegen_s", "Vorgesetztenverhalten_s", "Arbeitsbedingungen_s",
         "Kommunikation_s", "Gleichberechtigung_s", "Interessante Aufgaben_s"]]

# ------------------------ PARAMETERS ------------------------------#
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!PLEASE CHANGE AND PLAY WITH THESE PARAMETERS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# minimum amount of reviews per company
min_reviews = 5

# amount of years to be returned, counting from year of most recent review. This will obviously return twice as
# many half_years. This is required so that the samples for the AI model have constant length.
# Beware: return_years should not be bigger than continuity, if you wish to ensure continuity in the samples
return_years = 3

# choose how many continuous years of at least 1 review per year the samples require, counting from most recent year
# To avoid the continuity check, set continuity to -1
continuity = -1

# calc_arg specifies the resulting calculation that is returned in the output file.
# 'prior': calculates the differences of the moving average score to the score the half_year before
# 'first': calculates the differences of the moving average score to the first considered half_year score
#  'abs' : returns not the difference between moving average scores, but the scores themselves
calc_arg = 'abs'

# this boolean decides whether to drop the "Category" column in the ouput, which contains the names of the individual scores, like
# Arbeitsatmosphäre etc. If you chose False, you will have to remove them manually later on.
rem_category = True


# ------------------ MEHTOD DECLARATION ------------------------#
def get_dates(dates):
    # takes the timestamps and transforms them into half years

    years = []
    half_years = []
    for date in dates:
        year, month = date.split("-")[:2]
        if int(month) in range(1, 7):
            half_year = int(year)
        else:
            half_year = int(year) + 0.5

        half_years.append(half_year)
        years.append(int(year))
    return years, half_years


def get_outter_timestamps(comp_reviews):
    # get largest and smallest half years of the datasample

    max_timestamp = comp_reviews["HalfYear"].max()
    min_timestamp = comp_reviews["HalfYear"].min()

    # we do not consider 2020, so reduce it to 2019
    if max_timestamp >= 2020:
        max_timestamp = 2019.5

    if min_timestamp >= 2020:
        min_timestamp = 2019.5
    # print(max_timestamp, min_timestamp)
    # print(max_timestamp-min_timestamp)
    return max_timestamp, min_timestamp


def create_half_yearly_range(last_timestamp, first_timestamp):
    # create a list of half years

    stamp = first_timestamp
    stamps = []

    # insert first stamp to list already
    stamps.append(stamp)
    # increase timestamp by 0.5 in every iteration until it equals the last stamp
    while stamp != last_timestamp:
        stamp += 0.5;
        stamps.append(stamp)

    return stamps


def calculate_average(comp_reviews, col, half_year, last_weight, last_avg):
    # make all years to ints
    comp_reviews["HalfYear"] = comp_reviews["HalfYear"].apply(lambda x: float(x))

    # find values in the current ratings column where half_year is the currently looked at half_year
    values = comp_reviews[col].loc[comp_reviews['HalfYear'] == half_year]

    values2 = []

    # replace decimal seperator "," with "."
    for value in values:
        value2 = value
        try:
            value2 = float(value.replace(",", "."))
        except:
            pass
        values2.append(value2)
    values = pd.Series(values2)

    #  calculate individual weight and average of this half year alone
    ind_weight = values.size
    ind_average = values.mean(skipna=True)

    # if individual average is NaN
    if not isinstance(ind_average, np.float64):
        return last_avg, last_weight

    # if this is the first year or the previous year still doesnt have an average
    if last_avg == -1:
        return ind_average, ind_weight
    else:
        # calculate the moving average of the current year, taking into account all previous years and weighing them
        # according to their number of reviews
        average = (ind_average * ind_weight + last_avg * last_weight) / (ind_weight + last_weight)
        return average, (ind_weight + last_weight)


def calculate_half_yearly_averages(comp_reviews, last_timestamp, first_timestamp):
    # create a list of half_years according to the smallest and largest timestamps
    half_years = create_half_yearly_range(last_timestamp, first_timestamp)

    timeseries = []
    # iterate over columns
    for col in comp_reviews.drop(["Unternehmen", "Year", "HalfYear"], axis=1).columns:
        # initialize average and weight, weight is used to kep track of the number of reviews throughout the years,
        # is needed for moving average
        average = -1
        weight = 0

        averages = []

        # insert Name of column for understandability
        averages.append(col)
        # iterate over the half_years in the half years list
        for half_year in half_years:
            # calculate moving average for the specific half year
            average, weight = calculate_average(comp_reviews, col, half_year, weight, average)
            averages.append(average)
        timeseries.append(averages)
    # had to insert some bullshit name so that size of df matches the size of the half_years for column names
    half_years.insert(0, "Category")
    df = pd.DataFrame(timeseries, columns=half_years)
    return df


def check_data_continuity(comp_reviews, last_timestamp, first_timestamp, continuity_required):
    # make years to string to be comparable with years in Series, this is bullshit
    comp_reviews["HalfYear"] = comp_reviews["HalfYear"].apply(lambda x: str(x))

    year_range = int(last_timestamp) - int(first_timestamp) + 1
    # iterate backwards over required years
    for index in reversed(range(0, year_range)):
        year = int(first_timestamp) + index
        # if continuity is 0, we have reached enough continuous years and can return True
        if continuity_required == 0:
            return True
        # if sample is still continuous, subract -1 from continuity counter
        if year in comp_reviews["Year"].values:
            continuity_required -= 1
        else:
            return False


def handle_data(comp_reviews, continuity):
    # split datum timestamp into the relevant properties
    years, half_years = get_dates(comp_reviews["Datum"])
    comp_reviews = comp_reviews.assign(HalfYear=half_years, Year=years)
    comp_reviews = comp_reviews.drop('Datum', axis=1)

    # extract first and last timestamps of Series
    last_timestamp, first_timestamp = get_outter_timestamps(comp_reviews)

    # check if company reviews are continuous for the last X years, if continuity is wished for
    if continuity != -1:
        # if not continuous in regard to the requirement, return empty dataframe to signal ineligibility of company
        if not check_data_continuity(comp_reviews, last_timestamp, first_timestamp, continuity):
            return pd.DataFrame()

    return calculate_half_yearly_averages(comp_reviews, last_timestamp, first_timestamp)


def calculate_differences_to_first(df):
    # create new list that will later be the input for the dataframe
    new_df_list = []
    # for each score category
    for index, row in df.iterrows():
        new_elems = []
        # declare first elem, so that all other elements can subtract it
        first_elem = row[0]
        # if first_elem does not have an actual score, first elem should be 0 for calculation purposes
        if first_elem == -1:
            first_elem = 0
        # iterate through every value
        for elem in row:
            new_elem = elem - first_elem
            new_elems.append(new_elem)
        new_df_list.append(new_elems)
    new_df = pd.DataFrame(new_df_list, columns=df.columns)
    return new_df


def calculate_differences_to_prior(df):
    # create new list that will later be the input for the dataframe
    new_df_list = []
    # for each score category
    for i, row in df.iterrows():
        new_elems = []
        # first element is the prior to itself TODO: check if the actual prior can be taken, and use that instead
        prior_elem = row[0]

        # for each value in a rating row, calculate difference between element and prior element
        for elem in row:
            # if prior element doesnt have an average due to lack of data, new_elem should be considered
            if prior_elem == -1:
                new_elem = 0
            else:
                new_elem = elem - prior_elem
            new_elems.append(new_elem)
            prior_elem = elem

        new_df_list.append(new_elems)
    new_df = pd.DataFrame(new_df_list, columns=df.columns)
    return new_df


def return_specified_years(df, return_years, calc_arg):
    # check if there are enough years to be displayed. If not, exit by returning empty dataframe
    if (df.columns.size - 1 < 2 * return_years):
        return pd.DataFrame()

    # select the (2*return_years) last columns of the dataframe (each column is a half_year
    df1 = df.iloc[:, -(2 * return_years):]

    # forward to the correct method
    if calc_arg == 'abs':
        df2 = df1
    if calc_arg == 'prior':
        df2 = calculate_differences_to_prior(df1)
    if calc_arg == 'first':
        df2 = calculate_differences_to_first(df1)

    # insert category names in first column, might be dropped later, depending on rem_category
    df2.insert(0, "Category", df["Category"])
    return df2


# --------------------------------------------------------------#


# list for final data entries [X,y]
X = []
Y = []
print("Running script with continuity = " + str(continuity) + " and return_years = " + str(
    return_years) + ". Please wait.")

# iterate companies
index = 0
for company in company_list[:]:
    if (index % 100 == 0):
        print(str(index) + "/" + str(len(company_list)))
    index+=1
    # get parameters from attribute list
    old_name = company[0]
    n_employees = company[2]
    n_sales = company[3]
    insolvency = company[7]
    if insolvency == -1 or insolvency == "":
        continue

    # filter big companies, continue if company is too big
    if n_employees == "missing" and n_sales == "missing":
        None
    elif (n_employees == "missing" and float(n_sales.replace(",", "")) >= 40) or (
            n_sales == "missing" and int(n_employees.replace(",", "")) >= 250) or (
            n_employees != "missing" and n_sales != "missing" and float(n_sales.replace(",", "")) >= 40 and int(
        n_employees.replace(",", "")) >= 250):
        continue

    # get all reviews where company name matches company
    comp_reviews = df.loc[df['Unternehmen'] == old_name]

    # print(old_name)
    # print(len(comp_reviews))

    # check if company has enough reviews
    if len(comp_reviews) < min_reviews:
        continue

    # calculate moving averages and checking continuity requirement
    result = handle_data(comp_reviews, continuity)
    # if company does not contain the amount of continuous review years from last timestamp
    if result.empty:
        # print("continuity failed")
        continue

    # take moving averages and calculate half_yearly differences
    result2 = return_specified_years(result, return_years, calc_arg)
    # if company does not contain return_years years
    if result2.empty:
        # print("return_years failed")
        continue
    # remove Category column, if True
    if rem_category:
        result2 = result2.drop("Category", axis=1)
    columns = list(result2.columns)
    x = result2.to_numpy(dtype=float)

    #swap axis of array
    x = np.swapaxes(x, 0,1)
    y = insolvency


    X.append(x)
    Y.append(y)

    Xnp = np.array(X)
    Ynp = np.array(Y)


print(Xnp.shape)
print(Ynp.shape)

print("Done!")
print("Your dataset contains " + str(Xnp.shape[0]) + " samples, of which " + str(np.count_nonzero(Ynp)) + " are bankrupt.")
np.save('output/X.npy', Xnp, allow_pickle=True)
np.save('output/Y.npy', Ynp, allow_pickle=True)
