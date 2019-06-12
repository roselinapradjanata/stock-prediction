from flask import Blueprint, jsonify

from app.models import Stock


stock = Blueprint('stocks', __name__)


@stock.route('')
def get_all_stocks():
    stocks = Stock.query.order_by(Stock.id).all()
    result = []
    for stock in stocks:
        result.append({
            'id': stock.id,
            'code': stock.code,
            'name': stock.name
        })
    return jsonify(result)
