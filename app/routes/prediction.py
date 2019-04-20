from flask import Blueprint

prediction = Blueprint('predictions', __name__)


@prediction.route('/<stock_code>')
def get_prediction(stock_code):
    return stock_code
