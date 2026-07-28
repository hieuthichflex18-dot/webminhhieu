#!/usr/bin/env python3
# SubPro Lite - Dịch phụ đề + TTS, nhẹ, chạy trên RAM 256MB

import os
import sys
import subprocess
import tempfile
import threading
import time
import json
from datetime import datetime
import requests
from flask import Flask, request, jsonify, render_template_string, send_file

app = Flask(__name__)
tasks = {}
task_counter = 0

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
    }
}

# ================ HTML ================
HTML = '''
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🎙️ SubPro Lite - Dịch Phụ Đề</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0a0e14;color:#e0e8f0;font-family:'Segoe UI',-apple-system,sans-serif;padding:16px}
.container{max-width:1000px;margin:auto}
.header{display:flex;justify-content:space-between;align-items:center;padding:10px 0 20px;border-bottom:1px solid #00e5ff20;flex-wrap:wrap}
.header h1{color:#ffcc00;font-size:24px;display:flex;align-items:center;gap:10px}
.header h1 span{color:#00e5ff}
.header .badge{background:#00e5ff20;color:#00e5ff;padding:2px 12px;border-radius:20px;font-size:11px}
.card{background:#141c28;border-radius:12px;border:1px solid #00e5ff15;padding:20px;margin:15px 0}
.card-title{font-size:17px;font-weight:600;margin-bottom:14px;display:flex;align-items:center;gap:10px}
.card-title i{color:#ffcc00}
input,select{width:100%;padding:12px 16px;border-radius:8px;border:1px solid #00e5ff30;background:#0d1520;color:#e0e8f0;font-size:15px;margin-bottom:10px}
input:focus,select:focus{outline:none;border-color:#ffcc00;box-shadow:0 0 0 3px #ffcc0020}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;padding:12px 28px;border-radius:8px;border:none;font-weight:600;font-size:15px;cursor:pointer;transition:0.3s}
.btn-primary{background:linear-gradient(135deg,#00e5ff,#0088ff);color:#000}
.btn-primary:hover{transform:scale(1.02);box-shadow:0 4px 20px #00e5ff40}
.btn-outline{background:transparent;border:1px solid #00e5ff40;color:#00e5ff}
.btn-outline:hover{background:#00e5ff10}
.btn-sm{padding:6px 16px;font-size:12px}
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:15px}
.grid-3{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:8px}
.voice-card{background:#0d1520;padding:10px 14px;border-radius:8px;border:2px solid transparent;cursor:pointer;transition:0.3s;font-size:13px}
.voice-card:hover{border-color:#00e5ff40}
.voice-card.selected{border-color:#00e5ff;background:#00e5ff10}
.voice-card .v-provider{font-size:10px;color:#8899aa;background:#1a2530;padding:1px 8px;border-radius:10px}
.task-item{display:flex;justify-content:space-between;align-items:center;padding:12px 14px;border-bottom:1px solid #00e5ff08;gap:10px;cursor:pointer;transition:0.2s}
.task-item:hover{background:#00e5ff05}
.task-item .title{font-weight:500;font-size:14px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.task-item .meta{font-size:12px;color:#8899aa;display:flex;gap:10px;align-items:center}
.status{display:inline-block;padding:2px 12px;border-radius:20px;font-size:11px;font-weight:600}
.status-pending{background:#ffaa00;color:#000}
.status-processing{background:#0088ff;color:#fff}
.status-done{background:#00ff88;color:#000}
.status-fail{background:#ff4444;color:#fff}
.log-box{background:#0a0e14;padding:14px;max-height:350px;overflow:auto;border-radius:8px;border:1px solid #00e5ff08;font-family:monospace;font-size:13px;line-height:1.8}
.log-box .time{color:#ffcc00}
.log-box .ok{color:#00ff88}
.log-box .err{color:#ff4444}
.log-box .info{color:#88aacc}
.toast{position:fixed;bottom:30px;left:50%;transform:translateX(-50%);background:#141c28;border:1px solid #ffcc00;padding:12px 24px;border-radius:10px;display:none;z-index:999;font-size:14px;box-shadow:0 8px 30px rgba(0,0,0,0.6)}
@media(max-width:600px){.grid-2{grid-template-columns:1fr}.header h1{font-size:20px}}
</style>
</head>
<body>
<div class="container">
<div class="header">
<h1>🎙️ Sub<span>Pro</span> <span class="badge">Lite</span></h1>
<span style="color:#8899aa;font-size:13px;"><span id="taskCount">0</span> tasks</span>
</div>

<div id="toast" class="toast"></div>

<div class="card">
<div class="card-title"><i>📥</i> Tạo video mới</div>
<div class="grid-2">
<input id="videoUrl" placeholder="🔗 Dán link video (YouTube, FB, TikTok...)" />
<select id="srcLang">
<option value="auto">🌐 Tự động nhận diện</option>
<option value="en-US">🇺🇸 English</option>
<option value="vi-VN">🇻🇳 Tiếng Việt</option>
<option value="zh-CN">🇨🇳 中文</option>
<option value="ja-JP">🇯🇵 日本語</option>
<option value="ko-KR">🇰🇷 한국어</option>
<option value="fr-FR">🇫🇷 Français</option>
<option value="es-ES">🇪🇸 Español</option>
<option value="de-DE">🇩🇪 Deutsch</option>
<option value="it-IT">🇮🇹 Italiano</option>
<option value="pt-PT">🇵🇹 Português</option>
<option value="ru-RU">🇷🇺 Русский</option>
<option value="hi-IN">🇮🇳 हिन्दी</option>
</select>
</div>
<div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:6px;">
<button class="btn btn-primary" onclick="startProcess()">🚀 Bắt đầu xử lý</button>
<button class="btn btn-outline" onclick="clearInput()">🗑️ Xóa</button>
<span style="margin-left:auto;color:#8899aa;font-size:13px;display:flex;align-items:center;gap:6px;">
🎤 <span id="voiceDisplay">Chọn giọng</span>
</span>
</div>
<div id="result" style="margin-top:12px;color:#ffcc00;font-weight:500;"></div>
</div>

<div class="card">
<div class="card-title"><i>🗣️</i> Giọng nói <button class="btn btn-sm btn-outline" onclick="toggleVoices()" style="margin-left:auto;">Hiện</button></div>
<div id="voiceContainer" class="grid-3" style="display:none;"></div>
</div>

<div class="card">
<div class="card-title"><i>📋</i> Video của tôi <button class="btn btn-sm btn-outline" onclick="loadTasks()" style="margin-left:auto;">🔄</button></div>
<div id="taskList"></div>
</div>

<div class="card">
<div class="card-title"><i>📝</i> Log chi tiết</div>
<div id="logBox" class="log-box">▶ Chọn video để xem log</div>
</div>
</div>

<script>
const VOICES = {{ voices|tojson }};
let selectedVoice = localStorage.getItem('selectedVoice') || 'vi-VN-Standard-A';
let currentTaskId = null;
let allVoices = [];
let voiceVisible = false;

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
    if (!allVoices.length) flattenVoices();
    container.innerHTML = allVoices.map(v => `
        <div class="voice-card ${v.code === selectedVoice ? 'selected' : ''}" onclick="selectVoice('${v.code}')">
            <div>${v.name}</div>
            <div style="font-size:11px;color:#8899aa;display:flex;gap:8px;margin-top:2px;">
                <span>${v.gender}</span>
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

function toggleVoices() {
    voiceVisible = !voiceVisible;
    document.getElementById('voiceContainer').style.display = voiceVisible ? 'grid' : 'none';
    if (voiceVisible) renderVoices();
}

function showToast(msg) {
    const t = document.getElementById('toast');
    t.textContent = msg;
    t.style.display = 'block';
    clearTimeout(t._hide);
    t._hide = setTimeout(() => t.style.display = 'none', 3000);
}

function clearInput() {
    document.getElementById('videoUrl').value = '';
    document.getElementById('result').textContent = '';
}

async function startProcess() {
    const url = document.getElementById('videoUrl').value.trim();
    const lang = document.getElementById('srcLang').value;
    if (!url) { showToast('⚠️ Vui lòng dán link video'); return; }
    document.getElementById('result').textContent = '⏳ Đang khởi tạo...';
    try {
        const res = await fetch('/api/process', {
            method: 'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify({url, lang, voice: selectedVoice})
        });
        const data = await res.json();
        document.getElementById('result').textContent = '✅ Task #' + data.id + ' đã tạo';
        showToast('✅ Task #' + data.id);
        loadTasks();
        if (data.id) setTimeout(() => showLog(data.id), 1000);
    } catch(e) {
        showToast('❌ Lỗi: ' + e.message);
    }
}

async function loadTasks() {
    try {
        const res = await fetch('/api/tasks');
        const data = await res.json();
        document.getElementById('taskCount').textContent = data.length;
        const container = document.getElementById('taskList');
        if (!data.length) {
            container.innerHTML = '<div style="padding:20px;text-align:center;color:#556677;">Chưa có video nào</div>';
            return;
        }
        container.innerHTML = data.map(t => `
            <div class="task-item" onclick="showLog('${t.id}')">
                <div style="flex:1;min-width:0;">
                    <div class="title">${t.title || t.url.substring(0,50)}...</div>
                    <div class="meta">
                        <span class="status status-${t.status}">${t.status}</span>
                        <span>${t.time}</span>
                        <span style="color:#556677;">${t.voice || 'Mặc định'}</span>
                    </div>
                </div>
                <div style="display:flex;gap:6px;flex-shrink:0;">
                    ${t.status === 'done' ? `<button class="btn btn-sm btn-outline" onclick="event.stopPropagation();downloadFile('${t.id}','srt')">📄 SRT</button>` : ''}
                    ${t.status === 'done' && t.audio_path ? `<button class="btn btn-sm btn-primary" onclick="event.stopPropagation();downloadFile('${t.id}','audio')">🎧 Audio</button>` : ''}
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
        return `<div><span class="time">[${new Date().toLocaleTimeString()}]</span> <span class="${cls}">${l}</span></div>`;
    }).join('');
}

function downloadFile(id, type) {
    window.open('/api/download/' + type + '/' + id, '_blank');
}

flattenVoices();
renderVoices();
loadTasks();
setInterval(loadTasks, 5000);
</script>
</body>
</html>
'''

