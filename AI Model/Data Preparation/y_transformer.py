########################################################################################################################
# Use this script to bin and export the new y and additionally export the corresponding label dictionary
# ATTENTION: Use y_transformer_visualized.py to find the perfect class edges by creating different distributions
import numpy as np

Y = np.load('output\Y.npy', allow_pickle=True)
Y = Y.astype('float64')

# Input from y_transformer_visualized.py:
bin_def = [-np.inf, -0.15, -0.05, 0, 0.05, 0.15, +np.inf]


def binning_y(bins_definition):
    # Initialize bins
    bin_indices = np.digitize(Y, bins_definition)
    # print(bin_indices)
    return bin_indices


def produce_label_dic(calculated_edges):
    z = 1
    edges_labels = []
    while z < len(calculated_edges):
        label = str('' + str(round(calculated_edges[z - 1], 2)) + ' -> ' + str(round(calculated_edges[z], 2)))
        z += 1
        edges_labels.append(label)
    #print(edges_labels)
    label_dic = {}
    i = 0
    while i < len(edges_labels):
        label_dic.update({i: edges_labels[i]})
        i += 1
    #print(label_dic)
    return label_dic


Y_new = np.array(binning_y(bin_def), dtype=int)
Y_label_dic = produce_label_dic(bin_def)


# Export numpy and dictionary
# np.save('output/Y_new.npy', Y_new, allow_pickle=True)
#a_file = open("data.json", "w")
#json.dump(Y_label_dic, a_file)
#a_file.close()

# How to load dictionary
#a_file = open("data.json", "r")
#output = a_file.read()
#print(output)
#a_file.close()
