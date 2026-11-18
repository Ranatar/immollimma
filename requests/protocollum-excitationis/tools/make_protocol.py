"""somnus.html → protocol.html: режиссура «Протокола пробуждения» поверх фона."""
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src).read()
def R_(a, b, cnt=1):
    global s
    n = s.count(a); assert n == cnt, (n, a[:90]); s = s.replace(a, b)

R_("<title>Somnus Aeternus</title>","<title>Protocollum Excitationis</title>")
R_("""  #ui{position:fixed;right:14px;bottom:14px;display:flex;gap:8px;align-items:center;opacity:0;transition:opacity .6s;
    font:13px/1 ui-monospace,"DejaVu Sans Mono",monospace;letter-spacing:.06em;z-index:5}""",
"""  #ui{position:fixed;left:0;right:0;bottom:0;display:flex;flex-direction:column;opacity:0;transition:opacity .6s;
    font:13px/1 ui-monospace,"DejaVu Sans Mono",monospace;letter-spacing:.06em;z-index:5}
  #btns{display:flex;gap:8px;justify-content:flex-end;align-items:center;padding:8px 14px 10px}
  #tl{position:relative;height:4px;background:rgba(67,255,134,.15)}
  #tlFill{height:100%;width:0;background:#43ff86}
  #tl i{position:absolute;top:-3px;width:1px;height:10px;background:rgba(220,255,230,.7)}""")
R_("""<div id="ui">
  <button data-a="wake" title="W">Пробуждение</button>
  <button data-a="press" title="V">Склеп</button>
  <button data-a="mad" title="M">Безумие</button>
  <button data-a="pause" title="P">Пауза</button>
  <button data-a="fs" title="F">Во весь экран</button>
  <span>W · V · M · P · F</span>
</div>""","""<div id="ui">
  <div id="btns">
    <button data-a="restart" title="R">Сначала</button>
    <button data-a="loop" id="bLoop" title="L">Повтор: вкл</button>
    <button data-a="pause" title="P, пробел">Пауза</button>
    <button data-a="fs" title="F">Во весь экран</button>
    <span>R · L · P · F</span>
  </div>
  <div id="tl"><div id="tlFill"></div></div>
</div>""")
R_("""    x.strokeStyle = `rgba(67,255,134,${alpha})`; x.lineWidth = 1.3 * kk; x.beginPath(); pts.forEach((p, i) => i ? x.lineTo(...p) : x.moveTo(...p)); x.stroke();
  };""","""  };""")
R_("""  dctx.drawImage(amb, 0, 0); dctx.drawImage(traceC, 0, 0); dctx.drawImage(hallC, 0, 0);""",
"""  dctx.fillStyle = '#000'; dctx.fillRect(0, 0, W, H);
  dctx.globalAlpha = .22 + .78 * vis.power; dctx.drawImage(amb, 0, 0); dctx.drawImage(traceC, 0, 0);
  dctx.globalAlpha = vis.hall; dctx.drawImage(hallC, 0, 0); dctx.globalAlpha = 1;""")
R_("""  drawTraceBoosts(); drawPulses();""","""  drawTraceBoosts(); drawPulses();""")
R_("""  const sz = g * .92;
  if (q.void && q.state !== 'corrupt') return;
  const B = boost(q.d), base = .3 * power + .08;""","""  const sz = g * .92;
  if (q.void && q.state !== 'corrupt') return;
  const rp = cellReveal(q);
  if (rp <= 0) return;
  if (rp < 1 && q.state === 'norm') { drawWriteOn(q, sz, rp); return; }
  const B = boost(q.d), base = .3 * power + .08;""")
R_("""function drawGauss(q, sz) {""","""function cellReveal(q) { return clamp((vis.F - q.d) / (H * .15)); }
function drawWriteOn(q, sz, rp) {
  const n = q.glyph.S.length, lw = Math.max(1.1, sz * .055), pr = k => clamp(rp * n - k);
  const spr = glyphSprites(q.glyph, sz); dctx.globalAlpha = rp; dctx.drawImage(spr.G, q.x - spr.S / 2, q.y - spr.S / 2); dctx.globalAlpha = 1;
  lctx.lineCap = 'round'; lctx.lineJoin = 'round'; lctx.lineWidth = lw;
  lctx.strokeStyle = lctx.fillStyle = COL.hot; lctx.globalAlpha = .9 * (1 - rp) + .2;
  drawStrokes(lctx, q.glyph, q.x, q.y, sz, pr);
  lctx.globalAlpha = 1;
}
function drawGauss(q, sz) {""")
R_("""    const busy = k.cells.some(q => q.state === 'phase'), B = boost(k.cells[0].d);""","""    const busy = k.cells.some(q => q.state === 'phase'), B = boost(k.cells[0].d), rv = Math.min(...k.cells.map(cellReveal));
    if (rv <= 0) continue;""")
