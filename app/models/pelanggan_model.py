from app import db

class Pelanggan(db.Model):
    __tablename__ = 'pelanggan'

    id = db.Column(db.Integer, primary_key=True)
    uid_rfid = db.Column(db.String(50), unique=True, nullable=False)
    nik_pelanggan = db.Column(db.String(16), unique=True, nullable=False)
    nama_pelanggan = db.Column(db.String(100), nullable=False)
    kelas = db.Column(db.String(20))
    no_hp = db.Column(db.String(15))
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    transaksi = db.relationship('Transaksi', backref='pelanggan', lazy=True)

    def __repr__(self):
        return f"<Pelanggan {self.nama_pelanggan}>"
