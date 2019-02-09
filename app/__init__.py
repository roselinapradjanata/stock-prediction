from flask import Flask
import atexit

from app.extensions import db, migrate, scheduler
from app.routes import stock
from app.models import Stock, StockPrice


def create_app():
    app = Flask(__name__)
    app.config.from_object('config')

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(stock)

    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())

    return app
