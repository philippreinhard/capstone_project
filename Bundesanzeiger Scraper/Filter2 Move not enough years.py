
import os
import time
import re  # regex

start_time = time.time()

# get list of all files directly residing in folder 'scraped_data'
document_list = []
for root, dirs, files in os.walk('scraped_data'):
    document_list.extend(files)
    break

count_of_documentlist = len(document_list)
count_of_htmls = len([item for item in document_list if item.endswith('.html')])

overall_counter = 1

cwd = os.getcwd()
basepath_from = os.path.join(cwd, 'scraped_data')
basepath_to = os.path.join(cwd, 'scraped_data', 'filter2_not_enough_years')
counter = 0

for item in document_list:
    if document_list.index(item) < 1000000:  # for manually limiting to first X files

        if document_list.index(item) % 100 == 0:  # status every 100 files
            print("> scanning document:", overall_counter, "/", count_of_documentlist, "--", item)

        if overall_counter < count_of_documentlist:
            overall_counter = overall_counter + 1

        if item.endswith('.html'):
            trimmed_item = item[0:-16]
            r = re.compile(re.escape(trimmed_item) + r'_\d\d\.\d\d\.\d{4}\.html')

            matchlist = list(filter(r.match, document_list))
            # print("> scanning document:", overall_counter, "/", count_of_documentlist, "--", item)
            # print(len(matchlist), 'matches:', matchlist)

            if len(matchlist) < 3:
                try:
                    filename_from = os.path.join(basepath_from, item)
                    filename_to = os.path.join(basepath_to, item)
                    os.rename(filename_from, filename_to)
                    print('> moved', item, 'because it had only', len(matchlist), 'files')
                    counter += 1
                except Exception as e:
                    print('Exception while moving file:', item, repr(e))

            # break
        else:
            pass

    else:
        break

print('Done! Moved', counter, 'items')
print('--- %s seconds ---' % (time.time() - start_time))
