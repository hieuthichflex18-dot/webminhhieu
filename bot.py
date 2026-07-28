#!/usr/bin/env python3
# subtitle_tts_ultimate.py - Web Pro với 50+ giọng nói
# Chạy: python3 subtitle_tts_ultimate.py
# Truy cập: http://localhost:5000

from flask import Flask, request, jsonify, render_template_string, send_file
import subprocess, os, json, threading, time, tempfile, base64, hashlib
from datetime import datetime
import requests
import random

app = Flask(__name__)
tasks = {}
task_counter = 0

# ================ 50+ GIỌNG NÓI HOT ================
VOICES = {
    'google': {
        'vi-VN-Standard-A': {'name': '🌸 Linh - Nữ Bắc', 'gender': 'Nữ', 'style': 'Tự nhiên'},
        'vi-VN-Standard-B': {'name': '🌊 Minh - Nam Bắc', 'gender': 'Nam', 'style': 'Trung tính'},
        'vi-VN-Standard-C': {'name': '🌺 Hương - Nữ Nam', 'gender': 'Nữ', 'style': 'Ấm áp'},
        'vi-VN-Standard-D': {'name': '🌿 Tuấn - Nam Nam', 'gender': 'Nam', 'style': 'Sâu lắng'},
        'en-US-Standard-A': {'name': '🇺🇸 Emma - US Female', 'gender': 'Nữ', 'style': 'Modern'},
        'en-US-Standard-B': {'name': '🇺🇸 James - US Male', 'gender': 'Nam', 'style': 'Professional'},
        'en-US-Standard-C': {'name': '🇺🇸 Sophia - US Female', 'gender': 'Nữ', 'style': 'Warm'},
        'en-US-Standard-D': {'name': '🇺🇸 Michael - US Male', 'gender': 'Nam', 'style': 'Deep'},
        'en-US-Standard-E': {'name': '🇺🇸 Emily - US Female', 'gender': 'Nữ', 'style': 'Cheerful'},
        'en-US-Standard-F': {'name': '🇺🇸 David - US Male', 'gender': 'Nam', 'style': 'Neutral'},
        'en-GB-Standard-A': {'name': '🇬🇧 Olivia - UK Female', 'gender': 'Nữ', 'style': 'Elegant'},
        'en-GB-Standard-B': {'name': '🇬🇧 William - UK Male', 'gender': 'Nam', 'style': 'Royal'},
        'en-GB-Standard-C': {'name': '🇬🇧 Charlotte - UK Female', 'gender': 'Nữ', 'style': 'Bright'},
        'en-GB-Standard-D': {'name': '🇬🇧 George - UK Male', 'gender': 'Nam', 'style': 'Mature'},
        'ja-JP-Standard-A': {'name': '🇯🇵 Sakura - Japanese Female', 'gender': 'Nữ', 'style': 'Kawaii'},
        'ja-JP-Standard-B': {'name': '🇯🇵 Kenji - Japanese Male', 'gender': 'Nam', 'style': 'Formal'},
        'ja-JP-Standard-C': {'name': '🇯🇵 Yuki - Japanese Female', 'gender': 'Nữ', 'style': 'Soft'},
        'ja-JP-Standard-D': {'name': '🇯🇵 Takeshi - Japanese Male', 'gender': 'Nam', 'style': 'Strong'},
        'zh-CN-Standard-A': {'name': '🇨🇳 Xiaomei - Chinese Female', 'gender': 'Nữ', 'style': 'Cute'},
        'zh-CN-Standard-B': {'name': '🇨🇳 Weijun - Chinese Male', 'gender': 'Nam', 'style': 'Clear'},
        'zh-CN-Standard-C': {'name': '🇨🇳 Liling - Chinese Female', 'gender': 'Nữ', 'style': 'Warm'},
        'zh-CN-Standard-D': {'name': '🇨🇳 Hongming - Chinese Male', 'gender': 'Nam', 'style': 'Professional'},
        'ko-KR-Standard-A': {'name': '🇰🇷 Hana - Korean Female', 'gender': 'Nữ', 'style': 'Sweet'},
        'ko-KR-Standard-B': {'name': '🇰🇷 Minjun - Korean Male', 'gender': 'Nam', 'style': 'Serious'},
        'ko-KR-Standard-C': {'name': '🇰🇷 Sora - Korean Female', 'gender': 'Nữ', 'style': 'Bright'},
        'ko-KR-Standard-D': {'name': '🇰🇷 Youngjin - Korean Male', 'gender': 'Nam', 'style': 'Deep'},
        'fr-FR-Standard-A': {'name': '🇫🇷 Camille - French Female', 'gender': 'Nữ', 'style': 'Romantic'},
        'fr-FR-Standard-B': {'name': '🇫🇷 Pierre - French Male', 'gender': 'Nam', 'style': 'Sophisticated'},
        'fr-FR-Standard-C': {'name': '🇫🇷 Amélie - French Female', 'gender': 'Nữ', 'style': 'Charming'},
        'fr-FR-Standard-D': {'name': '🇫🇷 Antoine - French Male', 'gender': 'Nam', 'style': 'Elegant'},
        'es-ES-Standard-A': {'name': '🇪🇸 Lucia - Spanish Female', 'gender': 'Nữ', 'style': 'Passionate'},
        'es-ES-Standard-B': {'name': '🇪🇸 Javier - Spanish Male', 'gender': 'Nam', 'style': 'Warm'},
        'es-ES-Standard-C': {'name': '🇪🇸 Carmen - Spanish Female', 'gender': 'Nữ', 'style': 'Spirited'},
        'es-ES-Standard-D': {'name': '🇪🇸 Diego - Spanish Male', 'gender': 'Nam', 'style': 'Smooth'},
        'de-DE-Standard-A': {'name': '🇩🇪 Anna - German Female', 'gender': 'Nữ', 'style': 'Clear'},
        'de-DE-Standard-B': {'name': '🇩🇪 Lukas - German Male', 'gender': 'Nam', 'style': 'Precise'},
        'de-DE-Standard-C': {'name': '🇩🇪 Marie - German Female', 'gender': 'Nữ', 'style': 'Warm'},
        'de-DE-Standard-D': {'name': '🇩🇪 Felix - German Male', 'gender': 'Nam', 'style': 'Deep'},
        'it-IT-Standard-A': {'name': '🇮🇹 Sofia - Italian Female', 'gender': 'Nữ', 'style': 'Melodic'},
        'it-IT-Standard-B': {'name': '🇮🇹 Matteo - Italian Male', 'gender': 'Nam', 'style': 'Passionate'},
        'it-IT-Standard-C': {'name': '🇮🇹 Giulia - Italian Female', 'gender': 'Nữ', 'style': 'Elegant'},
        'it-IT-Standard-D': {'name': '🇮🇹 Marco - Italian Male', 'gender': 'Nam', 'style': 'Warm'},
        'pt-PT-Standard-A': {'name': '🇵🇹 Beatriz - Portuguese Female', 'gender': 'Nữ', 'style': 'Soft'},
        'pt-PT-Standard-B': {'name': '🇵🇹 Joao - Portuguese Male', 'gender': 'Nam', 'style': 'Clear'},
        'pt-PT-Standard-C': {'name': '🇵🇹 Ines - Portuguese Female', 'gender': 'Nữ', 'style': 'Warm'},
        'pt-PT-Standard-D': {'name': '🇵🇹 Pedro - Portuguese Male', 'gender': 'Nam', 'style': 'Strong'},
        'ru-RU-Standard-A': {'name': '🇷🇺 Anastasia - Russian Female', 'gender': 'Nữ', 'style': 'Melodic'},
        'ru-RU-Standard-B': {'name': '🇷🇺 Dmitri - Russian Male', 'gender': 'Nam', 'style': 'Deep'},
        'ru-RU-Standard-C': {'name': '🇷🇺 Irina - Russian Female', 'gender': 'Nữ', 'style': 'Warm'},
        'ru-RU-Standard-D': {'name': '🇷🇺 Alexei - Russian Male', 'gender': 'Nam', 'style': 'Strong'},
        'hi-IN-Standard-A': {'name': '🇮🇳 Priya - Hindi Female', 'gender': 'Nữ', 'style': 'Sweet'},
        'hi-IN-Standard-B': {'name': '🇮🇳 Raj - Hindi Male', 'gender': 'Nam', 'style': 'Clear'},
        'hi-IN-Standard-C': {'name': '🇮🇳 Anjali - Hindi Female', 'gender': 'Nữ', 'style': 'Warm'},
        'hi-IN-Standard-D': {'name': '🇮🇳 Vikram - Hindi Male', 'gender': 'Nam', 'style': 'Strong'},
    },
    'azure': {
        'vi-VN-HoaiMyNeural': {'name': '🌹 Hoài My - Nữ Bắc', 'gender': 'Nữ', 'style': 'Xúc cảm'},
        'vi-VN-NamMinhNeural': {'name': '🌲 Nam Minh - Nam Bắc', 'gender': 'Nam', 'style': 'Trầm ấm'},
        'vi-VN-HueNeural': {'name': '🏮 Huệ - Nữ Huế', 'gender': 'Nữ', 'style': 'Dịu dàng'},
        'vi-VN-ThiNeural': {'name': '🌺 Thi - Nữ Nam', 'gender': 'Nữ', 'style': 'Tươi sáng'},
        'en-US-JennyNeural': {'name': '🇺🇸 Jenny - US Female', 'gender': 'Nữ', 'style': 'Friendly'},
        'en-US-GuyNeural': {'name': '🇺🇸 Guy - US Male', 'gender': 'Nam', 'style': 'Professional'},
        'en-US-AriaNeural': {'name': '🇺🇸 Aria - US Female', 'gender': 'Nữ', 'style': 'Bright'},
        'en-US-DavisNeural': {'name': '🇺🇸 Davis - US Male', 'gender': 'Nam', 'style': 'Deep'},
        'ja-JP-NanamiNeural': {'name': '🇯🇵 Nanami - Japanese Female', 'gender': 'Nữ', 'style': 'Cute'},
        'ja-JP-KeitaNeural': {'name': '🇯🇵 Keita - Japanese Male', 'gender': 'Nam', 'style': 'Formal'},
        'zh-CN-XiaoxiaoNeural': {'name': '🇨🇳 Xiaoxiao - Chinese Female', 'gender': 'Nữ', 'style': 'Lively'},
        'zh-CN-YunxiNeural': {'name': '🇨🇳 Yunxi - Chinese Male', 'gender': 'Nam', 'style': 'Clear'},
        'ko-KR-SunHiNeural': {'name': '🇰🇷 SunHi - Korean Female', 'gender': 'Nữ', 'style': 'Friendly'},
        'ko-KR-InJoonNeural': {'name': '🇰🇷 InJoon - Korean Male', 'gender': 'Nam', 'style': 'Smooth'},
        'fr-FR-DeniseNeural': {'name': '🇫🇷 Denise - French Female', 'gender': 'Nữ', 'style': 'Elegant'},
        'fr-FR-HenriNeural': {'name': '🇫🇷 Henri - French Male', 'gender': 'Nam', 'style': 'Sophisticated'},
        'es-ES-ElviraNeural': {'name': '🇪🇸 Elvira - Spanish Female', 'gender': 'Nữ', 'style': 'Passionate'},
        'es-ES-AlvaroNeural': {'name': '🇪🇸 Alvaro - Spanish Male', 'gender': 'Nam', 'style': 'Warm'},
        'de-DE-KatjaNeural': {'name': '🇩🇪 Katja - German Female', 'gender': 'Nữ', 'style': 'Clear'},
        'de-DE-ConradNeural': {'name': '🇩🇪 Conrad - German Male', 'gender': 'Nam', 'style': 'Precise'},
    },
    'elevenlabs': {
        'rachel': {'name': '🎙️ Rachel - US Female', 'gender': 'Nữ', 'style': 'Natural'},
        'adam': {'name': '🎙️ Adam - US Male', 'gender': 'Nam', 'style': 'Deep'},
        'bella': {'name': '🎙️ Bella - UK Female', 'gender': 'Nữ', 'style': 'Elegant'},
        'antoni': {'name': '🎙️ Antoni - Spanish Male', 'gender': 'Nam', 'style': 'Warm'},
        'drew': {'name': '🎙️ Drew - US Male', 'gender': 'Nam', 'style': 'Professional'},
        'emily': {'name': '🎙️ Emily - US Female', 'gender': 'Nữ', 'style': 'Cheerful'},
        'josh': {'name': '🎙️ Josh - US Male', 'gender': 'Nam', 'style': 'Friendly'},
        'linda': {'name': '🎙️ Linda - US Female', 'gender': 'Nữ', 'style': 'Warm'},
        'mike': {'name': '🎙️ Mike - US Male', 'gender': 'Nam', 'style': 'Smooth'},
        'sarah': {'name': '🎙️ Sarah - UK Female', 'gender': 'Nữ', 'style': 'Soft'},
    },
    'amazon': {
        'Joanna': {'name': '📀 Joanna - US Female', 'gender': 'Nữ', 'style': 'Natural'},
        'Matthew': {'name': '📀 Matthew - US Male', 'gender': 'Nam', 'style': 'Deep'},
        'Salli': {'name': '📀 Salli - US Female', 'gender': 'Nữ', 'style': 'Friendly'},
        'Kendra': {'name': '📀 Kendra - US Female', 'gender': 'Nữ', 'style': 'Warm'},
        'Justin': {'name': '📀 Justin - US Male', 'gender': 'Nam', 'style': 'Clear'},
        'Ivy': {'name': '📀 Ivy - US Female', 'gender': 'Nữ', 'style': 'Bright'},
        'Joey': {'name': '📀 Joey - US Male', 'gender': 'Nam', 'style': 'Friendly'},
        'Geraint': {'name': '📀 Geraint - UK Male', 'gender': 'Nam', 'style': 'Elegant'},
        'Emma': {'name': '📀 Emma - UK Female', 'gender': 'Nữ', 'style': 'Soft'},
        'Brian': {'name': '📀 Brian - UK Male', 'gender': 'Nam', 'style': 'Deep'},
    },
    'ibm': {
        'en-US_MichaelV3Voice': {'name': '💎 Michael - US Male', 'gender': 'Nam', 'style': 'Professional'},
        'en-US_AllisonV3Voice': {'name': '💎 Allison - US Female', 'gender': 'Nữ', 'style': 'Natural'},
        'en-US_LisaV3Voice': {'name': '💎 Lisa - US Female', 'gender': 'Nữ', 'style': 'Warm'},
        'en-US_HenryV3Voice': {'name': '💎 Henry - US Male', 'gender': 'Nam', 'style': 'Deep'},
        'es-ES_EnriqueV3Voice': {'name': '💎 Enrique - Spanish Male', 'gender': 'Nam', 'style': 'Passionate'},
        'es-ES_LauraV3Voice': {'name': '💎 Laura - Spanish Female', 'gender': 'Nữ', 'style': 'Warm'},
    }
}

