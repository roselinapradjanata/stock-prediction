from app.extensions import db


class IndexDailyPrice(db.Model):
    __tablename__ = 'index_daily_prices'

    id = db.Column(db.Integer, primary_key=True)
    index_id = db.Column(db.Integer, db.ForeignKey('indexes.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    close = db.Column(db.Integer, nullable=False)
    open = db.Column(db.Integer, nullable=False)
    high = db.Column(db.Integer, nullable=False)
    low = db.Column(db.Integer, nullable=False)
    volume = db.Column(db.BigInteger, nullable=False)
    change = db.Column(db.Float, nullable=False)

    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def create(self):
        db.session.add(self)
        db.session.commit()

    def save(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
