from datetime import datetime
from keras.models import Sequential
from keras.layers import LSTM, Dense

from app.models import Index, Hyperparameter
from .preprocessor import process_raw_train_data


def train_model():
    print('Start training model')

    index_code = 'LQ45'
    train_split = 0.5
    x_train, y_train, _, _, _ = process_raw_train_data(index_code, train_split)

    hyperparameter = get_best_hyperparameter(index_code)

    model = build_model(hyperparameter.neurons, 5, 1)
    model.fit(x_train, y_train, epochs=hyperparameter.epochs, batch_size=hyperparameter.batch_size, verbose=1)
    model.save(index_code + '_model.h5')

    index = Index.query.filter_by(code=index_code).first()
    index.model_updated_at = datetime.now()
    index.save()

    print('Finished training model')


def build_model(n_neurons, n_steps, n_features):
    model = Sequential()
    model.add(LSTM(n_neurons, input_shape=(n_steps, n_features)))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='adam')
    return model


def get_best_hyperparameter(index_code):
    return Hyperparameter.query.join(Index).filter(Index.code == index_code).order_by(Hyperparameter.created_at.desc()).first()


def is_first_time_run():
    return not Hyperparameter.query.all()
