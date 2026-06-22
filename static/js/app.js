/* ══════════════════════════════════════════
   OjasGo — Frontend Application JS
   Talks to Flask /api/* endpoints
══════════════════════════════════════════ */

"use strict";

// ── State ──
const STATE = {
  sattva: 0,
  activeTab: null,
  busy: false,
  ragaData: [],
  herbData: [],
  pranayamaData: [],
  leelaData: { squares: {}, names: {} },
  playerPos: 1,
  rolling: false,
  dataLoaded: { ragas: false, herbs: false, leela: false }
};

// ── DOM refs ──
const $ = id => document.getElementById(id);

// ══════════════════════════════════════════
// INIT
// ══════════════════════════════════════════
document.addEventListener("DOMContentLoaded", () => {
  checkApiHealth();
  bindEvents();
  initReveal();
});

function bindEvents() {
  $("enterBtn").addEventListener("click", enterApp);
  $("logoBtn").addEventListener("click", showHero);
  $("themeBtn").addEventListener("click", toggleTheme);
  $("sendBtn").addEventListener("click", sendMessage);
  $("chatInput").addEventListener("keydown", e => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  });
  $("modalCloseBtn").addEventListener("click", closeModal);
  $("helpFab").addEventListener("click", showHelp);
  $("rollBtn").addEventListener("click", rollDice);

  // Tab buttons
  document.querySelectorAll("[data-tab]").forEach(btn => {
    btn.addEventListener("click", () => switchTab(btn.dataset.tab));
  });

  // Quick tips
  document.querySelectorAll(".quick-tip").forEach(btn => {
    btn.addEventListener("click", () => {
      $("chatInput").value = btn.dataset.tip;
      $("quickTips").style.display = "none";
      sendMessage();
    });
  });
}

// ══════════════════════════════════════════
// API HEALTH CHECK
// ══════════════════════════════════════════
async function checkApiHealth() {
  try {
    const res = await fetch("/api/health");
    const data = await res.json();
    const dot = $("apiDot");
    const txt = $("apiStatusText");
    if (data.gemini_configured) {
      dot.className = "api-dot ok";
      txt.textContent = "Gemini AI connected · gemini-2.5-flash";
    } else {
      dot.className = "api-dot warn";
      txt.textContent = "Gemini AI key not set — using local fallback engine";
    }
  } catch {
    $("apiDot").className = "api-dot error";
    $("apiStatusText").textContent = "Backend unreachable — check Flask server";
  }
}

// ══════════════════════════════════════════
// NAVIGATION
// ══════════════════════════════════════════
function enterApp() {
  $("hero").style.display = "none";
  $("appView").style.display = "block";
  $("nav").style.display = "flex";
  $("sattvaHeader").style.display = "block";
  switchTab("vikalpa");
}

function showHero() {
  $("hero").style.display = "flex";
  $("appView").style.display = "none";
  $("nav").style.display = "none";
  $("sattvaHeader").style.display = "none";
}

function switchTab(id) {
  if (STATE.activeTab) {
    $(`view-${STATE.activeTab}`).style.display = "none";
    $(`tab-${STATE.activeTab}`).classList.remove("active");
  }
  STATE.activeTab = id;
  const view = $(`view-${id}`);
  view.style.display = "block";
  $(`tab-${id}`).classList.add("active");
  window.scrollTo({ top: 0, behavior: "smooth" });
  initReveal();

  // Lazy-load tab data
  if (id === "raga"    && !STATE.dataLoaded.ragas)    loadRagas();
  if (id === "dharana" && !STATE.dataLoaded.herbs)    loadHerbs();
  if (id === "sadhana" && !STATE.dataLoaded.leela)    loadLeela();
}

// ══════════════════════════════════════════
// THEME
// ══════════════════════════════════════════
let isDark = false;
function toggleTheme() {
  isDark = !isDark;
  document.documentElement.classList.toggle("dark", isDark);
  $("themeBtn").textContent = isDark ? "☀️" : "🌙";
}

// ══════════════════════════════════════════
// SATTVA POINTS
// ══════════════════════════════════════════
function addSattva(n) {
  STATE.sattva += n;
  const t = `✦ ${STATE.sattva} Sattva`;
  $("sattvaHeader").textContent    = t;
  $("sattvaChatBadge").textContent = t;
}

