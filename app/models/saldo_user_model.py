from app import db
from datetime import datetime

class SaldoUser(db.Model):
    __tablename__ = 'saldo_user'

    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    saldo = db.Column(db.Numeric(12,2), default=0)

    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(
        db.DateTime, default=datetime.now, onupdate=datetime.now
    )

    user = db.relationship("User", backref="saldo_user")

    def __repr__(self):
        return f"<SaldoUser user={self.id_user} saldo={self.saldo}>"
