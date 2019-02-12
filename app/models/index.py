from app.extensions import db


class Index(db.Model):
    __tablename__ = 'indexes'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    scrape_id = db.Column(db.Integer, nullable=True)

    daily_prices = db.relationship('IndexDailyPrice', backref='index', lazy=True)

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
