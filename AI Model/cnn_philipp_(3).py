import numpy as np
import sys
from keras.models import Sequential
from keras.layers import Dense, Conv1D, Flatten, MaxPool1D, Dropout, Activation
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from imblearn.under_sampling import (RandomUnderSampler,
                                     ClusterCentroids,
                                     TomekLinks,
                                     NeighbourhoodCleaningRule,
                                     NearMiss)

epochs = 200
batch_size = 20

np.set_printoptions(threshold=sys.maxsize)
# fix random seed for reproducibility

np.random.seed(7)

# define filename
y_filename = 'Y_5_3_first_abs'

number_of_classes = 3

y_path = 'Data Preparation/output_categorized/' + y_filename + '_(' + str(number_of_classes) + ').npy'
x_path = 'Data Preparation/output/X_' + y_filename[2:] + '.npy'

X = np.load(x_path, allow_pickle=True)
Y = np.load(y_path, allow_pickle=True)

# X = np.load('Data Preparation\output\X.npy', allow_pickle=True)
# Y = np.load('Data Preparation\output\Y.npy', allow_pickle=True)

X = X.astype('float64')
Y = Y.astype('float64')

# TODO Reshape input
# orig_shape = X.shape
# arr = np.reshape(X, (X.shape[0], X.shape[1]))
# print(arr.shape)
# arr = np.reshape(arr, orig_shape)
# print(arr.shape)

# RandomUnderSampler
# sampler = RandomUnderSampler(random_state=0)
# X_rs, Y_rs = sampler.fit_sample(X, Y)
# print('Random undersampling {}'.format(Counter(y_rs)))
# plot_this(X_rs,y_rs,'Random undersampling')

print(X[0])
print(Y)

train_X, test_X, train_Y, test_Y = train_test_split(X, Y, train_size=0.7, random_state=1, stratify=Y)

# ClusterCentroids
# sampler = ClusterCentroids(ratio={1: 1000, 0: 65})
# X_rs, y_rs = sampler.fit_sample(X, y)
# print('Cluster centriods undersampling {}'.format(Counter(y_rs)))
# plot_this(X_rs,y_rs,'ClusterCentroids')

input_dim = len(train_X[0][0])
timesteps = len(train_X[0])

input_shape = train_X[0].shape

# class_weight = {0: 1,
#               1: 150}

print(train_X[0].shape)

# reshape into correct dimensions to input into cnn
# train_X = train_X.reshape(140,3920,1)
# test_X = test_X.reshape(60,3920,1)


model = Sequential()
model.add(Conv1D(filters=64, kernel_size=3, input_shape=input_shape, padding='same'))
# Options: relu, tanh, sigmoid
model.add(Activation('relu'))
model.add(MaxPool1D(pool_size=3)) # originally 2

# Dropout changed the concept of learning all the weights together to learning a fraction of the weights in the network in each training iteration
# In Keras, the dropout rate argument is (1-p). For intermediate layers, choosing (1-p) = 0.5 for large networks is ideal.
# For the input layer, (1-p) should be kept about 0.2 or lower. This is because dropping the input data can adversely affect the training.
# A (1-p) > 0.5 is not advised, as it culls more connections without boosting the regularization.
model.add(Dropout(0.2))
model.add(Flatten())
model.add(Dense(3, activation='softmax'))
model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
print(model.summary())
model.fit(train_X, train_Y, validation_data=(test_X, test_Y), epochs=epochs, batch_size=batch_size)

# score model and log accuracy and parameters
scores = model.evaluate(test_X, test_Y, verbose=0)
print("Accuracy: %.2f%%" % (scores[1] * 100))

predictions = model.predict_classes(test_X)

classification_report = classification_report(test_Y, predictions)
print(classification_report)
