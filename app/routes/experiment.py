from flask import Blueprint
from keras.models import Sequential
from keras.layers import LSTM, Dense

from .preprocessor import preprocess

exp = Blueprint('exp', __name__)


@exp.route('/experiment')
def experiment():
    x_train, y_train = preprocess()
    model = build_model(64, 3)
    model.fit(x_train, y_train, epochs=10, batch_size=5, verbose=1)
    model.save('lq45_model.h5')
    return 'finish'


def build_model(n_units, look_back):
    print('Building model')
    model = Sequential()
    model.add(LSTM(n_units, input_shape=(1, look_back)))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='adam')
    return model
