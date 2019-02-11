from flask import Flask

from app.extensions import db, migrate, scheduler
from app.routes import stock


def create_app():
    app = Flask(__name__)
    app.config.from_object('config')

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(stock)

    return app
