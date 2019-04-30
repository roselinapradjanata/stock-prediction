from flask import Blueprint, jsonify

from app.models import Stock
from app.experiments.stock_scraper import scrape_daily_prices
from app.experiments.testing import test_model
from app.experiments.evaluator import evaluate


prediction = Blueprint('predictions', __name__)


@prediction.route('/<stock_code>')
def get_prediction(stock_code):
    stock = Stock.query.filter_by(code=stock_code).first()
    if not stock or not stock.daily_prices:
        return jsonify({'code': 404, 'message': 'Stock code not found'}), 404
    scrape_daily_prices(stock)
    test_predict, y_test = test_model(stock.code)
    scores = evaluate(test_predict, y_test)
    [next_day_prediction] = test_predict[-1]
    return jsonify({'prediction': str(int(next_day_prediction)), 'scores': scores})
