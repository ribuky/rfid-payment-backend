from app import db
from datetime import datetime

class AdminLedger(db.Model):
    __tablename__ = 'admin_ledger'

    id = db.Column(db.Integer, primary_key=True)
    sumber = db.Column(
        db.Enum('topup', 'pembelian', 'topup_agen'),
        nullable=False
    )

    id_agen = db.Column(db.Integer, db.ForeignKey('users.id'))
    id_pelanggan = db.Column(db.Integer, db.ForeignKey('pelanggan.id'))

    nominal = db.Column(db.Numeric(12,2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    agen = db.relationship("User", lazy=True)
    pelanggan = db.relationship("Pelanggan", lazy=True)

    def __repr__(self):
        return f"<AdminLedger {self.sumber} Rp{self.nominal}>"
