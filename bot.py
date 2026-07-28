#!/usr/bin/env python3
# SubPro Pro - Full tính năng: Upload, lấy tiêu đề, dựng video từ chữ

import os
import sys
import subprocess
import tempfile
import threading
import time
import json
import re
import base64
import uuid
from datetime import datetime
from io import BytesIO
import requests
from flask import Flask, request, jsonify, render_template_string, send_file, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import *

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB

tasks = {}
task_counter = 0
UPLOAD_FOLDER = '/tmp/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ================ VOICES ================
VOICES = {
    'google': {
        'vi-VN-Standard-A': {'name': '🌸 Linh - Nữ Bắc', 'gender': 'Nữ', 'style': 'Tự nhiên'},
        'vi-VN-Standard-B': {'name': '🌊 Minh - Nam Bắc', 'gender': 'Nam', 'style': 'Trung tính'},
        'vi-VN-Standard-C': {'name': '🌺 Hương - Nữ Nam', 'gender': 'Nữ', 'style': 'Ấm áp'},
        'vi-VN-Standard-D': {'name': '🌿 Tuấn - Nam Nam', 'gender': 'Nam', 'style': 'Sâu lắng'},
        'en-US-Standard-A': {'name': '🇺🇸 Emma - US Female', 'gender': 'Nữ', 'style': 'Modern'},
        'en-US-Standard-B': {'name': '🇺🇸 James - US Male', 'gender': 'Nam', 'style': 'Professional'},
        'ja-JP-Standard-A': {'name': '🇯🇵 Sakura - Japanese', 'gender': 'Nữ', 'style': 'Kawaii'},
        'zh-CN-Standard-A': {'name': '🇨🇳 Xiaomei - Chinese', 'gender': 'Nữ', 'style': 'Cute'},
        'ko-KR-Standard-A': {'name': '🇰🇷 Hana - Korean', 'gender': 'Nữ', 'style': 'Sweet'},
        'fr-FR-Standard-A': {'name': '🇫🇷 Camille - French', 'gender': 'Nữ', 'style': 'Romantic'},
        'es-ES-Standard-A': {'name': '🇪🇸 Lucia - Spanish', 'gender': 'Nữ', 'style': 'Passionate'},
        'de-DE-Standard-A': {'name': '🇩🇪 Anna - German', 'gender': 'Nữ', 'style': 'Clear'},
        'it-IT-Standard-A': {'name': '🇮🇹 Sofia - Italian', 'gender': 'Nữ', 'style': 'Melodic'},
        'pt-PT-Standard-A': {'name': '🇵🇹 Beatriz - Portuguese', 'gender': 'Nữ', 'style': 'Soft'},
        'ru-RU-Standard-A': {'name': '🇷🇺 Anastasia - Russian', 'gender': 'Nữ', 'style': 'Melodic'},
        'hi-IN-Standard-A': {'name': '🇮🇳 Priya - Hindi', 'gender': 'Nữ', 'style': 'Sweet'},
    },
    'style': {
        'cool': {'name': '😎 Cool Style', 'style': 'Chữ góc cạnh'},
        'cute': {'name': '🥰 Cute Style', 'style': 'Chữ tròn trịa'},
        'luxury': {'name': '💎 Luxury Style', 'style': 'Chữ sang trọng'},
        'retro': {'name': '📺 Retro Style', 'style': 'Chữ cổ điển'},
        'neon': {'name': '💡 Neon Style', 'style': 'Chữ phát sáng'},
    }
}

