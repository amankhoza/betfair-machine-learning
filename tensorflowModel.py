from __future__ import division
import pandas as pd
import tensorflow as tf
import numpy as np
import os
from multilabelregressor import MultiLabelRegressor
from sklearn.model_selection import train_test_split
from evaluation import evaluate

tf.logging.set_verbosity(tf.logging.INFO)

COLUMNS = ["Home", "Away", "Home_Rank", "Away_Rank", "Home_pmP", "Away_pmP", "Draw_pmP",
           "Prev_home_p", "Prev_away_p", "Prev_draw_p", "Score_deficit", "Home_or_Away_goal",
           "Curr_home_p", "Curr_away_p", "Curr_draw_p", "Time_of_goal", "Change_home_p",
           "Change_away p", "Change_draw_p"]
FEATURES = ["Home_pmP", "Away_pmP", "Draw_pmP", "Prev_home_p", "Prev_away_p", "Prev_draw_p",
            "Score_deficit", "Home_or_Away_goal", "Time_of_goal"]
LABELS = ["Curr_home_p", "Curr_away_p", "Curr_draw_p"]


def split_data(data, split):
    n = len(data)
    boundaries = []
    for i in range(1, len(split)):
        boundaries.append(int(sum(split[:i]) * n))
    return np.split(data.sample(frac=1), boundaries)


def input_fn(data_set, label):
    feature_cols = {k: tf.constant(data_set[k].values, shape=[len(data_set), 1])
                    for k in FEATURES}
    labels = tf.constant(data_set[label].values)
    return feature_cols, labels


def main(unused_argv):
    os.system('reset')

    data_set_path = 'train.csv'
    df = pd.read_csv(data_set_path)
    training_set, test_set = train_test_split(df, test_size=0.2)

    # Feature cols
    feature_cols = [tf.contrib.layers.real_valued_column(k)
                    for k in FEATURES]

    multiRegressor = MultiLabelRegressor(input_fn, feature_cols, LABELS, [5, 18], 3000)
    multiRegressor.fit(training_set)
    predictions = multiRegressor.predict(test_set)

    actualLists = {}
    predictedLists = {}

    for label in LABELS:
        preds = predictions[label]
        actual = list(test_set[label].values)
        combined = zip(actual, preds)
        actualLists[label] = actual
        predictedLists[label] = preds
        print('Actual \t\t Prediction \t\t Diff')
        totalDiff = 0
        for pair in combined:
            diff = abs(pair[0]-pair[1])
            totalDiff += diff
            print('{:.2f} \t\t {:.2f} \t\t {:.2f}'.format(pair[0], pair[1], diff))
        avgDiff = float(totalDiff) / float(len(combined))
        print('Average diff = {}\n'.format(avgDiff))

    z_test = np.column_stack((actualLists['Curr_home_p'], actualLists['Curr_away_p'], actualLists['Curr_draw_p']))
    z_pred = np.column_stack((predictedLists['Curr_home_p'], predictedLists['Curr_away_p'], predictedLists['Curr_draw_p']))

    evaluate(z_pred, z_test)

if __name__ == "__main__":
    tf.app.run()
