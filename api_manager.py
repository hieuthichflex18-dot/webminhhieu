# api_manager.py
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv("mh.env")

GAMES = {
    "LC79":     {"name": "LC79",     "mode": "Tài Xỉu MD5", "endpoint": os.getenv("API_LC79_TXMD5"),     "icon": "🔥"},
    "SUNWIN":   {"name": "Sunwin",   "mode": "Tài Xỉu",     "endpoint": os.getenv("API_SUNWIN_TX"),      "icon": "☀️"},
    "XOCDIA88": {"name": "Xocdia88", "mode": "Tài Xỉu MD5", "endpoint": os.getenv("API_XOCDIA88_TXMD5"), "icon": "🎲"},
    "OGKFAN":   {"name": "OGKFAN",   "mode": "Tài Xỉu MD5", "endpoint": os.getenv("API_OGKFAN_TXMD5"),   "icon": "🎯"},
    "HITCLUB":  {"name": "Hitclub",  "mode": "Tài Xỉu MD5", "endpoint": os.getenv("API_HITCLUB_TXMD5"),  "icon": "🎰"},
    "BETVIP":   {"name": "Betvip",   "mode": "Tài Xỉu MD5", "endpoint": os.getenv("API_BETVIP_TXMD5"),   "icon": "💎"},
    "789CLUB":  {"name": "789Club",  "mode": "Tài Xỉu",     "endpoint": os.getenv("API_789CLUB_TX"),     "icon": "🎴"},
    "B52":      {"name": "B52",      "mode": "Tài Xỉu MD5", "endpoint": os.getenv("API_B52_TXMD5"),      "icon": "✈️"},
    "IWIN":     {"name": "Iwin",     "mode": "Tài Xỉu MD5", "endpoint": os.getenv("API_IWIN_TXMD5"),     "icon": "🏆"},
    "MAX789":   {"name": "Max789",   "mode": "Tài Xỉu MD5", "endpoint": os.getenv("API_MAX789_TXMD5"),   "icon": "👑"},
    "LUCK8":    {"name": "Luck8",    "mode": "Tài Xỉu MD5", "endpoint": os.getenv("API_LUCK8_TXMD5"),    "icon": "🍀"},
    "TA28":     {"name": "Ta28",     "mode": "Tài Xỉu MD5", "endpoint": os.getenv("API_TA28_TXMD5"),     "icon": "⚡"},
    "SON789":   {"name": "Son789",   "mode": "Tài Xỉu MD5", "endpoint": os.getenv("API_SON789_TXMD5"),   "icon": "🌟"},
    "RIKVIP":   {"name": "Rikvip",   "mode": "Tài Xỉu MD5", "endpoint": os.getenv("API_RIKVIP_TXMD5"),   "icon": "🎮"},
}

CACHE = {}
CACHE_TTL = 5

def fetch(game_key):
    game = GAMES.get(game_key)
    if not game or not game["endpoint"]:
        return {"error": "Game chưa cấu hình endpoint"}

    now = time.time()
    if game_key in CACHE and now - CACHE[game_key]["t"] < CACHE_TTL:
        return CACHE[game_key]["data"]

    try:
        r = requests.get(game["endpoint"], timeout=8, headers={
            "User-Agent": "Mozilla/5.0 MH-Predictor/1.0",
            "Accept": "application/json",
        })
        r.raise_for_status()
        data = r.json()
        CACHE[game_key] = {"t": now, "data": data}
        return data
    except requests.exceptions.Timeout:
        return {"error": "Timeout API"}
    except requests.exceptions.ConnectionError:
        return {"error": "Không kết nối được (tunnel có thể đã renew)"}
    except Exception as e:
        return {"error": f"Lỗi: {e}"}
