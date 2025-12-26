from app import db
from datetime import datetime

class Transaksi(db.Model):
    __tablename__ = 'transaksi'

    id = db.Column(db.Integer, primary_key=True)
    id_pelanggan = db.Column(db.Integer, db.ForeignKey('pelanggan.id'), nullable=False)
    id_user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    transaksi_keluar = db.Column(db.Numeric(10,2), default=0)
    transaksi_masuk = db.Column(db.Numeric(10,2), default=0)

    waktu_transaksi = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Transaksi {self.id}>"