// ══════════════════════════════════════════
// CHAT — AI CONSULTATION
// ══════════════════════════════════════════
async function sendMessage() {
  if (STATE.busy) return;
  const input = $("chatInput");
  const msg = input.value.trim();
  if (!msg) return;

  STATE.busy = true;
  const btn = $("sendBtn");
  btn.disabled = true;
  btn.textContent = "Consulting…";
  $("quickTips").style.display = "none";

  addBubble("user", msg);
  input.value = "";

  const loadId = "load_" + Date.now();
  addBubble("ai", `<div class="typing-dots"><span></span><span></span><span></span></div>`, loadId);

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: msg, type: "vaidya" })
    });
    const data = await res.json();
    $(loadId)?.remove();

    if (data.error) throw new Error(data.error);

    addBubble("ai", formatResponse(data.response), "", true);
    addSattva(data.sattva || 10);

    if (data.source === "fallback") {
      addBubble("ai", `<em style="font-size:.8rem;opacity:.7">Note: Gemini AI unavailable — using local Ayurvedic classifier.</em>`, "", true);
    }
  } catch (err) {
    $(loadId)?.remove();
    addBubble("ai", `<em>The Vaidya is momentarily unreachable. Please try again. (${err.message})</em>`, "", true);
  }

  STATE.busy = false;
  btn.disabled = false;
  btn.textContent = "Ask Vaidya";
}

function addBubble(role, html, id = "", raw = false) {
  const msgs = $("msgs");
  const wrap = document.createElement("div");
  wrap.className = `msg msg-${role === "user" ? "user" : "ai"}`;
  if (id) wrap.id = id;
  const label = role === "user" ? "You" : "Digital Vaidya";
  wrap.innerHTML = `<div class="msg-label">${label}</div><div class="msg-bubble">${html}</div>`;
  msgs.appendChild(wrap);
  msgs.scrollTop = msgs.scrollHeight;
}

// ── Format the AI response into pillar blocks ──
function formatResponse(text) {
  const pillarDefs = [
    { key: "PILLAR I",   cls: "pb-vikalpa", label: "🔮 Pillar I · Vikalpa — Dosha Analysis" },
    { key: "PILLAR II",  cls: "pb-raga",    label: "🎵 Pillar II · Raga — Sound Therapy" },
    { key: "PILLAR III", cls: "pb-dharana", label: "🌿 Pillar III · Dharana — Action Steps" },
    { key: "PILLAR IV",  cls: "pb-sadhana", label: "📿 Pillar IV · Sadhana — Long-term Path" },
  ];

  const hasPillars = pillarDefs.some(p => text.includes(p.key));
  if (!hasPillars) return renderMarkdown(text);

  const lines = text.split("\n");
  let html = '<div class="pillar-response">';
  let current = null;
  let body = [];

  function flush() {
    if (!current) return;
    const content = renderMarkdown(body.join("\n").trim());
    html += `<div class="pillar-block ${current.cls}"><div class="pillar-head">${current.label}</div><div class="pillar-body">${content}</div></div>`;
    body = [];
  }

  lines.forEach(line => {
    const found = pillarDefs.find(p => line.includes(p.key));
    if (found) { flush(); current = found; }
    else if (current) body.push(line);
  });
  flush();
  html += "</div>";
  return html;
}

function renderMarkdown(t) {
  return t
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.+?)\*/g, "<em>$1</em>")
    .replace(/^• /gm, "&nbsp;&nbsp;• ")
    .replace(/\n{2,}/g, "<br/><br/>")
    .replace(/\n/g, "<br/>");
}

// ══════════════════════════════════════════
// LOAD RAGAS FROM API
// ══════════════════════════════════════════
async function loadRagas() {
  try {
    const res = await fetch("/api/data/ragas");
    STATE.ragaData = await res.json();
    STATE.dataLoaded.ragas = true;
    renderRagas();
  } catch { $("ragaGrid").innerHTML = `<p class="loading-msg">Failed to load ragas.</p>`; }
}

function renderRagas() {
  const grid = $("ragaGrid");
  grid.innerHTML = STATE.ragaData.map((r, i) => `
    <div class="raga-card" data-name="${r.name}" data-context="${r.time} raga, ${r.dosha}, ${r.level} stress">
      <div class="raga-num">${String(i+1).padStart(2,"0")}</div>
      <div class="raga-name">${r.name}${r.id===9?" ✦ RCT":""}</div>
      <div class="raga-tags">
        <span class="rtag rt-time">${r.time}</span>
        <span class="rtag rt-dosha">${r.dosha} · ${r.chakra}</span>
        <span class="rtag rt-level">${r.level}</span>
      </div>
      <div class="raga-fx">${r.effect}</div>
    </div>`).join("");

  grid.querySelectorAll(".raga-card").forEach(card => {
    card.addEventListener("click", () => askAbout("raga", card.dataset.name, card.dataset.context));
  });
  initReveal();
}

