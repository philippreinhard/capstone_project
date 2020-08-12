import numpy as np
import matplotlib.pyplot as plt
import sys

# This script transforms the continuous references y into a categories in order to apply classification algorithms
# Use this script to find the perfect class edges by creating different distributions
# ATTENTION: Use the y_transformer.py to bin your data and export a new numpy array Y

# define the filename
filename = 'Y_10_3_abs_abs'

y_path = 'output/' + filename + '.npy'
Y = np.load(y_path, allow_pickle=True)
Y = Y.astype('float64')
# print(Y)

########################################################################################################################
# Binning by predefined (manually initialized) edges and labels
# Options and examples
# bins = [-np.inf, -0.10, -0.05, 0, 0.05, 0.10, +np.inf]
# bins = [-np.inf, -0.30, -0.20, -0.10, 0, 0.10, 0.20, 0.30, +np.inf]
# bins = [-np.inf, -0.20, -0.10, -0.05, 0, 0.05, 0.10, 0.20, +np.inf]
# bins = [-np.inf, -0.20, -0.15, -0.10, -0.05, 0, 0.05, 0.10, 0.15, 0.20, +np.inf]
# bins = [-np.inf, -0.40, -0.20, -0.10, -0.05, 0, 0.05, 0.10, 0.20, 0.40, + np.inf]
bins_2 = [-np.inf, 0, +np.inf]
bins_4 = [-np.inf, -0.10, 0, 0.10, +np.inf]
bins_5 = [-np.inf, -0.10, -0.02, 0.02, 0.10, +np.inf]
bins_6 = [-np.inf, -0.15, -0.05, 0, 0.05, 0.15, +np.inf]
bins_8 = [-np.inf, -0.20, -0.10, -0.05, 0, 0.05, 0.10, 0.20, +np.inf]


# For 2 classes: labels = ['risk\n(... -> 0)', 'no risk\n(0 -> ...)']
# For 4 classes: labels = ['high risk\n(...-> -0.10)', 'low risk\n(-0.10 -> 0)', 'no risk\n(0 -> 0.10)', 'positive\n(0.10 -> ...)']
# For 6 classes: labels = ['high risk', 'medium risk', 'low risk', 'no risk', 'positive', 'extremly positive']
# For 8 classes: labels = ['escalating', 'high risk', 'medium risk', 'low risk', 'no risk', 'positive', 'high positive', 'extreme positive']
# For 10 classes: labels = ['insolvency' ,'escalating', 'high risk', 'medium risk', 'low risk', 'no risk', 'positive', 'high positive', 'extreme positive', 'rocking']
labels_2 = ['risk\n(... -> 0)', 'no risk\n(0 -> ...)']
labels_4 = ['high risk\n(...-> -0.10)', 'low risk\n(-0.10 -> 0)', 'no risk\n(0 -> 0.10)', 'positive\n(0.10 -> ...)']
labels_5 = ['high risk\n(...-> -0.10)', 'low risk\n(-0.10 -> -0.02', 'no risk\n(-0.02 -> 0.02)', 'positive\n(0.02 -> 0.10)', 'positive\n(0.10 -> ...)']
labels_6 = ['high risk\n(...-> -0.15)', 'medium risk\n(-0.15 -> -0,05)', 'low risk\n(-0.05 -> 0)',
            'no risk\n(0 -> 0.05)', 'positive\n(0.05 -> 0.15)', 'extremly positive\n(0.15 -> ...)']
labels_8 = ['escalating\n(...-> -0.20)', 'high risk\n(-0.20 -> -0.10)', 'medium risk\n(-0.10 -> -0.05)',
            'low risk\n(-0.05 -> 0)', 'no risk\n(0 -> 0.05)', 'positive\n(0.05 -> 0.10)',
            'high positive\n(0.10 -> 0.20)', 'extreme positive\n(0.20 -> ...)']


# Function: Binning the y values based on the bin bin size
# Create a set of bins as the input for the classification problem
# bins: determines the edges of the classes
def binning_y(bins_definition):
    # Initialize bins
    bin_indices = np.digitize(Y, bins_definition)
    # print(bin_indices)
    return bin_indices


