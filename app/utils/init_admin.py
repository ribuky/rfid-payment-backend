from app import db, bcrypt
from app.models.user_model import User

def create_default_admin():
    """
    Membuat akun admin default jika tabel users masih kosong.
    Dipanggil sekali pada saat aplikasi startup.
    """
    try:
        # Cek jumlah user
        if User.query.count() == 0:
            hashed_password = bcrypt.generate_password_hash("admin1243").decode("utf-8")

            admin = User(
                nik_user="0000000000000000",        # placeholder NIK
                nama_user="Administrator",         # nama default
                username="admin",
                password_hash=hashed_password,
                role="admin"
            )

            db.session.add(admin)
            db.session.commit()
            print("=== Default Admin Created ===")
            print("Username : admin")
            print("Password : admin1243")
        else:
            print("Default admin skipped (users table not empty).")

    except Exception as e:
        print("Error creating default admin:", str(e))