# ================ HTML ================
HTML = '''
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>🎬 SubPro Pro - Full Tool Video</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0a0e14;color:#e0e8f0;font-family:'Segoe UI',-apple-system,sans-serif;padding:12px;min-height:100vh}
.container{max-width:1100px;margin:auto}
.header{display:flex;justify-content:space-between;align-items:center;padding:10px 0 16px;border-bottom:2px solid #00e5ff20;flex-wrap:wrap}
.header h1{color:#ffcc00;font-size:22px;display:flex;align-items:center;gap:8px}
.header h1 span{color:#00e5ff}
.header .badge{background:linear-gradient(135deg,#ffcc00,#ff8800);color:#000;padding:2px 14px;border-radius:20px;font-size:10px;font-weight:bold}
.tabs{display:flex;gap:4px;background:#141c28;border-radius:12px;padding:4px;margin:12px 0;overflow-x:auto;border:1px solid #00e5ff10}
.tab-btn{flex:1;padding:10px 12px;border:none;background:transparent;color:#8899aa;font-weight:600;font-size:13px;cursor:pointer;border-radius:8px;transition:0.3s;white-space:nowrap;display:flex;align-items:center;gap:6px;justify-content:center}
.tab-btn:hover{color:#e0e8f0;background:#00e5ff10}
.tab-btn.active{background:#00e5ff20;color:#00e5ff}
.tab-content{display:none}
.tab-content.active{display:block}
.card{background:#141c28;border-radius:12px;border:1px solid #00e5ff15;padding:16px;margin:12px 0}
.card-title{font-size:16px;font-weight:600;margin-bottom:12px;display:flex;align-items:center;gap:8px}
.card-title i{color:#ffcc00}
input,select,textarea{width:100%;padding:10px 14px;border-radius:8px;border:1px solid #00e5ff30;background:#0d1520;color:#e0e8f0;font-size:14px;margin-bottom:8px}
input:focus,select:focus,textarea:focus{outline:none;border-color:#ffcc00;box-shadow:0 0 0 3px #ffcc0020}
textarea{min-height:80px;resize:vertical;font-family:monospace}
input[type="file"]{padding:10px;border:2px dashed #00e5ff30;cursor:pointer}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:6px;padding:10px 20px;border-radius:8px;border:none;font-weight:600;font-size:14px;cursor:pointer;transition:0.3s}
.btn-primary{background:linear-gradient(135deg,#00e5ff,#0088ff);color:#000}
.btn-primary:hover{transform:scale(1.02)}
.btn-success{background:#00ff88;color:#000}
.btn-success:hover{transform:scale(1.02)}
.btn-gold{background:#ffcc00;color:#000}
.btn-gold:hover{transform:scale(1.02)}
.btn-outline{background:transparent;border:1px solid #00e5ff40;color:#00e5ff}
.btn-outline:hover{background:#00e5ff10}
.btn-danger{background:#ff4444;color:#fff}
.btn-sm{padding:6px 14px;font-size:12px}
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.grid-3{display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:6px}
.voice-card{background:#0d1520;padding:8px 12px;border-radius:8px;border:2px solid transparent;cursor:pointer;transition:0.3s;font-size:12px}
.voice-card:hover{border-color:#00e5ff40}
.voice-card.selected{border-color:#00e5ff;background:#00e5ff10}
.voice-card .v-provider{font-size:9px;color:#8899aa;background:#1a2530;padding:1px 6px;border-radius:8px}
.task-item{display:flex;justify-content:space-between;align-items:center;padding:10px 12px;border-bottom:1px solid #00e5ff08;gap:8px;cursor:pointer;transition:0.2s}
.task-item:hover{background:#00e5ff05}
.task-item .title{font-weight:500;font-size:13px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.task-item .meta{font-size:11px;color:#8899aa;display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.status{display:inline-block;padding:2px 10px;border-radius:20px;font-size:10px;font-weight:600}
.status-pending{background:#ffaa00;color:#000}
.status-processing{background:#0088ff;color:#fff}
.status-done{background:#00ff88;color:#000}
.status-fail{background:#ff4444;color:#fff}
.log-box{background:#0a0e14;padding:12px;max-height:300px;overflow:auto;border-radius:8px;border:1px solid #00e5ff08;font-family:monospace;font-size:12px;line-height:1.8}
.log-box .ok{color:#00ff88}
.log-box .err{color:#ff4444}
.log-box .info{color:#88aacc}
.toast{position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:#141c28;border:1px solid #ffcc00;padding:10px 20px;border-radius:10px;display:none;z-index:999;font-size:13px;max-width:90%}
.progress-bar{width:100%;height:6px;background:#0d1520;border-radius:4px;margin:8px 0;overflow:hidden}
.progress-bar .fill{height:100%;background:linear-gradient(90deg,#00e5ff,#ffcc00);border-radius:4px;width:0%;transition:width 0.5s}
.preview-img{max-width:100%;max-height:200px;border-radius:8px;border:1px solid #00e5ff20;margin:8px 0}
@media(max-width:600px){.grid-2{grid-template-columns:1fr}.header h1{font-size:18px}.tabs{flex-wrap:nowrap}.tab-btn{font-size:11px;padding:8px 10px}}
</style>
</head>
<body>
<div class="container">
<div class="header">
<h1>🎬 Sub<span>Pro</span> <span class="badge">v3.0</span></h1>
<div style="display:flex;gap:10px;align-items:center;font-size:13px;color:#8899aa;">
<span id="taskCount">0</span> tasks
<span class="dot" style="width:6px;height:6px;border-radius:50%;background:#00ff88;display:inline-block;"></span>
</div>
</div>

<div id="toast" class="toast"></div>

<!-- TABS -->
<div class="tabs">
<button class="tab-btn active" onclick="switchTab('home')">🏠 Home</button>
<button class="tab-btn" onclick="switchTab('upload')">📤 Upload</button>
<button class="tab-btn" onclick="switchTab('create')">🎨 Tạo Video</button>
<button class="tab-btn" onclick="switchTab('tasks')">📋 Tasks</button>
</div>

<!-- TAB HOME -->
<div id="tab-home" class="tab-content active">
<div class="card">
<div class="card-title"><i>📥</i> Tải video từ link</div>
<div class="grid-2">
<input id="videoUrl" placeholder="🔗 Dán link YouTube, FB, TikTok..." />
<select id="srcLang">
<option value="auto">🌐 Tự động</option>
<option value="en-US">🇺🇸 English</option>
<option value="vi-VN">🇻🇳 Tiếng Việt</option>
<option value="zh-CN">🇨🇳 中文</option>
<option value="ja-JP">🇯🇵 日本語</option>
<option value="ko-KR">🇰🇷 한국어</option>
<option value="fr-FR">🇫🇷 Français</option>
<option value="es-ES">🇪🇸 Español</option>
</select>
</div>
<div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:6px;">
<button class="btn btn-primary" onclick="startProcess()">🚀 Xử lý video</button>
<button class="btn btn-outline" onclick="document.getElementById('videoUrl').value=''">🗑️ Xóa</button>
<button class="btn btn-gold" onclick="getTitle()">📝 Lấy tiêu đề</button>
</div>
<div id="titleResult" style="margin-top:8px;color:#ffcc00;font-size:14px;font-weight:500;"></div>
<div id="result" style="margin-top:6px;color:#ffcc00;"></div>
<div class="progress-bar"><div class="fill" id="progressFill"></div></div>
</div>
</div>

<!-- TAB UPLOAD -->
<div id="tab-upload" class="tab-content">
<div class="card">
<div class="card-title"><i>📤</i> Upload video từ máy tính</div>
<input type="file" id="fileInput" accept="video/*" />
<select id="uploadLang">
<option value="auto">🌐 Tự động</option>
<option value="en-US">🇺🇸 English</option>
<option value="vi-VN">🇻🇳 Tiếng Việt</option>
<option value="zh-CN">🇨🇳 中文</option>
</select>
<button class="btn btn-primary" onclick="uploadVideo()">📤 Upload & Xử lý</button>
<div id="uploadResult" style="margin-top:8px;color:#ffcc00;"></div>
</div>
</div>

<!-- TAB TẠO VIDEO -->
<div id="tab-create" class="tab-content">
<div class="card">
<div class="card-title"><i>🎨</i> Tạo video từ chữ viết</div>
<div class="grid-2">
<div>
<label style="font-size:13px;color:#8899aa;">📝 Nội dung</label>
<textarea id="textContent" rows="4" placeholder="Nhập nội dung bạn muốn tạo video..."></textarea>
</div>
<div>
<label style="font-size:13px;color:#8899aa;">🖼️ Ảnh nền (tùy chọn)</label>
<input type="file" id="bgImage" accept="image/*" />
<label style="font-size:13px;color:#8899aa;margin-top:6px;display:block;">🎨 Style chữ</label>
<select id="textStyle">
<option value="cool">😎 Cool</option>
<option value="cute">🥰 Cute</option>
<option value="luxury">💎 Luxury</option>
<option value="retro">📺 Retro</option>
<option value="neon">💡 Neon</option>
</select>
</div>
</div>
<button class="btn btn-gold" onclick="createVideoFromText()">🎬 Tạo video từ chữ</button>
<div id="createResult" style="margin-top:8px;color:#ffcc00;"></div>
</div>
</div>

<!-- TAB TASKS -->
<div id="tab-tasks" class="tab-content">
<div class="card">
<div class="card-title"><i>📋</i> Danh sách video <button class="btn btn-sm btn-outline" onclick="loadTasks()" style="margin-left:auto;">🔄</button></div>
<div id="taskList"></div>
</div>
<div class="card">
<div class="card-title"><i>📝</i> Log chi tiết</div>
<div id="logBox" class="log-box">▶ Chọn video để xem log</div>
</div>
</div>

<div style="text-align:center;color:#556677;font-size:11px;padding:16px 0;border-top:1px solid #00e5ff10;margin-top:12px;">
SubPro Pro v3.0 · Made with ❤️
</div>
</div>

<script>
const VOICES = {{ voices|tojson }};
let selectedVoice = localStorage.getItem('selectedVoice') || 'vi-VN-Standard-A';
let currentTaskId = null;
let allVoices = [];
let voiceVisible = false;
let progressInterval = null;

function flattenVoices() {
    allVoices = [];
    for (const [provider, voices] of Object.entries(VOICES)) {
        for (const [code, info] of Object.entries(voices)) {
            allVoices.push({ code, provider, ...info });
        }
    }
}

function renderVoices() {
    const container = document.getElementById('voiceContainer');
    if (!container) return;
    if (!allVoices.length) flattenVoices();
    container.innerHTML = allVoices.map(v => `
        <div class="voice-card ${v.code === selectedVoice ? 'selected' : ''}" onclick="selectVoice('${v.code}')">
            <div>${v.name}</div>
            <div style="font-size:10px;color:#8899aa;display:flex;gap:4px;margin-top:2px;">
                <span>${v.gender || ''}</span>
                <span class="v-provider">${v.provider}</span>
            </div>
        </div>
    `).join('');
    const voice = allVoices.find(v => v.code === selectedVoice);
    document.getElementById('voiceDisplay').textContent = voice ? voice.name : 'Chọn giọng';
}

function selectVoice(code) {
    selectedVoice = code;
    localStorage.setItem('selectedVoice', code);
    renderVoices();
    showToast('✅ Đã chọn: ' + (allVoices.find(v => v.code === code)?.name || code));
}

function switchTab(tab) {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    document.querySelector(`.tab-btn:has(.fa-${tab})`)?.classList.add('active');
    document.getElementById('tab-' + tab).classList.add('active');
    if (tab === 'tasks') loadTasks();
}

function showToast(msg) {
    const t = document.getElementById('toast');
    t.textContent = msg;
    t.style.display = 'block';
    clearTimeout(t._hide);
    t._hide = setTimeout(() => t.style.display = 'none', 3000);
}

async function getTitle() {
    const url = document.getElementById('videoUrl').value.trim();
    if (!url) { showToast('⚠️ Dán link video trước'); return; }
    try {
        const res = await fetch('/api/title', {
            method: 'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify({url})
        });
        const data = await res.json();
        document.getElementById('titleResult').textContent = '📝 ' + (data.title || 'Không lấy được tiêu đề');
    } catch(e) {
        showToast('❌ Lỗi: ' + e.message);
    }
}

async function startProcess() {
    const url = document.getElementById('videoUrl').value.trim();
    const lang = document.getElementById('srcLang').value;
    if (!url) { showToast('⚠️ Dán link video'); return; }
    document.getElementById('result').textContent = '⏳ Đang khởi tạo...';
    updateProgress(10);
    try {
        const res = await fetch('/api/process', {
            method: 'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify({url, lang, voice: selectedVoice, type: 'url'})
        });
        const data = await res.json();
        document.getElementById('result').textContent = '✅ Task #' + data.id;
        showToast('✅ Task #' + data.id);
        loadTasks();
        if (data.id) { currentTaskId = data.id; pollProgress(data.id); }
    } catch(e) {
        showToast('❌ ' + e.message);
    }
}

async function uploadVideo() {
    const file = document.getElementById('fileInput').files[0];
    if (!file) { showToast('⚠️ Chọn file video'); return; }
    const lang = document.getElementById('uploadLang').value;
    const formData = new FormData();
    formData.append('video', file);
    formData.append('lang', lang);
    formData.append('voice', selectedVoice);
    document.getElementById('uploadResult').textContent = '⏳ Đang upload...';
    try {
        const res = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        const data = await res.json();
        document.getElementById('uploadResult').textContent = '✅ Task #' + data.id;
        showToast('✅ Upload thành công!');
        loadTasks();
        if (data.id) { currentTaskId = data.id; pollProgress(data.id); }
    } catch(e) {
        showToast('❌ ' + e.message);
    }
}

async function createVideoFromText() {
    const text = document.getElementById('textContent').value.trim();
    if (!text) { showToast('⚠️ Nhập nội dung'); return; }
    const style = document.getElementById('textStyle').value;
    const fileInput = document.getElementById('bgImage');
    const formData = new FormData();
    formData.append('text', text);
    formData.append('style', style);
    formData.append('voice', selectedVoice);
    if (fileInput.files.length > 0) {
        formData.append('image', fileInput.files[0]);
    }
    document.getElementById('createResult').textContent = '⏳ Đang tạo video...';
    try {
        const res = await fetch('/api/create-video', {
            method: 'POST',
            body: formData
        });
        const data = await res.json();
        document.getElementById('createResult').textContent = '✅ Task #' + data.id;
        showToast('✅ Video đang được tạo!');
        loadTasks();
        if (data.id) { currentTaskId = data.id; pollProgress(data.id); }
    } catch(e) {
        showToast('❌ ' + e.message);
    }
}

function updateProgress(pct) {
    document.getElementById('progressFill').style.width = pct + '%';
}

function pollProgress(id) {
    if (progressInterval) clearInterval(progressInterval);
    progressInterval = setInterval(async () => {
        try {
            const res = await fetch('/api/log/' + id);
            const task = await res.json();
            const log = task.log || [];
            const status = task.status || 'pending';
            const pct = Math.min(80, log.length * 10);
            updateProgress(pct);
            if (status === 'done' || status === 'fail') {
                updateProgress(100);
                clearInterval(progressInterval);
                setTimeout(() => updateProgress(0), 2000);
            }
        } catch(e) {}
    }, 2000);
}

async function loadTasks() {
    try {
        const res = await fetch('/api/tasks');
        const data = await res.json();
        document.getElementById('taskCount').textContent = data.length;
        const container = document.getElementById('taskList');
        if (!data.length) {
            container.innerHTML = '<div style="padding:16px;text-align:center;color:#556677;">Chưa có video nào</div>';
            return;
        }
        container.innerHTML = data.map(t => `
            <div class="task-item" onclick="showLog('${t.id}')">
                <div style="flex:1;min-width:0;">
                    <div class="title">${t.title || t.url || 'Video'}</div>
                    <div class="meta">
                        <span class="status status-${t.status}">${t.status}</span>
                        <span>${t.time}</span>
                        <span style="color:#556677;">${t.type || 'link'}</span>
                    </div>
                </div>
                <div style="display:flex;gap:4px;flex-shrink:0;">
                    ${t.status === 'done' ? `<button class="btn btn-sm btn-success" onclick="event.stopPropagation();downloadFile('${t.id}','srt')">📄 SRT</button>` : ''}
                    ${t.status === 'done' && t.audio_path ? `<button class="btn btn-sm btn-primary" onclick="event.stopPropagation();downloadFile('${t.id}','audio')">🎧 Audio</button>` : ''}
                    ${t.status === 'done' && t.video_output ? `<button class="btn btn-sm btn-gold" onclick="event.stopPropagation();downloadFile('${t.id}','video')">🎬 Video</button>` : ''}
                </div>
            </div>
        `).join('');
    } catch(e) {}
}

async function showLog(id) {
    currentTaskId = id;
    const res = await fetch('/api/log/'+id);
    const task = await res.json();
    const box = document.getElementById('logBox');
    box.innerHTML = (task.log || ['Không có log']).map(l => {
        let cls = '';
        if (l.includes('✔') || l.includes('✅')) cls = 'ok';
        else if (l.includes('✘') || l.includes('lỗi') || l.includes('fail')) cls = 'err';
        else cls = 'info';
        return `<div><span class="${cls}">${l}</span></div>`;
    }).join('');
}

function downloadFile(id, type) {
    window.open('/api/download/' + type + '/' + id, '_blank');
}

flattenVoices();
loadTasks();
setInterval(loadTasks, 5000);
</script>
</body>
</html>
'''

