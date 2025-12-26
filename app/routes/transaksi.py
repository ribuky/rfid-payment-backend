from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from openpyxl import Workbook
from sqlalchemy import or_, extract
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from app import db
from io import BytesIO
from decimal import Decimal
from app.models.saldo_model import Saldo
from app.models.biaya_admin_model import BiayaAdmin
from app.models.transakasi_model import Transaksi
from app.models.pelanggan_model import Pelanggan
from app.models.user_model import User
from app.models.admin_ledger_model import AdminLedger
from app.models.saldo_user_model import SaldoUser

transaksi_bp = Blueprint(
    'transaksi_bp',
    __name__,
    url_prefix='/api/transaksi'
)

def build_transaksi_query(user_id, filter_type, search):
    query = Transaksi.query.join(Pelanggan).filter(
        Transaksi.id_user == user_id
    )

    today = datetime.today()

    if filter_type == "today":
        query = query.filter(
            extract('year', Transaksi.waktu_transaksi) == today.year,
            extract('month', Transaksi.waktu_transaksi) == today.month,
            extract('day', Transaksi.waktu_transaksi) == today.day
        )

    elif filter_type == "week":
        start_week = today - timedelta(days=today.weekday())
        end_week = start_week + timedelta(days=6)
        query = query.filter(
            Transaksi.waktu_transaksi >= start_week,
            Transaksi.waktu_transaksi <= end_week
        )

    elif filter_type == "month":
        query = query.filter(
            extract('year', Transaksi.waktu_transaksi) == today.year,
            extract('month', Transaksi.waktu_transaksi) == today.month
        )

    if search:
        query = query.filter(
            db.or_(
                Pelanggan.nama_pelanggan.ilike(f"%{search}%"),
                Pelanggan.nik_pelanggan.ilike(f"%{search}%")
            )
        )

    return query

# =====================================
# TOPUP SALDO PELANGGAN
# =====================================
@transaksi_bp.route('/topup/<int:id_pelanggan>', methods=['POST'])
@jwt_required()
def topup_pelanggan(id_pelanggan):
    user_id = int(get_jwt_identity())

    pelanggan = Pelanggan.query.get_or_404(id_pelanggan)

    saldo_agen = SaldoUser.query.filter_by(id_user=user_id).first()
    if not saldo_agen or saldo_agen.saldo <= 0:
        return jsonify({"message": "Saldo agen tidak mencukupi"}), 400

    biaya_admin = BiayaAdmin.query.filter_by(id_agen=user_id).first()
    biaya = Decimal(biaya_admin.biaya_topup) if biaya_admin else Decimal(0)

    data = request.get_json()
    nominal = Decimal(str(data.get("nominal", 0)))

    if nominal <= 0:
        return jsonify({"message": "Nominal tidak valid"}), 400

    saldo_masuk = nominal - biaya
    if saldo_masuk < 0:
        return jsonify({"message": "Nominal < biaya admin"}), 400

    if saldo_agen.saldo < nominal:
        return jsonify({"message": "Saldo agen tidak cukup"}), 400

    saldo_pelanggan = Saldo.query.filter_by(id_pelanggan=pelanggan.id).first()
    if not saldo_pelanggan:
        saldo_pelanggan = Saldo(id_pelanggan=pelanggan.id, saldo=0)
        db.session.add(saldo_pelanggan)

    with db.session.begin():
        saldo_agen.saldo -= nominal
        saldo_pelanggan.saldo += saldo_masuk

        db.session.add(Transaksi(
            id_pelanggan=pelanggan.id,
            id_user=user_id,
            transaksi_masuk=saldo_masuk,
            transaksi_keluar=0
        ))

        if biaya > 0:
            db.session.add(AdminLedger(
                sumber="topup",
                id_agen=user_id,
                id_pelanggan=pelanggan.id,
                nominal=biaya
            ))

    return jsonify({
        "message": "Topup berhasil",
        "saldo_pelanggan": float(saldo_pelanggan.saldo),
        "saldo_agen": float(saldo_agen.saldo),
        "biaya_admin": float(biaya)
    }), 200


