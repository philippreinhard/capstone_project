import json
import numpy as np
import pandas as pd
import math
from sys import *
import os

data_path = "model_data/"
pd.set_option('display.width', 100)
pd.set_option('display.max_columns', 20)

print("Initializing...")

with open(data_path + 'new_company_attributes_merged.json', 'r') as file:
    company_attribute_list = json.load(file)

company_bundesanzeiger_entries = pd.read_csv(data_path + 'company_attributes_12_08_2020.csv', sep=";")

# remove duplicates in company_list
insolvencies = 0
company_list_unique = []
for company in company_attribute_list:
    if company in company_list_unique:
        continue
    else:
        company_list_unique.append(company)
company_attribute_list = company_list_unique
# print(insolvencies)

company_reviews = pd.read_csv(data_path + "reviews_merged_clean_05_08_2020.csv")
company_reviews.head()
company_reviews = company_reviews[
    ["Unternehmen", "Datum", "ReviewRating", "Arbeitsatmosphäre_s", "Image_s", "Work-Life-Balance_s",
     "Karriere/Weiterbildung_s", "Gehalt/Sozialleistungen_s", "Umwelt-/Sozialbewusstsein_s",
     "Kollegenzusammenhalt_s", "Umgang mit älteren Kollegen_s", "Vorgesetztenverhalten_s", "Arbeitsbedingungen_s",
     "Kommunikation_s", "Gleichberechtigung_s", "Interessante Aufgaben_s"]]

# ------------------------ PARAMETERS ------------------------------#
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!PLEASE CHANGE AND PLAY WITH THESE PARAMETERS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# minimum amount of reviews per company (standard = 5)
min_reviews = 10

# amount of years to be observed.  This is required so that the samples for the AI model have constant length.
# By specifying observed_years = n, the script will return n-1 differences between the years.
observed_years = 5


# calc_arg_reviews specifies the resulting calculation of the differences that is returned in the output file.
# 'prior': calculates the differences of the moving average score to the score the year before
# 'first': calculates the differences of the moving average score to the first considered year score
#  'abs' : returns not the difference between moving average scores, but the scores themselves
calc_arg_reviews = 'abs'

#  calc_arg_entries specifies the resulting calculation of the EK-Quote in the output file.
# 'abs': calculates the difference in "Prozentpunkten" between the EKQ of two years
# 'rel': calculates the percental difference between the EKQ of two years. Please note the difference to "abs".
calc_arg_entries = 'abs'

# this boolean decides whether to drop the "Category" column in the ouput, which contains the names of the individual scores, like
# Arbeitsatmosphäre etc. If you chose False, you will have to remove them manually later on. This has no effect on the
# calculations
rem_category = True


# ------------------ METHOD DECLARATION ------------------------#
# returns a list of all years that occur in the comp_reviews dataframe for one company
def get_all_review_years(comp_reviews):
    years = set()
    for date in comp_reviews["Datum"]:
        year, month = date.split("-")[:2]
        years.add(year)
    return [int(i) for i in sorted(years)]

# returns a list of all years that occur in the comp_entries dataframe for one company
def get_all_entry_years(comp_entries):
    years = set()
    for date in comp_entries["JA_von"]:
        if isinstance(date, str):
            day, month, year = date.split(".")
        else:
            continue
        years.add(year)
    return [int(i) for i in sorted(years)]

# figures out the years that are eligible to become a datapoint
def get_eligible_years(review_years, entry_years, observed_years, continuity, use_prior):
    possible_years = []
    if use_prior:
        observed_years+=1


    for entry_year in entry_years:

        do_append = True
        # check for successor entry year
        if not entry_year + 1 in entry_years:
            continue

        # check if continuity is required throughout years
        if continuity:

            for i in range(0, observed_years):
                if (entry_year - i in review_years):
                    pass
                else:
                    do_append = False
                    break
            if do_append:
                possible_years.append(entry_year)

        ## else, if continuity is not required, just check for minimum year
        else:
            if min(review_years) <= entry_year - observed_years+1 and entry_year in review_years:
                possible_years.append(entry_year)

    return possible_years

# creates a dataframe with all the averages for all occuring years
def create_review_space(comp_reviews):

    # split datum timestamp into the relevant properties
    years, half_years = get_review_dates(comp_reviews["Datum"])
    comp_reviews = comp_reviews.assign(HalfYear=half_years, Year=years)
    comp_reviews = comp_reviews.drop('Datum', axis=1)

    # extract first and last timestamps of Series
    last_timestamp, first_timestamp = get_outter_timestamps(comp_reviews)

    return calculate_yearly_averages(comp_reviews, first_timestamp, last_timestamp)