R_("""lctx.globalAlpha = clamp(.28 * power + .1 + B * .7 + (busy ? .35 : 0)); path(lctx); lctx.stroke();""","""lctx.globalAlpha = clamp(.28 * power + .1 + B * .7 + (busy ? .35 : 0)) * rv; path(lctx); lctx.stroke();""")
R_("""  for (const b of buses) for (const p of b.pieces) {
    const B = boost(p.d); if (B < .03) continue;
    if (inDead(b.side, b.r, p.xm)) continue;
    lctx.strokeStyle = B > .7 ? COL.hot : COL.light; lctx.globalAlpha = clamp(B);""","""  for (const b of buses) for (const p of b.pieces) {
    if (p.d > vis.F) continue;
    const head = clamp(1 - (vis.F - p.d) / (H * .04));
    const B = boost(p.d) + head * .9;
    lctx.strokeStyle = B > .7 ? COL.hot : COL.light; lctx.globalAlpha = clamp(.16 * (.4 + .6 * vis.power) + B);""")
R_("""  for (const f of floorLines) for (const p of f.pieces) {
    const B = boost(p.d); if (B < .03) continue;""","""  for (const f of floorLines) for (const p of f.pieces) {
    if (p.d > vis.FH) continue;
    const B = boost(p.d) + clamp(1 - (vis.FH - p.d) / (H * .04)) * .9 + .05; if (B < .03) continue;""")
R_("""  for (const tr of [trunkUp, trunkDown]) {
    const B = boost(tr.d0 + tr.len * .5) + .25 * power;
    lctx.strokeStyle = COL.light; lctx.globalAlpha = clamp(B); lctx.lineWidth = 1.6 * kk;
    lctx.beginPath(); lctx.moveTo(...tr.pts[0]); lctx.lineTo(...tr.pts[1]); lctx.stroke();
  }""","""  for (const [tr, Fr] of [[trunkUp, vis.F], [trunkDown, vis.FH]]) {
    const L = clamp(Fr - tr.d0, 0, tr.len); if (L <= 0) continue;
    const B = boost(tr.d0 + tr.len * .5) + .25 * power;
    lctx.strokeStyle = COL.light; lctx.globalAlpha = clamp(B); lctx.lineWidth = 1.6 * kk;
    lctx.beginPath(); lctx.moveTo(...tr.pts[0]); lctx.lineTo(...pointAt(tr, L)); lctx.stroke();
  }
  lctx.lineWidth = 1.2 * kk; lctx.strokeStyle = COL.light;
  for (const q of cells) { if (q.void) continue; const rp = cellReveal(q); if (rp <= 0) continue; lctx.globalAlpha = clamp(.13 * rp * (.4 + .6 * vis.power) + boost(q.d) * .4);
    lctx.beginPath(); lctx.moveTo(q.x, q.busY); lctx.lineTo(q.x, lerp(q.busY, q.y + g * .48, rp)); lctx.stroke(); }""")
R_("""  const sr = RF * (.17 + .1 * P), s = .55 + .12 * Math.sin(t * 1.3) + .1 * Math.sin(t * 3.7) + P * .9;""",
   """  if (vis.star <= 0 && vis.tessEdges <= 0) return;
  const sr = RF * (.17 + .1 * P + .25 * vis.flare + .1 * vis.gate + .12 * vis.gateOpen) * Math.max(.05, vis.star), s = (.55 + .12 * Math.sin(t * 1.3) + .1 * Math.sin(t * 3.7) + P * .9 + vis.flare * 1.5) * Math.min(1, vis.star * 1.5);""")
R_("""  const raw = tessRaw(t).map(""","""  const raw = tessRaw(tessAng).map(""")
R_("""  for (const e of order) {
    const q = clamp((e.d + 2.6) / 5.2), a = raw[e.i], b = raw[e.j];""","""  for (const e of order) {
    const ve = clamp(vis.tessEdges - TE_ORDER.get(e.i * 16 + e.j)); if (ve <= 0) continue;
    const q = clamp((e.d + 2.6) / 5.2), a = raw[e.i], b0 = raw[e.j], b = { x: lerp(a.x, b0.x, ve), y: lerp(a.y, b0.y, ve) };""")
