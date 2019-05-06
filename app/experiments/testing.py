from keras.models import load_model
from keras import backend

from .preprocessor import process_raw_test_data


def test_model(stock_code):
    index_code = 'LQ45'
    x_test, y_test, scaler = process_raw_test_data(stock_code)

    backend.clear_session()
    model = load_model(index_code + '_model.h5')

    test_predict = model.predict(x_test)
    backend.clear_session()

    y_test = scaler.inverse_transform(y_test)
    test_predict = scaler.inverse_transform(test_predict)

    return test_predict, y_test