# ================ BACKEND ================

def download_video(url, output_path):
    """Tải video bằng yt-dlp"""
    try:
        import yt_dlp
        ydl_opts = {
            'format': 'best[ext=mp4]',
            'quiet': True,
            'no_warnings': True,
            'outtmpl': output_path
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True, ''
    except Exception as e:
        return False, str(e)

def extract_audio(video_path, audio_path):
    """Trích xuất audio từ video"""
    cmd = f'ffmpeg -i "{video_path}" -acodec pcm_s16le -ar 16000 -ac 1 "{audio_path}" -y -loglevel error 2>&1'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode == 0

def transcribe_audio(audio_path, lang='auto'):
    """Nhận diện giọng nói bằng SpeechRecognition (Google API)"""
    try:
        import speech_recognition as sr
        from pydub import AudioSegment
        
        # Chuyển đổi audio sang WAV nếu cần
        if not audio_path.endswith('.wav'):
            wav_path = audio_path.replace('.wav', '_temp.wav')
            audio = AudioSegment.from_file(audio_path)
            audio.export(wav_path, format='wav')
            audio_path = wav_path
        
        r = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio_data = r.record(source)
        
        # Chuyển đổi language code
        lang_map = {
            'auto': 'vi-VN',
            'vi-VN': 'vi-VN',
            'en-US': 'en-US',
            'zh-CN': 'zh-CN',
            'ja-JP': 'ja-JP',
            'ko-KR': 'ko-KR',
            'fr-FR': 'fr-FR',
            'es-ES': 'es-ES',
            'de-DE': 'de-DE',
            'it-IT': 'it-IT',
            'pt-PT': 'pt-PT',
            'ru-RU': 'ru-RU',
            'hi-IN': 'hi-IN'
        }
        lang_code = lang_map.get(lang, 'vi-VN')
        
        text = r.recognize_google(audio_data, language=lang_code)
        
        # Trả về dạng segments
        return [{
            'start': 0,
            'end': 10,
            'text': text
        }]
    except ImportError:
        return [{'start': 0, 'end': 10, 'text': '⚠️ Cần cài: pip install speechrecognition pydub'}]
    except sr.UnknownValueError:
        return [{'start': 0, 'end': 10, 'text': '⚠️ Không nhận diện được giọng nói'}]
    except Exception as e:
        return [{'start': 0, 'end': 10, 'text': f'⚠️ Lỗi: {str(e)}'}]

def translate_text(text):
    """Dịch văn bản sang tiếng Việt"""
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            'client': 'gtx',
            'sl': 'auto',
            'tl': 'vi',
            'dt': 't',
            'q': text
        }
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        return ''.join([item[0] for item in data[0] if item[0]])
    except:
        return text