# calculates averages for a range of years
def calculate_yearly_averages(comp_reviews, first_year, last_year):
    # create a list of half_years according to the smallest and largest timestamps
    years = list(range(first_year, last_year+1))

    timeseries = []
    # iterate over columns (col is the name of each column)
    for col in comp_reviews.drop(["Unternehmen", "Year", "HalfYear"], axis=1).columns:
        # initialize average and weight, weight is used to kep track of the number of reviews throughout the years,
        # is needed for moving average
        average = -1
        weight = 0

        averages = []

        # insert Name of column for understandability
        averages.append(col)
        # iterate over the half_years in the half years list
        for year in years:
            # calculate moving average for the specific half year
            average, weight = calculate_average(comp_reviews, col, year, weight, average)
            averages.append(average)
        timeseries.append(averages)
    # had to insert some bullshit name so that size of df matches the size of the half_years for column names
    years.insert(0, "Category")
    df = pd.DataFrame(timeseries, columns=years)
    return df

# returns the unique years of company entries and throws out Jahresabschlüsse that have the same year
def get_entry_dates(comp_entries):
    temp_entries = pd.DataFrame(columns=comp_entries.columns)
    years = []
    for index,row in comp_entries.iterrows():
        #print(row.JA_von)
        if isinstance(row.JA_von, str):
            day, month, year = row.JA_von.split(".")
        else:
           continue
        year = int(year)
        if year in years:
            continue
        years.append(int(year))
        temp_entries = temp_entries.append(row)
    return years, temp_entries

# returns the EK-Quote Dataframe on a yearly basis
def create_eqk_space(comp_entries):
    # split datum timestamp into the relevant properties
    years, comp_entries = get_entry_dates(comp_entries)
    comp_entries = comp_entries.assign(Year = years)
    comp_entries = comp_entries[["Year", "EK-Quote"]]
    comp_entries = comp_entries.sort_values('Year')

    eqks = []
    for year in years:
        eqk = comp_entries["EK-Quote"].loc[comp_entries['Year'] == year].iloc[0]
        eqks.append(eqk)
    df = pd.DataFrame([eqks], columns=years)
    df = df.reindex(sorted(df.columns), axis=1)
    return df

# creates a datapoint based on an eligible year by forwarding the difference calculation for the reviews and calculating
# the EKQ diff
def create_datapoint(eligible_year, review_space, ekq_space, observed_years, use_prior, calc_arg_reviews, calc_arg_entries):
    # starts with calculation of review average differences
    first_year = eligible_year - observed_years + 1
    if use_prior:
        first_year = eligible_year - observed_years

    review_years = list(range(first_year, eligible_year+1))
    review_averages = review_space[review_years]

    # forward review average difference caluclation to the correct method
    if calc_arg_reviews == 'abs':
        review_average_differences = review_averages
    if calc_arg_reviews == 'prior':
        review_average_differences = calculate_differences_to_prior(review_averages)
    if calc_arg_reviews == 'first':
        review_average_differences = calculate_differences_to_first(review_averages)


    if use_prior:
        review_average_differences = review_average_differences.drop(review_average_differences.columns[0], axis=1)

    review_average_differences.insert(0, "Category", review_space["Category"])


    #from now on, diff of ekq calculation

    first_ekq = ekq_space[eligible_year][0]
    second_ekq = ekq_space[eligible_year+1][0]

    if calc_arg_entries == "abs":
        ekq_diff = second_ekq-first_ekq
    elif calc_arg_entries == "rel":
        ekq_diff = (second_ekq-first_ekq)/first_ekq

    return review_average_differences, ekq_diff


def calculate_differences_to_first(df):
    # create new list that will later be the input for the dataframe
    new_df_list = []
    # for each score category
    for index, row in df.iterrows():
        new_elems = []
        row = row.values
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
        # first element is the prior to itself
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

# currently unused
def return_specified_years(df, observed_years, calc_arg):
    # check if there are enough years to be displayed. If not, exit by returning empty dataframe
    if (df.columns.size - 1 < 2 * observed_years):
        return pd.DataFrame()

    # select the observed_years last columns of the dataframe (each column is a half_year)
    df1 = df.iloc[:, -(2 * observed_years):]

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


# takes the timestamps and transforms them into years
def get_review_dates(dates):

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


# get largest and smallest half years of the datasample
def get_outter_timestamps(comp_reviews):

    max_timestamp = comp_reviews["Year"].max()
    min_timestamp = comp_reviews["Year"].min()

    # we do not consider 2020, so reduce it to 2019
    if max_timestamp >= 2020:
        max_timestamp = 2019

    if min_timestamp >= 2020:
        min_timestamp = 2019

    return max_timestamp, min_timestamp

# currently unused
def create_half_yearly_range(last_timestamp, first_timestamp):
    # create a list of half years

    stamp = first_timestamp
    stamps = []

    # insert first stamp to list already
    stamps.append(stamp)
    # increase timestamp by 0.5 in every iteration until it equals the last stamp
    while stamp != last_timestamp:
        stamp += 0.5
        stamps.append(stamp)

    return stamps


