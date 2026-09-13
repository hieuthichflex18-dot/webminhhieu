# database.py
import sqlite3
import secrets
import string
from datetime import datetime, timedelta
from contextlib import contextmanager

DB_PATH = "mh_data.db"

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db():
    with get_db() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            tier TEXT DEFAULT 'free',
            expires_at TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            last_login TEXT,
            active INTEGER DEFAULT 1,
            created_by TEXT
        );

        CREATE TABLE IF NOT EXISTS access_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key_code TEXT UNIQUE NOT NULL,
            tier TEXT NOT NULL,
            duration_days INTEGER NOT NULL,
            max_uses INTEGER DEFAULT 1,
            used_count INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            expires_at TEXT,
            active INTEGER DEFAULT 1,
            created_by TEXT,
            note TEXT
        );

        CREATE TABLE IF NOT EXISTS sessions_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            action TEXT,
            ip TEXT,
            user_agent TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game TEXT,
            session_id TEXT,
            prediction TEXT,
            confidence INTEGER,
            actual TEXT,
            correct INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """)

def gen_key(prefix="MH"):
    def block(n=4):
        alphabet = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(n))
    return prefix + "-" + block() + "-" + block() + "-" + block() + "-" + block()

def create_key(tier, days, max_uses=1, created_by="admin", note=""):
    key = gen_key()
    exp = (datetime.now() + timedelta(days=days)).isoformat()
    with get_db() as db:
        db.execute(
            "INSERT INTO access_keys (key_code, tier, duration_days, max_uses, expires_at, created_by, note) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (key, tier, days, max_uses, exp, created_by, note)
        )
    return key

def use_key(key_code, username):
    with get_db() as db:
        row = db.execute("SELECT * FROM access_keys WHERE key_code=? AND active=1", (key_code,)).fetchone()
        if not row:
            return False, "Key không tồn tại"
        if row["used_count"] >= row["max_uses"]:
            return False, "Key đã hết lượt"
        if row["expires_at"] and datetime.fromisoformat(row["expires_at"]) < datetime.now():
            return False, "Key đã hết hạn"
        new_exp = (datetime.now() + timedelta(days=row["duration_days"])).isoformat()
        db.execute("UPDATE access_keys SET used_count=used_count+1 WHERE id=?", (row["id"],))
        db.execute("UPDATE users SET tier=?, expires_at=? WHERE username=?", (row["tier"], new_exp, username))
    return True, "Nâng cấp " + row["tier"] + " thành công"

def log_action(username, action, ip="", ua=""):
    with get_db() as db:
        db.execute(
            "INSERT INTO sessions_log (username, action, ip, user_agent) VALUES (?,?,?,?)",
            (username, action, ip, ua)
        )
