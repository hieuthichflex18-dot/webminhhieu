import os, json, sqlite3
from flask import Flask, render_template, request, jsonify, Response, stream_with_context
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "dev")

BAI_URL = os.getenv("BAI_URL", "https://api.b.ai/v1/chat/completions")
BAI_KEY = os.getenv("BAI_KEY", " BAI_KEY=sk-1onamwk2hglxbx6f0gmlcp2on0b8mnog
BAI_URL=https://api.b.ai/v1/chat/completions
MODELS=gpt-4o,claude-3.5-sonnet,gemini-1.5-pro
FLASK_SECRET=change_me_random_string
PORT=5000")
MODELS  = [m.strip() for m in os.getenv("MODELS", "gpt-4o").split(",") if m.strip()]
DB      = "data.db"

# ---------- DB ----------
def db():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    with db() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS history(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session TEXT, role TEXT, content TEXT,
            ts DATETIME DEFAULT CURRENT_TIMESTAMP);
        """)

init_db()

# ---------- ROUTES ----------
@app.route("/")
def index():
    return render_template("index.html", models=MODELS)

@app.route("/api/models")
def api_models():
    return jsonify(MODELS)

@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json(force=True) or {}
    session = data.get("session", "default")
    model   = data.get("model", MODELS[0] if MODELS else "gpt-4o")
    text    = (data.get("message") or "").strip()
    if not text:
        return jsonify(error="empty"), 400

    with db() as c:
        c.execute("INSERT INTO history(session,role,content) VALUES(?,?,?)",
                  (session, "user", text))
        rows = c.execute(
            "SELECT role,content FROM history WHERE session=? ORDER BY id DESC LIMIT 20",
            (session,)
        ).fetchall()

    msgs = [{"role": "system", "content":
             "Bạn là trợ lý AI tiếng Việt. Trả lời rõ ràng, ngắn gọn, chính xác. "
             "Khi viết code, luôn bọc trong ```ngôn_ngữ ... ```."}]
    msgs += [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]

    def gen():
        full = ""
        try:
            r = requests.post(
                BAI_URL,
                headers={"Authorization": f"Bearer {BAI_KEY}",
                         "Content-Type": "application/json"},
                json={"model": model, "messages": msgs,
                      "temperature": 0.7, "stream": True},
                timeout=180, stream=True
            )
            if r.status_code != 200:
                yield f"data: {json.dumps({'err': r.text[:200]})}\n\n"
                return
            for line in r.iter_lines():
                if not line:
                    continue
                line = line.decode("utf-8", "ignore")
                if not line.startswith("data:"):
                    continue
                chunk = line[5:].strip()
                if chunk == "[DONE]":
                    break
                try:
                    j = json.loads(chunk)
                    delta = j["choices"][0].get("delta", {}).get("content") or ""
                    if delta:
                        full += delta
                        yield f"data: {json.dumps({'t': delta})}\n\n"
                except Exception:
                    pass
        except Exception as e:
            yield f"data: {json.dumps({'err': str(e)})}\n\n"
            return

        with db() as c:
            c.execute("INSERT INTO history(session,role,content) VALUES(?,?,?)",
                      (session, "assistant", full))
        yield f"data: {json.dumps({'done': True})}\n\n"

    return Response(stream_with_context(gen()), mimetype="text/event-stream")

@app.route("/api/clear", methods=["POST"])
def api_clear():
    session = (request.get_json(force=True) or {}).get("session", "default")
    with db() as c:
        c.execute("DELETE FROM history WHERE session=?", (session,))
    return jsonify(ok=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), threaded=True)