R_("""  for (const v of raw) { const q = clamp((v.d + 2.6) / 5.2), r = (1.5 + 2.5 * q) * kk;""","""  if (vis.tessEdges >= 1) for (const v of raw) { const q = clamp((v.d + 2.6) / 5.2), r = (1.5 + 2.5 * q) * kk;""")
R_("""  const ring = (rr, amp, alpha, col, lw) => {
    lctx.strokeStyle = col;""","""  const ring = (rr, amp, alpha, col, lw) => {
    if (vis.field <= 0) return;
    lctx.strokeStyle = col;""")
R_("""for (let i = 0; i <= 120; i++) { const a = i / 120 * TAU, w = amp""","""for (let i = 0; i <= Math.round(120 * vis.field); i++) { const a = -Math.PI / 2 + i / 120 * TAU, w = amp""")
R_("""  wards.forEach((wd, i) => {
    const a = wd.a + t * .004""","""  wards.forEach((wd, i) => {
    const wv = clamp(vis.wards - i); if (wv <= 0) return;
    const a = wd.a + t * .004""")
R_("""    lctx.globalAlpha = clamp(.3 * power + .15 + chain + Bc * .4); lctx.drawImage(spr.L, -spr.S / 2, -spr.S / 2); lctx.restore();""",
   """    lctx.globalAlpha = clamp(.3 * power + .15 + chain + Bc * .4 + (1 - wv) * .8) * wv; lctx.drawImage(spr.L, -spr.S / 2, -spr.S / 2); lctx.restore();""")
R_("""  const B = boost(dLintel);
  const path = x =>""","""  const B = boost(dLintel), lv = clamp((vis.F - dLintel) / (H * .1));
  if (lv <= 0) return;
  const path = x =>""")
R_("""lctx.strokeStyle = COL.light; lctx.lineWidth = 1.5 * kk; lctx.globalAlpha = clamp(.3 * power + .15 + B); path(lctx); lctx.stroke();
  for (const ng of nameGlyphs) {
    const spr = glyphSprites(ng.glyph, ng.size);
    dctx.drawImage(spr.G, ng.x - spr.S / 2, ng.y - spr.S / 2);
    lctx.globalAlpha = clamp(.4 * power + .15 + B * .8); lctx.drawImage(spr.L, ng.x - spr.S / 2, ng.y - spr.S / 2);
  }""","""lctx.strokeStyle = COL.light; lctx.lineWidth = 1.5 * kk; lctx.globalAlpha = clamp(.3 * power + .15 + B) * lv; path(lctx); lctx.stroke();
  nameGlyphs.forEach((ng, i) => {
    const spr = glyphSprites(ng.glyph, ng.size), nv = clamp(vis.name - i), fl = nv > 0 && nv < 1 ? 1 - nv : 0;
    dctx.globalAlpha = lv; dctx.drawImage(spr.G, ng.x - spr.S / 2, ng.y - spr.S / 2); dctx.globalAlpha = 1;
    if (nv <= 0) return;
    lctx.globalAlpha = clamp((.55 + .45 * vis.power) * nv + B * .8 + vis.nameGlow); lctx.drawImage(spr.L, ng.x - spr.S / 2, ng.y - spr.S / 2);
    if (fl > 0 || vis.nameGlow > .05) { const h = glyphSprites(ng.glyph, ng.size, COL.hot); lctx.globalAlpha = clamp(fl * 1.2 + vis.nameGlow); lctx.drawImage(h.L, ng.x - h.S / 2, ng.y - h.S / 2); }
  });""")
R_("""    const b = boost(u.d); lctx.globalAlpha = clamp(.18 * power + .06 + b * .8);""","""    const fv = clamp((vis.F - u.d) / (H * .06)); if (fv <= 0) continue;
    const b = boost(u.d); lctx.globalAlpha = clamp(.18 * power + .06 + b * .8 + vis.nameGlow * .5) * fv;""")
R_("""  const h = digitBox.h, w = h * .62, gap = w * .45, x0 = CX - (n * (w + gap) - gap) / 2, y = digitBox.y;""","""  const h = vis.ch, w = h * .62, gap = w * .45, x0 = CX - (n * (w + gap) - gap) / 2, y = vis.cy;""")
R_("""  const years = 65000000 + Math.floor(t * 3.7), s = String(years), n = s.length;""","""  if (vis.counterA <= 0) return;
  const s = String(Math.max(0, Math.floor(vis.counterV))).padStart(vis.counterPad, '0'), n = s.length;""")
