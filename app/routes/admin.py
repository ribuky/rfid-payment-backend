from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from decimal import Decimal
from app import db
from app.models.saldo_user_model import SaldoUser
from app.models.admin_ledger_model import AdminLedger
from app.models.user_model import User

admin_bp = Blueprint(
    "admin_bp",
    __name__,
    url_prefix="/api/admin"
)

def admin_only():
    claims = get_jwt()
    return claims.get("role") == "admin"


# =====================================
# ADMIN (TOPUP SALDO AGEN)
# =====================================
@admin_bp.route("/topup-agen", methods=["POST"])
@jwt_required()
def topup_agen():
    if not admin_only():
        return jsonify({"message": "Akses ditolak"}), 403

    data = request.get_json()
    id_agen = data.get("id_agen")
    nominal = data.get("nominal")

    if not id_agen or not nominal:
        return jsonify({"message": "Data tidak lengkap"}), 400

    agen = User.query.get_or_404(id_agen)

    try:
        nominal = Decimal(str(nominal))
    except:
        return jsonify({"message": "Nominal tidak valid"}), 400

    if nominal <= 0:
        return jsonify({"message": "Nominal harus > 0"}), 400

    saldo_agen = SaldoUser.query.filter_by(id_user=agen.id).first()
    if not saldo_agen:
        saldo_agen = SaldoUser(id_user=agen.id, saldo=0)
        db.session.add(saldo_agen)

    with db.session.begin():
        saldo_agen.saldo += nominal

        ledger = AdminLedger(
            sumber="topup_agen",
            id_agen=agen.id,
            nominal=nominal
        )
        db.session.add(ledger)

    return jsonify({
        "message": "Saldo agen berhasil ditambahkan",
        "saldo_agen": float(saldo_agen.saldo)
    }), 200
    
    
# =====================================
# LAPORAN KEUANGAN ADMIN
# =====================================
@admin_bp.route("/pendapatan", methods=["GET"])
@jwt_required()
def pendapatan_admin():
    if not admin_only():
        return jsonify({"message": "Akses ditolak"}), 403

    total = db.session.query(
        db.func.sum(AdminLedger.nominal)
    ).scalar() or 0

    return jsonify({
        "total_pendapatan": float(total)
    }), 200


# =====================================
# REKAP SALDO AGEN
# =====================================
@admin_bp.route("/rekap-agen", methods=["GET"])
@jwt_required()
def rekap_agen():
    if not admin_only():
        return jsonify({"message": "Akses ditolak"}), 403

    data = db.session.query(
        User.id,
        User.username,
        SaldoUser.saldo
    ).join(
        SaldoUser, SaldoUser.id_user == User.id
    ).filter(
        User.role == "agen"
    ).all()

    return jsonify([
        {
            "id": d.id,
            "username": d.username,
            "saldo": float(d.saldo)
        } for d in data
    ]), 200