// ══════════════════════════════════════════
// LOAD HERBS FROM API
// ══════════════════════════════════════════
async function loadHerbs() {
  try {
    const [hRes, pRes] = await Promise.all([
      fetch("/api/data/herbs"),
      fetch("/api/data/pranayamas")
    ]);
    STATE.herbData      = await hRes.json();
    STATE.pranayamaData = await pRes.json();
    STATE.dataLoaded.herbs = true;
    renderHerbs();
    renderPranayamas();
  } catch { $("herbGrid").innerHTML = `<p class="loading-msg">Failed to load herbs.</p>`; }
}

function renderHerbs() {
  $("herbGrid").innerHTML = STATE.herbData.map(h => `
    <div class="herb-card" data-name="${h.name}" data-context="${h.dosha} dosha, ${h.sanskrit}">
      <span class="herb-emoji">${h.emoji}</span>
      <div class="herb-name">${h.name}</div>
      <div class="herb-sk">${h.sanskrit}</div>
      <span class="herb-tag">${h.dosha} · ${h.tag}</span>
      <p class="herb-body">${h.body}</p>
    </div>`).join("");

  $("herbGrid").querySelectorAll(".herb-card").forEach(card => {
    card.addEventListener("click", () => askAbout("herb", card.dataset.name, card.dataset.context));
  });
}

function renderPranayamas() {
  $("pranayamaGrid").innerHTML = STATE.pranayamaData.map(p => `
    <div class="pranayama-card">
      <div class="prana-head">${p.icon} ${p.name}</div>
      <div class="prana-body"><strong>${p.dosha}</strong> — ${p.body}</div>
    </div>`).join("");
}

// ── Ask about a raga or herb via AI ──
async function askAbout(type, name, context) {
  switchTab("vikalpa");
  await new Promise(r => setTimeout(r, 320));
  const query = type === "raga"
    ? `Tell me about Raga ${name} (${context}): its healing properties, chakra connection, how to listen therapeutically, and what Ayurvedic conditions it treats.`
    : `Tell me everything about the Ayurvedic herb ${name} (${context}): preparation, dosage, contraindications, and scientific evidence.`;

  const res = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: query, type })
  });
  const data = await res.json();
  addBubble("user", `Tell me about: ${name}`);
  addBubble("ai", formatResponse(data.response || ""), "", true);
  addSattva(5);
}

// ══════════════════════════════════════════
// LEELA BOARD
// ══════════════════════════════════════════
async function loadLeela() {
  try {
    const res = await fetch("/api/data/leela");
    STATE.leelaData = await res.json();
    STATE.dataLoaded.leela = true;
    buildLeelaBoard();
  } catch { $("leelaBoard").innerHTML = `<p class="loading-msg">Failed to load board.</p>`; }
}

function buildLeelaBoard() {
  const { squares, names } = STATE.leelaData;
  const board = $("leelaBoard");
  board.innerHTML = "";

  // Build 8 rows of 9
  const allIds = [];
  for (let r = 0; r < 8; r++) {
    const row = [];
    for (let n = r * 9 + 1; n <= r * 9 + 9; n++) if (n <= 72) row.push(n);
    if (r % 2 === 1) row.reverse();
    allIds.push(row);
  }
  allIds.reverse();

  allIds.forEach(row => row.forEach(id => {
    if (id > 72) return;
    const sq = squares[id];
    let cls = "sq-normal";
    if (sq?.type === "ladder")  cls = "sq-ladder";
    else if (sq?.type === "snake")   cls = "sq-snake";
    else if (sq?.type === "special") cls = "sq-special";

    const el = document.createElement("div");
    el.className = `sq ${cls}`;
    el.id = `sq${id}`;
    el.innerHTML = `<span class="sq-id">${id}</span><span class="sq-name">${names[id] || ""}</span>`;
    el.addEventListener("click", () => {
      const msg = $("gameMsg");
      if (sq?.type === "ladder")       msg.textContent = `${id}: ${sq.name} → lifts to ${sq.dest} ✦`;
      else if (sq?.type === "snake")   msg.textContent = `${id}: ${sq.name} → descends to ${sq.dest}`;
      else if (sq?.type === "special") msg.textContent = `${id}: ${sq.name} — ${sq.desc?.substring(0, 60)}…`;
      else                             msg.textContent = `Square ${id}: ${names[id] || ""}`;
      msg.classList.add("active");
    });
    board.appendChild(el);
  }));
  renderToken();
}

