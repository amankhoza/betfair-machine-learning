from __future__ import division
from sklearn import tree
from sklearn.model_selection import cross_val_score
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


max_cv_score = 0

for depth in range(1, 15):
    for min_samples in range(1, 15):
        clf = tree.DecisionTreeRegressor(max_depth=depth, min_samples_leaf=min_samples)
        scores = cv_scores(clf)
        print(depth, min_samples, str(scores))
