# app.py
import os
import bcrypt
from datetime import datetime, timedelta
from functools import wraps
from flask import (Flask, render_template, request, jsonify, session,
                   redirect, abort)
from dotenv import load_dotenv

from database import init_db, get_db, create_key, use_key, log_action
from predictor import analyze, normalize_history
import api_manager

load_dotenv("mh.env")

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-change-me")

ADMIN_USER = os.getenv("ADMIN_USER")
ADMIN_PASS_HASH = os.getenv("ADMIN_PASS_HASH")

init_db()


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("username"):
            return redirect("/login")
        return f(*args, **kwargs)
    return wrapper


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("role") != "admin":
            abort(403)
        return f(*args, **kwargs)
    return wrapper


@app.route("/")
@login_required
def home():
    return render_template("index.html",
                           username=session["username"],
                           role=session.get("role", "user"),
                           tier=session.get("tier", "free"))


@app.route("/register")
def register_page():
    return render_template("register.html")


@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.json or {}
    u = data.get("username", "").strip()
    p = data.get("password", "")

    if len(u) < 4 or len(u) > 20:
        return jsonify({"ok": False, "message": "Tài khoản từ 4-20 ký tự"})
    for c in u:
        if not (c.isalnum() or c == "_"):
            return jsonify({"ok": False, "message": "Tài khoản chỉ dùng chữ, số, gạch dưới"})
    if len(p) < 6:
        return jsonify({"ok": False, "message": "Mật khẩu từ 6 ký tự"})

    pw_hash = bcrypt.hashpw(p.encode(), bcrypt.gensalt(12)).decode()

    try:
        with get_db() as db:
            db.execute(
                "INSERT INTO users (username, password_hash, role, tier, created_by) VALUES (?, ?, ?, ?, ?)",
                (u, pw_hash, "user", "free", "self_register")
            )
        log_action(u, "self_register", request.remote_addr, request.user_agent.string)
        return jsonify({"ok": True, "message": "Đăng ký thành công"})
    except Exception as e:
        msg = str(e)
        if "UNIQUE" in msg or "unique" in msg:
            return jsonify({"ok": False, "message": "Tài khoản đã tồn tại"})
        return jsonify({"ok": False, "message": "Lỗi: " + msg})


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form.get("username", "").strip()
        p = request.form.get("password", "")

        if u == ADMIN_USER:
            try:
                if bcrypt.checkpw(p.encode(), ADMIN_PASS_HASH.encode()):
                    session.update({
                        "username": u,
                        "role": "admin",
                        "tier": "admin",
                        "login_at": datetime.now().isoformat()
                    })
                    log_action(u, "admin_login", request.remote_addr, request.user_agent.string)
                    return redirect("/admin")
            except Exception:
                pass

        with get_db() as db:
            row = db.execute(
                "SELECT * FROM users WHERE username=? AND active=1",
                (u,)
            ).fetchone()
            if row and bcrypt.checkpw(p.encode(), row["password_hash"].encode()):
                if row["expires_at"]:
                    if datetime.fromisoformat(row["expires_at"]) < datetime.now():
                        return render_template("login.html", error="Tài khoản đã hết hạn")
                session.update({
                    "username": u,
                    "role": row["role"],
                    "tier": row["tier"],
                    "login_at": datetime.now().isoformat()
                })
                db.execute(
                    "UPDATE users SET last_login=? WHERE id=?",
                    (datetime.now().isoformat(), row["id"])
                )
                log_action(u, "user_login", request.remote_addr, request.user_agent.string)
                return redirect("/")

        return render_template("login.html", error="Sai tài khoản hoặc mật khẩu")

    return render_template("login.html")


@app.route("/logout")
def logout():
    u = session.get("username")
    if u:
        log_action(u, "logout", request.remote_addr, request.user_agent.string)
    session.clear()
    return redirect("/login")


@app.route("/api/games")
@login_required
def api_games():
    return jsonify([
        {"key": k, "name": v["name"], "mode": v["mode"], "icon": v["icon"]}
        for k, v in api_manager.GAMES.items()
    ])


@app.route("/api/game/<game_key>")
@login_required
def api_game_detail(game_key):
    game_key = game_key.upper()
    if game_key not in api_manager.GAMES:
        return jsonify({"error": "Game không tồn tại"}), 404

    game = api_manager.GAMES[game_key]
    raw = api_manager.fetch(game_key)

    if "error" in raw:
        return jsonify({"error": raw["error"]})

    history = normalize_history(raw)
    if len(history) < 3:
        return jsonify({"error": "API không trả đủ dữ liệu T/X"})

    result = analyze(history)
    now = datetime.now()
    session_id = "#" + game_key + "-" + now.strftime("%H%M%S")

    return jsonify({
        "game": game["name"],
        "mode": game["mode"],
        "icon": game["icon"],
        "session_id": session_id,
        "current_history": history[-20:],
        "block_session": {
            "title": "PHIÊN " + game["name"],
            "mode": game["mode"],
            "last": history[-1],
            "last_text": "TÀI" if history[-1] == "T" else "XỈU",
            "streak": result["streak"],
            "session_id": session_id
        },
        "block_prediction": {
            "title": "DỰ ĐOÁN PHIÊN SAU · " + game["name"],
            "mode": game["mode"],
            "prediction": result["prediction"],
            "prediction_text": result["prediction_text"],
            "confidence": result["confidence"],
            "reasons": result["reasons"]
        },
        "stats": {
            "freq_t": result.get("freq_t", 0),
            "freq_x": result.get("freq_x", 0),
            "history_len": result.get("history_len", 0)
        }
    })


