from flask import Flask
from flask_cors import CORS

import atexit
from app.extensions import db, migrate, scheduler
from app.routes import prediction, stock
from app.experiments import system_scheduler

# scheduler.start()
# atexit.register(lambda: scheduler.shutdown())


def create_app():
    app = Flask(__name__)
    app.config.from_object('config')
    CORS(app)

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(prediction, url_prefix='/api/v1/predictions')
    app.register_blueprint(stock, url_prefix='/api/v1/stocks')

    return app
