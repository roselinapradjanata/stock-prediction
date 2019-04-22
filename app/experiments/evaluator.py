from math import sqrt
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error


def evaluate(test_predict, y_test):
    n_steps = 3

    mse_test_score = sqrt(mean_squared_error(y_test[n_steps:, 0], test_predict[:-1, 0]))
    mae_test_score = mean_absolute_error(y_test[n_steps:, 0], test_predict[:-1, 0])
    mape_test_score = mean_absolute_percentage_error(y_test[n_steps:, 0], test_predict[:-1, 0])

    return {'mse': '%.4f' % mse_test_score, 'mae': '%.4f' % mae_test_score, 'mape': '%.4f%%' % mape_test_score}


def mean_absolute_percentage_error(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100
