from flask import Blueprint, request, jsonify
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import requests
import re
import atexit
import pandas as pd
from urllib.parse import urlencode

from app.models import Stock, StockPrice
from app.extensions import scheduler

stock = Blueprint('stock', __name__)

# scheduler.start()
# atexit.register(lambda: scheduler.shutdown())


@stock.route('/scrape/prices/<stock_code>')
def scrape_stock_prices(stock_code):
    start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d')
    end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d')

    stock = Stock.query.filter_by(code=stock_code).first()
    if not stock:
        return 'Not found'

    url = 'https://quotes.wsj.com/ID/XIDX/' + stock_code + '/historical-prices/download'
    payload = {
        'num_rows': (end_date - start_date).days,
        'range_days': (end_date - start_date).days,
        'startDate': start_date.strftime('%Y-%m-%d'),
        'endDate': end_date.strftime('%Y-%m-%d')
    }

    stock_csv = pd.read_csv(url + '?' + urlencode(payload), sep=', ')
    historical_prices = stock_csv.to_dict(orient='records')

    return jsonify(historical_prices)


@stock.route('/scrape/prices')
# @scheduler.scheduled_job('interval', days=1)
def scrape_all_stock_prices():
    # print('Daily scheduler start')
    #
    # from app import create_app
    # app = create_app()
    #
    # with app.app_context():
    #     stocks = Stock.query.all().limit(20)
    #
    #     for stock in stocks:
    #         scrape_daily_prices(stock)
    #
    # print('Daily scheduler end')
    import time
    stocks = Stock.query.limit(20)

    for stock in stocks:
        start = time.time()
        scrape_daily_prices(stock)
        end = time.time()
        print(end - start)


# @stock.route('/scrape/stock/prices/<code>')
def scrape_daily_prices(stock):
    print('Scraping stock %s' % stock.code)
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

    return jsonify(stock_prices)


# @scheduler.scheduled_job('interval', weeks=1)
@stock.route('/scrape/stocks')
def scrape_stocks():
    print('Weekly scheduler start')

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

    print('Weekly scheduler end')
    # return jsonify(stock_list)


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
