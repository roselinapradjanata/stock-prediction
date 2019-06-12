from flask import Blueprint, jsonify, request

from app.models import Stock
from app.experiments.stock_scraper import scrape_daily_prices
from app.experiments.testing import test_model, test_model_tl
from app.experiments.evaluator import evaluate


prediction = Blueprint('predictions', __name__)


@prediction.route('/<stock_code>')
def get_prediction(stock_code):
    days = int(request.args.get('days', 1))

    stock = Stock.query.filter_by(code=stock_code.upper()).first()
    if not stock or not stock.daily_prices:
        return jsonify({'code': 404, 'message': 'Stock code not found'}), 404

    scrape_daily_prices(stock)
    date, test_predict, y_test = test_model(stock.code, days)
    scores = evaluate(test_predict, y_test, days)

    display_days = 30
    date = list(map(lambda x: x.strftime('%Y-%m-%d'), date[-display_days:].flatten().tolist()))
    prediction_date = date + ['Day %d' % (display_days + x) for x in range(1, days + 1)]
    actual = y_test[-display_days:].flatten().tolist()
    predicted = test_predict[-(display_days + days):].flatten().tolist()

    actual = list(map(lambda x: {'date': x[0], 'price': int(x[1])}, zip(date, actual)))
    predicted = list(map(lambda x: {'date': x[0], 'price': int(x[1])}, zip(prediction_date, predicted)))

    return jsonify({
        'scores': scores,
        'actual': actual,
        'predicted': predicted
    })


@prediction.route('/tl/<stock_code>')
def get_prediction_tl(stock_code):
    days = int(request.args.get('days', 1))

    stock = Stock.query.filter_by(code=stock_code.upper()).first()
    if not stock or not stock.daily_prices:
        return jsonify({'code': 404, 'message': 'Stock code not found'}), 404

    scrape_daily_prices(stock)
    date, test_predict, y_test = test_model_tl(stock.code, days)
    scores = evaluate(test_predict, y_test, days)

    display_days = 30
    date = list(map(lambda x: x.strftime('%Y-%m-%d'), date[-display_days:].flatten().tolist()))
    prediction_date = date + ['Day %d' % (display_days + x) for x in range(1, days + 1)]
    actual = y_test[-display_days:].flatten().tolist()
    predicted = test_predict[-(display_days + days):].flatten().tolist()

    actual = list(map(lambda x: {'date': x[0], 'price': int(x[1])}, zip(date, actual)))
    predicted = list(map(lambda x: {'date': x[0], 'price': int(x[1])}, zip(prediction_date, predicted)))

    return jsonify({
        'scores': scores,
        'actual': actual,
        'predicted': predicted
    })
