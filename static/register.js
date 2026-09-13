// static/register.js

const btn = document.getElementById('btnRegister');
const errMsg = document.getElementById('errMsg');
const okMsg = document.getElementById('okMsg');

function showErr(msg) {
  errMsg.textContent = msg;
  errMsg.style.display = 'block';
  okMsg.style.display = 'none';
}

function showOk(msg) {
  okMsg.textContent = msg;
  okMsg.style.display = 'block';
  errMsg.style.display = 'none';
}

btn.addEventListener('click', async () => {
  const username = document.getElementById('r-user').value.trim();
  const password = document.getElementById('r-pass').value;
  const password2 = document.getElementById('r-pass2').value;

  if (username.length < 4) {
    showErr('Tài khoản phải từ 4 ký tự');
    return;
  }
  if (username.length > 20) {
    showErr('Tài khoản tối đa 20 ký tự');
    return;
  }
  if (!/^[a-zA-Z0-9_]+$/.test(username)) {
    showErr('Tài khoản chỉ dùng chữ, số, gạch dưới (không dấu)');
    return;
  }
  if (password.length < 6) {
    showErr('Mật khẩu phải từ 6 ký tự');
    return;
  }
  if (password !== password2) {
    showErr('Mật khẩu nhập lại không khớp');
    return;
  }

  btn.disabled = true;
  btn.textContent = 'Đang xử lý...';

  try {
    const res = await fetch('/api/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    const data = await res.json();

    if (data.ok) {
      showOk('Đăng ký thành công! Đang chuyển sang trang đăng nhập...');
      setTimeout(() => {
        window.location.href = '/login';
      }, 1500);
    } else {
      showErr(data.message || 'Đăng ký thất bại');
      btn.disabled = false;
      btn.textContent = 'Đăng ký';
    }
  } catch (e) {
    showErr('Lỗi kết nối: ' + e.message);
    btn.disabled = false;
    btn.textContent = 'Đăng ký';
  }
});