def generate_srt(segments, output_path):
    """Tạo file SRT"""
    with open(output_path, 'w', encoding='utf-8') as f:
        for i, seg in enumerate(segments, 1):
            def fmt(t):
                h = int(t//3600)
                m = int((t%3600)//60)
                s = int(t%60)
                ms = int((t%1)*1000)
                return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
            f.write(f"{i}\n")
            f.write(f"{fmt(seg['start'])} --> {fmt(seg['end'])}\n")
            f.write(f"{seg['text']}\n\n")

def text_to_speech(text, voice_code, output_path):
    """Tạo audio TTS bằng gTTS"""
    from gtts import gTTS
    
    # Map voice code to language
    lang_map = {}
    for provider, voices in VOICES.items():
        for code in voices.keys():
            parts = code.split('-')
            if len(parts) >= 2:
                lang_map[code] = parts[0].lower()
            else:
                lang_map[code] = 'vi'
    
    lang = lang_map.get(voice_code, 'vi')
    if lang == 'en' and 'GB' in voice_code:
        lang = 'en-uk'
    elif lang == 'zh':
        lang = 'zh-cn'
    
    try:
        tts = gTTS(text=text[:5000], lang=lang, slow=False)
        tts.save(output_path)
        return True
    except:
        # Fallback
        tts = gTTS(text=text[:5000], lang='vi', slow=False)
        tts.save(output_path)
        return True

def process_task(task_id):
    """Xử lý task trong background"""
    task = tasks[task_id]
    task['status'] = 'processing'
    task['log'].append('🔄 Bắt đầu xử lý...')
    
    # Tạo thư mục tạm
    temp_dir = tempfile.mkdtemp()
    video_path = os.path.join(temp_dir, 'video.mp4')
    audio_path = os.path.join(temp_dir, 'audio.wav')
    srt_path = os.path.join(temp_dir, 'subtitle.srt')
    tts_path = os.path.join(temp_dir, 'tts.mp3')
    
    # 1. Download video
    task['log'].append(f'📥 Đang tải: {task["url"]}')
    ok, err = download_video(task['url'], video_path)
    if not ok:
        task['status'] = 'fail'
        task['log'].append(f'✘ Lỗi tải: {err[:300]}')
        return
    task['log'].append('✔ Đã tải xong')
    
    # Lấy title
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
    
    # 3. Transcribe
    task['log'].append('🔊 Nhận diện giọng nói...')
    try:
        segments = transcribe_audio(audio_path, task['lang'])
    except Exception as e:
        task['status'] = 'fail'
        task['log'].append(f'✘ Lỗi: {str(e)}')
        return
    task['log'].append(f'✔ Nhận diện {len(segments)} đoạn')
    
    # 4. Translate
    task['log'].append('🌐 Dịch sang tiếng Việt...')
    translated = []
    for seg in segments:
        translated_text = translate_text(seg['text'])
        translated.append({
            'start': seg['start'],
            'end': seg['end'],
            'text': translated_text
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

# ================ MAIN ================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("""
╔═══════════════════════════════════════════╗
║  🎙️ SUBPRO LITE - Nhẹ, Nhanh, Chạy tốt  ║
║  ─────────────────────────────────────── ║
║  📍 Truy cập: http://0.0.0.0:%s         ║
║  💾 RAM yêu cầu: ~100MB                  ║
║  🎯 Dùng SpeechRecognition thay Whisper  ║
╚═══════════════════════════════════════════╝
    """ % port)
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)