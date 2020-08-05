
import numpy as np
import sys
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
from  sklearn.model_selection import train_test_split
np.set_printoptions(threshold=sys.maxsize)
# fix random seed for reproducibility

np.random.seed(6)

X = np.load('Data Preparation\output\X.npy', allow_pickle=True)
Y = np.load('Data Preparation\output\Y.npy', allow_pickle=True)


X = X.astype('float64')
Y = Y.astype('float64')

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.1)


input_dim = len(X_train[0][0])
timesteps = len(X_train[0])

input_shape = X_train[0].shape

class_weight = {0: 1,
                1: 50}

print(X_train[0].shape)
# model definition
model = Sequential()
model.add(LSTM(100, input_shape= input_shape))
model.add(Dense(1, activation='sigmoid'))
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

model.fit(X_train, Y_train, validation_data=(X_test, Y_test), epochs=4, batch_size=32, class_weight = class_weight)
print(model.summary())
# Final evaluation of the model
scores = model.evaluate(X_test, Y_test, verbose=0)
print("Accuracy: %.2f%%" % (scores[1]*100))

predictions = model.predict_classes(X_test)

cm = confusion_matrix(Y_test, predictions)
print(cm)
classification_report = classification_report(Y_test, predictions)
print(classification_report)

import seaborn as sn
import matplotlib.pyplot as plt
labels = ['0', '1']
plt.figure(figsize=(5,5))
ax= plt.subplot()
sn.set(font_scale=1.4)#for label size
sn.heatmap(cm, annot=True, ax = ax, annot_kws={"size": 7},cmap='Greens'); #annot=True to annotate cells

# labels, title and ticks
ax.set_xlabel('Predicted labels');
ax.set_ylabel('True labels');
ax.set_title('Confusion Matrix');
plt.xticks(rotation=45)
plt.yticks(rotation=0)
plt.show()

