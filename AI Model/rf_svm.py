import numpy as np
# Import train_test_split function
from sklearn.model_selection import train_test_split
# Import Random Forest Model
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
# Import scikit-learn metrics module for accuracy calculation
from sklearn import metrics
from sklearn.metrics import confusion_matrix
import seaborn as sn
import matplotlib.pyplot as plt

# Load data
# minimum amount of reviews per company (standard = 5)
min_reviews = [5, 10]

# amount of years to be observed.  This is required so that the samples for the AI model have constant length.
# By specifying observed_years = n, the script will return n-1 differences between the years.
observed_years = [4, 5, 6]  # 4

# calc_arg_reviews specifies the resulting calculation of the differences that is returned in the output file.
# 'prior': calculates the differences of the moving average score to the score the year before
# 'first': calculates the differences of the moving average score to the first considered year score
#  'abs' : returns not the difference between moving average scores, but the scores themselves
calc_arg_reviews = ['abs', 'first', 'prior']

#  calc_arg_entries specifies the resulting calculation of the EK-Quote in the output file.
# 'abs': calculates the difference in "Prozentpunkten" between the EKQ of two years
# 'rel': calculates the percental difference between the EKQ of two years. Please note the difference to "abs".
calc_arg_entrie = 'abs'

#
number_of_classes = [3, 5, 6]

# Specify which models to run
# 'rf': Random Forest
# 'svm' Support Vector Machine
ai_model = ['rf', 'svm']

# aggregate years
# 'first': only use first feature (ReviewRating)
# 'avg': average over all years for each feature
calc_agg_years = ['first', 'avg']


def get_random_forest_classification(x_path, y_path, classes, years, aggregation, selected_model, n_estimators, n_jobs):
    x_path_git = 'AI Model/Data Preparation/output/' + x_path + '.npy'
    y_path_git = 'AI Model/Data Preparation/output_categorized/' + y_path + '.npy'

    X = np.load(x_path_git, allow_pickle=True)
    Y = np.load(y_path_git, allow_pickle=True)

    print(X.shape)
    print(X[0])
    print('Y:')
    print(Y)

    if aggregation == 'first':
        # only use Overall Review Rating
        X_new = X[:, :, 0]

    elif aggregation == 'avg':
        X_new = np.zeros((np.size(X, 0), 14))

        c = 0
        for comp in X:

            new_comp = np.zeros((14))
            for i in range(13):

                years_sum = 0
                for year in range(observed_year - 1):
                    years_sum = years_sum + comp[year][i]

                new_comp[i] = years_sum / (observed_year - 1)

            X_new[c] = new_comp
            c = c + 1

    else:
        raise ValueError("not supported value 'calc_agg_year':" + years)

    # Split dataset into training set and test set
    X_train, X_test, y_train, y_test = train_test_split(X_new, Y, test_size=0.2)

    ## PCA
    # from sklearn.decomposition import PCA
    #
    # pca = PCA()
    # X_train = pca.fit_transform(X_train)
    # X_test = pca.transform(X_test)
    #
    # pca.explained_variance_ratio_

    # Create a Gaussian Classifier
    rfc = RandomForestClassifier(n_estimators=n_estimators, n_jobs=n_jobs)

    # Train the model using the training sets y_pred=clf.predict(X_test)
    rfc.fit(X_train, y_train)

    y_pred = rfc.predict(X_test)

    accuracy = metrics.accuracy_score(y_test, y_pred)
    report = metrics.classification_report(y_test, y_pred)

    # plots
    cm = confusion_matrix(y_test, y_pred)

    labels = ['0', '1']
    plt.figure(figsize=(5, 5))
    ax = plt.subplot()
    sn.set(font_scale=1.4)  # for label size
    sn.heatmap(cm, annot=True, ax=ax, annot_kws={"size": 7}, cmap='Greens')

    # labels, title and ticks
    ax.set_xlabel('Predicted labels')
    ax.set_ylabel('True labels')
    ax.set_title('Confusion Matrix:\n' + Y_path
                 + '\nselected model:' + selected_model
                 + '\naggregation: ' + aggregation, fontsize=12)
    plt.suptitle(report, fontsize=8)
    ax.xaxis.tick_top()
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig('AI Model/plots/' + selected_model + '/' + aggregation + '/' + str(classes) + '/' + Y_path + '.png')

    # Model Accuracy, how often is the classifier correct?
    print("Accuracy:", accuracy)

    return report, accuracy


