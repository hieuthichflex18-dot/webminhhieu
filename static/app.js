/* ═══════════════════════════════════════════════════════
   NOVA — App
   ═══════════════════════════════════════════════════════ */

(function(){
  'use strict';

  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const isTouch = window.matchMedia('(pointer: coarse)').matches;
  const isMobile = window.innerWidth < 768;

  /* ═══════════════════════════════════════════════════
     NAVBAR — scroll shrink
     ═══════════════════════════════════════════════════ */
  const nav = document.getElementById('nav');
  let lastScroll = 0;
  function onScroll(){
    const y = window.scrollY;
    if(y > 20) nav.classList.add('scrolled');
    else nav.classList.remove('scrolled');
    lastScroll = y;
  }
  window.addEventListener('scroll', onScroll, {passive:true});
  onScroll();

  /* ═══════════════════════════════════════════════════
     MOBILE MENU
     ═══════════════════════════════════════════════════ */
  const burger = document.getElementById('hamburger');
  const mobileMenu = document.getElementById('mobile-menu');
  if(burger && mobileMenu){
    burger.addEventListener('click', () => {
      const open = burger.classList.toggle('open');
      mobileMenu.classList.toggle('open', open);
      burger.setAttribute('aria-expanded', open);
    });
    mobileMenu.querySelectorAll('a').forEach(a => {
      a.addEventListener('click', () => {
        burger.classList.remove('open');
        mobileMenu.classList.remove('open');
        burger.setAttribute('aria-expanded', 'false');
      });
    });
  }

  /* ═══════════════════════════════════════════════════
     ACTIVE NAV LINK — theo scroll
     ═══════════════════════════════════════════════════ */
  const navLinks = document.querySelectorAll('.nav-links a');
  const sections = [...navLinks]
    .map(a => document.querySelector(a.getAttribute('href')))
    .filter(Boolean);
  if(sections.length){
    const navObserver = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if(e.isIntersecting){
          const id = '#' + e.target.id;
          navLinks.forEach(a => a.classList.toggle('active', a.getAttribute('href') === id));
        }
      });
    }, {rootMargin:'-40% 0px -55% 0px', threshold:0});
    sections.forEach(s => navObserver.observe(s));
  }

  /* ═══════════════════════════════════════════════════
     REVEAL ON SCROLL
     ═══════════════════════════════════════════════════ */
  const reveals = document.querySelectorAll('.reveal');
  if(!prefersReduced){
    const revealObs = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if(e.isIntersecting){
          const delay = parseInt(e.target.dataset.delay || '0', 10);
          setTimeout(() => e.target.classList.add('in'), delay);
          revealObs.unobserve(e.target);
        }
      });
    }, {threshold:0.12, rootMargin:'0px 0px -60px 0px'});
    reveals.forEach(el => revealObs.observe(el));
  } else {
    reveals.forEach(el => el.classList.add('in'));
  }

  /* ═══════════════════════════════════════════════════
     BACKGROUND — particles canvas
     ═══════════════════════════════════════════════════ */
  const canvas = document.getElementById('bg-canvas');
  if(canvas && !prefersReduced){
    const ctx = canvas.getContext('2d');
    let W, H, particles = [], stars = [];
    const mouse = {x: -9999, y: -9999};

    function resize(){
      W = canvas.width = window.innerWidth * devicePixelRatio;
      H = canvas.height = window.innerHeight * devicePixelRatio;
      canvas.style.width = window.innerWidth + 'px';
      canvas.style.height = window.innerHeight + 'px';
      initParticles();
    }

    function initParticles(){
      const density = isMobile ? 30 : 70;
      particles = [];
      for(let i=0;i<density;i++){
        particles.push({
          x: Math.random() * W,
          y: Math.random() * H,
          r: (Math.random() * 1.6 + 0.4) * devicePixelRatio,
          vx: (Math.random() - 0.5) * 0.3,
          vy: (Math.random() - 0.5) * 0.3,
          hue: Math.random() < 0.5 ? '59,130,246' : (Math.random() < 0.5 ? '34,211,238' : '139,92,246'),
          a: Math.random() * 0.5 + 0.2
        });
      }
      stars = [];
      for(let i=0;i<40;i++){
        stars.push({
          x: Math.random() * W,
          y: Math.random() * H,
          r: Math.random() * 1 + 0.3,
          a: Math.random() * 0.6 + 0.2,
          tw: Math.random() * Math.PI * 2
        });
      }
    }

    window.addEventListener('resize', resize);
    window.addEventListener('mousemove', e => {
      mouse.x = e.clientX * devicePixelRatio;
      mouse.y = e.clientY * devicePixelRatio;
    });
    window.addEventListener('mouseleave', () => {
      mouse.x = -9999; mouse.y = -9999;
    });

    let t = 0;
    function tick(){
      t += 0.01;
      ctx.clearRect(0, 0, W, H);

      // stars
      stars.forEach(s => {
        s.tw += 0.02;
        const a = s.a * (0.6 + Math.sin(s.tw) * 0.4);
        ctx.fillStyle = `rgba(248,250,252,${a})`;
        ctx.beginPath();
        ctx.arc(s.x, s.y, s.r * devicePixelRatio, 0, Math.PI * 2);
        ctx.fill();
      });

      // particles
      particles.forEach(p => {
        // repel from mouse
        const dx = p.x - mouse.x;
        const dy = p.y - mouse.y;
        const dist2 = dx*dx + dy*dy;
        const R = 160 * devicePixelRatio;
        if(dist2 < R*R){
          const dist = Math.sqrt(dist2) || 1;
          const f = (1 - dist / R) * 0.4;
          p.x += (dx / dist) * f * 3;
          p.y += (dy / dist) * f * 3;
        }

        p.x += p.vx;
        p.y += p.vy;

        if(p.x < 0) p.x = W;
        if(p.x > W) p.x = 0;
        if(p.y < 0) p.y = H;
        if(p.y > H) p.y = 0;

        ctx.fillStyle = `rgba(${p.hue},${p.a})`;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fill();
      });

      // connections
      if(!isMobile){
        for(let i=0;i<particles.length;i++){
          for(let j=i+1;j<particles.length;j++){
            const a = particles[i], b = particles[j];
            const dx = a.x - b.x, dy = a.y - b.y;
            const d2 = dx*dx + dy*dy;
            const maxD = 120 * devicePixelRatio;
            if(d2 < maxD*maxD){
              const alpha = (1 - Math.sqrt(d2) / maxD) * 0.12;
              ctx.strokeStyle = `rgba(148,163,184,${alpha})`;
              ctx.lineWidth = 0.5;
              ctx.beginPath();
              ctx.moveTo(a.x, a.y);
              ctx.lineTo(b.x, b.y);
              ctx.stroke();
            }
          }
        }
      }

      requestAnimationFrame(tick);
    }
    resize();
    tick();
  }

  /* ═══════════════════════════════════════════════════
     CURSOR — dot + aura + spotlight
     ═══════════════════════════════════════════════════ */
  const spotlight = document.getElementById('spotlight');
  if(!isTouch && !prefersReduced){
    document.body.classList.add('cursor-on');
    const dot = document.getElementById('c-dot');
    const aura = document.getElementById('c-aura');
    let mx = window.innerWidth / 2, my = window.innerHeight / 2;
    let dx = mx, dy = my;
    let ax = mx, ay = my;
    let tx = mx, ty = my;

    window.addEventListener('mousemove', e => {
      mx = e.clientX; my = e.clientY;
    });

    function animCursor(){
      dx += (mx - dx) * 0.9;
      dy += (my - dy) * 0.9;
      ax += (mx - ax) * 0.15;
      ay += (my - ay) * 0.15;
      tx += (mx - tx) * 0.06;
      ty += (my - ty) * 0.06;

      if(dot) dot.style.transform = `translate(${dx}px,${dy}px) translate(-50%,-50%)`;
      if(aura) aura.style.transform = `translate(${ax}px,${ay}px) translate(-50%,-50%)`;
      if(spotlight){
        spotlight.style.transform = `translate(${tx}px,${ty}px) translate(-50%,-50%)`;
      }
      requestAnimationFrame(animCursor);
    }
    animCursor();

    // grow dot on interactive
    document.addEventListener('mouseover', e => {
      const t = e.target.closest('a,button,input,textarea,select,.card,.price-card,.chip,.snip');
      if(dot){
        dot.style.width = t ? '10px' : '6px';
        dot.style.height = t ? '10px' : '6px';
      }
    });
  }

  /* ═══════════════════════════════════════════════════
     3D TILT — cards
     ═══════════════════════════════════════════════════ */
  if(!isTouch && !prefersReduced){
    document.querySelectorAll('[data-tilt]').forEach(el => {
      let raf = null;
      let rx = 0, ry = 0;

      function onMove(e){
        const r = el.getBoundingClientRect();
        const px = (e.clientX - r.left) / r.width;
        const py = (e.clientY - r.top) / r.height;
        rx = (py - 0.5) * -8;
        ry = (px - 0.5) * 8;
        if(!raf) raf = requestAnimationFrame(apply);
      }
      function apply(){
        el.style.transform = `perspective(900px) rotateX(${rx}deg) rotateY(${ry}deg) translateY(-6px)`;
        raf = null;
      }
      function onLeave(){
        el.style.transform = '';
      }
      el.addEventListener('mousemove', onMove);
      el.addEventListener('mouseleave', onLeave);
    });
  }

  /* ═══════════════════════════════════════════════════
     BUTTON RIPPLE
     ═══════════════════════════════════════════════════ */
  document.addEventListener('click', e => {
    const btn = e.target.closest('.btn');
    if(!btn || prefersReduced) return;
    const r = btn.getBoundingClientRect();
    const span = document.createElement('span');
    span.className = 'ripple';
    const size = Math.max(r.width, r.height);
    span.style.width = span.style.height = size + 'px';
    span.style.left = (e.clientX - r.left) + 'px';
    span.style.top = (e.clientY - r.top) + 'px';
    btn.appendChild(span);
    setTimeout(() => span.remove(), 600);
  });

  /* ═══════════════════════════════════════════════════
     STATS COUNTER
     ═══════════════════════════════════════════════════ */
  const counters = document.querySelectorAll('[data-count]');
  if(counters.length){
    const cObs = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if(!e.isIntersecting) return;
        const el = e.target;
        cObs.unobserve(el);
        const target = parseFloat(el.dataset.count);
        const suffix = el.dataset.suffix || '';
        const dur = 1800;
        const start = performance.now();
        function step(now){
          const p = Math.min((now - start) / dur, 1);
          const eased = 1 - Math.pow(1 - p, 3);
          const val = target * eased;
          let disp;
          if(target >= 1000) disp = Math.round(val).toLocaleString('en-US');
          else if(target % 1 !== 0) disp = val.toFixed(1);
          else disp = Math.round(val);
          el.textContent = disp + suffix;
          if(p < 1) requestAnimationFrame(step);
        }
        requestAnimationFrame(step);
      });
    }, {threshold:0.4});
    counters.forEach(c => cObs.observe(c));
  }

  /* ═══════════════════════════════════════════════════
     PRICING TOGGLE
     ═══════════════════════════════════════════════════ */
  const sw = document.getElementById('billing-switch');
  const lblM = document.getElementById('lbl-m');
  const lblY = document.getElementById('lbl-y');
  if(sw){
    sw.addEventListener('click', () => {
      const yearly = sw.getAttribute('aria-checked') !== 'true';
      sw.setAttribute('aria-checked', yearly);
      lblM.classList.toggle('active', !yearly);
      lblY.classList.toggle('active', yearly);
      document.querySelectorAll('.price .amount').forEach(a => {
        const v = yearly ? a.dataset.y : a.dataset.m;
        a.textContent = v;
      });
    });
  }

  /* ═══════════════════════════════════════════════════
     FAQ — chỉ mở 1 cái
     ═══════════════════════════════════════════════════ */
  document.querySelectorAll('.faq-item').forEach(item => {
    item.addEventListener('toggle', () => {
      if(item.open){
        document.querySelectorAll('.faq-item[open]').forEach(o => {
          if(o !== item) o.open = false;
        });
      }
    });
  });

  /* ═══════════════════════════════════════════════════
     TESTIMONIAL CAROUSEL
     ═══════════════════════════════════════════════════ */
  const track = document.getElementById('carousel-track');
  if(track){
    const cards = [...track.children];
    const dotsWrap = document.getElementById('dots');
    const prev = document.getElementById('prev');
    const next = document.getElementById('next');
    let idx = 0;
    let autoTimer = null;
    const total = cards.length;

    function perView(){
      if(window.innerWidth < 768) return 1;
      if(window.innerWidth < 1024) return 2;
      return 2;
    }
    function maxIdx(){
      return Math.max(0, total - perView());
    }
    function apply(){
      const cardW = cards[0].getBoundingClientRect().width;
      const gap = 20;
      track.style.transform = `translateX(-${idx * (cardW + gap)}px)`;
      [...dotsWrap.children].forEach((d, i) => d.classList.toggle('active', i === idx));
    }
    function buildDots(){
      dotsWrap.innerHTML = '';
      const n = maxIdx() + 1;
      for(let i=0;i<n;i++){
        const d = document.createElement('span');
        d.className = 'dot' + (i === idx ? ' active' : '');
        d.addEventListener('click', () => { idx = i; apply(); restart(); });
        dotsWrap.appendChild(d);
      }
    }
    function go(dir){
      idx = Math.max(0, Math.min(idx + dir, maxIdx()));
      apply();
    }
    function start(){
      if(prefersReduced) return;
      autoTimer = setInterval(() => {
        idx = idx >= maxIdx() ? 0 : idx + 1;
        apply();
      }, 5000);
    }
    function stop(){ if(autoTimer) clearInterval(autoTimer); autoTimer = null; }
    function restart(){ stop(); start(); }

    prev.addEventListener('click', () => { go(-1); restart(); });
    next.addEventListener('click', () => { go(1); restart(); });

    track.parentElement.addEventListener('mouseenter', stop);
    track.parentElement.addEventListener('mouseleave', start);

    // touch swipe
    let sx = 0;
    track.addEventListener('touchstart', e => { sx = e.touches[0].clientX; }, {passive:true});
    track.addEventListener('touchend', e => {
      const dx = e.changedTouches[0].clientX - sx;
      if(Math.abs(dx) > 40){ go(dx > 0 ? -1 : 1); restart(); }
    }, {passive:true});

    window.addEventListener('resize', () => {
      if(idx > maxIdx()) idx = maxIdx();
      buildDots(); apply();
    });

    buildDots(); apply(); start();
  }

  /* ═══════════════════════════════════════════════════
     CHAT AI
     ═══════════════════════════════════════════════════ */
  const chatBody = document.getElementById('chat-body');
  const chatForm = document.getElementById('chat-form');
  const chatInput = document.getElementById('chat-input');
  const chatSend = document.getElementById('chat-send');
  const modelSel = document.getElementById('model');
  const welcome = document.getElementById('chat-welcome');

  const session = (() => {
    let s = localStorage.getItem('nova_sid');
    if(!s){ s = Date.now().toString(36) + Math.random().toString(36).slice(2,6); localStorage.setItem('nova_sid', s); }
    return s;
  })();

  let busy = false;

  function hideWelcome(){ if(welcome && welcome.parentNode) welcome.remove(); }

  function addBubble(who, html){
    hideWelcome();
    const wrap = document.createElement('div');
    wrap.className = 'msg ' + who;
    const bubble = document.createElement('div');
    bubble.className = 'msg-bubble';
    if(html !== undefined) bubble.innerHTML = html;
    wrap.appendChild(bubble);
    chatBody.appendChild(wrap);
    chatBody.scrollTop = chatBody.scrollHeight;
    return bubble;
  }

  function escapeHtml(s){
    return s.replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  }

  function renderMarkdownish(el, text){
    // tách code block
    const parts = text.split(/```(\w+)?\n([\s\S]*?)```/g);
    el.innerHTML = '';
    for(let i=0;i<parts.length;i++){
      if(i % 3 === 0){
        if(parts[i]){
          const span = document.createElement('span');
          span.innerHTML = escapeHtml(parts[i]);
          el.appendChild(span);
        }
      } else if(i % 3 === 2){
        const lang = parts[i-1] || 'code';
        const code = parts[i];
        const pre = document.createElement('pre');
        const codeEl = document.createElement('code');
        codeEl.textContent = code;
        pre.appendChild(codeEl);
        const cp = document.createElement('button');
        cp.className = 'cp';
        cp.textContent = '📋 Copy';
        cp.onclick = () => {
          navigator.clipboard.writeText(code).then(() => {
            cp.textContent = '✅ Đã copy';
            cp.classList.add('ok');
            setTimeout(() => { cp.textContent = '📋 Copy'; cp.classList.remove('ok'); }, 1500);
          });
        };
        pre.appendChild(cp);
        el.appendChild(pre);
      }
    }
    chatBody.scrollTop = chatBody.scrollHeight;
  }

  async function sendMsg(){
    const text = chatInput.value.trim();
    if(!text || busy) return;
    busy = true;
    chatSend.disabled = true;
    chatInput.value = '';
    chatInput.style.height = 'auto';

    addBubble('me').textContent = text;

    const aiBubble = addBubble('ai');
    aiBubble.innerHTML = '<span class="typing"><i></i><i></i><i></i></span>';

    let full = '';
    try{
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          session,
          model: modelSel ? modelSel.value : 'gpt-4o',
          message: text
        })
      });

      if(!res.ok || !res.body){
        aiBubble.textContent = '❌ Không kết nối được API';
        busy = false; chatSend.disabled = false;
        return;
      }

      const reader = res.body.getReader();
      const dec = new TextDecoder();
      let buf = '';

      while(true){
        const {value, done} = await reader.read();
        if(done) break;
        buf += dec.decode(value, {stream:true});
        const lines = buf.split('\n\n');
        buf = lines.pop();
        for(const ln of lines){
          if(!ln.startsWith('data:')) continue;
          const raw = ln.slice(5).trim();
          if(!raw) continue;
          let obj;
          try{ obj = JSON.parse(raw); }catch{ continue; }
          if(obj.t){
            if(!full) aiBubble.innerHTML = '';
            full += obj.t;
            renderMarkdownish(aiBubble, full);
          }
          if(obj.err){
            aiBubble.textContent = '❌ ' + obj.err;
          }
          if(obj.done){ /* xong */ }
        }
      }
    } catch(e){
      aiBubble.textContent = '❌ ' + (e.message || e);
    }

    busy = false;
    chatSend.disabled = false;
    chatInput.focus();
  }

  if(chatForm && chatInput){
    chatInput.addEventListener('input', () => {
      chatInput.style.height = 'auto';
      chatInput.style.height = Math.min(chatInput.scrollHeight, 160) + 'px';
    });
    chatInput.addEventListener('keydown', e => {
      if(e.key === 'Enter' && !e.shiftKey){
        e.preventDefault();
        sendMsg();
      }
    });
    chatForm.addEventListener('submit', e => {
      e.preventDefault();
      sendMsg();
    });
    chatSend.addEventListener('click', e => {
      e.preventDefault();
      sendMsg();
    });
  }

  // quick chips
  document.querySelectorAll('.chip[data-q]').forEach(c => {
    c.addEventListener('click', () => {
      if(!chatInput) return;
      chatInput.value = c.dataset.q;
      chatInput.focus();
      sendMsg();
    });
  });

  window.clearChat = async function(){
    try{
      await fetch('/api/clear', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({session})
      });
    } catch(e){}
    if(chatBody){
      chatBody.innerHTML = `
        <div class="chat-welcome" id="chat-welcome">
          <div class="cw-icon">
            <svg viewBox="0 0 32 32" width="40" height="40" fill="none">
              <path d="M16 2 L28 9 L28 23 L16 30 L4 23 L4 9 Z" stroke="url(#lg1)" stroke-width="1.5" fill="rgba(59,130,246,0.08)"/>
              <circle cx="16" cy="16" r="4" fill="url(#lg1)"/>
            </svg>
          </div>
          <h3>Đã xóa</h3>
          <p>Bắt đầu cuộc trò chuyện mới.</p>
        </div>`;
    }
  };

  /* ═══════════════════════════════════════════════════
     PARALLAX — nhẹ
     ═══════════════════════════════════════════════════ */
  if(!prefersReduced && !isMobile){
    const orbs = document.querySelectorAll('.bg-orb');
    window.addEventListener('scroll', () => {
      const y = window.scrollY;
      orbs.forEach((o, i) => {
        o.style.transform = `translateY(${y * (0.05 + i * 0.03)}px)`;
      });
    }, {passive:true});
  }

  /* ═══════════════════════════════════════════════════
     SMOOTH ANCHOR
     ═══════════════════════════════════════════════════ */
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
      const id = a.getAttribute('href');
      if(id === '#' || id === '#top') return;
      const target = document.querySelector(id);
      if(!target) return;
      e.preventDefault();
      const top = target.getBoundingClientRect().top + window.scrollY - 80;
      window.scrollTo({top, behavior: prefersReduced ? 'auto' : 'smooth'});
    });
  });

})();
