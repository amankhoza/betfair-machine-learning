from sklearn import kernel_ridge
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
import pandas as pd
import os
import numpy
import sys

os.system('reset')

FEATURES = ["Home_Rank", "Away_Rank", "Home_pmP", "Away_pmP", "Draw_pmP", "Prev_home_p", "Prev_away_p", "Prev_draw_p",
            "Score_deficit", "Home_or_Away_goal", "Time_of_goal"]
LABELS = ["Curr_home_p", "Curr_away_p", "Curr_draw_p"]

data_set_path = sys.argv[1]

df = pd.read_csv(data_set_path)

train, test = train_test_split(df, test_size=0.2)

x_train = train.as_matrix(columns=FEATURES)
x_test = test.as_matrix(columns=FEATURES)

z_train = train.as_matrix(columns=LABELS)
z_test = test.as_matrix(columns=LABELS)

kernel = sys.argv[2]

if kernel == 'linear':
    clf = kernel_ridge.KernelRidge(kernel="linear")
else:
    clf = kernel_ridge.KernelRidge(kernel="poly", degree=2, alpha=0.5, gamma=0.01)

clf.fit(x_train, z_train)

z_pred = clf.predict(x_test)

avgDiffs = sum(abs(z_test-z_pred)) / len(z_pred)

outputDirectory = 'Sklearn_Model_Output'

if not os.path.exists(outputDirectory):
    os.makedirs('./'+outputDirectory)

numpy.set_printoptions(formatter={'float_kind': '{:f}'.format})
numpy.savetxt(outputDirectory+"/pred.csv", z_pred, delimiter=",", fmt='%f')
numpy.savetxt(outputDirectory+"/act.csv", z_test, delimiter=",", fmt='%f')

for i in range(0, len(LABELS)):
    print('Avg diff for '+LABELS[i]+': '+str(avgDiffs[i]))

mse = mean_squared_error(z_test, z_pred)
print('MSE: '+str(mse))