def get_random_forest_regression(y_path, x_path, years, aggregation, selected_model, n_estimators, n_jobs):
    x_path_git = 'AI Model/Data Preparation/output/' + x_path + '.npy'
    y_path_git = 'AI Model/Data Preparation/output/' + y_path + '.npy'

    X = np.load(x_path_git, allow_pickle=True)
    Y = np.load(y_path_git, allow_pickle=True)

    if aggregation == 'first':
        # only use Overall Review Rating
        X_new = X[:, :, 0]

    elif aggregation == 'avg':
        X_new = np.zeros((np.size(X, 0), 14))

        c = 0
        for comp in X:

            new_comp = np.zeros((14))
            for i in range(13):

                years_sum = 0
                for year in range(observed_year - 1):
                    years_sum = years_sum + comp[year][i]

                new_comp[i] = years_sum / (observed_year - 1)

            X_new[c] = new_comp
            c = c + 1

    else:
        raise ValueError("not supported value 'calc_agg_year':" + years)
    # Split dataset into training set and test set
    X_train, X_test, y_train, y_test = train_test_split(X_new, Y, test_size=0.2)

    #
    rfr = RandomForestRegressor(n_estimators=n_estimators, n_jobs=n_jobs)

    # Train the model using the training sets y_pred=clf.predict(X_test)
    rfr.fit(X_train, y_train)

    y_pred = rfr.predict(X_test)

    mae = metrics.mean_absolute_error(y_test, y_pred)
    mse = metrics.mean_squared_error(y_test, y_pred)
    rmse = metrics.mean_squared_error(y_test, y_pred, squared=False)

    # fig = plt.figure()
    # ax = fig.add_axes([0, 0, 1, 1])
    # # ax.lines(range(len(y_test)), y_test, color='b')
    # # ax.lines(range(len(y_pred)), y_pred, color='r')
    # plt.plot(range(len(y_test)), y_test, color='b')
    # plt.plot(range(len(y_pred)), y_pred, color='r')
    # ax.set_title('scatter plot')
    # plt.show()

    return mae, mse, rmse

    # # 4 categories
    # categories = [-0.15, -0.05, 0.05]
    #
    # y_test_cat = np.array(binning_y(categories, y_test), dtype=int)
    # y_pred_cat = np.array(binning_y(categories, y_pred), dtype=int)
    #
    # report = metrics.classification_report(y_test_cat, y_pred_cat)
    #
    # cm = confusion_matrix(y_test_cat, y_pred_cat)
    #
    # labels = ['high risk', 'medium risk', 'low risk', 'no risk']
    # plt.figure(figsize=(5, 5))
    # ax = plt.subplot()
    # sn.set(font_scale=1.4)  # for label size
    # sn.heatmap(cm, annot=True, ax=ax, annot_kws={"size": 7}, cmap='Greens')
    #
    # # labels, title and ticks
    # ax.set_xlabel('Predicted labels')
    # ax.set_ylabel('True labels')
    # ax.xaxis.tick_top()
    # # ax.set_xticklabels(labels)
    # # ax.set_yticklabels(labels)
    # ax.set_title('Confusion Matrix:\n' + Y_path, fontsize=12)
    # plt.xticks(rotation=0)
    # plt.yticks(rotation=0)
    # plt.show()
    #
    # # Model Accuracy, how often is the classifier correct?
    # print("Accuracy:", accuracy)


all_accuracy = []
all_mae = []
all_mse = []
all_rmse = []
reports = []
# define filename
for min_review in min_reviews:
    for calc_arg_review in calc_arg_reviews:
        for observed_year in observed_years:
            for number_of_class in number_of_classes:
                for calc_agg_year in calc_agg_years:
                    X_path = 'X_' + str(min_review) + '_' + str(observed_year) + '_' + calc_arg_review + '_' \
                             + calc_arg_entrie
                    Y_path = 'Y_' + str(min_review) + '_' + str(observed_year) + '_' + calc_arg_review + '_' \
                             + calc_arg_entrie + '_(' + str(number_of_class) + ')'

                    if 'rf' in ai_model:
                        print("RF:")

                        # Classification
                        report, accuracy = get_random_forest_classification(X_path, Y_path, classes=number_of_class,
                                                                            years=observed_year,
                                                                            aggregation=calc_agg_year,
                                                                            selected_model='rf', n_estimators=10000,
                                                                            n_jobs=-1)

                        reports.append(report)
                        all_accuracy.append(accuracy)

                        # Regression
                        # Y_path = 'Y_' + str(min_review) + '_' + str(observed_year) + '_' + calc_arg_review + '_' \
                        #          + calc_arg_entrie
                        #
                        # mae, mse, rmse = get_random_forest_regression(X_path, Y_path, classes=number_of_class,
                        #                                                 years=observed_year,
                        #                                                 aggregation=calc_agg_year,
                        #                                                 selected_model='rf', n_estimators=1000,
                        #                                                 n_jobs=-1)
                        # all_mae.append(mae)
                        # all_mse.append(mse)
                        # all_rmse.append(rmse)

                    if 'svm' in ai_model:
                        print("SVM:")
                        # Jan hier code für SVM

print(reports)
print(max(all_accuracy))
