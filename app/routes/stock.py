from flask import Blueprint, request, jsonify
import requests
from bs4 import BeautifulSoup
from datetime import datetime

stock = Blueprint('stock', __name__)


@stock.route('/')
def hello():
    return 'Hello, World!'


@stock.route('/scrape')
def scrape():
    start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d').strftime('%m/%d/%Y')
    end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d').strftime('%m/%d/%Y')

    url = 'https://www.investing.com/instruments/HistoricalDataAjax'
    headers = {
        'user-agent': 'Chrome/71.0.3578.98',
        'x-requested-with': 'XMLHttpRequest'
    }
    payload = {
        'curr_id': '29046',
        'smlID': '2053974',
        'header': 'Jakarta Stock Exchange LQ45 Historical Data',
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
    table_rows = soup.find('tbody').find_all('tr')
    for table_row in table_rows:
        table_columns = table_row.find_all('td')
        historical_prices.append({
            'date': table_columns[0].text,
            'price': table_columns[1].text,
            'open': table_columns[2].text,
            'high': table_columns[3].text,
            'low': table_columns[4].text,
            'volume': table_columns[5].text,
            'change': table_columns[6].text
        })

    return jsonify(historical_prices)
