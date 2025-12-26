from app import db, bcrypt

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    nik_user = db.Column(db.String(16), unique=True, nullable=False)
    nama_user = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('admin', 'agen'), nullable=False)
    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )

    transaksi = db.relationship('Transaksi', backref='user', lazy=True)

    @property
    def password(self):
        raise AttributeError("Password tidak bisa diakses langsung")

    @password.setter
    def password(self, password_plain):
        self.password_hash = bcrypt.generate_password_hash(
            password_plain
        ).decode("utf-8")

    def check_password(self, password_plain):
        return bcrypt.check_password_hash(
            self.password_hash,
            password_plain
        )

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "nama_user": self.nama_user,
            "role": self.role
        }

    def __repr__(self):
        return f"<User {self.username}>"
