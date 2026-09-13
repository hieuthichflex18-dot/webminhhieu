// static/app.js

const nav = document.getElementById('nav');
window.addEventListener('scroll', () => {
  nav.classList.toggle('scrolled', window.scrollY > 20);
}, { passive: true });

const orbs = document.querySelectorAll('.orb');
document.addEventListener('mousemove', (e) => {
  const x = e.clientX / window.innerWidth - 0.5;
  const y = e.clientY / window.innerHeight - 0.5;
  orbs.forEach((orb, i) => {
    const depth = (i + 1) * 15;
    orb.style.transform = `translate(${x * depth}px, ${y * depth}px)`;
  });
}, { passive: true });

function attachCardFX(el) {
  el.addEventListener('mousemove', (e) => {
    const rect = el.getBoundingClientRect();
    const mx = ((e.clientX - rect.left) / rect.width) * 100;
    const my = ((e.clientY - rect.top) / rect.height) * 100;
    el.style.setProperty('--mx', mx + '%');
    el.style.setProperty('--my', my + '%');
  });
}

let currentGame = null;

async function loadGames() {
  try {
    const res = await fetch('/api/games');
    const games = await res.json();
    const grid = document.getElementById('gamesGrid');
    grid.innerHTML = '';

    games.forEach((g, i) => {
      const card = document.createElement('div');
      card.className = 'game-card';
      card.dataset.key = g.key;
      card.style.animation = `panelIn 0.5s ${i * 0.04}s both`;
      card.innerHTML = `
        <span class="game-icon">${g.icon}</span>
        <div class="game-name">${g.name}</div>
        <div class="game-mode">${g.mode}</div>
      `;
      card.onclick = () => selectGame(g.key);
      attachCardFX(card);
      grid.appendChild(card);
    });
  } catch (e) {
    document.getElementById('gamesGrid').innerHTML =
      `<div class="empty-state" style="grid-column:1/-1;"><div class="icon">⚠️</div><div>Lỗi tải game: ${e.message}</div></div>`;
  }
}

async function selectGame(key) {
  currentGame = key;
  document.querySelectorAll('.game-card').forEach(c =>
    c.classList.toggle('active', c.dataset.key === key)
  );

  const panel = document.getElementById('dualPanel');
  panel.style.display = 'grid';
  panel.innerHTML = `
    <div class="glass panel">
      <div class="panel-header"><div class="panel-title">📡 Đang tải...</div></div>
      <div class="result-big">--</div>
    </div>
    <div class="glass panel">
      <div class="panel-header"><div class="panel-title">🧠 Đang phân tích...</div></div>
      <div class="pred-big">--</div>
    </div>
  `;

  try {
    const res = await fetch(`/api/game/${key}`);
    const data = await res.json();

    if (data.error) {
      panel.innerHTML = `<div class="empty-state" style="grid-column:1/-1;">
        <div class="icon">⚠️</div><div>${data.error}</div>
      </div>`;
      return;
    }

    const bs = data.block_session;
    const bp = data.block_prediction;
    const st = data.stats;

    const historyHtml = data.current_history.map(h =>
      `<div class="h-dot ${h === 'T' ? 't' : 'x'}">${h}</div>`
    ).join('');

    panel.innerHTML = `
      <div class="glass panel">
        <div class="panel-header">
          <div class="panel-title">${bs.title}</div>
          <div class="panel-mode">${bs.mode}</div>
        </div>
        <div class="session-id">${bs.session_id}</div>
        <div style="font-size:0.75rem;text-transform:uppercase;letter-spacing:2px;color:#94A3B8;text-align:center;">
          Kết quả phiên vừa rồi
        </div>
        <div class="result-big ${bs.last === 'T' ? 'tai' : 'xiu'}">${bs.last_text}</div>
        <div style="text-align:center;font-size:0.8rem;color:#94A3B8;">
          Chuỗi bệt: <strong style="color:#22D3EE;">${bs.streak} phiên ${bs.last}</strong>
        </div>
        <div style="margin-top:16px;font-size:0.75rem;text-transform:uppercase;letter-spacing:2px;color:#94A3B8;">
          Lịch sử gần đây
        </div>
        <div class="history-strip">${historyHtml}</div>
        <div class="stats-row">
          <div class="stat-mini"><div class="v">${st.freq_t}</div><div class="l">Tần suất T</div></div>
          <div class="stat-mini"><div class="v">${st.freq_x}</div><div class="l">Tần suất X</div></div>
          <div class="stat-mini"><div class="v">${st.history_len}</div><div class="l">Tổng phiên</div></div>
        </div>
      </div>

      <div class="glass panel">
        <div class="panel-header">
          <div class="panel-title">${bp.title}</div>
          <div class="panel-mode">${bp.mode}</div>
        </div>
        <div style="font-size:0.75rem;text-transform:uppercase;letter-spacing:2px;color:#94A3B8;text-align:center;margin-top:8px;">
          Dự đoán
        </div>
        <div class="pred-big">${bp.prediction_text}</div>
        <div style="font-size:0.75rem;color:#94A3B8;text-align:center;">
          Độ tin cậy: <strong style="color:#22D3EE;">${bp.confidence}%</strong>
        </div>
        <div class="conf-bar"><div class="conf-fill" style="width:${bp.confidence}%"></div></div>
        <ul class="reasons-list">
          ${bp.reasons.map(r => `<li>${r}</li>`).join('')}
        </ul>
      </div>
    `;
  } catch (e) {
    panel.innerHTML = `<div class="empty-state" style="grid-column:1/-1;">
      <div class="icon">⚠️</div><div>Lỗi: ${e.message}</div>
    </div>`;
  }
}

setInterval(() => {
  if (currentGame) selectGame(currentGame);
}, 15000);

loadGames();
