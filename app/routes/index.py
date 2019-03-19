from flask import Blueprint, jsonify
from urllib.parse import urlencode
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from app.models import Index, IndexPrice, ProcessedIndexPrice

index = Blueprint('index', __name__)


@index.route('/scrape/index/prices')
def scrape_all_index_prices():
    indexes = Index.query.all()

    for index in indexes:
        scrape_daily_prices(index)


def scrape_daily_prices(index):
    print('Scraping index %s' % index.code)
    latest_price = IndexPrice.query.join(Index).filter(Index.code == index.code).order_by(IndexPrice.date.desc()).first()

    start_date = (datetime.combine(latest_price.date, datetime.min.time()) + timedelta(days=1) if latest_price else datetime(2000, 1, 1))
    end_date = datetime.now()

    url = 'https://quotes.wsj.com/index/XX/' + index.code + '/historical-prices/download'
    payload = {
        'num_rows': (end_date - start_date).days,
        'range_days': (end_date - start_date).days,
        'startDate': start_date.strftime('%Y-%m-%d'),
        'endDate': end_date.strftime('%Y-%m-%d')
    }

    index_csv = pd.read_csv(url + '?' + urlencode(payload), sep=', ', engine='python')
    index_csv.columns = map(str.lower, index_csv.columns)
    index_csv['date'] = pd.to_datetime(index_csv['date'])

    index_prices = index_csv.to_dict(orient='records')

    for index_price in index_prices:
        index.daily_prices.append(IndexPrice(**index_price))
    index.save()


@index.route('/preprocess/index')
def preprocess():
    index = Index.query.filter_by(code='LQ45').first()
    latest_price = ProcessedIndexPrice.query.join(Index).filter(Index.code == index.code).order_by(ProcessedIndexPrice.date.desc()).first()

    start_date = (datetime.combine(latest_price.date, datetime.min.time()) + timedelta(days=1) if latest_price else datetime(2000, 1, 1)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')

    index_prices = IndexPrice.query.join(Index).filter(Index.code == 'LQ45', IndexPrice.date >= start_date, IndexPrice.date <= end_date).order_by(IndexPrice.date)

    dataframe = pd.read_sql(index_prices.statement, index_prices.session.bind)
    index_prices = dataframe[['close']].values
    print(index_prices)

    from sklearn.preprocessing import MinMaxScaler
    scaler = MinMaxScaler(feature_range=(0, 1))
    index_prices = scaler.fit_transform(index_prices)

    look_back = 3
    train_x, train_y = create_dataset(index_prices, look_back)

    train_x = np.reshape(train_x, (train_x.shape[0], 1, train_x.shape[1]))

    print(train_x)

    return 'asdasd'


def create_dataset(dataset, look_back=1):
    data_X, data_Y = [], []
    for i in range(len(dataset)-look_back):
        a = dataset[i:(i+look_back), 0]
        data_X.append(a)
        data_Y.append(dataset[i + look_back, 0])
    return np.array(data_X), np.array(data_Y)
