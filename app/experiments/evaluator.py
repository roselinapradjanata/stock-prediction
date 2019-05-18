from math import sqrt
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error


def evaluate(test_predict, y_test, days):
    n_steps = 5

    rmse_test_score = sqrt(mean_squared_error(y_test[n_steps:, 0], test_predict[:-days, 0]))
    mae_test_score = mean_absolute_error(y_test[n_steps:, 0], test_predict[:-days, 0])
    mape_test_score = mean_absolute_percentage_error(y_test[n_steps:, 0], test_predict[:-days, 0])

    return {'rmse': '%.4f' % rmse_test_score, 'mae': '%.4f' % mae_test_score, 'mape': '%.4f%%' % mape_test_score}


def mean_absolute_percentage_error(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100
