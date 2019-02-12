from flask import Blueprint, jsonify
from bs4 import BeautifulSoup
from datetime import datetime
import requests

from app.models import Index

index = Blueprint('index', __name__)


@index.route('/scrape/index')
def scrape_all_index_prices():
    print('Index list update start')

    url = 'https://www.investing.com/indices/indonesia-indices'
    headers = {
        'user-agent': 'Chrome/71.0.3578.98'
    }

    r = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')

    index_list = soup.find(id='cr1').find('tbody').find_all('tr')

    for idx, index_data in enumerate(index_list):
        href = index_data.find('a')['href']
        scrape_id = int(index_data.find_all('span')[1]['data-id'])

        url = 'https://www.investing.com' + href

        r = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')

        title = soup.title.text
        code = title[title.find("(") + 1:title.find(")")]
        name = title.split(' Index ')[0]

        index = Index.query.filter_by(code=code).first()
        if index:
            index.scrape_id = scrape_id
            index.save()
            print('Updated index %s (%d/%d)' % (code, idx + 1, len(index_list)))
        else:
            Index(code=code, name=name, scrape_id=scrape_id).create()
            print('Inserted index %s (%d/%d)' % (code, idx + 1, len(index_list)))

    print('Index list updated on %s' % (str(datetime.now())))
    return 'Finished'