R_("""    lctx.globalAlpha = .35 * power + .12 + (isLow ? .25 : 0);""","""    lctx.globalAlpha = clamp((.45 + (isLow ? .25 : 0) + vis.counterFlash) * vis.counterA); lctx.lineWidth = Math.max(1, h * .07);
    lctx.strokeStyle = lctx.fillStyle = vis.counterFlash > .05 ? COL.hot : COL.light;""")
R_("""function drawEyes() {
  for (const n of niches) {
    const L = n.lvl = eyeLevel(n);""","""function riteEye(n) {
  // [уровень, ширина щели 0..1]; полностью определяется временем обряда
  const ta = n.ta, tg = n.tg;
  if (rt < ta) { const s = t - n.stir; return [vis.hall * (.06 + (s < 1.4 && rt > 31 ? .25 * Math.sin(Math.PI * clamp(s / 1.4)) : 0)), 1]; }
  if (n.bad) { n.mark = rt > ta + .7; const e = rt - ta; return [[.3, 0, .22, 0, .12, 0, 0][Math.floor(e / .1)] ?? 0, 1]; }
  let L, w = 1; const e = rt - ta;
  if (e < .16) L = [.9, .05, 1, .15][Math.floor(e / .04)] ?? .9; else L = .82 + .7 * Math.exp(-(e - .16) * 6) + .05 * Math.sin(t * 1.6 + n.ph);
  if (rt >= tg) { const f = rt - tg; if (f < .15) L = .85 + 5 * f; else if (f < .5) { L = 1.6; w = 1 - (f - .15) / .35; } else return [0, 0]; }
  return [L, w];
}
function drawEyes() {
  for (const n of niches) {
    let [L, wf] = riteEye(n); L += boost(n.d) * (L > .3 ? .8 : 0);
    if (n.mark && vis.hall < .02) continue;""")
R_("""    const ew = Math.max(1, n.w * .19), eh""","""    if (wf <= 0) continue;
    const ew = Math.max(.6, n.w * .19 * wf), eh""")
R_("""      if (n.h > 8) { lctx.globalAlpha = .22; lctx.fillStyle = COL.dim;""","""      if (n.h > 8) { lctx.globalAlpha = .22 * vis.hall; lctx.fillStyle = COL.dim;""")
R_("""function frame(now) {
  requestAnimationFrame(frame);
  const dt = Math.min(.05, (now - last) / 1000); last = now;
  if (paused) return;
  update(dt); render();
}""","""function frame(now) {
  requestAnimationFrame(frame);
  const rdt = (now - last) / 1000; last = now;
  if (paused) return;
  step(rdt); render();
}
// часы обряда идут по настоящему времени без ограничения шага (события не отстают); dt ограничен лишь для частиц
function step(rdt) { riteUpdate(rdt); update(Math.min(.05, rdt)); }""")
R_("""  t += dt;
  // расписание
  if (t >= sched.wake && wakeState.phase === 'sleep') startWake();
  if (t >= sched.press && !press.on) { startPress(); sched.press = t + rnd(40, 70); }
  if (t >= sched.mad && !mad) { startMad(); if (!mad) sched.mad = t + 30; }
  if (t >= sched.gauss) { startGauss(); sched.gauss = t + rnd(8, 15); }
  if (t >= sched.phase) { startPhase(); sched.phase = t + rnd(20, 34); }
  if (t >= sched.flip) {""","""  t += dt;
  power = vis.power;
  if (vis.life && t >= sched.gauss) { startGauss(); sched.gauss = t + rnd(6, 11); }
  if (vis.life && t >= sched.phase) { startPhase(); sched.phase = t + rnd(14, 22); }
  if (vis.life && t >= sched.flip) {""")
R_("""  if (t >= sched.beat) { emit('beat', { amp: .35, w: H * .035, v: H * .7 }); sched.beat = t + rnd(8, 13); }
  if (t >= sched.stir) { const n = pick(niches); if (n.state === 'sleep') n.stir = t; sched.stir = t + rnd(.15, .45); }
  if (t >= sched.pulse) { launchPulse(); sched.pulse = t + rnd(.12, .35) / (power > .8 ? 2 : 1); }""","""  if (t >= sched.stir) { const n = pick(niches); n.stir = t; sched.stir = t + rnd(.15, .45); }
  if (vis.life && t >= sched.pulse) { launchPulse(); sched.pulse = t + rnd(.12, .35) / (power > .8 ? 2 : 1); }""")