@transaksi_bp.route('/topup/<int:id_pelanggan>', methods=['GET'])
@jwt_required()
def get_info_topup(id_pelanggan):
    user_id = get_jwt_identity()

    pelanggan = Pelanggan.query.get_or_404(id_pelanggan)

    biaya_admin = BiayaAdmin.query.filter_by(id_agen=user_id).first()

    saldo_record = Saldo.query.filter_by(id_pelanggan=id_pelanggan).first()

    return jsonify({
        "pelanggan": {
            "id": pelanggan.id,
            "nama": pelanggan.nama_pelanggan,
            "nik": pelanggan.nik_pelanggan
        },
        "saldo": float(saldo_record.saldo) if saldo_record else 0,
        "biaya_admin": float(biaya_admin.biaya_topup) if biaya_admin else 0
    }), 200

# =====================================
# INFO PEMBELIAN PELANGGAN
# =====================================
@transaksi_bp.route('/pembelian/<int:id_pelanggan>', methods=['GET'])
@jwt_required()
def get_info_pembelian(id_pelanggan):
    user_id = get_jwt_identity()

    pelanggan = Pelanggan.query.get(id_pelanggan)
    if not pelanggan:
        return jsonify({"message": "Pelanggan tidak ditemukan"}), 404

    saldo_record = Saldo.query.filter_by(id_pelanggan=pelanggan.id).first()
    if not saldo_record:
        return jsonify({"message": "Saldo pelanggan belum tersedia"}), 400

    biaya_admin = BiayaAdmin.query.filter_by(id_agen=user_id).first()
    biaya_transaksi = Decimal(biaya_admin.biaya_transaksi) if biaya_admin else Decimal(0)

    return jsonify({
        "pelanggan": {
            "id": pelanggan.id,
            "uid": pelanggan.uid_rfid,
            "nama": pelanggan.nama_pelanggan,
            "nik": pelanggan.nik_pelanggan,
            "kelas": pelanggan.kelas,
            "no_hp": pelanggan.no_hp
        },
        "saldo": float(saldo_record.saldo),
        "biaya_transaksi": float(biaya_transaksi)
    }), 200
    
@transaksi_bp.route('/pembelian/<int:id_pelanggan>', methods=['POST'])
@jwt_required()
def proses_pembelian(id_pelanggan):
    user_id = int(get_jwt_identity())

    pelanggan = Pelanggan.query.get_or_404(id_pelanggan)

    saldo_pelanggan = Saldo.query.filter_by(id_pelanggan=pelanggan.id).first()
    saldo_agen = SaldoUser.query.filter_by(id_user=user_id).first()

    if not saldo_pelanggan or saldo_pelanggan.saldo <= 0:
        return jsonify({"message": "Saldo pelanggan tidak cukup"}), 400

    if not saldo_agen:
        saldo_agen = SaldoUser(id_user=user_id, saldo=0)
        db.session.add(saldo_agen)

    biaya_admin = BiayaAdmin.query.filter_by(id_agen=user_id).first()
    biaya = Decimal(biaya_admin.biaya_transaksi) if biaya_admin else Decimal(0)

    data = request.get_json()
    nominal = Decimal(str(data.get("nominal", 0)))

    total = nominal + biaya

    if saldo_pelanggan.saldo < total:
        return jsonify({"message": "Saldo pelanggan tidak mencukupi"}), 400

    with db.session.begin():
        saldo_pelanggan.saldo -= total
        saldo_agen.saldo += nominal

        db.session.add(Transaksi(
            id_pelanggan=pelanggan.id,
            id_user=user_id,
            transaksi_keluar=total,
            transaksi_masuk=0
        ))

        if biaya > 0:
            db.session.add(AdminLedger(
                sumber="pembelian",
                id_agen=user_id,
                id_pelanggan=pelanggan.id,
                nominal=biaya
            ))

    return jsonify({
        "message": "Pembayaran berhasil",
        "saldo_pelanggan": float(saldo_pelanggan.saldo),
        "saldo_agen": float(saldo_agen.saldo),
        "biaya_admin": float(biaya)
    }), 200


# =====================================
# RIWAYAT TRANSAKSI ADMIN / AGEN
# =====================================
@transaksi_bp.route('/riwayat', methods=['GET'])
@jwt_required()
def riwayat_transaksi_user():
    user_id = get_jwt_identity()
    filter_type = request.args.get('filter', 'all')
    search = request.args.get('q', '')

    query = build_transaksi_query(user_id, filter_type, search)

    data = query.order_by(Transaksi.waktu_transaksi.desc()).all()

    return jsonify([
        {
            "id": t.id,
            "pelanggan": {
                "nama": t.pelanggan.nama_pelanggan,
                "nik": t.pelanggan.nik_pelanggan
            },
            "transaksi_masuk": float(t.transaksi_masuk),
            "transaksi_keluar": float(t.transaksi_keluar),
            "waktu": t.waktu_transaksi.strftime('%Y-%m-%d %H:%M:%S')
        } for t in data
    ]), 200


