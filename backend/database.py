import sqlite3
from pathlib import Path
from contextlib import contextmanager
from werkzeug.security import generate_password_hash

ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = ROOT / "database" / "inventory.db"

@contextmanager
def get_db():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 0 CHECK(quantity >= 0),
                unit TEXT NOT NULL,
                location TEXT NOT NULL,
                condition TEXT NOT NULL CHECK(
                    condition IN ('Baik', 'Perlu Perbaikan', 'Rusak')
                ),
                notes TEXT DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

def create_default_admin(username, password):
    """Create the initial admin only when the users table is empty."""
    with get_db() as db:
        exists = db.execute("SELECT id FROM users LIMIT 1").fetchone()
        if exists is None:
            db.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, generate_password_hash(password))
            )
