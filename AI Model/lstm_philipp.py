
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

np.random.seed(7)

X = np.load('Data Preparation\output\X.npy', allow_pickle=True)
Y = np.load('Data Preparation\output\Y.npy', allow_pickle=True)

print(Y)
X = X.astype('float64')
Y = Y.astype('float64')
print(X.shape)

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2)


input_dim = len(X_train[0][0])
timesteps = len(X_train[0])

input_shape = X_train[0].shape

class_weight = {0: 1,
                1: 150}

print(X_train[0].shape)
# model definition
model = Sequential()
model.add(LSTM(100, input_shape= input_shape))
model.add(Dense(1, activation='sigmoid'))
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

model.fit(X_train, Y_train, validation_data=(X_test, Y_test), epochs=5, batch_size=32, class_weight = class_weight)
print(model.summary())
# Final evaluation of the model
scores = model.evaluate(X_test, Y_test, verbose=0)
print("Accuracy: %.2f%%" % (scores[1]*100))

predictions = model.predict_classes(X_test)

classification_report = classification_report(Y_test, predictions)
print(classification_report)
