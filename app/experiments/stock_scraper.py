import requests
import pandas as pd
from datetime import datetime, timedelta
from urllib.parse import urlencode

from app.models import Stock, StockPrice


def start_stock_scraper():
    print('Stock scraper scheduler start')
    scrape_stocks()
    scrape_all_stock_prices()
    print('Stock scraper scheduler end')


def scrape_all_stock_prices():
    print('Stock price update start')

    stocks = Stock.query.all()

    for idx, stock in enumerate(stocks):
        print('Scraping stock %s (%d/%d)' % (stock.code, idx + 1, len(stocks)))
        scrape_daily_prices(stock)

    print('Stock price updated on %s' % (str(datetime.now())))


def scrape_daily_prices(stock):
    latest_price = StockPrice.query.join(Stock).filter(Stock.code == stock.code).order_by(StockPrice.date.desc()).first()

    start_date = (datetime.combine(latest_price.date, datetime.min.time()) + timedelta(days=1) if latest_price else datetime(2000, 1, 1))
    end_date = datetime.now()

    url = 'https://quotes.wsj.com/ID/XIDX/' + stock.code + '/historical-prices/download'
    payload = {
        'num_rows': (end_date - start_date).days,
        'range_days': (end_date - start_date).days,
        'startDate': start_date.strftime('%Y-%m-%d'),
        'endDate': end_date.strftime('%Y-%m-%d')
    }

    stock_csv = pd.read_csv(url + '?' + urlencode(payload), sep=', ', engine='python')
    stock_csv.columns = map(str.lower, stock_csv.columns)
    stock_csv['date'] = pd.to_datetime(stock_csv['date'])

    stock_prices = stock_csv.to_dict(orient='records')

    for stock_price in stock_prices:
        stock.daily_prices.append(StockPrice(**stock_price))
    stock.save()


def scrape_stocks():
    url = 'https://www.idx.co.id/umbraco/Surface/StockData/GetSecuritiesStock'
    payload = {
        'start': 0,
        'length': 100
    }

    r = requests.get(url=url, params=payload)

    data = r.json()
    stock_count = data['recordsTotal']

    stock_list = []
    stock_list += data['data']

    for i in range(stock_count // payload['length']):
        payload['start'] += payload['length']

        r = requests.get(url=url, params=payload)

        data = r.json()
        stock_list += data['data']

    insert_or_update_stocks(stock_list)


def insert_or_update_stocks(stock_list):
    print('Stock list update start')

    for idx, stock_data in enumerate(stock_list):
        stock = Stock.query.filter_by(code=stock_data['Code']).first()

        if stock:
            stock.name = stock_data['Name']
            stock.listing_date = stock_data['ListingDate']
            stock.outstanding_shares = stock_data['Shares']
            stock.save()
            print('Updated stock %s (%d/%d)' % (stock_data['Code'], idx + 1, len(stock_list)))
        else:
            Stock(code=stock_data['Code'],
                  name=stock_data['Name'],
                  listing_date=stock_data['ListingDate'],
                  outstanding_shares=stock_data['Shares']).create()
            print('Inserted stock %s (%d/%d)' % (stock_data['Code'], idx + 1, len(stock_list)))

    print('Stock list updated on %s' % (str(datetime.now())))
