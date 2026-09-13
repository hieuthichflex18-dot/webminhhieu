// static/admin.js
const nav = document.getElementById('nav');
window.addEventListener('scroll', () => nav.classList.toggle('scrolled', window.scrollY > 20), { passive: true });

document.querySelectorAll('.admin-tab').forEach(tab => {
  tab.onclick = () => {
    document.querySelectorAll('.admin-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.admin-panel').forEach(p => p.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById('tab-' + tab.dataset.tab).classList.add('active');
  };
});

async function loadStats() {
  const res = await fetch('/api/admin/stats');
  const d = await res.json();
  document.getElementById('statsGrid').innerHTML =
    '<div class="glass stat-card"><div class="l">Tổng user</div><div class="v">' + d.total_users + '</div></div>' +
    '<div class="glass stat-card"><div class="l">Tổng key</div><div class="v">' + d.total_keys + '</div></div>' +
    '<div class="glass stat-card"><div class="l">Key hoạt động</div><div class="v">' + d.active_keys + '</div></div>' +
    '<div class="glass stat-card"><div class="l">Số dự đoán</div><div class="v">' + d.total_predictions + '</div></div>' +
    '<div class="glass stat-card"><div class="l">Độ chính xác</div><div class="v">' + d.accuracy + '%</div></div>';
}

async function loadUsers() {
  const res = await fetch('/api/admin/users');
  const users = await res.json();
  const tbody = document.querySelector('#usersTable tbody');
  tbody.innerHTML = users.map(u =>
    '<tr>' +
      '<td>' + u.id + '</td>' +
      '<td><strong>' + u.username + '</strong></td>' +
      '<td>' + u.role + '</td>' +
      '<td><span class="tier-badge ' + (u.role === 'admin' ? 'admin' : '') + '">' + u.tier + '</span></td>' +
      '<td style="font-size:0.75rem;">' + (u.expires_at ? u.expires_at.substring(0, 10) : '—') + '</td>' +
      '<td style="font-size:0.75rem;">' + (u.last_login ? u.last_login.substring(0, 16).replace('T', ' ') : '—') + '</td>' +
      '<td>' + (u.active ? 'OK' : 'X') + '</td>' +
      '<td>' +
        '<button class="btn sm ghost" onclick="toggleUser(' + u.id + ')">' + (u.active ? 'Khoá' : 'Mở') + '</button>' +
        '<button class="btn sm danger" onclick="deleteUser(' + u.id + ')">Xoá</button>' +
      '</td>' +
    '</tr>'
  ).join('');
}

async function createUser() {
  const body = {
    username: document.getElementById('u-name').value.trim(),
    password: document.getElementById('u-pass').value.trim(),
    tier: document.getElementById('u-tier').value,
    role: document.getElementById('u-role').value,
    days: parseInt(document.getElementById('u-days').value) || 30
  };
  const res = await fetch('/api/admin/users/create', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  const d = await res.json();
  document.getElementById('createUserMsg').innerHTML =
    '<div class="' + (d.ok ? 'key-display' : 'error-msg') + '">' + d.message + '</div>';
  if (d.ok) { loadUsers(); loadStats(); }
}

async function toggleUser(id) {
  await fetch('/api/admin/users/' + id + '/toggle', { method: 'POST' });
  loadUsers();
}

async function deleteUser(id) {
  if (!confirm('Chắc chắn xoá user này?')) return;
  await fetch('/api/admin/users/' + id, { method: 'DELETE' });
  loadUsers(); loadStats();
}

async function createKey() {
  const body = {
    tier: document.getElementById('k-tier').value,
    days: parseInt(document.getElementById('k-days').value) || 30,
    max_uses: parseInt(document.getElementById('k-uses').value) || 1,
    note: document.getElementById('k-note').value
  };
  const res = await fetch('/api/admin/keys/create', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  const d = await res.json();
  document.getElementById('keyDisplay').innerHTML =
    '<div class="key-display" onclick="navigator.clipboard.writeText(\'' + d.key + '\');this.textContent=\'Đã copy: ' + d.key + '\';">' + d.key + ' (click copy)</div>';
  loadKeys(); loadStats();
}

async function loadKeys() {
  const res = await fetch('/api/admin/keys');
  const keys = await res.json();
  const tbody = document.querySelector('#keysTable tbody');
  tbody.innerHTML = keys.map(k =>
    '<tr>' +
      '<td><code style="font-size:0.75rem;color:#22D3EE;">' + k.key_code + '</code></td>' +
      '<td><span class="tier-badge">' + k.tier + '</span></td>' +
      '<td>' + k.duration_days + '</td>' +
      '<td>' + k.used_count + '/' + k.max_uses + '</td>' +
      '<td style="font-size:0.75rem;">' + (k.expires_at ? k.expires_at.substring(0, 10) : '—') + '</td>' +
      '<td style="font-size:0.75rem;">' + (k.created_by || '—') + '</td>' +
      '<td><button class="btn sm danger" onclick="deleteKey(' + k.id + ')">Xoá</button></td>' +
    '</tr>'
  ).join('');
}

async function deleteKey(id) {
  if (!confirm('Xoá key này?')) return;
  await fetch('/api/admin/keys/' + id, { method: 'DELETE' });
  loadKeys(); loadStats();
}

async function loadLogs() {
  const res = await fetch('/api/admin/logs');
  const logs = await res.json();
  const tbody = document.querySelector('#logsTable tbody');
  tbody.innerHTML = logs.map(l =>
    '<tr>' +
      '<td><strong>' + (l.username || '—') + '</strong></td>' +
      '<td>' + l.action + '</td>' +
      '<td style="font-size:0.75rem;color:#94A3B8;">' + (l.ip || '—') + '</td>' +
      '<td style="font-size:0.75rem;color:#94A3B8;">' + l.created_at + '</td>' +
    '</tr>'
  ).join('');
}

loadStats();
loadUsers();
loadKeys();
loadLogs();
setInterval(loadStats, 10000);