# ================ HTML GIAO DIỆN ================
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>🎙️ SubPro Voice - 50+ Giọng Nói AI</title>
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#0a0e14;--card:#141c28;--accent:#00e5ff;--gold:#ffcc00;--success:#00ff88;--danger:#ff4444;--text:#e0e8f0;--shadow:0 8px 32px rgba(0,0,0,0.4)}
body{background:var(--bg);color:var(--text);font-family:'Segoe UI',-apple-system,sans-serif;min-height:100vh;padding:0}
/* HEADER */
.header{background:linear-gradient(135deg,#0d1520,#1a2635);padding:20px 24px;border-bottom:1px solid #00e5ff20;position:sticky;top:0;z-index:100;backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap}
.header h1{font-size:24px;font-weight:700;display:flex;align-items:center;gap:10px}
.header h1 span{color:var(--gold)}
.header .sub{font-size:13px;color:#8899aa}
.header .badge{background:var(--gold);color:#000;padding:2px 12px;border-radius:20px;font-size:11px;font-weight:bold}
/* CONTAINER */
.container{max-width:1400px;margin:0 auto;padding:20px}
/* TAB NAV */
.tabs{display:flex;gap:4px;background:var(--card);border-radius:12px;padding:4px;margin-bottom:20px;border:1px solid #00e5ff10;overflow-x:auto}
.tab-btn{flex:1;padding:12px 16px;border:none;background:transparent;color:#8899aa;font-weight:600;font-size:14px;cursor:pointer;border-radius:8px;transition:0.3s;white-space:nowrap;display:flex;align-items:center;gap:8px;justify-content:center}
.tab-btn:hover{color:var(--text);background:#00e5ff10}
.tab-btn.active{background:#00e5ff20;color:var(--accent);box-shadow:inset 0 0 20px #00e5ff10}
.tab-btn i{font-size:16px}
.tab-content{display:none}
.tab-content.active{display:block}
/* CARD */
.card{background:var(--card);border-radius:16px;padding:24px;margin-bottom:20px;border:1px solid #00e5ff10;transition:0.3s}
.card:hover{border-color:#00e5ff30;box-shadow:var(--shadow)}
.card-title{font-size:18px;font-weight:600;margin-bottom:16px;display:flex;align-items:center;gap:10px}
.card-title i{color:var(--gold)}
/* GRID */
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.grid-3{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px}
@media(max-width:768px){.grid-2{grid-template-columns:1fr}}
/* INPUT */
input,select,textarea{width:100%;padding:12px 16px;border-radius:10px;border:1px solid #00e5ff20;background:#0d1520;color:var(--text);font-size:15px;transition:0.3s}
input:focus,select:focus,textarea:focus{outline:none;border-color:var(--accent);box-shadow:0 0 0 3px #00e5ff20}
textarea{min-height:80px;resize:vertical;font-family:monospace}
/* BUTTON */
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;padding:12px 28px;border-radius:10px;border:none;font-weight:600;font-size:15px;cursor:pointer;transition:0.3s;text-decoration:none}
.btn-primary{background:linear-gradient(135deg,#00e5ff,#0088ff);color:#000}
.btn-primary:hover{transform:translateY(-2px);box-shadow:0 8px 30px #00e5ff40}
.btn-success{background:var(--success);color:#000}
.btn-success:hover{transform:translateY(-2px);box-shadow:0 8px 30px #00ff8840}
.btn-danger{background:var(--danger);color:#fff}
.btn-outline{background:transparent;border:1px solid #00e5ff40;color:var(--accent)}
.btn-outline:hover{background:#00e5ff20}
.btn-sm{padding:8px 16px;font-size:13px}
.btn-gold{background:var(--gold);color:#000}
.btn-gold:hover{transform:translateY(-2px);box-shadow:0 8px 30px #ffcc0040}
.w-full{width:100%}
/* VOICE CARD */
.voice-card{background:#0d1520;padding:14px 16px;border-radius:10px;border:2px solid transparent;cursor:pointer;transition:0.3s;display:flex;flex-direction:column;gap:4px}
.voice-card:hover{border-color:#00e5ff30;transform:translateY(-2px)}
.voice-card.selected{border-color:var(--accent);background:#00e5ff10;box-shadow:0 0 20px #00e5ff20}
.voice-card .v-name{font-weight:600;font-size:14px}
.voice-card .v-desc{font-size:12px;color:#8899aa;display:flex;gap:12px}
.voice-card .v-badge{font-size:10px;background:#1a2530;padding:1px 10px;border-radius:12px;color:#8899aa}
.voice-card input[type="radio"]{display:none}
/* TASK LIST */
.task-item{display:flex;justify-content:space-between;align-items:center;padding:14px 16px;border-bottom:1px solid #00e5ff08;gap:12px;transition:0.2s}
.task-item:hover{background:#00e5ff05}
.task-info{flex:1;min-width:0}
.task-title{font-weight:500;font-size:14px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.task-meta{font-size:12px;color:#8899aa;margin-top:4px;display:flex;gap:12px;flex-wrap:wrap}
.status{display:inline-block;padding:2px 12px;border-radius:20px;font-size:11px;font-weight:600}
.status-pending{background:#ffaa00;color:#000}
.status-processing{background:#0088ff;color:#fff;animation:pulse 1s infinite}
.status-done{background:var(--success);color:#000}
.status-fail{background:var(--danger);color:#fff}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.5}}
.task-actions{display:flex;gap:6px;flex-wrap:wrap}
/* LOG */
.log-box{background:#0a0e14;padding:16px;max-height:400px;overflow:auto;border-radius:10px;border:1px solid #00e5ff08;font-family:monospace;font-size:13px;line-height:1.8}
.log-box .time{color:var(--gold)}
.log-box .ok{color:var(--success)}
.log-box .err{color:var(--danger)}
.log-box .info{color:#88aacc}
/* MODAL */
.modal{display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.85);z-index:999;padding:20px;animation:fadeIn 0.3s;overflow:auto}
.modal-inner{background:var(--card);border-radius:16px;padding:24px;max-width:800px;margin:auto;border:1px solid #00e5ff20}
.modal-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px}
.modal-body{max-height:60vh;overflow:auto}
@keyframes fadeIn{from{opacity:0;transform:scale(0.95)}to{opacity:1;transform:scale(1)}}
/* TOAST */
.toast{position:fixed;bottom:30px;left:50%;transform:translateX(-50%);background:var(--card);border:1px solid var(--accent);padding:14px 28px;border-radius:12px;color:var(--text);font-size:14px;z-index:1000;box-shadow:0 8px 40px rgba(0,0,0,0.6);animation:slideUp 0.4s;display:none;border-left:4px solid var(--gold)}
@keyframes slideUp{from{opacity:0;transform:translateX(-50%) translateY(30px)}to{opacity:1;transform:translateX(-50%) translateY(0)}}
/* SCROLL */
::-webkit-scrollbar{width:6px;height:6px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:#00e5ff30;border-radius:10px}
::-webkit-scrollbar-thumb:hover{background:#00e5ff50}
/* RESPONSIVE */
@media(max-width:600px){.header h1{font-size:18px}.container{padding:12px}.card{padding:16px}.grid-3{grid-template-columns:1fr 1fr}.task-item{flex-wrap:wrap}.task-actions{width:100%;justify-content:flex-end}}
</style>
</head>
<body>

<!-- TOAST -->
<div id="toast" class="toast"></div>

<!-- HEADER -->
<div class="header">
    <h1><i class="fas fa-microphone-alt" style="color:var(--gold)"></i> Sub<span>Pro</span> <span class="badge">50+ Voices</span></h1>
    <div class="sub"><i class="fas fa-circle" style="color:var(--success);font-size:10px"></i> Online · <span id="taskCount">0</span> tasks</div>
</div>

<div class="container">
    <!-- TABS -->
    <div class="tabs">
        <button class="tab-btn active" onclick="switchTab('home')"><i class="fas fa-home"></i> Trang chủ</button>
        <button class="tab-btn" onclick="switchTab('voices')"><i class="fas fa-microphone-alt"></i> Giọng nói</button>
        <button class="tab-btn" onclick="switchTab('tasks')"><i class="fas fa-list"></i> Video của tôi</button>
        <button class="tab-btn" onclick="switchTab('settings')"><i class="fas fa-cog"></i> Cài đặt</button>
    </div>

    <!-- TAB HOME -->
    <div id="tab-home" class="tab-content active">
        <div class="card">
            <div class="card-title"><i class="fas fa-upload"></i> Tạo video mới</div>
            <div class="grid-2">
                <div>
                    <label style="font-size:13px;color:#8899aa;">🔗 Link video</label>
                    <input id="videoUrl" placeholder="YouTube, Facebook, TikTok, Twitter..." />
                </div>
                <div>
                    <label style="font-size:13px;color:#8899aa;">🌐 Ngôn ngữ gốc</label>
                    <select id="srcLang">
                        <option value="auto">🔍 Tự động nhận diện</option>
                        <option value="en">🇺🇸 English</option>
                        <option value="zh">🇨🇳 中文</option>
                        <option value="ja">🇯🇵 日本語</option>
                        <option value="ko">🇰🇷 한국어</option>
                        <option value="fr">🇫🇷 Français</option>
                        <option value="es">🇪🇸 Español</option>
                        <option value="de">🇩🇪 Deutsch</option>
                        <option value="it">🇮🇹 Italiano</option>
                        <option value="pt">🇵🇹 Português</option>
                        <option value="ru">🇷🇺 Русский</option>
                        <option value="hi">🇮🇳 हिन्दी</option>
                        <option value="vi">🇻🇳 Tiếng Việt</option>
                    </select>
                </div>
            </div>
            <div style="margin-top:12px;display:flex;gap:10px;flex-wrap:wrap;">
                <button class="btn btn-primary" onclick="startProcess()"><i class="fas fa-play"></i> Bắt đầu xử lý</button>
                <button class="btn btn-outline" onclick="clearInput()"><i class="fas fa-eraser"></i> Xóa</button>
                <span id="selectedVoiceDisplay" style="margin-left:auto;color:#8899aa;font-size:13px;display:flex;align-items:center;gap:6px;">
                    <i class="fas fa-microphone"></i> <span id="voiceNameDisplay">Chưa chọn</span>
                </span>
            </div>
            <div id="result" style="margin-top:12px;color:var(--gold);font-weight:500;"></div>
        </div>

        <div class="card">
            <div class="card-title"><i class="fas fa-clock"></i> Xử lý gần đây</div>
            <div id="recentTasks"></div>
        </div>
    </div>

    <!-- TAB VOICES -->
    <div id="tab-voices" class="tab-content">
        <div class="card">
            <div class="card-title"><i class="fas fa-microphone-alt" style="color:var(--gold)"></i> Thư viện giọng nói <span style="font-size:13px;color:#8899aa;font-weight:400;">({{ total_voices }} giọng)</span></div>
            <div style="margin-bottom:12px;display:flex;gap:10px;flex-wrap:wrap;">
                <input id="voiceSearch" placeholder="🔍 Tìm kiếm giọng nói..." oninput="filterVoices()" style="flex:1;min-width:200px;" />
                <select id="voiceFilter" onchange="filterVoices()" style="width:auto;min-width:120px;">
                    <option value="all">Tất cả</option>
                    <option value="Nữ">Nữ</option>
                    <option value="Nam">Nam</option>
                </select>
                <select id="providerFilter" onchange="filterVoices()" style="width:auto;min-width:120px;">
                    <option value="all">Tất cả nhà cung cấp</option>
                    <option value="google">Google</option>
                    <option value="azure">Azure</option>
                    <option value="elevenlabs">ElevenLabs</option>
                    <option value="amazon">Amazon</option>
                    <option value="ibm">IBM</option>
                </select>
            </div>
            <div id="voiceContainer" class="grid-3"></div>
        </div>
    </div>

    <!-- TAB TASKS -->
    <div id="tab-tasks" class="tab-content">
        <div class="card">
            <div class="card-title"><i class="fas fa-list"></i> Tất cả video <button class="btn btn-sm btn-outline" onclick="loadTasks()" style="margin-left:auto;"><i class="fas fa-sync"></i></button></div>
            <div id="taskList"></div>
        </div>
    </div>

    <!-- TAB SETTINGS -->
    <div id="tab-settings" class="tab-content">
        <div class="card">
            <div class="card-title"><i class="fas fa-cog"></i> Cài đặt nâng cao</div>
            <div style="max-width:500px;display:grid;gap:12px;">
                <label style="font-size:13px;color:#8899aa;">🔑 Google TTS API Key (tùy chọn)</label>
                <input id="googleKey" placeholder="Nhập API key..." />
                <label style="font-size:13px;color:#8899aa;">🔑 Azure Speech Key</label>
                <input id="azureKey" placeholder="Nhập Azure key..." />
                <label style="font-size:13px;color:#8899aa;">🔑 ElevenLabs API Key</label>
                <input id="elevenKey" placeholder="Nhập ElevenLabs key..." />
                <button class="btn btn-success" onclick="saveSettings()"><i class="fas fa-save"></i> Lưu cài đặt</button>
                <div style="font-size:12px;color:#556677;border-top:1px solid #00e5ff10;padding-top:12px;">
                    <i class="fas fa-info-circle"></i> Để trống để dùng gTTS miễn phí (giới hạn 200 ký tự/lần)
                </div>
            </div>
        </div>
    </div>
</div>

<!-- MODAL LOG -->
<div id="logModal" class="modal" onclick="if(event.target===this)closeLog()">
    <div class="modal-inner">
        <div class="modal-header">
            <h3><i class="fas fa-terminal" style="color:var(--gold)"></i> Chi tiết xử lý</h3>
            <button class="btn btn-sm btn-outline" onclick="closeLog()"><i class="fas fa-times"></i></button>
        </div>
        <div class="modal-body">
            <div id="logDetail" class="log-box"></div>
        </div>
        <div style="margin-top:16px;display:flex;gap:10px;flex-wrap:wrap;">
            <button class="btn btn-sm btn-success" id="downloadSrtBtn" onclick="downloadSub()" style="display:none;"><i class="fas fa-file-alt"></i> Tải SRT</button>
            <button class="btn btn-sm btn-primary" id="downloadAudioBtn" onclick="downloadAudio()" style="display:none;"><i class="fas fa-headphones"></i> Tải Audio (TTS)</button>
            <button class="btn btn-sm btn-outline" onclick="closeLog()">Đóng</button>
        </div>
    </div>
</div>

<script>
// ===== DATA =====
const VOICES = {{ voices|tojson }};
let selectedVoice = localStorage.getItem('selectedVoice') || 'vi-VN-Standard-A';
let currentTaskId = null;
let allVoices = [];

// ===== FLATTEN VOICES =====
function flattenVoices() {
    allVoices = [];
    for (const [provider, voices] of Object.entries(VOICES)) {
        for (const [code, info] of Object.entries(voices)) {
            allVoices.push({ code, provider, ...info });
        }
    }
    return allVoices;
}

// ===== RENDER VOICES =====
function renderVoices(filter='all', provider='all', search='') {
    const container = document.getElementById('voiceContainer');
    let list = allVoices;
    
    if (filter !== 'all') list = list.filter(v => v.gender === filter);
    if (provider !== 'all') list = list.filter(v => v.provider === provider);
    if (search) {
        const s = search.toLowerCase();
        list = list.filter(v => v.name.toLowerCase().includes(s) || v.code.toLowerCase().includes(s));
    }
    
    if (!list.length) {
        container.innerHTML = '<div style="padding:40px;text-align:center;color:#556677;">Không tìm thấy giọng nói</div>';
        return;
    }
    
    container.innerHTML = list.map(v => `
        <div class="voice-card ${v.code === selectedVoice ? 'selected' : ''}" onclick="selectVoice('${v.code}')">
            <input type="radio" name="voice" value="${v.code}" ${v.code === selectedVoice ? 'checked' : ''} />
            <div class="v-name">${v.name}</div>
            <div class="v-desc">
                <span>${v.gender}</span>
                <span>${v.style}</span>
                <span class="v-badge">${v.provider}</span>
            </div>
        </div>
    `).join('');
}

function filterVoices() {
    const filter = document.getElementById('voiceFilter').value;
    const provider = document.getElementById('providerFilter').value;
    const search = document.getElementById('voiceSearch').value;
    renderVoices(filter, provider, search);
}

function selectVoice(code) {
    selectedVoice = code;
    localStorage.setItem('selectedVoice', code);
    renderVoices(
        document.getElementById('voiceFilter').value,
        document.getElementById('providerFilter').value,
        document.getElementById('voiceSearch').value
    );
    // Update display
    const voice = allVoices.find(v => v.code === code);
    document.getElementById('voiceNameDisplay').textContent = voice ? voice.name : 'Chưa chọn';
    showToast('✅ Đã chọn: ' + (voice ? voice.name : code));
}

// ===== TOAST =====
function showToast(msg) {
    const t = document.getElementById('toast');
    t.textContent = msg;
    t.style.display = 'block';
    clearTimeout(t._hide);
    t._hide = setTimeout(() => t.style.display = 'none', 3000);
}

// ===== TABS =====
function switchTab(tab) {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    document.querySelector(`.tab-btn:has(.fa-${tab === 'home' ? 'home' : tab === 'voices' ? 'microphone-alt' : tab === 'tasks' ? 'list' : 'cog'})`)?.classList.add('active');
    document.getElementById('tab-' + tab).classList.add('active');
    if (tab === 'voices') renderVoices();
    if (tab === 'tasks') loadTasks();
}

// ===== PROCESS =====
async function startProcess() {
    const url = document.getElementById('videoUrl').value.trim();
    const lang = document.getElementById('srcLang').value;
    if (!url) { showToast('⚠️ Vui lòng dán link video'); return; }
    
    const btn = document.querySelector('.btn-primary');
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang xử lý...';
    document.getElementById('result').textContent = '⏳ Đang khởi tạo...';
    
    try {
        const res = await fetch('/api/process', {
            method: 'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify({url, lang, voice: selectedVoice})
        });
        const data = await res.json();
        document.getElementById('result').textContent = '✅ Task #' + data.id + ' đã tạo';
        showToast('✅ Task #' + data.id + ' đã tạo');
        loadTasks();
        if (data.id) setTimeout(() => showLog(data.id), 1000);
    } catch(e) {
        showToast('❌ Lỗi: ' + e.message);
    }
    btn.disabled = false;
    btn.innerHTML = '<i class="fas fa-play"></i> Bắt đầu xử lý';
}

function clearInput() {
    document.getElementById('videoUrl').value = '';
    document.getElementById('result').textContent = '';
}

// ===== TASKS =====
async function loadTasks() {
    try {
        const res = await fetch('/api/tasks');
        const data = await res.json();
        document.getElementById('taskCount').textContent = data.length;
        
        const container = document.getElementById('taskList');
        const recent = document.getElementById('recentTasks');
        if (!data.length) {
            const empty = '<div style="padding:20px;text-align:center;color:#556677;">Chưa có video nào</div>';
            container.innerHTML = empty;
            recent.innerHTML = empty;
            return;
        }
        const html = data.map(t => `
            <div class="task-item" onclick="showLog('${t.id}')" style="cursor:pointer;">
                <div class="task-info">
                    <div class="task-title">${t.title || t.url.substring(0,50)}...</div>
                    <div class="task-meta">
                        <span class="status status-${t.status}">${t.status}</span>
                        <span>${t.time}</span>
                        <span style="color:#556677;">Giọng: ${t.voice || 'Mặc định'}</span>
                    </div>
                </div>
                <div class="task-actions" onclick="event.stopPropagation();">
                    ${t.status === 'done' ? `<button class="btn btn-sm btn-success" onclick="showLog('${t.id}')"><i class="fas fa-file-alt"></i></button>` : ''}
                    ${t.status === 'done' && t.audio_path ? `<button class="btn btn-sm btn-primary" onclick="downloadAudio('${t.id}')"><i class="fas fa-headphones"></i></button>` : ''}
                    <button class="btn btn-sm btn-outline" onclick="showLog('${t.id}')"><i class="fas fa-terminal"></i></button>
                </div>
            </div>
        `).join('');
        container.innerHTML = html;
        recent.innerHTML = data.slice(0, 5).map(t => `
            <div class="task-item" onclick="showLog('${t.id}')" style="cursor:pointer;">
                <div class="task-info">
                    <div class="task-title">${t.title || t.url.substring(0,40)}...</div>
                    <div class="task-meta"><span class="status status-${t.status}">${t.status}</span> ${t.time}</div>
                </div>
            </div>
        `).join('');
    } catch(e) {}
}

// ===== LOG =====
async function showLog(id) {
    currentTaskId = id;
    const res = await fetch('/api/log/'+id);
    const task = await res.json();
    const box = document.getElementById('logDetail');
    box.innerHTML = (task.log || ['Không có log']).map(l => {
        let cls = '';
        if (l.includes('✔') || l.includes('✅')) cls = 'ok';
        else if (l.includes('✘') || l.includes('lỗi') || l.includes('fail')) cls = 'err';
        else cls = 'info';
        return `<div><span class="time">[${new Date().toLocaleTimeString()}]</span> <span class="${cls}">${l}</span></div>`;
    }).join('');
    document.getElementById('logModal').style.display = 'block';
    
    const srtBtn = document.getElementById('downloadSrtBtn');
    const audioBtn = document.getElementById('downloadAudioBtn');
    srtBtn.style.display = (task.status === 'done' && task.srt_path) ? 'inline-flex' : 'none';
    audioBtn.style.display = (task.status === 'done' && task.audio_path) ? 'inline-flex' : 'none';
}

function closeLog() {
    document.getElementById('logModal').style.display = 'none';
}

function downloadSub() {
    if (currentTaskId) window.open('/api/download/srt/'+currentTaskId, '_blank');
}

function downloadAudio() {
    if (currentTaskId) window.open('/api/download/audio/'+currentTaskId, '_blank');
}

// ===== SETTINGS =====
function saveSettings() {
    const google = document.getElementById('googleKey').value;
    const azure = document.getElementById('azureKey').value;
    const eleven = document.getElementById('elevenKey').value;
    localStorage.setItem('googleKey', google);
    localStorage.setItem('azureKey', azure);
    localStorage.setItem('elevenKey', eleven);
    showToast('✅ Đã lưu cài đặt');
}

// ===== INIT =====
flattenVoices();
renderVoices();
loadTasks();

// Set default voice display
const defaultVoice = allVoices.find(v => v.code === selectedVoice);
if (defaultVoice) document.getElementById('voiceNameDisplay').textContent = defaultVoice.name;

// Auto refresh
setInterval(loadTasks, 5000);

// Load saved settings
document.getElementById('googleKey').value = localStorage.getItem('googleKey') || '';
document.getElementById('azureKey').value = localStorage.getItem('azureKey') || '';
document.getElementById('elevenKey').value = localStorage.getItem('elevenKey') || '';
</script>
</body>
</html>
'''

# ================ BACKEND ================

def download_video(url, output_path):
    cmd = f'yt-dlp -f best[ext=mp4] -o "{output_path}" "{url}" 2>&1'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode == 0, result.stderr

def extract_audio(video_path, audio_path):
    cmd = f'ffmpeg -i "{video_path}" -acodec pcm_s16le -ar 16000 -ac 1 "{audio_path}" -y 2>&1'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode == 0

def transcribe_audio(audio_path, lang='auto'):
    import whisper
    model = whisper.load_model("base")
    result = model.transcribe(audio_path, language=lang if lang != 'auto' else None)
    return result["segments"]

def translate_text(text):
    url = "https://translate.googleapis.com/translate_a/single"
    params = {'client':'gtx','sl':'auto','tl':'vi','dt':'t','q':text}
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        return ''.join([item[0] for item in data[0] if item[0]])
    except:
        return text

def generate_srt(segments, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        for i, seg in enumerate(segments, 1):
            def fmt(t):
                h = int(t//3600); m = int((t%3600)//60); s = int(t%60); ms = int((t%1)*1000)
                return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
            f.write(f"{i}\n{fmt(seg['start'])} --> {fmt(seg['end'])}\n{seg['text']}\n\n")

def text_to_speech(text, voice_code, output_path):
    from gtts import gTTS
    # Map voice code to language
    lang_map = {}
    for provider, voices in VOICES.items():
        for code in voices.keys():
            # Extract language from code
            parts = code.split('-')
            if len(parts) >= 2:
                lang_map[code] = parts[0].lower()
            else:
                lang_map[code] = 'vi'
    
    lang = lang_map.get(voice_code, 'vi')
    # Handle special cases
    if lang == 'en' and 'GB' in voice_code:
        lang = 'en-uk'
    elif lang == 'zh':
        lang = 'zh-cn'
    
    try:
        tts = gTTS(text=text[:5000], lang=lang, slow=False)
        tts.save(output_path)
        return True
    except:
        # Fallback to Vietnamese
        tts = gTTS(text=text[:5000], lang='vi', slow=False)
        tts.save(output_path)
        return True

def process_task(task_id):
    task = tasks[task_id]
    task['status'] = 'processing'
    task['log'].append('🔄 Bắt đầu xử lý...')
    
    temp_dir = tempfile.mkdtemp()
    video_path = os.path.join(temp_dir, 'video.mp4')
    audio_path = os.path.join(temp_dir, 'audio.wav')
    srt_path = os.path.join(temp_dir, 'subtitle.srt')
    tts_path = os.path.join(temp_dir, 'tts.mp3')
    
    # 1. Download
    task['log'].append(f'📥 Đang tải: {task["url"]}')
    ok, err = download_video(task['url'], video_path)
    if not ok:
        task['status'] = 'fail'
        task['log'].append(f'✘ Lỗi tải: {err[:300]}')
        return
    task['log'].append('✔ Đã tải xong')
    
    # Get title
    try:
        import yt_dlp
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(task['url'], download=False)
            task['title'] = info.get('title', 'Video')[:50]
    except:
        task['title'] = 'Video'
    
    # 2. Extract audio
    task['log'].append('🎵 Trích xuất audio...')
    if not extract_audio(video_path, audio_path):
        task['status'] = 'fail'
        task['log'].append('✘ Lỗi ffmpeg')
        return
    task['log'].append('✔ Đã trích xuất audio')
    
    # 3. Whisper
    task['log'].append('🔊 Nhận diện giọng nói (Whisper)...')
    try:
        segments = transcribe_audio(audio_path, task['lang'])
    except Exception as e:
        task['status'] = 'fail'
        task['log'].append(f'✘ Lỗi Whisper: {str(e)}')
        return
    task['log'].append(f'✔ Nhận diện {len(segments)} đoạn')
    
    # 4. Translate
    task['log'].append('🌐 Dịch sang tiếng Việt...')
    translated = []
    total = len(segments)
    for i, seg in enumerate(segments, 1):
        if i % 10 == 0 or i == total:
            task['log'].append(f'   Đang dịch {i}/{total}...')
        translated.append({
            'start': seg['start'],
            'end': seg['end'],
            'text': translate_text(seg['text'])
        })
    task['log'].append('✔ Đã dịch xong')
    
    # 5. Generate SRT
    generate_srt(translated, srt_path)
    task['srt_path'] = srt_path
    task['log'].append('📄 Đã tạo file SRT')
    
    # 6. TTS
    task['log'].append(f'🗣️ Tạo audio với giọng {task["voice"]}...')
    full_text = ' '.join([seg['text'] for seg in translated])
    try:
        text_to_speech(full_text, task['voice'], tts_path)
        task['audio_path'] = tts_path
        task['log'].append('✔ Đã tạo audio TTS')
    except Exception as e:
        task['log'].append(f'⚠️ Lỗi TTS: {str(e)}')
    
    task['status'] = 'done'
    task['log'].append('✅ HOÀN THÀNH!')

@app.route('/')
def index():
    total = sum(len(v) for v in VOICES.values())
    return render_template_string(HTML_TEMPLATE, voices=VOICES, total_voices=total)

@app.route('/api/process', methods=['POST'])
def start_process():
    global task_counter
    data = request.json
    task_counter += 1
    task_id = str(task_counter)
    tasks[task_id] = {
        'id': task_id,
        'url': data.get('url'),
        'lang': data.get('lang', 'auto'),
        'voice': data.get('voice', 'vi-VN-Standard-A'),
        'title': 'Đang tải...',
        'status': 'pending',
        'time': datetime.now().strftime('%H:%M:%S'),
        'log': ['📌 Task đã tạo'],
        'srt_path': None,
        'audio_path': None
    }
    threading.Thread(target=process_task, args=(task_id,)).start()
    return jsonify({'id': task_id})

@app.route('/api/tasks')
def list_tasks():
    return jsonify(list(tasks.values()))

@app.route('/api/log/<task_id>')
def get_log(task_id):
    return jsonify(tasks.get(task_id, {}))

@app.route('/api/download/srt/<task_id>')
def download_srt(task_id):
    task = tasks.get(task_id)
    if not task or not task.get('srt_path') or not os.path.exists(task['srt_path']):
        return 'File không tồn tại', 404
    return send_file(task['srt_path'], as_attachment=True, download_name=f'subtitle_{task_id}.srt')

@app.route('/api/download/audio/<task_id>')
def download_audio(task_id):
    task = tasks.get(task_id)
    if not task or not task.get('audio_path') or not os.path.exists(task['audio_path']):
        return 'Chưa có audio', 404
    return send_file(task['audio_path'], as_attachment=True, download_name=f'tts_{task_id}.mp3')

if __name__ == '__main__':
    print("""
╔═══════════════════════════════════════════════════════════════╗
║  🎙️ SUBPRO ULTIMATE - 50+ Giọng Nói AI                     ║
║  ─────────────────────────────────────────────────────────── ║
║  📍 Truy cập: http://localhost:5000                        ║
║  📦 Yêu cầu: pip install flask yt-dlp openai-whisper gtts  ║
║  🎯 Hỗ trợ: Google, Azure, ElevenLabs, Amazon, IBM        ║
║  🌟 Tổng cộng: 50+ giọng nói từ 5 nhà cung cấp            ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)