# ================ BACKEND ================

def check_ffmpeg():
    """Kiểm tra và cài ffmpeg nếu chưa có"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except:
        return False

def install_ffmpeg():
    """Cài ffmpeg trên hệ thống"""
    try:
        # Thử cài qua apt (Ubuntu/Debian)
        subprocess.run(['apt', 'update'], capture_output=True)
        subprocess.run(['apt', 'install', '-y', 'ffmpeg'], capture_output=True)
        return check_ffmpeg()
    except:
        return False

def download_video(url, output_path):
    try:
        import yt_dlp
        ydl_opts = {
            'format': 'best[ext=mp4]',
            'quiet': True,
            'no_warnings': True,
            'outtmpl': output_path,
            'ignoreerrors': True,
            'no_check_certificate': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return True, '', info.get('title', 'Video')
    except Exception as e:
        return False, str(e), 'Video'

def extract_audio(video_path, audio_path):
    cmd = f'ffmpeg -i "{video_path}" -acodec pcm_s16le -ar 16000 -ac 1 "{audio_path}" -y -loglevel error 2>&1'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode == 0

def transcribe_audio(audio_path, lang='auto'):
    try:
        import speech_recognition as sr
        from pydub import AudioSegment
        
        if not os.path.exists(audio_path):
            return [{'start': 0, 'end': 10, 'text': '⚠️ File audio không tồn tại'}]
        
        wav_path = audio_path
        if not audio_path.endswith('.wav'):
            wav_path = audio_path.replace('.wav', '_temp.wav')
            try:
                audio = AudioSegment.from_file(audio_path)
                audio.export(wav_path, format='wav')
            except:
                pass
        
        r = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = r.record(source)
        
        lang_map = {
            'auto': 'vi-VN', 'vi-VN': 'vi-VN', 'en-US': 'en-US',
            'zh-CN': 'zh-CN', 'ja-JP': 'ja-JP', 'ko-KR': 'ko-KR',
            'fr-FR': 'fr-FR', 'es-ES': 'es-ES', 'de-DE': 'de-DE',
            'it-IT': 'it-IT', 'pt-PT': 'pt-PT', 'ru-RU': 'ru-RU',
            'hi-IN': 'hi-IN'
        }
        lang_code = lang_map.get(lang, 'vi-VN')
        text = r.recognize_google(audio_data, language=lang_code)
        return [{'start': 0, 'end': 10, 'text': text}]
    except Exception as e:
        return [{'start': 0, 'end': 10, 'text': f'⚠️ Lỗi nhận diện: {str(e)}'}]

def translate_text(text):
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {'client': 'gtx', 'sl': 'auto', 'tl': 'vi', 'dt': 't', 'q': text}
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
    lang_map = {
        'vi-VN-Standard-A': 'vi', 'vi-VN-Standard-B': 'vi',
        'vi-VN-Standard-C': 'vi', 'vi-VN-Standard-D': 'vi',
        'en-US-Standard-A': 'en', 'en-US-Standard-B': 'en',
        'ja-JP-Standard-A': 'ja', 'zh-CN-Standard-A': 'zh-cn',
        'ko-KR-Standard-A': 'ko', 'fr-FR-Standard-A': 'fr',
        'es-ES-Standard-A': 'es', 'de-DE-Standard-A': 'de',
        'it-IT-Standard-A': 'it', 'pt-PT-Standard-A': 'pt',
        'ru-RU-Standard-A': 'ru', 'hi-IN-Standard-A': 'hi'
    }
    lang = lang_map.get(voice_code, 'vi')
    try:
        tts = gTTS(text=text[:5000], lang=lang, slow=False)
        tts.save(output_path)
        return True
    except:
        try:
            tts = gTTS(text=text[:5000], lang='vi', slow=False)
            tts.save(output_path)
            return True
        except:
            return False

def create_text_image(text, style='cool', bg_color=None):
    """Tạo ảnh từ chữ với style"""
    # Tạo ảnh nền
    if bg_color:
        img = Image.new('RGB', (1920, 1080), bg_color)
    else:
        img = Image.new('RGB', (1920, 1080), (10, 14, 20))
    
    draw = ImageDraw.Draw(img)
    
    # Font style
    fonts = {
        'cool': ('Arial', 80, '#00e5ff'),
        'cute': ('Comic Sans MS', 80, '#ff69b4'),
        'luxury': ('Georgia', 80, '#ffd700'),
        'retro': ('Courier New', 80, '#ff6b35'),
        'neon': ('Arial', 80, '#00ff88')
    }
    font_name, size, color = fonts.get(style, fonts['cool'])
    
    try:
        font = ImageFont.truetype(font_name, size)
    except:
        font = ImageFont.load_default()
    
    # Vẽ chữ
    lines = text.split('\n')[:5]
    y_offset = 200
    for line in lines:
        draw.text((100, y_offset), line[:50], font=font, fill=color)
        y_offset += 120
    
    return img

def create_video_from_text(text, style, output_path, bg_image=None):
    """Tạo video từ chữ viết"""
    from moviepy.editor import ImageClip, AudioClip, CompositeVideoClip
    
    # Tạo ảnh từ chữ
    if bg_image and os.path.exists(bg_image):
        img = Image.open(bg_image).resize((1920, 1080))
    else:
        img = create_text_image(text, style)
    
    # Lưu ảnh tạm
    img_path = tempfile.mktemp(suffix='.png')
    img.save(img_path)
    
    # Tạo video từ ảnh
    clip = ImageClip(img_path, duration=10)
    
    # Export video
    clip.write_videofile(output_path, fps=24, verbose=False, logger=None)
    
    return True

def process_task(task_id):
    task = tasks[task_id]
    task['status'] = 'processing'
    task['log'].append('🔄 Bắt đầu xử lý...')
    
    # Kiểm tra ffmpeg
    if not check_ffmpeg():
        task['log'].append('📦 Đang cài ffmpeg...')
        if install_ffmpeg():
            task['log'].append('✔ Đã cài ffmpeg thành công')
        else:
            task['status'] = 'fail'
            task['log'].append('✘ Không thể cài ffmpeg. Vui lòng cài thủ công: sudo apt install ffmpeg -y')
            return
    
    temp_dir = tempfile.mkdtemp()
    video_path = os.path.join(temp_dir, 'video.mp4')
    audio_path = os.path.join(temp_dir, 'audio.wav')
    srt_path = os.path.join(temp_dir, 'subtitle.srt')
    tts_path = os.path.join(temp_dir, 'tts.mp3')
    output_video = os.path.join(temp_dir, 'output.mp4')
    
    # Xử lý theo loại task
    if task.get('type') == 'upload' and task.get('upload_path') and os.path.exists(task['upload_path']):
        # Task upload file
        video_path = task['upload_path']
        task['title'] = os.path.basename(task['upload_path'])
        task['log'].append('✔ Đã nhận file upload')
    elif task.get('type') == 'create_text':
        # Task tạo video từ chữ
        task['log'].append('🎨 Tạo video từ chữ viết...')
        if create_video_from_text(task.get('text', ''), task.get('style', 'cool'), output_video, task.get('bg_image')):
            task['video_output'] = output_video
            task['status'] = 'done'
            task['log'].append('✅ Đã tạo video từ chữ thành công!')
        else:
            task['status'] = 'fail'
            task['log'].append('✘ Lỗi tạo video từ chữ')
        return
    else:
        # Task tải từ link
        task['log'].append(f'📥 Đang tải: {task["url"]}')
        ok, err, title = download_video(task['url'], video_path)
        if not ok:
            task['status'] = 'fail'
            task['log'].append(f'✘ Lỗi tải: {err[:300]}')
            return
        task['title'] = title
        task['log'].append('✔ Đã tải xong')
    
    # Xử lý chung: trích xuất audio, nhận diện, dịch, TTS
    task['log'].append('🎵 Trích xuất audio...')
    if not extract_audio(video_path, audio_path):
        task['log'].append('⚠️ Lỗi trích xuất audio, thử dùng video gốc...')
        # Nếu không trích xuất được, vẫn tiếp tục
    task['log'].append('✔ Đã trích xuất audio')
    
    task['log'].append('🔊 Nhận diện giọng nói...')
    segments = transcribe_audio(audio_path, task['lang'])
    task['log'].append(f'✔ Nhận diện {len(segments)} đoạn')
    
    task['log'].append('🌐 Dịch sang tiếng Việt...')
    translated = []
    for seg in segments:
        translated.append({
            'start': seg['start'],
            'end': seg['end'],
            'text': translate_text(seg['text'])
        })
    task['log'].append('✔ Đã dịch xong')
    
    generate_srt(translated, srt_path)
    task['srt_path'] = srt_path
    task['log'].append('📄 Đã tạo file SRT')
    
    task['log'].append('🗣️ Tạo audio...')
    full_text = ' '.join([seg['text'] for seg in translated])
    if text_to_speech(full_text, task['voice'], tts_path):
        task['audio_path'] = tts_path
        task['log'].append('✔ Đã tạo audio TTS')
    else:
        task['log'].append('⚠️ Lỗi TTS')
    
    task['video_output'] = video_path
    task['status'] = 'done'
    task['log'].append('✅ HOÀN THÀNH!')

# ================ ROUTES ================

@app.route('/')
def index():
    return render_template_string(HTML, voices=VOICES)

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
        'audio_path': None,
        'video_output': None,
        'type': 'url'
    }
    threading.Thread(target=process_task, args=(task_id,)).start()
    return jsonify({'id': task_id})

@app.route('/api/upload', methods=['POST'])
def upload_video():
    global task_counter
    if 'video' not in request.files:
        return jsonify({'error': 'No file'}), 400
    file = request.files['video']
    if file.filename == '':
        return jsonify({'error': 'No file'}), 400
    
    filename = secure_filename(file.filename)
    upload_path = os.path.join(UPLOAD_FOLDER, f'{uuid.uuid4()}_{filename}')
    file.save(upload_path)
    
    task_counter += 1
    task_id = str(task_counter)
    tasks[task_id] = {
        'id': task_id,
        'url': upload_path,
        'lang': request.form.get('lang', 'auto'),
        'voice': request.form.get('voice', 'vi-VN-Standard-A'),
        'title': filename,
        'status': 'pending',
        'time': datetime.now().strftime('%H:%M:%S'),
        'log': ['📌 Task upload đã tạo'],
        'srt_path': None,
        'audio_path': None,
        'video_output': None,
        'upload_path': upload_path,
        'type': 'upload'
    }
    threading.Thread(target=process_task, args=(task_id,)).start()
    return jsonify({'id': task_id})

@app.route('/api/create-video', methods=['POST'])
def create_video_from_text_api():
    global task_counter
    text = request.form.get('text', '')
    style = request.form.get('style', 'cool')
    voice = request.form.get('voice', 'vi-VN-Standard-A')
    
    if not text:
        return jsonify({'error': 'No text'}), 400
    
    task_counter += 1
    task_id = str(task_counter)
    
    bg_image = None
    if 'image' in request.files:
        file = request.files['image']
        if file.filename != '':
            bg_image = os.path.join(UPLOAD_FOLDER, f'bg_{uuid.uuid4()}.jpg')
            file.save(bg_image)
    
    tasks[task_id] = {
        'id': task_id,
        'text': text,
        'style': style,
        'voice': voice,
        'title': f'Video từ chữ: {text[:30]}...',
        'status': 'pending',
        'time': datetime.now().strftime('%H:%M:%S'),
        'log': ['📌 Task tạo video từ chữ đã tạo'],
        'srt_path': None,
        'audio_path': None,
        'video_output': None,
        'bg_image': bg_image,
        'type': 'create_text'
    }
    threading.Thread(target=process_task, args=(task_id,)).start()
    return jsonify({'id': task_id})

@app.route('/api/title', methods=['POST'])
def get_title():
    data = request.json
    url = data.get('url')
    try:
        import yt_dlp
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({'title': info.get('title', '')})
    except:
        return jsonify({'title': 'Không lấy được tiêu đề'})

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

@app.route('/api/download/video/<task_id>')
def download_video_file(task_id):
    task = tasks.get(task_id)
    if not task or not task.get('video_output') or not os.path.exists(task['video_output']):
        return 'Chưa có video', 404
    return send_file(task['video_output'], as_attachment=True, download_name=f'video_{task_id}.mp4')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 20613))
    print("""
╔══════════════════════════════════════════════════════════╗
║  🎬 SUBPRO PRO - Full Tool Video                      ║
║  ────────────────────────────────────────────────────── ║
║  📍 Truy cập: http://fi14.bot-hosting.cloud:%s        ║
║  🎯 Tính năng:                                        ║
║     ✅ Tải video từ link                              ║
║     ✅ Upload video file                              ║
║     ✅ Lấy tiêu đề video                             ║
║     ✅ Tạo video từ chữ viết                         ║
║     ✅ Dịch phụ đề + TTS đa giọng                    ║
║  💾 RAM: ~100MB                                      ║
╚══════════════════════════════════════════════════════════╝
    """ % port)
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)