function renderToken() {
  document.querySelectorAll(".player-token").forEach(t => t.remove());
  const sq = $(`sq${STATE.playerPos}`);
  if (sq) {
    const t = document.createElement("div");
    t.className = "player-token";
    sq.appendChild(t);
  }
}

function rollDice() {
  if (STATE.rolling) return;
  STATE.rolling = true;
  const btn = $("rollBtn");
  btn.disabled = true;

  const faces = ["⚀","⚁","⚂","⚃","⚄","⚅"];
  let i = 0;
  const anim = setInterval(() => {
    $("diceBox").textContent = faces[Math.floor(Math.random() * 6)];
    if (++i > 11) clearInterval(anim);
  }, 70);

  setTimeout(() => {
    const roll = Math.floor(Math.random() * 6) + 1;
    $("diceBox").textContent = faces[roll - 1];

    const { squares, names } = STATE.leelaData;
    let np = Math.min(STATE.playerPos + roll, 72);
    const sq = squares[np];
    const msg = $("gameMsg");
    let showModal = false, icon = "✦", title = "", body = "", win = false;

    if (sq?.type === "ladder") {
      setTimeout(() => { STATE.playerPos = sq.dest; renderToken(); }, 450);
      msg.textContent = `${sq.name}! Virtue lifts ${np} → ${sq.dest} ✦`;
      msg.classList.add("active");
      icon = "⬆"; title = `✦ ${sq.name}`;
      body = `Your virtue of ${sq.name} lifts you from square ${np} to ${sq.dest}.`;
      showModal = true; addSattva(roll + 5);

    } else if (sq?.type === "snake") {
      setTimeout(() => { STATE.playerPos = sq.dest; renderToken(); }, 450);
      msg.textContent = `${sq.name}… descends ${np} → ${sq.dest}`;
      msg.classList.add("active");
      icon = "⬇"; title = `The Teaching of ${sq.name}`;
      body = `${sq.name} descends your spirit from ${np} to ${sq.dest}. Reflect and rise again.`;
      showModal = true; addSattva(1);

    } else if (np === 72) {
      STATE.playerPos = 72; renderToken();
      msg.textContent = "🕉 Moksha! Liberation attained!";
      msg.classList.add("active");
      icon = "🕉"; title = "Moksha Attained";
      body = "You have reached the 72nd square — Liberation from the cycle of birth and death. OM.";
      win = true; showModal = true; addSattva(50);

    } else {
      STATE.playerPos = np; renderToken();
      msg.textContent = `Square ${np}: ${names[np] || ""}${sq?.type === "special" ? " — Sacred Station" : ""}`;
      msg.classList.add("active"); addSattva(roll);
    }

    if (showModal) {
      setTimeout(() => {
        $("modalIcon").textContent   = icon;
        $("modalTitle").textContent  = title;
        $("modalTitle").style.color  = win ? "var(--lavender)" : "var(--section-title)";
        $("modalText").textContent   = body;
        $("modalSattva").textContent = `✦ ${STATE.sattva} Sattva Points`;
        $("modal").classList.add("show");
      }, 800);
    }

    STATE.rolling = false;
    btn.disabled = false;
  }, 900);
}

// ══════════════════════════════════════════
// MODAL q
// ══════════════════════════════════════════
function closeModal() { $("modal").classList.remove("show"); }

function showHelp() {
  $("modalIcon").textContent  = "🌿";
  $("modalTitle").textContent = "Safe Exit & Support";
  $("modalTitle").style.color = "var(--green)";
  $("modalText").innerHTML    =
    `OjasGo is a wellness companion — <em>not</em> a substitute for professional care.<br><br>
     📞 <strong>iCall India:</strong> +91 9511501034<br>
     📧 <strong>Email:</strong> <a href="mailto:kunalsol2005@gmail.com">kunalsol2005@gmail.com</a><br>
     🏥 <strong>NIMHANS:</strong> nimhans.ac.in<br>
     💚 <strong>Vandrevala Foundation:</strong> 1860-2662-345<br><br>
     <em style="font-size:.8rem">All AI recommendations are for educational purposes only.</em>`;
  $("modalSattva").textContent = "";
  $("modal").classList.add("show");
}

// Close modal on overlay click
$("modal").addEventListener("click", e => {
  if (e.target === $("modal")) closeModal();
});

// ══════════════════════════════════════════
// SCROLL REVEAL
// ══════════════════════════════════════════
function initReveal() {
  const obs = new IntersectionObserver(
    entries => entries.forEach(e => { if (e.isIntersecting) e.target.classList.add("visible"); }),
    { threshold: 0.08 }
  );
  document.querySelectorAll(".reveal:not(.visible)").forEach(el => obs.observe(el));
}
