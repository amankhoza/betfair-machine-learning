from __future__ import division
from sklearn import kernel_ridge
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn import tree
import pandas as pd
import os
import numpy
import sys
from evaluation import evaluate

os.system('reset')

FEATURES = ["Home_Rank", "Away_Rank", "Home_pmP", "Away_pmP", "Draw_pmP", "Prev_home_p", "Prev_away_p", "Prev_draw_p",
            "Score_deficit", "Home_or_Away_goal", "Time_of_goal"]
LABELS = ["Curr_home_p", "Curr_away_p", "Curr_draw_p"]

data_set_path = 'train.csv'
df = pd.read_csv(data_set_path)
train, test = train_test_split(df, test_size=0.2)

x_train = train.as_matrix(columns=FEATURES)
x_test = test.as_matrix(columns=FEATURES)

z_train = train.as_matrix(columns=LABELS)
z_test = test.as_matrix(columns=LABELS)

model = sys.argv[1]

if model == 'linear':
    clf = kernel_ridge.KernelRidge(kernel="linear")
elif model == 'poly':
    clf = kernel_ridge.KernelRidge(kernel="poly", degree=2, alpha=0.6, gamma=0.9)
elif model == 'tree':
    clf = tree.DecisionTreeRegressor(max_depth=5, min_samples_leaf=4)

clf.fit(x_train, z_train)

z_pred = clf.predict(x_test)

cv_scores = cross_val_score(clf, x_train, z_train, cv=5)
print("Accuracy: %0.2f (+/- %0.2f)" % (cv_scores.mean(), cv_scores.std() * 2))

avgDiffs = sum(abs(z_test-z_pred)) / len(z_pred)

outputDirectory = 'Sklearn_Model_Output'

if not os.path.exists(outputDirectory):
    os.makedirs('./'+outputDirectory)

numpy.set_printoptions(formatter={'float_kind': '{:f}'.format})
numpy.savetxt(outputDirectory+"/pred.csv", z_pred, delimiter=",", fmt='%f')
numpy.savetxt(outputDirectory+"/act.csv", z_test, delimiter=",", fmt='%f')

print('Actual\tPred')

for i in range(0, len(LABELS)):
    print('Avg diff for '+LABELS[i]+': '+str(avgDiffs[i]))

print('Total absolute error: '+str(numpy.sum(avgDiffs)))

evaluate(z_pred, z_test)
