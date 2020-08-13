
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn import svm
from sklearn import preprocessing
from sklearn.metrics import classification_report, confusion_matrix


np.random.seed(7)

y_filename = 'Y_5_4_first_abs'
print(y_filename[2:])
number_of_classes = 3

y_path = 'output_categorized/' + y_filename + '_(' + str(number_of_classes) + ').npy'
x_path = 'output/X_' + y_filename[2:] + '.npy'

X = np.load(x_path, allow_pickle=True)
Y = np.load(y_path, allow_pickle=True)


X = X.astype('float64')
Y = Y.astype('float64')

print(X.shape)

np.set_printoptions(threshold=np.inf)

def get_avg(a,b,c,j):
    avg=(a[j]+b[j]+c[j])/3
    return avg



new_X = np.zeros((np.size(X,0),14))
c=0
for comp in X:

    new_comp = np.zeros((14))
    for i in range(13):

        new_comp[i] = get_avg(comp[0], comp[1], comp[2], i)

    new_X[c] = new_comp
    c=c+1


X = new_X
print(X.shape)


X_train, X_test, Y_train, Y_test = train_test_split(X, Y, train_size=0.7, random_state=1, stratify=Y)

print(X_train.shape)
print(X_train[1])

print("start")


linear = svm.SVC(kernel='linear', C=1, decision_function_shape='ovo').fit(X_train, Y_train)
print("linear finished")
rbf = svm.SVC(kernel='rbf', gamma=1, C=1, decision_function_shape='ovo').fit(X_train, Y_train)
print("rbf finished")
poly = svm.SVC(kernel='poly', degree=3, C=1, decision_function_shape='ovo').fit(X_train, Y_train)
print("poly finished")
sig = svm.SVC(kernel='sigmoid', C=1, decision_function_shape='ovo').fit(X_train, Y_train)
print("sig finished")

titles = ['Linear kernel', 'RBF kernel', 'Sigmoid kernel', 'Polynomial kernel']


for i, clf in enumerate((linear, rbf, sig, poly)):

    Y_pred = clf.predict(X_test)

    print("File: " + y_filename + "(" + str(number_of_classes) +")")
    print(titles[i] + ": confusion_matrix(Y_test, Y_pred):\n", confusion_matrix(Y_test, Y_pred))
    print(titles[i] + ": classification_report(Y_test, Y_pred):\n", classification_report(Y_test, Y_pred))