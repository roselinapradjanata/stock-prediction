import numpy as np
from itertools import product
from prettytable import PrettyTable

from app.models import Index, Hyperparameter
from .training import build_model
from .preprocessor import process_raw_train_data


def experiment():
    print('Experiment start')

    index_code = 'LQ45'
    train_split = 0.67
    n_steps, n_features = 5, 1
    x_train, y_train, x_test, y_test, scaler = process_raw_train_data(index_code, train_split)

    batch_sizes = [20, 25, 30, 35, 40]
    epochs = [170, 160, 150, 140, 130]
    neurons = [70, 65, 60, 55, 50]
    hyperparameters = [batch_sizes, epochs, neurons]

    configs = []
    for config in list(product(*hyperparameters)):
        configs.append({
            'batch_size': config[0],
            'epochs': config[1],
            'neurons': config[2]
        })

    best_config = None
    best_score = float('inf')
    mape_scores = []

    for index, config in enumerate(configs):
        print('Experiment %d/%d:' % (index + 1, len(configs)), config)
        model = build_model(n_neurons=config['neurons'], n_steps=n_steps, n_features=n_features)
        model.fit(x_train, y_train, epochs=config['epochs'], batch_size=config['batch_size'], verbose=1)
        score = evaluate_mape(model, scaler, x_test, y_test)
        mape_scores.append(score)
        if score <= best_score:
            best_config = config
            best_score = score

    index = Index.query.filter_by(code=index_code).first()
    Hyperparameter(index_id=index.id,
                   batch_size=best_config['batch_size'],
                   epochs=best_config['epochs'],
                   neurons=best_config['neurons']).create()

    print('Minimum MAPE: %.4f%%' % best_score)
    print('Best Config:', best_config)

    print_experiment_result(configs, mape_scores)

    print('Experiment end')


def print_experiment_result(configs, scores):
    table = PrettyTable()

    table.field_names = ['No', 'Batch Size', 'Epoch', 'Neuron', 'MAPE']

    for i in range(len(configs)):
        table.add_row([i + 1, configs[i]['batch_size'], configs[i]['epochs'], configs[i]['neurons'], '%.4f%%' % scores[i]])

    print(table)


def evaluate_mape(model, scaler, x_test, y_test):
    test_predict = scaler.inverse_transform(model.predict(x_test))
    test_actual = scaler.inverse_transform([y_test])
    mape_test_score = mean_absolute_percentage_error(test_actual[0], test_predict[:, 0])
    print('MAPE Test Score: %.4f%%' % mape_test_score)
    return mape_test_score


def mean_absolute_percentage_error(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100
