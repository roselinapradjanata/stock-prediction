from flask import Blueprint, request, jsonify
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import requests
import re
import atexit

from app.models import Stock, StockDailyPrice
from app.extensions import scheduler

stock = Blueprint('stock', __name__)

scheduler.start()
atexit.register(lambda: scheduler.shutdown())


@stock.route('/scrape/prices/<stock_code>')
def scrape_stock_prices(stock_code):
    start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d').strftime('%m/%d/%Y')
    end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d').strftime('%m/%d/%Y')

    stock = Stock.query.filter_by(code=stock_code).first()
    if not stock or not stock.scrape_id:
        return 'Not found'

    url = 'https://www.investing.com/instruments/HistoricalDataAjax'
    headers = {
        'user-agent': 'Chrome/71.0.3578.98',
        'x-requested-with': 'XMLHttpRequest'
    }
    payload = {
        'curr_id': stock.scrape_id,
        'st_date': start_date,
        'end_date': end_date,
        'interval_sec': 'Daily',
        'sort_col': 'date',
        'sort_ord': 'ASC',
        'action': 'historical_data'
    }

    r = requests.post(url=url, data=payload, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')

    historical_prices = []
    if soup.find('tbody').find('tr').find('td').text != 'No results found':
        table_rows = soup.find('tbody').find_all('tr')
        for table_row in table_rows:
            table_columns = table_row.find_all('td')
            historical_price = {
                'date': datetime.strptime(table_columns[0].text, '%b %d, %Y').strftime('%Y-%m-%d'),
                'close': table_columns[1]['data-real-value'].replace(',', ''),
                'open': table_columns[2]['data-real-value'].replace(',', ''),
                'high': table_columns[3]['data-real-value'].replace(',', ''),
                'low': table_columns[4]['data-real-value'].replace(',', ''),
                'volume': table_columns[5]['data-real-value'],
                'change': float(table_columns[6].text.strip('%')) / 100
            }
            historical_prices.append(historical_price)

    return jsonify(historical_prices)


@scheduler.scheduled_job('interval', days=1)
# @scheduler.scheduled_job('interval', seconds=30)
def scrape_all_stock_prices():
    print('Daily scheduler start')

    from app import create_app
    app = create_app()

    with app.app_context():
        stocks = Stock.query.filter(Stock.scrape_id != None).limit(20)

        for stock in stocks:
            scrape_daily_prices(stock)

    print('Daily scheduler end')


def scrape_daily_prices(stock):
    print('Scraping stock %s' % stock.code)
    latest_price = StockDailyPrice.query.join(Stock).filter(Stock.code == stock.code).order_by(StockDailyPrice.date.desc()).first()

    start_date = (latest_price.date + timedelta(days=1) if latest_price else datetime(2000, 1, 1)).strftime('%m/%d/%Y')
    end_date = datetime.now().strftime('%m/%d/%Y')

    url = 'https://www.investing.com/instruments/HistoricalDataAjax'
    headers = {
        'user-agent': 'Chrome/71.0.3578.98',
        'x-requested-with': 'XMLHttpRequest'
    }
    payload = {
        'curr_id': stock.scrape_id,
        'st_date': start_date,
        'end_date': end_date,
        'interval_sec': 'Daily',
        'sort_col': 'date',
        'sort_ord': 'ASC',
        'action': 'historical_data'
    }

    r = requests.post(url=url, data=payload, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')

    historical_prices = []
    if soup.find('tbody').find('tr').find('td').text != 'No results found':
        print('Parsing stock %s' % stock.code)
        table_rows = soup.find('tbody').find_all('tr')
        for table_row in table_rows:
            table_columns = table_row.find_all('td')
            historical_price = {
                'date': datetime.strptime(table_columns[0].text, '%b %d, %Y').strftime('%Y-%m-%d'),
                'close': table_columns[1]['data-real-value'].replace(',', ''),
                'open': table_columns[2]['data-real-value'].replace(',', ''),
                'high': table_columns[3]['data-real-value'].replace(',', ''),
                'low': table_columns[4]['data-real-value'].replace(',', ''),
                'volume': table_columns[5]['data-real-value'],
                'change': float(table_columns[6].text.strip('%')) / 100
            }
            historical_prices.append(historical_price)
            stock.daily_prices.append(StockDailyPrice(**historical_price))
        stock.save()


@scheduler.scheduled_job('interval', weeks=1)
# @stock.route('/scrape/stocks')
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

    print('Weekly scheduler start')
    # return jsonify(stock_list)


def insert_or_update_stocks(stock_list):
    for stock_data in stock_list:
        stock = Stock.query.filter_by(code=stock_data['Code']).first()

        if stock:
            stock.name = stock_data['Name']
            stock.listing_date = stock_data['ListingDate']
            stock.outstanding_shares = stock_data['Shares']
            stock.save()
            print('Updated stock %s' % (stock_data['Code']))
        else:
            Stock(code=stock_data['Code'],
                  name=stock_data['Name'],
                  listing_date=stock_data['ListingDate'],
                  outstanding_shares=stock_data['Shares'],
                  scrape_id=get_scrape_id(stock_data['Code'])).create()
            print('Inserted stock %s' % (stock_data['Code']))

    print('Stock list updated on %s' % (str(datetime.now())))


def get_scrape_id(stock_code):
    url = 'https://www.investing.com/search'
    headers = {
        'user-agent': 'Chrome/71.0.3578.98'
    }
    payload = {
        'q': stock_code
    }

    r = requests.get(url=url, params=payload, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')

    search_results = soup.find('div', class_='searchSectionMain').find_all('a')
    href = [a['href'] for a in search_results
            if a.find('span', class_='second').text == stock_code
            and a.find('span', class_='fourth').text == 'Stock - Jakarta  equities']

    return scrape_info(href[0]) if href else None


def scrape_info(sub_url):
    url = 'https://www.investing.com' + sub_url + '-historical-data'
    headers = {
        'user-agent': 'Chrome/71.0.3578.98'
    }

    r = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')

    info = soup.find(string=re.compile("histDataExcessInfo")).replace(' ', '').replace('\n', '')
    params = info[info.find("{") + 1:info.find("}")].split(',')

    # scripts = soup.find_all('script')
    # info = scripts[27].text.replace(' ', '').replace('\n', '')
    # params = info[info.find("{") + 1:info.find("}")].split(',')

    curr_id = params[0].split(':')[1]

    return curr_id
