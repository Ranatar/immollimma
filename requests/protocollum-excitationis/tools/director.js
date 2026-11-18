
/* =============================== протокол пробуждения: режиссура =============================== */
// сетка для музыки: 100 уд/мин, доля 0,6 с; сердце гробницы — каждые 1,2 с с 28,8 по 57,6; ключевые метки кратны 0,3 с
const RITE_LEN = 96, BEAT_S = .6;
const STAGES = [[0, 'I', 'Тьма и счётчик сна'], [8.1, 'II', 'Склеп'], [15, 'III', 'Каналы и стена'], [21, 'IV', 'Сердце гробницы'],
  [28.8, 'V', 'Зал'], [31.2, 'VI', 'Легион просыпается'], [48, 'VII', 'Имя повелителя'], [52.8, 'VIII', 'Давление в склепе'],
  [57.6, 'IX', 'Приказ'], [59.4, 'X', 'Уход легиона'], [72, 'XI', 'Возвращение в сон'], [86.4, 'XII', 'Новый сон']];
const BEATS_ACC = [21.0, 23.1, 24.6, 25.8, 26.7, 27.3, 27.9, 28.5];
const BEATS = []; for (let k = 0; k <= 24; k++) BEATS.push(+(28.8 + 1.2 * k).toFixed(1));
const V_WALL = .24, T_WALL = 15, T_LEG = 31.2, D_LEG = 13.2, T_GO = 59.4, D_GO = 10.2, T_RET = 72, D_RET = 8.4;
let rt = 0, loopOn = true, tessAng = 0, cueIdx = 0, lastStage = null;
const vis = { gate: 0, gateOpen: 0, power: 0, hall: 0, F: 0, FH: 0, star: 0, flare: 0, tessEdges: 0, tessSpeed: 0, field: 0, wards: 0, name: 0, nameGlow: 0,
  counterA: 0, counterV: 0, cy: 0, ch: 1, counterPad: 8, counterFlash: 0, life: false };
