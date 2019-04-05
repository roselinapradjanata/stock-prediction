from flask import Flask

import atexit
from app.extensions import db, migrate, scheduler
from app.routes import stock, index, preprocessor, exp
from app.experiments import weekly_scheduler

scheduler.start()
atexit.register(lambda: scheduler.shutdown())


def create_app():
    app = Flask(__name__)
    app.config.from_object('config')

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(stock)
    app.register_blueprint(index)
    app.register_blueprint(preprocessor)
    app.register_blueprint(exp)

    return app
