def create_default_admin():
    from app.models.user_model import User
    from app import db

    admin = User.query.filter_by(username="admin").first()
    if not admin:
        admin = User(
            nik_user="0000000000000000",
            nama_user="Administrator",
            username="admin",
            role="admin"
        )
        admin.password = "admin123"
        db.session.add(admin)
        db.session.commit()