let FMAX = 0, FHMAX = 0;
const TE_ORDER = new Map(); TE.forEach(([i, j], k) => TE_ORDER.set(i * 16 + j, k));
function riteTimes() {   // моменты пробуждения и ухода каждой ниши — заранее и детерминированно
  FMAX = Math.max(...cells.map(q => q.d), dLintel + W / 2) + H * .2;
  FHMAX = Math.max(...floorLines.flatMap(f => f.pieces.map(p => p.d))) + H * .05;
  const span = hallMaxD - dVP + rowStep * .4;
  for (const n of niches) {
    n.ta = T_LEG + (n.d - dVP + n.jit) / span * D_LEG;
    n.tg = T_GO + (hallMaxD - n.d + n.jit) / span * D_GO;
  }
  // уход ряда — по его центральной нише (она же просыпается первой); свет доходит до врат через GATE_LAG
  ROW_DEP = [];
  for (let r = 0; r < NROWS; r++) {
    const row = niches.filter(n => n.i === r && !n.bad); if (!row.length) continue;
    const c = row.reduce((a, b) => a.ta < b.ta ? a : b);
    ROW_DEP.push({ row: r, t: c.tg });
  }
  // часть ниш шлёт видимый «след»: по полу в точку схода, по стволу в склеп
  streaks = niches.filter((n, k) => !n.bad && n.h > 6 && (k % 9 === 0 || ROW_DEP.some(rd => Math.abs(rd.t - n.tg) < 1e-9)))
    .map(n => ({ n, path: polyline([[n.x, n.y - n.h], [n.x, n.y], [CX, HY], [CX, VY + RF]], 0) }));
}
const GATE_LAG = 1.1;
let ROW_DEP = [], streaks = [];
const lin = (a, b, x) => clamp((x - a) / (b - a));
const EVLOG = []; let cueT = null;
const ev = (type, data = {}) => EVLOG.push({ type, ...data, t: +(data.t ?? cueT ?? rt).toFixed(4) });
const CUES = [
  [1.2, 'counter_on'], [7.2, 'counter_stop'], [8.1, 'star_ignites'], [8.4, 'tesseract_draw'], [11.4, 'field_draw'], [12.6, 'wards_light'],
  [15.0, 'wall_front'], ...BEATS_ACC.map(x => [x, 'heart_acc']), ...BEATS.map(x => [x, 'heart']), [28.8, 'hall_front'],
  [31.2, 'legion_wave'], [48.0, 'name_1'], [48.9, 'name_2'], [49.8, 'name_3'], [50.7, 'name_4'], [51.6, 'name_5'],
  [52.8, 'vault_pressure'], [57.6, 'command'], [59.4, 'legion_depart'], [72.0, 'retract'], [80.4, 'wards_off'], [82.2, 'field_off'],
  [83.4, 'tesseract_undraw'], [86.4, 'counter_zero'], [89.4, 'star_dot'], [90.0, 'star_off']
].sort((a, b) => a[0] - b[0]);
function fireCue(name, at) {
  cueT = at;
  const late = rt - at;   // на сколько кадр опоздал к метке — волны и давление ставятся на точное время
  if (name.startsWith('heart')) {
    const k = name === 'heart' ? 1 : (BEATS_ACC.indexOf(at) + 1) / BEATS_ACC.length;
    emit('beat', { amp: name === 'heart' ? .55 : .25 + .35 * k, w: H * .04, v: H * .8, t0: t - late });
  }
  if (name === 'star_ignites') burst(CX, VY, 24, COL.star, 70, 1.2);
  if (name === 'vault_pressure') press = { on: true, t0: at, p: 0 };
  if (name === 'command') emit('cmd', { amp: 2.2, w: H * .07, v: H * .9, t0: t - late });
  if (name.startsWith('name_')) { const ng = nameGlyphs[+name.slice(5) - 1]; burst(ng.x, ng.y, 16, COL.hot, 50, .9); }
  ev(name.startsWith('heart') ? 'heart' : 'cue', name.startsWith('heart') ? { kind: name } : { name });
  cueT = null;
}
function riteRestart() {
  rt = 0; cueIdx = 0; lastStage = null; tessAng = 0; waves = []; pulses = []; particles = [];
  press = { on: false, p: 0 };
  for (const q of cells) { q.state = 'norm'; q.ev = null; q.flip = null; }
  for (const n of niches) n.mark = false;
}
const tlFill = document.getElementById('tlFill');
(() => { const tl = document.getElementById('tl'); for (const [at, num, name] of STAGES) { const i = document.createElement('i'); i.style.left = (at / RITE_LEN * 100) + '%'; i.title = num + ' · ' + name; tl.appendChild(i); } })();

