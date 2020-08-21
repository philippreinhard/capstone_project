import glob
import os
import numpy as np
import sys
from keras.models import Sequential
from keras.layers import Dense, Conv1D, Flatten, MaxPool1D, Dropout, Activation
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, f1_score
import itertools
import pandas as pd
from sympy.printing.tests.test_tensorflow import tf
from datetime import datetime

# define filename
#y_filename = 'Y_10_4_first_abs'
folder_path = 'Data Preparation/output/'

# Parameters
train_size = 0.7

params = {
    'number_of_classes': [3, 5, 6],
    'epochs': [100, 200],
    'batch_size': [10, 20],
    'padding': ['same'],
    'kernel_size': [4],
    'filters': [64],
    'first_activation_function': ['relu'],
    'dropout': [0.1],
    # Dropout changed the concept of learning all the weights together to learning a fraction of the weights in the network in each training iteration
    # In Keras, the dropout rate argument is (1-p). For intermediate layers, choosing (1-p) = 0.5 for large networks is ideal.
    # For the input layer, (1-p) should be kept about 0.2 or lower. This is because dropping the input data can adversely affect the training.
    # A (1-p) > 0.5 is not advised, as it culls more connections without boosting the regularization.
    'output_activation_function': ['softmax'],
}

keys = list(params)

#tf.logging.set_verbosity(tf.logging.ERROR)
#np.set_printoptions(threshold=sys.maxsize)

# fix random seed for reproducibility
np.random.seed(7)

df = pd.DataFrame(
    columns=['Data Set', 'epochs', 'batch_size', 'padding', 'kernel-size', 'filters', 'first_activation', 'dropout',
             'output_activation', 'accuracy', 'F1-Score'])

def main(**args):
    # Load parameters
    # print(args)
    number_of_classes = args.get('number_of_classes')
    epochs = args.get('epochs')
    batch_size = args.get('batch_size')
    padding = args.get('padding')
    kernel_size = args.get('kernel_size')
    filters = args.get('filters')
    first_activation_function = args.get('first_activation_function')
    dropout = args.get('dropout')
    output_activation_function = args.get('output_activation_function')

    # Load data
    y_path = 'Data Preparation/output_categorized/' + y_filename + '_(' + str(number_of_classes) + ').npy'
    x_path = 'Data Preparation/output/X_' + y_filename[2:] + '.npy'

    X = np.load(x_path, allow_pickle=True)
    Y = np.load(y_path, allow_pickle=True)

    X = X.astype('float64')
    Y = Y.astype('float64')

    # print(X[0])
    # print(Y)

    # Prepare test & train data and set input dimension
    train_X, test_X, train_Y, test_Y = train_test_split(X, Y, train_size=train_size, random_state=1, stratify=Y)
    input_dim = len(train_X[0][0])
    timesteps = len(train_X[0])
    input_shape = train_X[0].shape

    # print(train_X[0].shape)

    # Build model
    model = Sequential()
    model.add(Conv1D(filters=filters, kernel_size=kernel_size, input_shape=input_shape, padding=padding))
    model.add(Activation(first_activation_function))
    model.add(MaxPool1D(pool_size=2))
    model.add(Dropout(dropout))
    model.add(Flatten())
    model.add(Dense(number_of_classes, activation=output_activation_function))
    model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    # print(model.summary())

    model.fit(train_X, train_Y, validation_data=(test_X, test_Y), epochs=epochs, batch_size=batch_size, verbose=0)

    # score model and log accuracy and parameters
    scores = model.evaluate(test_X, test_Y, verbose=0)
    accuracy = scores[1] * 100
    print("Accuracy: %.2f%%" % (scores[1] * 100))
    predictions = model.predict_classes(test_X)
    report = classification_report(test_Y, predictions)
    f1 = f1_score(test_Y, predictions, labels=None, pos_label=1, average='weighted')
    print('F1 Score: ', f1)

    # Write dataframe with parameter information and accuracy
    df.loc[z] = [y_filename + '_(' + str(number_of_classes) + ')', epochs, batch_size, padding, kernel_size, filters,
                 first_activation_function, dropout,
                 output_activation_function, accuracy, f1]

z = 0
# Start building all models
for filename in glob.glob(os.path.join(folder_path, '*.npy')):
    if filename.startswith('Data Preparation/output\\Y'):
        y_filename = (filename[24:])[:-4]
        print(y_filename)
        i = 0

        for values in itertools.product(*map(params.get, keys)):
            main(**dict(zip(keys, values)))
            i += 1
            z += 1

# Print all model results
pd.options.display.width = None
pd.set_option('display.max_columns', None)
print(df)
dateTimeObj = datetime.now()
timeStamp = str(dateTimeObj.year) + '_' + str(dateTimeObj.month) + '_' + str(dateTimeObj.day) + '-' + str(dateTimeObj.hour) + '_' + str(dateTimeObj.second)
df.to_csv('PhilippR/trained_models_results' + timeStamp + '.csv')