@app.route("/api/redeem", methods=["POST"])
@login_required
def api_redeem():
    key = request.json.get("key", "").strip()
    ok, msg = use_key(key, session["username"])
    if ok:
        with get_db() as db:
            row = db.execute(
                "SELECT tier FROM users WHERE username=?",
                (session["username"],)
            ).fetchone()
            if row:
                session["tier"] = row["tier"]
    return jsonify({"ok": ok, "message": msg})


@app.route("/admin")
@admin_required
def admin_page():
    return render_template("admin.html", username=session["username"])


@app.route("/api/admin/stats")
@admin_required
def admin_stats():
    with get_db() as db:
        users = db.execute("SELECT COUNT(*) c FROM users").fetchone()["c"]
        keys = db.execute("SELECT COUNT(*) c FROM access_keys").fetchone()["c"]
        active_keys = db.execute("SELECT COUNT(*) c FROM access_keys WHERE active=1").fetchone()["c"]
        preds = db.execute("SELECT COUNT(*) c FROM predictions").fetchone()["c"]
        correct = db.execute("SELECT COUNT(*) c FROM predictions WHERE correct=1").fetchone()["c"]
    accuracy = 0
    if preds > 0:
        accuracy = round(correct / preds * 100, 1)
    return jsonify({
        "total_users": users,
        "total_keys": keys,
        "active_keys": active_keys,
        "total_predictions": preds,
        "correct_predictions": correct,
        "accuracy": accuracy
    })


@app.route("/api/admin/users")
@admin_required
def admin_users():
    with get_db() as db:
        rows = db.execute(
            "SELECT id, username, role, tier, expires_at, created_at, last_login, active FROM users ORDER BY id DESC"
        ).fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/admin/users/create", methods=["POST"])
@admin_required
def admin_create_user():
    data = request.json
    u = data.get("username", "").strip()
    p = data.get("password", "").strip()
    tier = data.get("tier", "free")
    days = int(data.get("days", 30))
    role = data.get("role", "user")

    if not u or not p or len(p) < 8:
        return jsonify({"ok": False, "message": "Username/password không hợp lệ (password >= 8 ký tự)"})

    exp = (datetime.now() + timedelta(days=days)).isoformat()
    pw_hash = bcrypt.hashpw(p.encode(), bcrypt.gensalt(12)).decode()

    try:
        with get_db() as db:
            db.execute(
                "INSERT INTO users (username, password_hash, role, tier, expires_at, created_by) VALUES (?, ?, ?, ?, ?, ?)",
                (u, pw_hash, role, tier, exp, session["username"])
            )
        log_action(session["username"], "create_user:" + u, request.remote_addr, "")
        return jsonify({"ok": True, "message": "Đã tạo user " + u})
    except Exception as e:
        return jsonify({"ok": False, "message": "Lỗi: " + str(e)})


@app.route("/api/admin/users/<int:uid>/toggle", methods=["POST"])
@admin_required
def admin_toggle_user(uid):
    with get_db() as db:
        row = db.execute("SELECT active FROM users WHERE id=?", (uid,)).fetchone()
        if not row:
            return jsonify({"ok": False})
        new_val = 0 if row["active"] else 1
        db.execute("UPDATE users SET active=? WHERE id=?", (new_val, uid))
    return jsonify({"ok": True})


@app.route("/api/admin/users/<int:uid>", methods=["DELETE"])
@admin_required
def admin_delete_user(uid):
    with get_db() as db:
        db.execute("DELETE FROM users WHERE id=?", (uid,))
    return jsonify({"ok": True})


@app.route("/api/admin/keys")
@admin_required
def admin_keys():
    with get_db() as db:
        rows = db.execute("SELECT * FROM access_keys ORDER BY id DESC LIMIT 200").fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/admin/keys/create", methods=["POST"])
@admin_required
def admin_create_key():
    data = request.json
    tier = data.get("tier", "premium")
    days = int(data.get("days", 30))
    max_uses = int(data.get("max_uses", 1))
    note = data.get("note", "")
    key = create_key(tier, days, max_uses, session["username"], note)
    return jsonify({"ok": True, "key": key})


@app.route("/api/admin/keys/<int:kid>", methods=["DELETE"])
@admin_required
def admin_delete_key(kid):
    with get_db() as db:
        db.execute("DELETE FROM access_keys WHERE id=?", (kid,))
    return jsonify({"ok": True})


@app.route("/api/admin/logs")
@admin_required
def admin_logs():
    with get_db() as db:
        rows = db.execute("SELECT * FROM sessions_log ORDER BY id DESC LIMIT 100").fetchall()
    return jsonify([dict(r) for r in rows])


if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=debug)
