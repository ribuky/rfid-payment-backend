from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models.pelanggan_model import Pelanggan
from app.models.saldo_model import Saldo
from app import db

pelanggan_bp = Blueprint('pelanggan_api', __name__, url_prefix='/api/pelanggan')


# =========================
# GET LIST + SEARCH
# =========================
@pelanggan_bp.route('', methods=['GET'])
@jwt_required()
def get_pelanggan():
    q = request.args.get('q')

    query = Pelanggan.query

    if q:
        query = query.filter(
            (Pelanggan.nik_pelanggan.like(f"%{q}%")) |
            (Pelanggan.uid_rfid.like(f"%{q}%"))
        )

    data = query.all()

    return jsonify([
        {
            "id": p.id,
            "uid": p.uid_rfid,
            "nik": p.nik_pelanggan,
            "nama": p.nama_pelanggan,
            "kelas": p.kelas,
            "no_hp": p.no_hp
        } for p in data
    ]), 200


# =========================
# ADD PELANGGAN
# =========================
@pelanggan_bp.route('', methods=['POST'])
@jwt_required()
def add_pelanggan():
    data = request.get_json()

    pelanggan = Pelanggan(
        uid_rfid=data.get('uid'),
        nik_pelanggan=data['nik'],
        nama_pelanggan=data['nama'],
        kelas=data['kelas'],
        no_hp=data['no_hp']
    )

    db.session.add(pelanggan)
    db.session.commit()

    saldo = Saldo(
        id_pelanggan=pelanggan.id,
        saldo=0
    )
    db.session.add(saldo)
    db.session.commit()

    return jsonify({"message": "Pelanggan berhasil ditambahkan"}), 201


# =========================
# GET DETAIL
# =========================
@pelanggan_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_pelanggan_detail(id):
    p = Pelanggan.query.get_or_404(id)

    saldo = Saldo.query.filter_by(id_pelanggan=p.id).first()

    return jsonify({
        "id": p.id,
        "uid": p.uid_rfid,
        "nik": p.nik_pelanggan,
        "nama": p.nama_pelanggan,
        "kelas": p.kelas,
        "no_hp": p.no_hp,
        "saldo": saldo.saldo if saldo else 0
    }), 200


# =========================
# UPDATE
# =========================
@pelanggan_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_pelanggan(id):
    p = Pelanggan.query.get_or_404(id)
    data = request.get_json()

    p.nik_pelanggan = data['nik']
    p.nama_pelanggan = data['nama']
    p.kelas = data['kelas']
    p.no_hp = data['no_hp']

    db.session.commit()

    return jsonify({"message": "Pelanggan berhasil diperbarui"}), 200


# =========================
# DELETE
# =========================
@pelanggan_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_pelanggan(id):
    p = Pelanggan.query.get_or_404(id)

    Saldo.query.filter_by(id_pelanggan=p.id).delete()
    db.session.delete(p)
    db.session.commit()

    return jsonify({"message": "Pelanggan berhasil dihapus"}), 200
