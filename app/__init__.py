from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    CORS(
        app,
        resources={r"/api/*": {"origins": "*"}},
        supports_credentials=True
    )

    # =========================
    # REGISTER BLUEPRINTS
    # =========================
    from app.routes.auth import auth
    from app.routes.user import user_bp
    from app.routes.pelanggan import pelanggan_bp
    from app.routes.tapping import tapping_bp
    from app.routes.biaya_admin import biaya_admin_bp
    from app.routes.transaksi import transaksi_bp

    app.register_blueprint(auth)
    app.register_blueprint(user_bp)
    app.register_blueprint(pelanggan_bp)
    app.register_blueprint(tapping_bp)
    app.register_blueprint(biaya_admin_bp)
    app.register_blueprint(transaksi_bp)

    # =========================
    # DB INIT
    # =========================
    from app.utils.init_admin import create_default_admin
    with app.app_context():
        db.create_all()
        create_default_admin()

    return app
