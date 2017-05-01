import tensorflow as tf


class MultiLabelRegressor:

    def __init__(self, input_fn, feature_cols, labels, hidden_units, steps):
        self.input_fn = input_fn
        self.feature_cols = feature_cols
        self.labels = labels
        self.hidden_units = hidden_units
        self.steps = steps

    def fit(self, data_set):
        self.regressors = {}
        for label in self.labels:
            regressor = tf.contrib.learn.DNNRegressor(feature_columns=self.feature_cols,
                                                      hidden_units=self.hidden_units)
            regressor.fit(input_fn=lambda: self.input_fn(data_set, label), steps=self.steps)
            self.regressors[label] = regressor

    def evaluate(self, data_set):
        for label in self.labels:
            ev = self.regressors[label].evaluate(input_fn=lambda: self.input_fn(data_set, label), steps=1)
            loss_score = ev["loss"]
            print("Loss for "+label+": {0:f}".format(loss_score))

    def predict(self, data_set):
        predictions = {}
        for label in self.labels:
            regressor = self.regressors[label]
            prediction = regressor.predict(input_fn=lambda: self.input_fn(data_set, label))
            predictions[label] = list(prediction)
        return predictions
