from datetime import datetime
from keras.models import Sequential
from keras.layers import LSTM, Dense

from app.models import Index
from .preprocessor import process_raw_data


def train_model():
    print('Start training model')

    index_code = 'LQ45'
    x_train, y_train = process_raw_data(index_code)
    model = build_model(64, 3)
    model.fit(x_train, y_train, epochs=10, batch_size=5, verbose=1)
    model.save(index_code + '_model.h5')

    index = Index.query.filter_by(code=index_code).first()
    index.model_updated_at = datetime.now()
    index.save()

    print('Finished training model')


def build_model(n_units, look_back):
    model = Sequential()
    model.add(LSTM(n_units, input_shape=(1, look_back)))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='adam')
    return model
