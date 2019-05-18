import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from app.models import Index, IndexPrice, Stock, StockPrice


def process_raw_train_data(index_code, train_split):
    dataframe = query_index_dataframe(index_code)
    dataset = dataframe[['close']].values

    scaler = MinMaxScaler(feature_range=(0, 1))
    dataset = scaler.fit_transform(dataset)

    n_steps, n_features = 5, 1
    train_size = int(len(dataset) * train_split)
    train, test = dataset[:train_size, :], dataset[train_size:len(dataset), :]

    x_train, y_train = create_train_dataset(train, n_steps)
    x_test, y_test = create_train_dataset(test, n_steps)

    x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], n_features))
    x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], n_features))

    return x_train, y_train, x_test, y_test, scaler


def create_train_dataset(dataset, n_steps=1):
    x_data, y_data = [], []
    for i in range(len(dataset) - n_steps):
        a = dataset[i:(i + n_steps), 0]
        x_data.append(a)
        y_data.append(dataset[i + n_steps, 0])
    return np.array(x_data), np.array(y_data)


def query_index_dataframe(index_code):
    index_prices = IndexPrice.query.join(Index).filter(Index.code == index_code).order_by(IndexPrice.date)
    dataframe = pd.read_sql(index_prices.statement, index_prices.session.bind)

    return dataframe


def process_raw_test_data(stock_code):
    dataframe = query_stock_dataframe(stock_code)
    dataset = dataframe[['close']].values

    scaler = MinMaxScaler(feature_range=(0, 1))
    dataset = scaler.fit_transform(dataset)

    n_steps, n_features = 5, 1
    x_test, y_test = create_test_dataset(dataset, n_steps)
    x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], n_features))

    return x_test, y_test, scaler


def create_test_dataset(dataset, n_steps=1):
    x_data, y_data = [], dataset
    for i in range(len(dataset) - n_steps + 1):
        a = dataset[i:(i + n_steps), 0]
        x_data.append(a)
    return np.array(x_data), np.array(y_data)


def query_stock_dataframe(stock_code):
    stock_prices = StockPrice.query.join(Stock).filter(Stock.code == stock_code).order_by(StockPrice.date)
    dataframe = pd.read_sql(stock_prices.statement, stock_prices.session.bind)

    return dataframe


def process_raw_train_data_tl(normalized_dataset):
    train = normalized_dataset[:730]

    n_steps, n_features = 5, 1
    x_train, y_train = create_train_dataset(train, n_steps)
    x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], n_features))

    return x_train, y_train
