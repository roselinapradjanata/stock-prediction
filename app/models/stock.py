from app.extensions import db


class Stock(db.Model):
    __tablename__ = 'stocks'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    listing_date = db.Column(db.Date, nullable=False)
    outstanding_shares = db.Column(db.BigInteger, nullable=False)
    prices = db.relationship('StockPrice', backref='stock', lazy=True)
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
