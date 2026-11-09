from flask import Flask, jsonify, request, send_from_directory
from pathlib import Path
from backend.database import init_db, get_db
import sqlite3

ROOT = Path(__file__).resolve().parent
FRONTEND = ROOT / "frontend"

app = Flask(__name__, static_folder=None)
app.config["JSON_SORT_KEYS"] = False

@app.get("/")
def index():
    return send_from_directory(FRONTEND, "index.html")

@app.get("/<path:filename>")
def frontend_files(filename):
    # Only serve files from the dedicated frontend directory.
    return send_from_directory(FRONTEND, filename)

@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "message": "Lab Inventory API is running"})

@app.get("/api/items")
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
def get_item(item_id):
    with get_db() as db:
        row = db.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    if row is None:
        return jsonify({"error": "Barang tidak ditemukan"}), 404
    return jsonify(dict(row))

@app.post("/api/items")
def create_item():
    data = request.get_json(silent=True) or {}
    error = validate_item(data)
    if error:
        return jsonify({"error": error}), 400

    values = item_values(data)
    try:
        with get_db() as db:
            cursor = db.execute("""
                INSERT INTO items
                (code, name, category, quantity, unit, location, condition, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, values)
            row = db.execute("SELECT * FROM items WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return jsonify(dict(row)), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Kode inventaris sudah digunakan"}), 409

@app.put("/api/items/<int:item_id>")
def update_item(item_id):
    data = request.get_json(silent=True) or {}
    error = validate_item(data)
    if error:
        return jsonify({"error": error}), 400

    values = item_values(data)
    try:
        with get_db() as db:
            existing = db.execute("SELECT id FROM items WHERE id = ?", (item_id,)).fetchone()
            if existing is None:
                return jsonify({"error": "Barang tidak ditemukan"}), 404
            db.execute("""
                UPDATE items
                SET code = ?, name = ?, category = ?, quantity = ?, unit = ?,
                    location = ?, condition = ?, notes = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (*values, item_id))
            row = db.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
        return jsonify(dict(row))
    except sqlite3.IntegrityError:
        return jsonify({"error": "Kode inventaris sudah digunakan"}), 409

@app.delete("/api/items/<int:item_id>")
def delete_item(item_id):
    with get_db() as db:
        cursor = db.execute("DELETE FROM items WHERE id = ?", (item_id,))
    if cursor.rowcount == 0:
        return jsonify({"error": "Barang tidak ditemukan"}), 404
    return jsonify({"message": "Barang berhasil dihapus"})

@app.get("/api/dashboard")
def dashboard():
    with get_db() as db:
        total_items = db.execute("SELECT COUNT(*) FROM items").fetchone()[0]
        total_quantity = db.execute("SELECT COALESCE(SUM(quantity), 0) FROM items").fetchone()[0]
        total_categories = db.execute(
            "SELECT COUNT(DISTINCT category) FROM items WHERE category != ''"
        ).fetchone()[0]
        good = db.execute(
            "SELECT COUNT(*) FROM items WHERE condition = 'Baik'"
        ).fetchone()[0]
        repair = db.execute(
            "SELECT COUNT(*) FROM items WHERE condition != 'Baik'"
        ).fetchone()[0]
    return jsonify({
        "total_items": total_items,
        "total_quantity": total_quantity,
        "total_categories": total_categories,
        "good": good,
        "repair": repair
    })

def validate_item(data):
    required = ["code", "name", "category", "unit", "location", "condition"]
    for field in required:
        if not str(data.get(field, "")).strip():
            return f"Kolom {field} wajib diisi"
    try:
        quantity = int(data.get("quantity", 0))
        if quantity < 0:
            return "Jumlah stok tidak boleh negatif"
    except (TypeError, ValueError):
        return "Jumlah stok harus berupa angka bulat"
    if data.get("condition") not in ("Baik", "Perlu Perbaikan", "Rusak"):
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
    app.run(host="127.0.0.1", port=5000, debug=True)
