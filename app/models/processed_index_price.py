from app.extensions import db


class ProcessedIndexPrice(db.Model):
    __tablename__ = 'processed_index_prices'

    id = db.Column(db.Integer, primary_key=True)
    index_id = db.Column(db.Integer, db.ForeignKey('indexes.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    close = db.Column(db.Integer, nullable=False)

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