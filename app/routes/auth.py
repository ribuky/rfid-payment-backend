from flask import Blueprint, request, jsonify
from app.models.user_model import User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt

auth = Blueprint("auth", __name__, url_prefix="/api/auth")


# =========================
# LOGIN API
# POST /api/auth/login
# =========================
@auth.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return jsonify({"message": "Invalid JSON"}), 400

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "Username dan password wajib diisi"}), 400

    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return jsonify({"message": "Username atau password salah"}), 401

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={
            "username": user.username,
            "role": user.role
        }
    )

    return jsonify({
        "success": True,
        "access_token": access_token,
        "user": {
            "id": user.id,
            "username": user.username,
            "nama_user": user.nama_user,
            "role": user.role
        }
    }), 200

# =========================
# LOGOUT API
# POST /api/auth/logout
# =========================

@auth.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    return jsonify({
        "success": True,
        "message": "Logout berhasil (client wajib hapus token)"
    }), 200
    
@auth.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    claims = get_jwt()

    return jsonify({
        "success": True,
        "user": {
            "id": int(user_id),
            "username": claims.get("username"),
            "role": claims.get("role")
        }
    }), 200