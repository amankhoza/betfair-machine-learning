from __future__ import division
from sklearn import kernel_ridge
from sklearn.model_selection import cross_val_score
import numpy as np
import pandas as pd
import os

os.system('reset')

FEATURES = ["Home_Rank", "Away_Rank", "Home_pmP", "Away_pmP", "Draw_pmP", "Prev_home_p", "Prev_away_p", "Prev_draw_p",
            "Score_deficit", "Home_or_Away_goal", "Time_of_goal"]
LABELS = ["Curr_home_p", "Curr_away_p", "Curr_draw_p"]

data_set_path = 'train.csv'
df = pd.read_csv(data_set_path)

X = df.as_matrix(columns=FEATURES)
y = df.as_matrix(columns=LABELS)


def cv_scores(clf):
    cv_scores = cross_val_score(clf, X, y, cv=10)
    return (cv_scores.mean(), cv_scores.std())


optimal_degree = 0
max_cv_score = 0

for i in range(1, 16):
    clf = kernel_ridge.KernelRidge(kernel="poly", degree=i)
    scores = cv_scores(clf)
    if scores[0] > max_cv_score:
        max_cv_score = scores[0]
        optimal_degree = i
    print('Degree '+str(i)+' poly cv_score and std: '+str(scores))

print('Optimal Degree: '+str(optimal_degree))

for i in np.arange(0, 1, 0.1):
    for j in np.arange(0, 1, 0.01):
        alpha = round(i, 2)
        gamma = round(j, 2)
        clf = kernel_ridge.KernelRidge(kernel="poly", degree=optimal_degree, alpha=alpha, gamma=gamma)
        scores = cv_scores(clf)
        print(alpha, gamma, str(scores))
