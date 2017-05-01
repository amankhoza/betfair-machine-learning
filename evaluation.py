from __future__ import division
from sklearn.metrics import mean_squared_error
import numpy as np


def evaluate(predicted_probabilities, actual_probabilities):
    print('\n*** BEGINNING EVALUATION ***\n')
    total = len(predicted_probabilities)
    almost_exact = 0
    extremely_good = 0
    average = 0
    bad = 0

    for i in range(0, len(predicted_probabilities)):
        avg_err = np.mean(abs(actual_probabilities[i]-predicted_probabilities[i]))
        if avg_err < 1:
            almost_exact += 1
        elif avg_err < 2:
            extremely_good += 1
        elif avg_err < 5:
            average += 1
        else:
            bad += 1
        print(str(actual_probabilities[i])+'\t'+str(predicted_probabilities[i])+'\t'+str(avg_err))

    mse = mean_squared_error(actual_probabilities, predicted_probabilities)
    print('MSE: '+str(mse))

    print('almost_exact', 'extremely_good', 'average', 'bad')
    print(almost_exact, extremely_good, average, bad)
    print(almost_exact/total, extremely_good/total, average/total, bad/total)
