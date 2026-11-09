
import os
import sqlite3
from functools import wraps
from pathlib import Path

from flask import (
    Flask, jsonify, request, send_from_directory,
    session, redirect, url_for
)

from backend.database import init_db, get_db, create_default_admin

ROOT = Path(__file__).resolve().parent
FRONTEND = ROOT / "frontend"

app = Flask(__name__, static_folder=None)

app.config.update(
    SECRET_KEY=os.environ.get(
        "SECRET_KEY", "dev-only-change-this-secret-key"
    ),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "0") == "1",
    PERMANENT_SESSION_LIFETIME=60 * 60 * 8,
)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            if request.path.startswith("/api/"):
                return jsonify({
                    "error": "Sesi login tidak ditemukan. Silakan login kembali."
                }), 401
            return redirect(url_for("login_page"))
        return view(*args, **kwargs)
    return wrapped


@app.get("/")
def index():
    if not session.get("user_id"):
        return redirect(url_for("login_page"))
    return send_from_directory(FRONTEND, "index.html")


@app.get("/login")
def login_page():
    if session.get("user_id"):
        return redirect(url_for("index"))
    return send_from_directory(FRONTEND, "login.html")


@app.get("/css/<path:filename>")
def css_files(filename):
    return send_from_directory(FRONTEND / "css", filename)


@app.get("/js/<path:filename>")
def js_files(filename):
    return send_from_directory(FRONTEND / "js", filename)


@app.post("/api/login")
def login():
    data = request.get_json(silent=True) or {}

    username = str(data.get("username", "")).strip()
    password = str(data.get("password", ""))

    if not username or not password:
        return jsonify({
            "error": "Username dan password wajib diisi"
        }), 400

    with get_db() as db:
        user = db.execute(
            """
            SELECT id, username, password
            FROM users
            WHERE username = ?
            """,
            (username,)
        ).fetchone()

    # Validasi password tanpa hashing
    if user is None or user["password"] != password:
        return jsonify({
            "error": "Username atau password salah"
        }), 401

    session.clear()
    session["user_id"] = user["id"]
    session["username"] = user["username"]
    session.permanent = True

    return jsonify({
        "message": "Login berhasil",
        "username": user["username"]
    })


@app.post("/api/logout")
@login_required
def logout():
    session.clear()
    return jsonify({"message": "Logout berhasil"})


@app.get("/api/session")
def check_session():
    if not session.get("user_id"):
        return jsonify({"authenticated": False}), 401

    return jsonify({
        "authenticated": True,
        "username": session.get("username")
    })


@app.get("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "message": "Lab Inventory API is running"
    })


@app.get("/api/items")
@login_required
def list_items():
    search = request.args.get("search", "").strip()
    condition = request.args.get("condition", "").strip()
    category = request.args.get("category", "").strip()

    sql = """
        SELECT id, code, name, category, quantity, unit, location,
               condition, notes, created_at, updated_at
        FROM items
        WHERE (code LIKE ? OR name LIKE ? OR category LIKE ?)
          AND (? = '' OR condition = ?)
          AND (? = '' OR category = ?)
        ORDER BY updated_at DESC, id DESC
    """

    pattern = f"%{search}%"

    with get_db() as db:
        rows = db.execute(sql, (
            pattern, pattern, pattern,
            condition, condition,
            category, category
        )).fetchall()

    return jsonify([dict(row) for row in rows])


@app.get("/api/items/<int:item_id>")
@login_required
def get_item(item_id):
    with get_db() as db:
        row = db.execute(
            "SELECT * FROM items WHERE id = ?",
            (item_id,)
        ).fetchone()

    if row is None:
        return jsonify({"error": "Barang tidak ditemukan"}), 404

    return jsonify(dict(row))


