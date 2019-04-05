import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime, timedelta
from app.models import Index, IndexPrice


def process_raw_data(index_code):
    dataframe = query_dataframe(index_code)
    dataset = dataframe[['close']].values

    scaler = MinMaxScaler(feature_range=(0, 1))
    dataset = scaler.fit_transform(dataset)

    look_back = 3
    x_train, y_train = create_dataset(dataset, look_back)
    x_train = np.reshape(x_train, (x_train.shape[0], 1, x_train.shape[1]))

    return x_train, y_train


def create_dataset(dataset, look_back=1):
    data_X, data_Y = [], []
    for i in range(len(dataset)-look_back):
        a = dataset[i:(i+look_back), 0]
        data_X.append(a)
        data_Y.append(dataset[i + look_back, 0])
    return np.array(data_X), np.array(data_Y)


def query_dataframe(index_code):
    index = Index.query.filter_by(code=index_code).first()
    latest_price = index.model_updated_at

    start_date = (datetime.combine(latest_price.date, datetime.min.time()) + timedelta(days=1) if latest_price else datetime(2000, 1, 1)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')

    index_prices = IndexPrice.query.join(Index).filter(Index.code == index_code, IndexPrice.date >= start_date, IndexPrice.date <= end_date).order_by(IndexPrice.date)
    dataframe = pd.read_sql(index_prices.statement, index_prices.session.bind)

    return dataframe
