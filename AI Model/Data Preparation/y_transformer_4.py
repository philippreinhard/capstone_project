########################################################################################################################
# Use this script to bin and export the new y and additionally export the corresponding label dictionary
# ATTENTION: Use y_transformer_visualized.py to find the perfect class edges by creating different distributions
import json
import numpy as np
import os,glob

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

def calculate_edges(bin_number, list):
    bin_width = round(len(list) / bin_number, 0)
    x = 1
    edges = [-np.inf]
    while x <= len(list):
        if x % bin_width == 0:
            edges.append(list[x - 1])
        x += 1
    edges.append(+np.inf)
    return edges

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

# print(calculate_edges(6))

# 4 equal bins



for filename in glob.glob(os.path.join(folder_path, '*.npy')):
    if filename.startswith('output\Y'):
        print(filename)
        single_filename = (filename[7:])[:-4]

        y_path = 'output/' + single_filename + '.npy'
        Y = np.load(y_path, allow_pickle=True)
        Y = Y.astype('float64')

        Y = np.sort(Y)

        edges_4 = calculate_edges(4, Y)
        Y_new = np.array(binning_y(edges_4, Y), dtype=int)
        Y_label_dic = produce_label_dic(edges_4)
        print(Y_new)

        # Export numpy and dictionary
        number_of_classes = len(edges_4)-1
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
