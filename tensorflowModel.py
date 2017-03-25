import pandas as pd
import tensorflow as tf
import numpy as np
import os

tf.logging.set_verbosity(tf.logging.INFO)

COLUMNS = ["Home", "Away", "Home_Rank", "Away_Rank", "Home_pmP", "Away_pmP", "Draw_pmP",
           "Prev_home_p", "Prev_away_p", "Prev_draw_p", "Score_deficit", "Home_or_Away_goal",
           "Curr_home_p", "Curr_away_p", "Curr_draw_p", "Time_of_goal", "Change_home_p",
           "Change_away p", "Change_draw_p"]
FEATURES = ["Home_pmP", "Away_pmP", "Draw_pmP", "Prev_home_p", "Prev_away_p", "Prev_draw_p",
            "Score_deficit", "Home_or_Away_goal", "Time_of_goal"]
LABELS = ["Change_home_p", "Change_away_p", "Change_draw_p"]


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


class MultiLabelRegressor:

    def __init__(self, input_fn, feature_cols, labels):
        self.input_fn = input_fn
        self.feature_cols = feature_cols
        self.labels = labels

    def fit(self, data_set):
        self.regressors = {}
        for label in self.labels:
            # Build 2 layer fully connected DNN with 10, 10 units respectively.
            regressor = tf.contrib.learn.DNNRegressor(feature_columns=self.feature_cols,
                                                      hidden_units=[10, 10])
            # Fit
            regressor.fit(input_fn=lambda: self.input_fn(data_set, label), steps=5000)
            self.regressors[label] = regressor

    def evaluate(self, data_set):
        for label in self.labels:
            # Score accuracy
            ev = self.regressors[label].evaluate(input_fn=lambda: self.input_fn(data_set, label), steps=1)
            loss_score = ev["loss"]
            print("Loss for "+label+": {0:f}".format(loss_score))

    def predict(self, data_set):
        predictions = {}
        for label in self.labels:
            regressor = self.regressors[label]
            prediction = regressor.predict(input_fn=lambda: input_fn(data_set, label))
            predictions[label] = list(prediction)
        return predictions


def main(unused_argv):
    os.system('reset')

    # Load datasets
    training_set = pd.read_csv("betfair_train.csv")
    test_set = pd.read_csv("betfair_test.csv")
    prediction_set = pd.read_csv("betfair_pred.csv")

    # df = pd.read_csv("train50.csv")
    # training_set, test_set, prediction_set = split_data(df, [0.7, 0.2, 0.1])

    # Feature cols
    feature_cols = [tf.contrib.layers.real_valued_column(k)
                    for k in FEATURES]

    multiRegressor = MultiLabelRegressor(input_fn, feature_cols, LABELS)
    multiRegressor.fit(training_set)
    multiRegressor.evaluate(test_set)
    predictions = multiRegressor.predict(prediction_set)

    for label in LABELS:
        actual = predictions[label]
        preds = list(prediction_set[label].values)
        combined = zip(actual, preds)
        print('Actual \t\t Prediction \t\t Diff')
        totalDiff = 0
        for pair in combined:
            diff = abs(pair[0]-pair[1])
            totalDiff += diff
            print('{:.2f} \t\t {:.2f} \t\t {:.2f}'.format(pair[0], pair[1], diff))
        avgDiff = float(totalDiff) / float(len(combined))
        print('Average diff = {}\n'.format(avgDiff))


if __name__ == "__main__":
    tf.app.run()
