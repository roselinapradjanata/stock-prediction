import pandas as pd
from urllib.parse import urlencode
from datetime import datetime, timedelta

from app.models import Index, IndexPrice


def start_index_scraper():
    print('Index scraper scheduler start')
    scrape_index()
    scrape_all_index_prices()
    print('Index scraper scheduler end')


def scrape_index():
    index_list = ['LQ45']
    for idx, index_code in enumerate(index_list):
        index = Index.query.filter_by(code=index_code).first()
        if not index:
            Index(code=index_code).create()
            print('Inserted index %s (%d/%d)' % (index_code, idx + 1, len(index_list)))


def scrape_all_index_prices():
    print('Index price update start')

    indexes = Index.query.all()

    for idx, index in enumerate(indexes):
        print('Scraping index %s (%d/%d)' % (index.code, idx + 1, len(indexes)))
        scrape_daily_prices(index)

    print('Index price updated on %s' % (str(datetime.now())))


def scrape_daily_prices(index):
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
