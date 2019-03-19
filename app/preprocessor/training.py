from flask import jsonify
from datetime import datetime, timedelta
from app.models import Index, IndexPrice, ProcessedIndexPrice


def preprocessed(index):
    latest_price = IndexPrice.query.join(Index).filter(Index.code == index.code).order_by(IndexPrice.date.desc()).first()

    start_date = (datetime.combine(latest_price.date, datetime.min.time()) + timedelta(days=1) if latest_price else datetime(2000, 1, 1)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')

    index_prices = IndexPrice.query.join(Index).filter(Index.code == 'LQ45', IndexPrice.date >= start_date, IndexPrice.date <= end_date).order_by(IndexPrice.date)
    return jsonify(index_prices)
