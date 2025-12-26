from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash
from flask_jwt_extended import jwt_required
from flask_login import login_required
from app.models.pelanggan_model import Pelanggan
from app.models.saldo_model import Saldo
from app import db
import os

tapping_bp = Blueprint('tapping', __name__)

# ================================
# PATH FILE last_uid.txt
# ================================
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LAST_UID_PATH = os.path.join(ROOT_DIR, "last_uid.txt")
# Debug:
print("[DEBUG] UID File Path:", LAST_UID_PATH)


# ================================
# HELPER UNTUK UID
# ================================
def write_uid(uid):
    with open(LAST_UID_PATH, "w") as f:
        f.write(uid)


def read_uid():
    if not os.path.exists(LAST_UID_PATH):
        return None
    with open(LAST_UID_PATH, "r") as f:
        return f.read().strip() or None


def clear_uid_file():
    with open(LAST_UID_PATH, "w") as f:
        f.write("")


# ================================
# ESP32 KIRIM UID (POST /api/set_uid)
# ================================
@tapping_bp.route('/api/set_uid', methods=['POST'])
def tapping_receive():
    data = request.get_json()
    uid = data.get('uid')

    if not uid:
        return jsonify({"status": "error", "message": "UID tidak diberikan"}), 400

    write_uid(uid)
    print("[ESP32] UID diterima:", uid)

    return jsonify({"status": "success"})


# ================================
# DASHBOARD REQUESTS UID HERE
# ================================
@tapping_bp.route('/api/last_uid', methods=['GET'])
@jwt_required()
def get_last_uid():
    uid = read_uid()
    return jsonify({"uid": uid})


# ================================
# CLEAR LAST UID
# ================================
@tapping_bp.route('/api/clear_uid', methods=['GET'])
@jwt_required()
def clear_uid():
    clear_uid_file()
    return jsonify({"status": "cleared"})


# ================================
# AUTO REDIRECT PAGE /tapping/<uid>
# ================================
@tapping_bp.route('/api/tapping/<key>', methods=['GET'])
@jwt_required()
def api_tapping_detail(key):
    pelanggan = Pelanggan.query.filter(
        (Pelanggan.uid_rfid == key) |
        (Pelanggan.nik_pelanggan == key)
    ).first()

    if not pelanggan:
        return jsonify({
            "success": False,
            "message": "Pelanggan tidak ditemukan"
        }), 404

    saldo_record = Saldo.query.filter_by(id_pelanggan=pelanggan.id).first()

    if not saldo_record:
        saldo_record = Saldo(
            id_pelanggan=pelanggan.id,
            saldo=0
        )
        db.session.add(saldo_record)
        db.session.commit()

    return jsonify({
        "success": True,
        "pelanggan": {
            "id": pelanggan.id,
            "uid": pelanggan.uid_rfid,
            "nama": pelanggan.nama_pelanggan,
            "nik": pelanggan.nik_pelanggan,
            "kelas": pelanggan.kelas,
            "no_hp": pelanggan.no_hp
        },
        "saldo": float(saldo_record.saldo)
    }), 200

    