@app.post("/api/items")
@login_required
def create_item():
    data = request.get_json(silent=True) or {}
    error = validate_item(data)

    if error:
        return jsonify({"error": error}), 400

    try:
        with get_db() as db:
            cursor = db.execute("""
                INSERT INTO items
                (code, name, category, quantity, unit, location, condition, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, item_values(data))

            row = db.execute(
                "SELECT * FROM items WHERE id = ?",
                (cursor.lastrowid,)
            ).fetchone()

        return jsonify(dict(row)), 201

    except sqlite3.IntegrityError:
        return jsonify({
            "error": "Kode inventaris sudah digunakan"
        }), 409


@app.put("/api/items/<int:item_id>")
@login_required
def update_item(item_id):
    data = request.get_json(silent=True) or {}
    error = validate_item(data)

    if error:
        return jsonify({"error": error}), 400

    try:
        with get_db() as db:
            existing = db.execute(
                "SELECT id FROM items WHERE id = ?",
                (item_id,)
            ).fetchone()

            if existing is None:
                return jsonify({
                    "error": "Barang tidak ditemukan"
                }), 404

            db.execute("""
                UPDATE items
                SET code = ?, name = ?, category = ?, quantity = ?, unit = ?,
                    location = ?, condition = ?, notes = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (*item_values(data), item_id))

            row = db.execute(
                "SELECT * FROM items WHERE id = ?",
                (item_id,)
            ).fetchone()

        return jsonify(dict(row))

    except sqlite3.IntegrityError:
        return jsonify({
            "error": "Kode inventaris sudah digunakan"
        }), 409


@app.delete("/api/items/<int:item_id>")
@login_required
def delete_item(item_id):
    with get_db() as db:
        cursor = db.execute(
            "DELETE FROM items WHERE id = ?",
            (item_id,)
        )

    if cursor.rowcount == 0:
        return jsonify({"error": "Barang tidak ditemukan"}), 404

    return jsonify({"message": "Barang berhasil dihapus"})


@app.get("/api/dashboard")
@login_required
def dashboard():
    with get_db() as db:
        total_items = db.execute(
            "SELECT COUNT(*) FROM items"
        ).fetchone()[0]

        total_quantity = db.execute(
            "SELECT COALESCE(SUM(quantity), 0) FROM items"
        ).fetchone()[0]

        total_categories = db.execute(
            "SELECT COUNT(DISTINCT category) FROM items WHERE category != ''"
        ).fetchone()[0]

        good = db.execute(
            "SELECT COUNT(*) FROM items WHERE condition = 'Baik'"
        ).fetchone()[0]

        repair = db.execute(
            "SELECT COUNT(*) FROM items WHERE condition IN ('Perlu Perbaikan', 'Rusak')"
        ).fetchone()[0]

    return jsonify({
        "total_items": total_items,
        "total_quantity": total_quantity,
        "total_categories": total_categories,
        "good": good,
        "repair": repair
    })


def validate_item(data):
    for field in [
        "code", "name", "category",
        "unit", "location", "condition"
    ]:
        if not str(data.get(field, "")).strip():
            return f"Kolom {field} wajib diisi"

    try:
        quantity = int(data.get("quantity", 0))
        if quantity < 0:
            return "Jumlah stok tidak boleh negatif"
    except (TypeError, ValueError):
        return "Jumlah stok harus berupa angka bulat"

    if data.get("condition") not in (
        "Baik", "Perlu Perbaikan", "Rusak"
    ):
        return "Kondisi barang tidak valid"

    return None


def item_values(data):
    return (
        str(data["code"]).strip(),
        str(data["name"]).strip(),
        str(data["category"]).strip(),
        int(data.get("quantity", 0)),
        str(data["unit"]).strip(),
        str(data["location"]).strip(),
        str(data["condition"]).strip(),
        str(data.get("notes", "")).strip()
    )


if __name__ == "__main__":
    init_db()

    create_default_admin(
        os.environ.get("ADMIN_USERNAME", "admin"),
        os.environ.get("ADMIN_PASSWORD", "Admin123!")
    )

    app.run(host="127.0.0.1", port=5000, debug=True)
