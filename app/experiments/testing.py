import numpy as np
from keras.models import load_model
from keras import backend

from .preprocessor import process_raw_test_data, process_raw_train_data_tl
from .training import get_best_hyperparameter


def test_model(stock_code, days):
    index_code = 'LQ45'
    date, x_test, y_test, scaler = process_raw_test_data(stock_code)

    backend.clear_session()
    model = load_model(index_code + '_model.h5')

    for _ in range(days):
        test_predict = model.predict(x_test)
        x_new = np.array([np.concatenate((np.array(x_test[-1][1:]), np.array([test_predict[-1]])))])
        x_test = np.concatenate((x_test, x_new))
    backend.clear_session()

    y_test = scaler.inverse_transform(y_test)
    test_predict = scaler.inverse_transform(test_predict)

    return date, test_predict, y_test


def test_model_tl(stock_code, days):
    index_code = 'LQ45'
    date, x_test, y_test, scaler = process_raw_test_data(stock_code)

    backend.clear_session()
    model = load_model(index_code + '_model.h5')

    x_train, y_train = process_raw_train_data_tl(y_test)
    hyperparameter = get_best_hyperparameter(index_code)

    model.fit(x_train, y_train, epochs=hyperparameter.epochs, batch_size=hyperparameter.batch_size, verbose=1)

    for _ in range(days):
        test_predict = model.predict(x_test)
        x_new = np.array([np.concatenate((np.array(x_test[-1][1:]), np.array([test_predict[-1]])))])
        x_test = np.concatenate((x_test, x_new))
    backend.clear_session()

    y_test = scaler.inverse_transform(y_test)
    test_predict = scaler.inverse_transform(test_predict)

    return date, test_predict, y_test
