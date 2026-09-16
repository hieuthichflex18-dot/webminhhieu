import json
import os
from pathlib import Path

CONFIG_PATH = Path("config.json")


def _load_from_streamlit_secrets():
    """Thử load config từ Streamlit secrets (khi deploy cloud)."""
    try:
        import streamlit as st
        if hasattr(st, "secrets") and len(st.secrets) > 0:
            return dict(st.secrets)
    except Exception:
        pass
    return None


def _load_from_file():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def _default_config():
    return {
        "api": {
            "base_url": os.getenv("API_BASE_URL", "https://api.your-provider.com/v1"),
            "api_key": os.getenv("API_KEY", ""),
            "default_model": os.getenv("DEFAULT_MODEL", "gpt-4o-mini"),
        },
        "tiktok_cookies": {
            "sessionid": os.getenv("TIKTOK_SESSIONID", ""),
            "tt-target-idc": os.getenv("TIKTOK_IDC", "useast5"),
        },
        "tts": {"default_voice": "adam_vi"},
        "whisper": {"model": "base", "language": "vi"},
        "video": {
            "width": 1080, "height": 1920, "fps": 30,
            "bg_color": [0, 0, 0],
            "font": "assets/fonts/BeVietnamPro-Bold.ttf",
            "font_size": 60,
            "subtitle_color": "white",
        },
        "paths": {
            "downloads": "./downloads",
            "audio": "./audio",
            "output": "./output",
            "backgrounds": "./assets/backgrounds",
        },
    }


def load_config():
    cfg = _load_from_streamlit_secrets()
    if cfg:
        return cfg
    cfg = _load_from_file()
    if cfg:
        return cfg
    return _default_config()


CONFIG = load_config()

# Tạo thư mục cần thiết
for key in ("downloads", "audio", "output", "backgrounds"):
    try:
        Path(CONFIG["paths"][key]).mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
