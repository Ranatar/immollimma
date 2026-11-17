
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
const vis = { power: 0, hall: 0, F: 0, FH: 0, star: 0, flare: 0, tessEdges: 0, tessSpeed: 0, field: 0, wards: 0, name: 0, nameGlow: 0,
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
}
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
  vis.counterFlash = x >= 7.2 && x < 31.2 ? Math.exp(-(x - 7.2) * 3) : 0;
  if (x < 31.2) { vis.counterPad = 8; vis.counterV = 65000000 + 4800 * (1 - Math.exp(-(clamp(x, 1.2, 7.2) - 1.2) / 1.7)); vis.counterA = sstep(1.2, 1.8, x) * (1 - .45 * sstep(9, 12, x)) * (1 - sstep(30.4, 31.2, x)); }
  else if (x < 86.4) { vis.counterPad = 3; let awake = 0; for (const n of niches) if (!n.bad && rt >= n.ta && rt < n.tg + .5) awake++; vis.counterV = awake; vis.counterA = .55 * sstep(31.2, 32, x) * (1 - sstep(70, 72, x)); }
  else { vis.counterPad = 8; vis.counterV = (x - 86.4) * 3.7; vis.counterA = sstep(86.4, 87, x) * (1 - sstep(90, 92.4, x)); }
  const cs = sstep(8.1, 10.5, x);
  vis.cy = x < 86.4 ? lerp(VY, digitBox.y, cs) : VY + RF * .55; vis.ch = x < 86.4 ? lerp(H * .055, digitBox.h, cs) : H * .03;
  tlFill.style.width = (rt / RITE_LEN * 100).toFixed(2) + '%';
}
window.__protocol = { step, render, EVLOG: () => EVLOG, RITE_LEN, STAGES, BEATS, BEATS_ACC, get rt() { return rt; },
  niches: () => niches.map(n => ({ row: n.i, ta: +n.ta.toFixed(4), tg: +n.tg.toFixed(4), bad: n.bad })),
  state: () => ({ rt, power: vis.power, hall: vis.hall, star: vis.star, F: vis.F, tessSpeed: vis.tessSpeed, press: press.p }) };
