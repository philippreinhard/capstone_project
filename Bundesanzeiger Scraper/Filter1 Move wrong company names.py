import os
import pandas as pd

# read input CSV
try:
    df = pd.read_csv('wrong company names analysis/files_to_be_moved.csv', header=0, names=['filenames'])
except Exception as e:
    print('An exception occured while reading the CSV:', repr(e))
    df = None
cwd = os.getcwd()
basepath_from = os.path.join(cwd, 'scraped_data')
basepath_to = os.path.join(cwd, 'scraped_data', 'filter1_wrong_filenames')
counter = 0

# iterate through DataFrame and move each file
if df is not None and isinstance(df, pd.DataFrame):
    for index, row in df.iterrows():
        # print(row[0])
        try:
            filename_from = os.path.join(basepath_from, row[0])
            filename_to = os.path.join(basepath_to, row[0])
            os.rename(filename_from, filename_to)
            print('> moved', row[0])
            counter += 1
        except Exception as e:
            print('Exception while moving file:', row[0], repr(e))

print('Done! Moved', counter, 'files.')

