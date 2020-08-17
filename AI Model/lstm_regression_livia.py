
import numpy as np
from math import sqrt
import sys
from matplotlib import pyplot
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import LSTM
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
np.set_printoptions(threshold=sys.maxsize)
# fix random seed for reproducibility

np.random.seed(6)

X = np.load('Data Preparation\output\X_5_5_first_abs.npy', allow_pickle=True)
Y = np.load('Data Preparation\output\Y_5_5_first_abs.npy', allow_pickle=True)

#print(X[0])
#print(Y)

# Plot
'''names = ["Review", "Arb", "Image", "Work", "Karriere", "Gehalt", "Umwelt", "Kollegen", "Umgang", "Vorgesetzte",
          "Bedingungen", "Kommunikation", "Gleichberechtigung", "Interessante"]
i = 1
# plot each column
pyplot.figure()
for group in groups:
	pyplot.subplot(len(groups), 1, i)
	pyplot.plot(values[:, group])
	pyplot.title(names, y=0.5, loc='right')
	i += 1
pyplot.show()'''

# Prepare

X = X.astype('float64')
Y = Y.astype('float64')

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.1)


input_dim = len(X_train[0][0])  # 14
timesteps = len(X_train[0])

input_shape = X_train[0].shape

print(X_train[0].shape)
# model definition
model = Sequential()
model.add(LSTM(70, input_shape=input_shape))
#model.add(Dropout(0.2))
model.add(Dense(1))
model.compile(loss='mae', optimizer='adam')

history = model.fit(X_train, Y_train, validation_data=(X_test, Y_test), epochs=200, batch_size=32, verbose=2)
print(model.summary())
# plot history
pyplot.plot(history.history['loss'], label='train')
pyplot.plot(history.history['val_loss'], label='test')
pyplot.legend()
pyplot.show()

# Predict
predictions = model.predict(X_test)

# calculate RMSE & r2
rmse = sqrt(mean_squared_error(Y_test, predictions))
print('Test RMSE: %.3f' % rmse)
r2 = r2_score(Y_test, predictions)
print('Test R^2: %.3f' % r2)

#print(predictions)
pyplot.plot(predictions)
pyplot.plot(Y_test)
pyplot.show()
#print(Y_test)
#pyplot.plot(Y_test)
#pyplot.show()

# rescale needed?
'''test_X = test_X.reshape((test_X.shape[0], n_hours*n_features))
# invert scaling for forecast
inv_yhat = concatenate((yhat, test_X[:, -7:]), axis=1)
inv_yhat = scaler.inverse_transform(inv_yhat)
inv_yhat = inv_yhat[:,0]
# invert scaling for actual
test_y = test_y.reshape((len(test_y), 1))
inv_y = concatenate((test_y, test_X[:, -7:]), axis=1)
inv_y = scaler.inverse_transform(inv_y)
inv_y = inv_y[:,0]'''

'''# Final evaluation of the model
scores = model.evaluate(X_test, Y_test, verbose=0)
print("Accuracy: %.2f%%" % (scores[1]*100))'''

