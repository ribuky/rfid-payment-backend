from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from app.models.user_model import User
from app import db

user_bp = Blueprint('user_api', __name__, url_prefix='/api/users')


def admin_only():
    claims = get_jwt()
    return claims.get("role") == "admin"


# ============================
# GET ALL USERS (ADMIN)
# ============================
@user_bp.route('', methods=['GET'])
@jwt_required()
def get_users():
    if not admin_only():
        return jsonify({"message": "Akses ditolak"}), 403

    users = User.query.all()
    return jsonify([
        {
            "id": u.id,
            "nik": u.nik_user,
            "nama": u.nama_user,
            "username": u.username,
            "role": u.role
        } for u in users
    ]), 200


# ============================
# ADD USER
# ============================
@user_bp.route('', methods=['POST'])
@jwt_required()
def add_user():
    if not admin_only():
        return jsonify({"message": "Akses ditolak"}), 403

    data = request.get_json()

    if User.query.filter_by(username=data['username']).first():
        return jsonify({"message": "Username sudah digunakan"}), 400

    user = User(
        nik_user=data['nik'],
        nama_user=data['nama'],
        username=data['username'],
        role=data['role']
    )
    user.set_password(data['password'])

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User berhasil ditambahkan"}), 201


# ============================
# UPDATE USER
# ============================
@user_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_user(id):
    if not admin_only():
        return jsonify({"message": "Akses ditolak"}), 403

    user = User.query.get_or_404(id)
    data = request.get_json()

    user.nik_user = data['nik']
    user.nama_user = data['nama']
    user.username = data['username']
    user.role = data['role']

    if data.get('password'):
        user.set_password(data['password'])

    db.session.commit()
    return jsonify({"message": "User berhasil diperbarui"}), 200


# ============================
# DELETE USER
# ============================
@user_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_user(id):
    if not admin_only():
        return jsonify({"message": "Akses ditolak"}), 403

    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "User berhasil dihapus"}), 200