# basic average calculation
def calculate_average(comp_reviews, col, year, last_weight, last_avg):
    # make all years to floats
    comp_reviews["Year"] = comp_reviews["Year"].apply(lambda x: float(x))

    # find values in the current ratings column where half_year is the currently looked at half_year
    values = comp_reviews[col].loc[comp_reviews['Year'] == year]

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

    #  calculate individual weight and average of this  year alone
    ind_weight = values.size
    ind_average = values.mean(skipna=True)


    # if individual average is NaN
    if np.isnan(ind_average):
        return last_avg, last_weight

    # if this is the first year or the previous year still doesnt have an average
    if last_avg == -1:
        return ind_average, ind_weight
    else:
        # calculate the moving average of the current year, taking into account all previous years and weighing them
        # according to their number of reviews
        average = (ind_average * ind_weight + last_avg * last_weight) / (ind_weight + last_weight)
        return average, (ind_weight + last_weight)


# currently unused
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


# --------------------------------------------------------------#

### DO NOT CHANGE THESE PARAMETERS ###
continuity = False
use_prior = True
observed_years = observed_years-1
# EXPLANATION: use_prior used to decide whether to use the year before the first year in our 3-year review window as an
# anchorpoint for our difference calculation. This is not required anymore because observed_years is now interpreted
# differently. continuity is not required checked for anymore.

# list for final data entries [X,y]
X = []
Y = []
print("Running script with observed_years = " + str(
    observed_years) + " This will return "+str(observed_years-1)+" differences. Please wait.")

# iterate companies via company attribute list (not eqk csv!)
index = 0

for company in company_attribute_list[:]:

    if (index % 100 == 0):
        print(str(index) + "/" + str(len(company_attribute_list)))
    index += 1
    # get parameters from attribute list
    old_name = company[0]
    n_employees = company[2]
    n_sales = company[3]
    insolvency = company[7]

    # filter big companies, continue if company is too big
    if n_employees == "missing" and n_sales == "missing":
        pass
    elif (n_employees == "missing" and float(n_sales.replace(",", "")) >= 40) or (
            n_sales == "missing" and int(n_employees.replace(",", "")) >= 250) or (
            n_employees != "missing" and n_sales != "missing" and float(n_sales.replace(",", "")) >= 40 and int(
        n_employees.replace(",", "")) >= 250):
        #print("Unternehmen zu groß")
        continue

    # get all reviews where company name matches company
    comp_reviews = company_reviews.loc[company_reviews['Unternehmen'] == old_name]

    # check if company has enough reviews
    if len(comp_reviews) < min_reviews:
        #print("Zu wenig Reviews")
        continue

    # get all Bundesanzeiger entries where company name matches company
    comp_entries = company_bundesanzeiger_entries.loc[
        company_bundesanzeiger_entries['Unternehmensname_given'] == old_name]

    # check if company has any bundesanzeiger entries
    if len(comp_entries) == 0:
        #print("Keine Bundesanzeiger Einträge")
        continue




    # calculate all yearly averages of a company
    review_space = create_review_space(comp_reviews)
    if review_space.empty:
        continue


    # create list of all EQKs of a company
    ekq_space = create_eqk_space(comp_entries)
    if ekq_space.empty:
        continue

    ### check which years are eligible to become a datapoint
    # get a list of all years that contain reviews
    review_years = get_all_review_years(comp_reviews)
    # get a list of all years that contain bundesanzeiger entries
    entry_years = get_all_entry_years(comp_entries)

    eligible_years = get_eligible_years(review_years, entry_years, observed_years, continuity, use_prior)
    #print(review_years)
    #print(entry_years)
    #print(eligible_years)
    # if list is empty
    if not eligible_years:
        continue


    for eligible_year in eligible_years:
        review,ekq = create_datapoint(eligible_year, review_space, ekq_space, observed_years, use_prior, calc_arg_reviews, calc_arg_entries)

        if np.isnan(ekq):
            continue
        # remove Category column, if True
        if rem_category:
            review = review.drop("Category", axis=1)
        columns = list(review.columns)
        x = review.to_numpy(dtype=float)

        # swap axis of array
        x = np.swapaxes(x, 0, 1)
        y = ekq

        X.append(x)
        Y.append(y)

Xnp = np.array(X)
Ynp = np.array(Y)

print(Xnp.shape)
print(Ynp.shape)

print("Done!")
print("Your dataset contains " + str(Xnp.shape[0]) + " samples.")
X_path = 'output/X_' + str(min_reviews) + '_' + str(observed_years) + '_' + calc_arg_reviews + '_' + calc_arg_entries
Y_path = 'output/Y_' + str(min_reviews) + '_' + str(observed_years) + '_' + calc_arg_reviews + '_' + calc_arg_entries
print(Y_path)
# Naming: X_<min_reviews>_<observed_years>_<calc_arg_reviews>_<calc_arg_entries>
# Hint: Observed years = Number of differences
np.save(X_path, Xnp, allow_pickle=True)
np.save(Y_path, Ynp, allow_pickle=True)

#np.save('output/X_.npy', Xnp, allow_pickle=True)
#np.save('output/Y.npy', Ynp, allow_pickle=True)