# =====================================
# RIWAYAT TRANSAKSI PER PELANGGAN
# =====================================
@transaksi_bp.route('/pelanggan/<int:id_pelanggan>', methods=['GET'])
@jwt_required()
def riwayat_transaksi_pelanggan(id_pelanggan):
    Pelanggan.query.get_or_404(id_pelanggan)

    data = Transaksi.query.filter_by(id_pelanggan=id_pelanggan)\
                          .order_by(Transaksi.id.desc())\
                          .all()

    return jsonify([
        {
            "id": t.id,
            "transaksi_masuk": float(t.transaksi_masuk),
            "transaksi_keluar": float(t.transaksi_keluar),
            "waktu": t.waktu_transaksi.strftime('%Y-%m-%d %H:%M:%S'),
            "user": t.user.username
        } for t in data
    ]), 200


# =====================================
# LAPORAN KEUANGAN BULANAN
# =====================================
@transaksi_bp.route('/laporan', methods=['GET'])
@jwt_required()
def laporan_bulanan():
    year = int(request.args.get('year', datetime.today().year))
    month = int(request.args.get('month', datetime.today().month))

    total_topup = db.session.query(
        db.func.sum(Transaksi.transaksi_masuk)
    ).filter(
        extract('year', Transaksi.waktu_transaksi) == year,
        extract('month', Transaksi.waktu_transaksi) == month
    ).scalar() or 0

    total_pembelian = db.session.query(
        db.func.sum(Transaksi.transaksi_keluar)
    ).filter(
        extract('year', Transaksi.waktu_transaksi) == year,
        extract('month', Transaksi.waktu_transaksi) == month
    ).scalar() or 0

    return jsonify({
        "year": year,
        "month": month,
        "total_topup": float(total_topup),
        "total_pembelian": float(total_pembelian)
    }), 200

# =====================================
# EXPORT LAPORAN KEUANGAN EXCEL
# =====================================
@transaksi_bp.route('/export/excel')
@jwt_required()
def export_transaksi_excel():
    user_id = get_jwt_identity()
    filter_type = request.args.get('filter', 'all')
    search = request.args.get('q', '')

    transaksi = build_transaksi_query(
        user_id, filter_type, search
    ).order_by(Transaksi.waktu_transaksi.desc()).all()

    wb = Workbook()
    ws = wb.active
    ws.title = "Riwayat Transaksi"

    ws.append(["Tanggal", "Nama", "NIK", "Masuk", "Keluar"])

    for t in transaksi:
        ws.append([
            t.waktu_transaksi.strftime("%Y-%m-%d %H:%M"),
            t.pelanggan.nama_pelanggan,
            t.pelanggan.nik_pelanggan,
            float(t.transaksi_masuk),
            float(t.transaksi_keluar)
        ])

    stream = BytesIO()
    wb.save(stream)
    stream.seek(0)

    return send_file(
        stream,
        as_attachment=True,
        download_name="riwayat_transaksi.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


# =====================================
# EXPORT LAPORAN KEUANGAN PDF
# =====================================
@transaksi_bp.route('/export/pdf')
@jwt_required()
def export_transaksi_pdf():
    user_id = get_jwt_identity()
    filter_type = request.args.get('filter', 'all')
    search = request.args.get('q', '')

    transaksi = build_transaksi_query(
        user_id, filter_type, search
    ).order_by(Transaksi.waktu_transaksi.desc()).all()

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 50
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y, "Riwayat Transaksi")
    y -= 30

    pdf.setFont("Helvetica", 10)

    for t in transaksi:
        if y < 60:
            pdf.showPage()
            y = height - 50

        pdf.drawString(50, y, f"{t.waktu_transaksi.strftime('%Y-%m-%d %H:%M')}")
        y -= 14
        pdf.drawString(
            50, y,
            f"{t.pelanggan.nama_pelanggan} ({t.pelanggan.nik_pelanggan})"
        )
        y -= 14
        pdf.drawString(
            50, y,
            f"Masuk: Rp {t.transaksi_masuk} | Keluar: Rp {t.transaksi_keluar}"
        )
        y -= 22

    pdf.save()
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="riwayat_transaksi.pdf",
        mimetype="application/pdf"
    )

