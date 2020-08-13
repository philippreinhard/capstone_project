########################################################################################################################
# Use this script to bin and export the new y and additionally export the corresponding label dictionary
# ATTENTION: Use y_transformer_visualized.py to find the perfect class edges by creating different distributions
import json
import numpy as np
import os,glob

# Input from y_transformer_visualized.py:
bin_def_6 = [-np.inf, -0.15, -0.05, 0, 0.05, 0.15, +np.inf]
bin_def_5 = [-np.inf, -0.10, -0.02, 0.02, 0.10, +np.inf]
bin_def_3 = [-np.inf, -0.05, 0.05, +np.inf]

bin_defs = [bin_def_3, bin_def_5, bin_def_6]

folder_path = 'output/'

def binning_y(bins_definition,Y_input):
    # Initialize bins
    bin_indices = np.digitize(Y_input, bins_definition)
    # print(bin_indices)
    i=0
    bins = []
    while i < len(bin_indices):
        bins.append(bin_indices[i]-1)
        i += 1
    return bins


def produce_label_dic(calculated_edges):
    z = 1
    edges_labels = []
    while z < len(calculated_edges):
        label = str('' + str(round(calculated_edges[z - 1], 2)) + ' -> ' + str(round(calculated_edges[z], 2)))
        z += 1
        edges_labels.append(label)
    # print(edges_labels)
    label_dic = {}
    i = 0
    while i < len(edges_labels):
        label_dic.update({i: edges_labels[i]})
        i += 1
    # print(label_dic)
    return label_dic

for filename in glob.glob(os.path.join(folder_path, '*.npy')):
    if filename.startswith('output\Y'):
        print(filename)
        single_filename = (filename[7:])[:-4]
        print(single_filename)
        y_path = 'output/' + single_filename + '.npy'
        Y = np.load(y_path, allow_pickle=True)
        Y = Y.astype('float64')

        for defs in bin_defs:
            Y_new = np.array(binning_y(defs,Y), dtype=int)
            Y_label_dic = produce_label_dic(defs)
            print(Y_new)

            # Export numpy and dictionary
            number_of_classes = len(defs)-1
            y_path_categorized = 'output_categorized/' + single_filename + '_(' + str(number_of_classes) + ').npy'
            np.save(y_path_categorized, Y_new, allow_pickle=True)

'''
dic_path = 'output_categorized/y_dic_('+ str(number_of_classes) + ').json'
a_file = open(dic_path, "w")
json.dump(Y_label_dic, a_file)
a_file.close()

# How to load dictionary
a_file = open(dic_path, "r")
output = a_file.read()
print(output)
a_file.close()
'''