# Calculate the bin size respectively the counts of each bin/class
# Bins_indices:  binned y input
# Labels_for_bin:  labels for the bin indices
def calculate_bins_size(bins_indices, labels_for_bin):
    # Initialize parameters
    i = 1
    bin_counts = {}

    # Check bins and labels length
    if len(set(bins_indices)) != len(labels_for_bin):
        sys.exit('The lists bins and labels have too be of the same length')
    while i <= len(set(bins_indices)):
        counter = 0
        for bin_id in bins_indices:
            if i == bin_id:
                counter += 1
        bin_counts.update({labels_for_bin[i - 1]: counter})
        i += 1
    # print(bin_counts)
    return bin_counts


# Visualize bin size in a categorical plot
def plot_bin_counts(bin_dic):
    names = [*bin_dic]
    values = list(bin_dic.values())
    plt.figure(figsize=(9, 3))
    plt.bar(names, values)
    # plt.suptitle('Categorical Plotting')
    plt.xticks(rotation=45)
    plt.show()


counts_bins_2 = calculate_bins_size(binning_y(bins_2), labels_2)
counts_bins_4 = calculate_bins_size(binning_y(bins_4), labels_4)
counts_bins_5 = calculate_bins_size(binning_y(bins_5), labels_5)
counts_bins_6 = calculate_bins_size(binning_y(bins_6), labels_6)
counts_bins_8 = calculate_bins_size(binning_y(bins_8), labels_8)
# counts_bins_10 = calculate_bins_size(binning_y(bins_10), labels_10)
plot_bin_counts(counts_bins_2)
plot_bin_counts(counts_bins_4)
plot_bin_counts(counts_bins_5)
plot_bin_counts(counts_bins_6)
plot_bin_counts(counts_bins_8)
# plot_bin_counts(counts_bins_10)

########################################################################################################################
# Calculate equally great bins starting from -inf
# Calculate the edges
Z = np.sort(Y)


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


def produce_labels(calculated_edges):
    z = 1
    edges_labels = []
    while z < len(calculated_edges):
        label = str('' + str(round(calculated_edges[z - 1], 2)) + ' -> ' + str(round(calculated_edges[z], 2)))
        z += 1
        edges_labels.append(label)
    return edges_labels


# print(calculate_edges(6))

# 6 equal bins
edges_6 = calculate_edges(6, Z)
# print(edges_6)
# print(produce_labels(edges_6))
counts_bins_equal_6 = calculate_bins_size(binning_y(edges_6), produce_labels(edges_6))
plot_bin_counts(counts_bins_equal_6)

# 8 equal bins
edges_8 = calculate_edges(8, Z)
counts_bins_equal_8 = calculate_bins_size(binning_y(edges_8), produce_labels(edges_8))
plot_bin_counts(counts_bins_equal_8)

########################################################################################################################
# Create equally sized bins from -inf to 0 and from 0 to +inf
# At first separate the y into negative and positive samples
X_positive = []
X_negative = []

for x in Z:
    if x >= 0:
        X_positive.append(x)
    else:
        X_negative.append(x)

print('Number of negative values: ', len(X_negative))
print('Number of positive values: ', len(X_positive))


# number of bins one one side is "bin_number - 1"
def calculate_zero_based_edges(bin_number, list):
    bin_width = round(len(list) / (bin_number-1), 0)
    edges = []
    if list[0] < 0:
        x = 1
        edges.append(-np.inf)
        while x <= len(list)-2:
            if x % bin_width == 0:
                edges.append(list[x - 1])
            x += 1
        edges.append(0)
    else:
        x = 1
        edges.append(0)
        while x <= len(list)-1:
            if x % bin_width == 0:
                edges.append(list[x - 1])
            x += 1
        edges.append(+np.inf)
    return edges


print(calculate_zero_based_edges(4, X_negative))
print(calculate_zero_based_edges(4, X_positive))

around_zero_edges = calculate_zero_based_edges(4, X_negative) +  calculate_zero_based_edges(4, X_positive)[1:]

print(around_zero_edges)
counts_bins_zero_edges = calculate_bins_size(binning_y(around_zero_edges), produce_labels(around_zero_edges))
plot_bin_counts(counts_bins_zero_edges)