function riteUpdate(dt) {
  rt += dt;
  if (rt >= RITE_LEN) { if (loopOn) { const over = rt - RITE_LEN; riteRestart(); rt = over; ev('restart', { t: 0 }); } else rt = RITE_LEN; }
  while (cueIdx < CUES.length && CUES[cueIdx][0] <= rt) { const [at, name] = CUES[cueIdx++]; fireCue(name, at); }
  const st = STAGES.reduce((a, s) => rt >= s[0] ? s : a, STAGES[0]);
  if (st !== lastStage) { lastStage = st; ev('stage', { t: st[0], num: st[1], name: st[2] }); }
  const x = rt;
  vis.F = x < T_WALL ? 0 : x < T_RET ? Math.min(FMAX, (x - T_WALL) * H * V_WALL) : FMAX * (1 - lin(T_RET, T_RET + D_RET, x));
  vis.FH = x < 28.8 ? 0 : x < T_RET ? lerp(dVP - 1, FHMAX, lin(28.8, 31.2, x)) : lerp(FHMAX, 0, lin(T_RET, 75.6, x));
  vis.hall = sstep(28.8, 31.2, x) * (1 - sstep(T_RET, 76, x));
  vis.power = clamp(.15 + .35 * sstep(15, 20, x) + .5 * sstep(28.8, 44.4, x) - .5 * sstep(59.4, 69.6, x) - .35 * sstep(T_RET, 80.4, x)) * (x < 1.2 ? 0 : 1);
  vis.star = x < 8.1 ? 0 : x < 86.4 ? sstep(8.1, 8.6, x) : x < 90 ? lerp(1, .12, lin(86.4, 89.4, x)) : 0;
  vis.flare = (x >= 57.6 ? Math.exp(-(x - 57.6) * 1.6) : 0) + (x >= 8.1 ? .6 * Math.exp(-(x - 8.1) * 4) : 0);
  vis.tessEdges = x < 8.4 ? 0 : x < 83.4 ? Math.min(TE.length, (x - 8.4) / .1) : TE.length * (1 - lin(83.4, 86.4, x));
  vis.field = x < 11.4 ? 0 : x < 82.2 ? lin(11.4, 12.9, x) : 1 - lin(82.2, 83.7, x);
  vis.wards = x < 12.6 ? 0 : x < 80.4 ? Math.min(24, (x - 12.6) / .1) : 24 * (1 - lin(80.4, 82.8, x));
  vis.tessSpeed = x < 8.4 ? 0 : x < 57.3 ? sstep(8.4, 12, x) : x < 59.4 ? 1 - sstep(57.3, 57.6, x) : x < 80 ? sstep(59.4, 61, x) : 1 - sstep(80, 86.4, x);
  tessAng += dt * vis.tessSpeed;
  vis.name = x < 48 ? 0 : x < T_RET ? Math.min(5, (x - 48) / .9) : 5 * (1 - lin(T_RET, 74, x));
  vis.nameGlow = x >= 51.6 ? Math.exp(-(x - 51.6) * 1.2) * .8 + (x >= 57.6 ? Math.exp(-(x - 57.6) * 1.5) : 0) : 0;
  vis.life = x > 20 && x < T_RET;
  // врата: пульс на приход света каждого ряда, общее раскрытие к концу ухода и схлопывание
  let gte = 0; for (const rd of ROW_DEP) { const e = x - rd.t - GATE_LAG; if (e >= 0) gte += Math.exp(-e * 4.5); }
  vis.gate = Math.min(1.6, gte); vis.gateOpen = sstep(60, 69, x) * (1 - sstep(70.4, 71.2, x));
  vis.counterFlash = x >= 7.2 && x < 31.2 ? Math.exp(-(x - 7.2) * 3) : 0;
  if (x < 31.2) { vis.counterPad = 8; vis.counterV = 65000000 + 4800 * (1 - Math.exp(-(clamp(x, 1.2, 7.2) - 1.2) / 1.7)); vis.counterA = sstep(1.2, 1.8, x) * (1 - .45 * sstep(9, 12, x)) * (1 - sstep(30.4, 31.2, x)); }
  else if (x < 86.4) { vis.counterPad = 3; let awake = 0; for (const n of niches) if (!n.bad && rt >= n.ta && rt < n.tg + .5) awake++; vis.counterV = awake; vis.counterA = .55 * sstep(31.2, 32, x) * (1 - sstep(70, 72, x)); }
  else { vis.counterPad = 8; vis.counterV = (x - 86.4) * 3.7; vis.counterA = sstep(86.4, 87, x) * (1 - sstep(90, 92.4, x)); }
  const cs = sstep(8.1, 10.5, x);
  vis.cy = x < 86.4 ? lerp(VY, digitBox.y, cs) : VY + RF * .55; vis.ch = x < 86.4 ? lerp(H * .055, digitBox.h, cs) : H * .03;
  tlFill.style.width = (rt / RITE_LEN * 100).toFixed(2) + '%';
}
// уход легиона: саркофаг загорается и разбирается развёрткой сверху вниз, из ниши бьёт луч, свет уходит во врата
function drawDepart() {
  if (rt < T_GO - .1 || vis.hall < .01) return;
  for (const n of niches) {
    if (n.bad || n.h < 3) continue;
    const f = rt - n.tg; if (f < 0) continue;
    if (f > .55) {                                   // пустая ниша
      nicheShape(dctx, n); dctx.fillStyle = `rgba(0,0,0,${.55 * vis.hall})`; dctx.fill();
      if (n.h > 20) { lctx.globalAlpha = .12 * vis.hall; lctx.strokeStyle = COL.dim; lctx.lineWidth = Math.max(.6, n.w * .015); nicheShape(lctx, n); lctx.stroke(); }
      continue;
    }
    const q = clamp((f - .1) / .35), top = n.y - n.h, ys = top + q * n.h;
    lctx.save(); nicheShape(lctx, n); lctx.clip();
    lctx.globalAlpha = .38 * (1 - q) + .12; lctx.fillStyle = COL.light; lctx.fillRect(n.x - n.w, ys, n.w * 2, n.y - ys);
    if (n.h > 14) { lctx.globalAlpha = .55; lctx.fillStyle = COL.hot; const st = Math.max(2, n.h * .06); for (let yy = ys; yy < n.y; yy += st) lctx.fillRect(n.x - n.w, yy, n.w * 2, Math.max(.8, n.h * .012)); }
    lctx.restore();
    lctx.globalAlpha = clamp(1.2 - q); lctx.strokeStyle = COL.hot; lctx.lineWidth = Math.max(.7, n.w * .03); nicheShape(lctx, n); lctx.stroke();
    lctx.fillStyle = COL.hot; lctx.globalAlpha = .9 * (1 - q); lctx.fillRect(n.x - n.w * .55, ys - 1, n.w * 1.1, Math.max(1.2, n.h * .015));
    if (f > .25) {                                   // луч вверх
      const b = clamp((f - .25) / .3), L = n.h * (1.2 + 2.8 * b), bw = Math.max(1.4, n.w * .09);
      const g = lctx.createLinearGradient(0, top - L, 0, top);
      g.addColorStop(0, 'rgba(67,255,134,0)'); g.addColorStop(1, COL.hot);
      lctx.globalAlpha = .75 * (1 - b); lctx.fillStyle = g; lctx.fillRect(n.x - bw / 2, top - L, bw, L);
    }
    if (n.h > 20 && Math.random() < .35) particles.push({ x: n.x + rnd(-n.w * .4, n.w * .4), y: ys, vx: rnd(-6, 6) * kk, vy: -rnd(40, 90) * kk, life: .6, max: .6, col: COL.light, s: 1.5 * kk });
  }
  // следы: по полу к точке схода и по стволу во врата
  lctx.lineCap = 'round';
  for (const sk of streaks) {
    const f = rt - sk.n.tg - .3; if (f < 0 || f > GATE_LAG - .3) continue;
    const s0 = sk.path.len * clamp(f / (GATE_LAG - .3));
    for (let j = 0; j < 6; j++) {
      const s1 = s0 - j * H * .02, s2 = s1 - H * .02; if (s1 < 0) break;
      const [x1, y1] = pointAt(sk.path, Math.max(0, s2)), [x2, y2] = pointAt(sk.path, s1);
      lctx.strokeStyle = j < 2 ? COL.hot : COL.light; lctx.globalAlpha = .85 * (1 - j / 6); lctx.lineWidth = (2.2 - j * .25) * kk;
      lctx.beginPath(); lctx.moveTo(x1, y1); lctx.lineTo(x2, y2); lctx.stroke();
    }
  }
  // кольцо врат при каждом приходе ряда
  if (vis.gate > .05) { lctx.strokeStyle = COL.hot; lctx.globalAlpha = clamp(vis.gate * .5); lctx.lineWidth = 2.5 * kk; lctx.beginPath(); lctx.arc(CX, VY, RF * (.55 + .25 * vis.gateOpen + .1 * vis.gate), 0, TAU); lctx.stroke(); }
  lctx.globalAlpha = 1;
}
window.__protocol = { step, render, EVLOG: () => EVLOG, RITE_LEN, STAGES, BEATS, BEATS_ACC, get rt() { return rt; },
  niches: () => niches.map(n => ({ row: n.i, ta: +n.ta.toFixed(4), tg: +n.tg.toFixed(4), bad: n.bad })),
  rowDepart: () => ROW_DEP.map(r => ({ row: r.row, t: +r.t.toFixed(4), gate: +(r.t + GATE_LAG).toFixed(4) })),
  state: () => ({ rt, power: vis.power, hall: vis.hall, star: vis.star, F: vis.F, tessSpeed: vis.tessSpeed, press: press.p }) };