R_("""  updWake(); updMad(); updVoids();""","""""")
R_("""    const e = t - press.t0;
    press.p = e""","""    const e = rt - press.t0;
    press.p = e""")
R_("""    if (e > 3.6 && !press.snap) { press.snap = true; emit('ward', { amp: .8, w: H * .03, v: H * .9 }); }""","""    if (e > 3.6 && !press.snap) { press.snap = true; emit('ward', { amp: .8, w: H * .03, v: H * .9, t0: t - (e - 3.6) }); }""")
R_("""  if (press.snap && t - press.t0 < 4.3) { const q = (t - press.t0 - 3.6) / .7;""","""  if (press.snap && rt - press.t0 < 4.3) { const q = (rt - press.t0 - 3.6) / .7;""")
R_("""  const pool = cells.filter(q => q.state === 'norm' && !q.flip && !q.void && q.cart < 0);
  if (!pool.length) return;
  const q = pick(pool); q.state = 'gauss'; q.ev = { t0: t };""","""  const pool = cells.filter(q => q.state === 'norm' && !q.flip && !q.void && q.cart < 0 && cellReveal(q) >= 1);
  if (!pool.length) return;
  const q = pick(pool); q.state = 'gauss'; q.ev = { t0: t };""")
R_("""  const avail = carts.filter(k => k.cells.every(q => q.state === 'norm' && !q.void));""","""  const avail = carts.filter(k => k.cells.every(q => q.state === 'norm' && !q.void && cellReveal(q) >= 1));""")
R_("""function act(a) {
  if (a === 'wake') { if (wakeState.phase === 'sleep') startWake(); }
  else if (a === 'press') startPress();
  else if (a === 'mad') startMad();
  else if (a === 'pause') paused = !paused;""","""function act(a) {
  if (a === 'restart') { riteRestart(); paused = false; }
  else if (a === 'loop') { loopOn = !loopOn; document.getElementById('bLoop').textContent = 'Повтор: ' + (loopOn ? 'вкл' : 'выкл'); }
  else if (a === 'pause') paused = !paused;""")
R_("""addEventListener('keydown', e => { const m = { KeyW: 'wake', KeyV: 'press', KeyM: 'mad', KeyP: 'pause', KeyF: 'fs' }[e.code]; if (m) act(m); });""",
   """addEventListener('keydown', e => { const m = { KeyR: 'restart', KeyL: 'loop', KeyP: 'pause', Space: 'pause', KeyF: 'fs' }[e.code]; if (m) { e.preventDefault(); act(m); } });""")
R_("""let rzT = 0; addEventListener('resize', () => { clearTimeout(rzT); rzT = setTimeout(() => { deadSpans = []; voids = []; mad = null; build(); }, 150); });
window.__somnus = { update, render, get t() { return t; }, act };

build();""","""let rzT = 0; addEventListener('resize', () => { clearTimeout(rzT); rzT = setTimeout(() => { deadSpans = []; voids = []; mad = null; build(); riteTimes(); }, 150); });

build(); riteTimes(); riteRestart();""")
R_("lctx.arc(x + (d - (dots - 1) / 2) * w * .26, yd, kk * 1.3, 0, TAU)", "lctx.arc(x + (d - (dots - 1) / 2) * w * .26, yd, Math.max(kk * 1.3, h * .065), 0, TAU)")
R_("    let n = 1; if (P > 0) n += P * (.12 + .2 * Math.sin(t * 21 + i * 1.7));",
   "    let n = 1 + vis.gate * .13 + vis.gateOpen * .22; if (P > 0) n += P * (.12 + .2 * Math.sin(t * 21 + i * 1.7));")
R_("lctx.strokeStyle = P > .5 && Math.random() < P * .3 ? COL.star : q > .7 ? COL.hot : COL.light;",
   "lctx.strokeStyle = P > .5 && Math.random() < P * .3 ? COL.star : (q > .7 || vis.gate > .45) ? COL.hot : COL.light;")
R_("drawCarts(); drawLintel(); drawCounter(); drawVault(); drawEyes(); drawMad();",
   "drawCarts(); drawLintel(); drawCounter(); drawVault(); drawEyes(); drawDepart(); drawMad();")
s = s.replace("\n/* =============================== кадр =============================== */",
              open(sys.argv[3]).read() + "\n/* =============================== кадр =============================== */", 1)
open(dst, 'w').write(s); print('ok')
