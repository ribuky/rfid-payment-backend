from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models.biaya_admin_model import BiayaAdmin
from app.models.user_model import User

biaya_admin_bp = Blueprint(
    'biaya_admin_api',
    __name__,
    url_prefix='/api/biaya-admin'
)


# =========================
# GET LIST
# =========================
@biaya_admin_bp.route('', methods=['GET'])
@jwt_required()
def get_biaya_admin():
    data = BiayaAdmin.query.all()

    return jsonify([
        {
            "id": b.id,
            "id_agen": b.id_agen,
            "nama_agen": b.agen.username if b.agen else None,
            "biaya_topup": float(b.biaya_topup),
            "biaya_transaksi": float(b.biaya_transaksi)
        } for b in data
    ]), 200


# =========================
# ADD
# =========================
@biaya_admin_bp.route('', methods=['POST'])
@jwt_required()
def add_biaya_admin():
    data = request.get_json()

    if not data.get('id_agen'):
        return jsonify({"message": "Agen harus dipilih"}), 400

    biaya = BiayaAdmin(
        id_agen=data['id_agen'],
        biaya_topup=data.get('biaya_topup', 0),
        biaya_transaksi=data.get('biaya_transaksi', 0)
    )

    db.session.add(biaya)
    db.session.commit()

    return jsonify({"message": "Biaya transaksi berhasil ditambahkan"}), 201


# =========================
# DETAIL
# =========================
@biaya_admin_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_biaya_admin_detail(id):
    b = BiayaAdmin.query.get_or_404(id)

    return jsonify({
        "id": b.id,
        "id_agen": b.id_agen,
        "biaya_topup": float(b.biaya_topup),
        "biaya_transaksi": float(b.biaya_transaksi)
    }), 200


# =========================
# UPDATE
# =========================
@biaya_admin_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_biaya_admin(id):
    b = BiayaAdmin.query.get_or_404(id)
    data = request.get_json()

    b.id_agen = data.get('id_agen', b.id_agen)
    b.biaya_topup = data.get('biaya_topup', b.biaya_topup)
    b.biaya_transaksi = data.get('biaya_transaksi', b.biaya_transaksi)

    db.session.commit()

    return jsonify({"message": "Biaya transaksi berhasil diperbarui"}), 200


# =========================
# DELETE
# =========================
@biaya_admin_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_biaya_admin(id):
    b = BiayaAdmin.query.get_or_404(id)

    db.session.delete(b)
    db.session.commit()

    return jsonify({"message": "Biaya transaksi berhasil dihapus"}), 200
