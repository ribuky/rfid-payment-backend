from app import db
from datetime import datetime

class BiayaAdmin(db.Model):
    __tablename__ = 'biaya_admin'

    id = db.Column(db.Integer, primary_key=True)
    id_agen = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    biaya_topup = db.Column(db.Numeric(10,2), default=0)
    biaya_transaksi = db.Column(db.Numeric(10,2), default=0)

    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # Relasi tabel users
    agen = db.relationship("User", backref="biaya_admin", lazy=True)

    def __repr__(self):
        return f'<BiayaAdmin {self.id} - Agen {self.id_agen}>'
