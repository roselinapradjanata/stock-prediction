from flask import Blueprint
from urllib.parse import urlencode
import pandas as pd
from datetime import datetime, timedelta

from app.models import Index, IndexPrice

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
