
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from  sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix
np.random.seed(7)

X = np.load('output/X.npy', allow_pickle=True)
Y = np.load('output/Y.npy', allow_pickle=True)


X = X.astype('float64')
Y = Y.astype('float64')

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2)

nsamples, nx, ny = X_train.shape
d2_X_train = X_train.reshape((nsamples,nx*ny))
msamples, mx, my = X_test.shape
d2_X_test = X_test.reshape((msamples,mx*my))

print("d2_X_train and Y_train.shape = ", d2_X_train.shape, Y_train.shape)
print("d2_X_test and Y_test.shape = ", d2_X_test.shape, Y_test.shape)

plt.plot(d2_X_test,'b,', Y_test, 'r.')
plt.show()

svm = SVC(kernel="poly", C=1, gamma="auto")
svm.fit(d2_X_train ,Y_train)

Y_pred = svm.predict(d2_X_test)


print("confusion_matrix(Y_test, Y_pred):\n", confusion_matrix(Y_test, Y_pred))
print("classification_report(Y_test, Y_pred):\n", classification_report(Y_test, Y_pred))