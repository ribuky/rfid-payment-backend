from app import db
from datetime import datetime

class Saldo(db.Model):
    __tablename__ = 'saldo'

    id = db.Column(db.Integer, primary_key=True)
    id_pelanggan = db.Column(db.Integer, db.ForeignKey('pelanggan.id'), unique=True, nullable=False)

    saldo = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)

    pelanggan = db.relationship("Pelanggan", backref="saldo_record", lazy=True)

    def __repr__(self):
        return f"<Saldo pelanggan={self.id_pelanggan} saldo={self.saldo}>"
