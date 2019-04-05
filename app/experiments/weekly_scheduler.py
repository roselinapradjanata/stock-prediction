from datetime import datetime
from app.extensions import scheduler

from .index_scraper import start_index_scraper
from .stock_scraper import start_stock_scraper
from .experiment import train_model


@scheduler.scheduled_job('interval', weeks=1, next_run_time=datetime.now())
def start_weekly_scheduler():
    from app import create_app
    app = create_app()

    with app.app_context():
        start_index_scraper()
        start_stock_scraper()
        train_model()
