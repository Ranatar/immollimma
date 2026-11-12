#!/usr/bin/env python3
"""Tractatus: sieben Sätze — семь корневых утверждений «Логико-философского трактата» (≈ 6:30).

Не иллюстрация настроений, а музыкальная модель логической формы каждого утверждения (plan.md):

  девиз   — каждое утверждение «произносит» соло-кларнет: ритм по слогам немецкого оригинала (ударный — четверть,
            безударный — восьмая, запятая — пауза, последний слог — половинная), высота — первая буква слога
            по кругу A–G (индекс буквы mod 7) как ступень лада части;
  1       — логическое пространство: 21 звук × сетка шестнадцатых, каждая клетка звучит независимо (1.21);
  2       — семь неизменных предметов (свои высота и тембр, квинтовая цепь D–A–E–B–F♯–C♯–G♯); меняется лишь их
            конфигурация, по одному за шаг (2.0271);
  3       — факт (фагот) и его картины: ускорение, обращение, растяжение — мензуральный канон (2.17);
  4       — одна фраза у разных инструментов; над бурдоном «действительности» кончается совпадением (истинно)
            или диссонансом (ложно) (4.06);
  5       — 16 функций истинности в порядке 5.101: доля = строка (p, q), пиццикато = p, ксилофон = q,
            медный аккорд = «истинно»; тавтология звучит четырежды, противоречие молчит; 5.6 — сужение в унисон;
  6       — [p̄, ξ̄, N(ξ̄)]: аккорд ξ и его отрицание — дополнение до двенадцати, от 1+11 до 6+6 (кульминация);
            6.41 — звук вне темперации (на четверть тона выше); 6.44 — мистическое: «что», а не «как»;
            6.54 — лестница, которую отбрасывают (обрыв);
  7       — «Wovon…» — и молчание.

    python3 -m kit run requests/tractatus/piece.py --sketch --parts
    python3 -m kit run requests/tractatus/piece.py --parts
"""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from kit.devices import Composer  # noqa: E402
from kit.events import Piece  # noqa: E402

BEAT = 60.0 / 96
D = 62  # D4

IONIAN = [0, 2, 4, 5, 7, 9, 11]
LYDIAN = [0, 2, 4, 6, 7, 9, 11]
DORIAN = [0, 2, 3, 5, 7, 9, 10]
MIXO = [0, 2, 4, 5, 7, 9, 10]
AEOLIAN = [0, 2, 3, 5, 7, 8, 10]
PHRYG = [0, 1, 3, 5, 7, 8, 10]

# '!' — ударный слог, '-' — граница слогов, ',' / '.' / ':' — пауза (восьмая)
SATZ = {
    1: ("Die !Welt ist !al-les, was der !Fall ist.", IONIAN),
    2: ("Was der !Fall ist, die !Tat-sa-che, ist das Be-!ste-hen von !Sach-ver-hal-ten.", LYDIAN),
    3: ("Das !lo-gi-sche !Bild der !Tat-sa-chen ist der Ge-!dan-ke.", DORIAN),
    4: ("Der Ge-!dan-ke ist der !sinn-vol-le !Satz.", MIXO),
    5: ("Der !Satz ist ei-ne !Wahr-heits-funk-ti-!on der E-le-men-!tar-sät-ze.", IONIAN),
    6: ("Die !all-ge-mei-ne !Form der !Wahr-heits-funk-ti-!on ist:", PHRYG),
    7: ("Wo-!von", AEOLIAN),  # … man nicht sprechen kann — не досказано
}

# 5.101: функции истинности в порядке Витгенштейна; строки — (p, q) = (W,W), (F,W), (W,F), (F,F)
FUNCS = ["WWWW", "FWWW", "WFWW", "WWFW", "WWWF", "FFWW", "FWFW", "FWWF",
         "WFFW", "WFWF", "WWFF", "FFFW", "FFWF", "FWFF", "WFFF", "FFFF"]
ROWS = [(1, 1), (0, 1), (1, 0), (0, 0)]
NAMES = {"WWWW": "Tautologie", "FFFF": "Kontradiktion", "WWFF": "p", "WFWF": "q", "FFWW": "~p", "FWFW": "~q",
         "WFFF": "p.q", "WWWF": "pvq", "WFWW": "q>p", "WWFW": "p>q", "WFFW": "p=q", "FWWF": "p≠q",
         "FWWW": "~(p.q)", "FFFW": "~p.~q", "FFWF": "~p.q", "FWFF": "p.~q"}

# семь предметов (2): высота и тембр неизменны — квинтовая цепь от D
OBJECTS = [("cb_sus", 38), ("vc_sus", 45), ("vla_sus", 52), ("hn_sus", 59), ("vln_sus", 66), ("fl_sus", 73),
           ("vln_harm", 80)]


def syllables(text):
    """→ [(syllable, stressed, rest_after)]"""
    out = []
    for word in text.split():
        rest = word[-1] in ",.:"
        parts = word.rstrip(",.:").split("-")
        for i, s in enumerate(parts):
            out.append((s.lstrip("!"), s.startswith("!"), rest and i == len(parts) - 1))
    return out


def letter_degree(s):
    c = s[0].lower()
    c = {"ä": "a", "ö": "o", "ü": "u", "ß": "s"}.get(c, c)
    return (ord(c) - ord("a")) % 7


class T:
    """состояние пьесы"""

    LEVEL = {}

    def __init__(self, ctx):
        self.cues = ctx.cues["cues"]
        self.total = ctx.cues["duration_s"]
        self.p = Piece("Tractatus: sieben Sätze", bpm=96, meter=(4, 4), key="D", seed=1921)
        self.p.meta["sends"] = {"choir": 0.55, "organ": 0.45, "harp": 0.45, "winds": 0.35, "strings": 0.38,
                                "brass": 0.3}
        self.p.meta["length"] = self.total  # молчание седьмой — часть пьесы, оно остаётся в файле
        self.c = Composer(self.p, lib="sso", seed=1918)
        self.rng = random.Random(1889)
        for cue in self.cues:
            if cue["kind"] in ("section", "hit", "silence", "accent", "transition", "swell"):
                self.p.mark(cue["t"], cue["label"][:24])

    def t(self, label):
        return next(c["t"] for c in self.cues if c["label"] == label)

    def n(self, inst, m, t, d, **kw):
        if inst in self.LEVEL:
            kw["gain"] = kw.get("gain", 1.0) * self.LEVEL[inst]
        if inst == "org_quiet" and m < 36:  # у тихого органа нет записей ниже C2
            inst = "org_loud"
            kw["gain"] = kw.get("gain", 1.0) * 0.55
        return self.p.note(inst, m, t, d, **kw)

    def motto(self, k, t, vel=0.55, gain=0.6):
        """девиз k-го утверждения у соло-кларнета; → время конца"""
        text, mode = SATZ[k]
        syl = syllables(text)
        tt = t
        for i, (s, stress, rest) in enumerate(syl):
            last = i == len(syl) - 1
            beats = 2.0 if last else (1.0 if stress else 0.5)
            m = D + mode[letter_degree(s)]
            d = beats * BEAT
            self.n("cl_sus", m, tt, d * (0.98 if last else 0.9), vel=vel + (0.06 if stress else 0.0), gain=gain,
                   attack=0.03, release=0.5 if not last else 1.2, pan=-0.05)
            tt += d + (0.5 * BEAT if rest and not last else 0.0)
        return tt


# ------------------------------------------------------------------------------------------------------------
def welt(g, t0, t1):
    """1: логическое пространство — каждая клетка независимо"""
    t = g.motto(1, t0 + 0.4)
    scale = [50 + 12 * o + iv for o in range(3) for iv in IONIAN]  # D3…C♯6, 21 звук
    s16 = BEAT / 4
    g_start, g_end = t + 0.3, t1 - 6.0
    slots = int((g_end - g_start) / s16)
    rng = random.Random(121)
    for k in range(slots):
        x = k / slots
        prob = 0.03 + 0.09 * x ** 1.6
        ts = g_start + k * s16
        for j, m in enumerate(scale):
            if rng.random() >= prob:
                continue
            v = 0.3 + 0.25 * x + 0.12 * rng.random()
            pan = -0.6 + 1.2 * j / 20
            if j < 7:
                g.n("vc_pizz" if j % 2 else "cb_pizz", m, ts, 0.6, vel=v, gain=0.5, pan=pan, release=0.4)
            elif j < 14:
                g.n("marimba" if (k + j) % 2 else "harp", m, ts, 1.2, vel=v, gain=0.5, pan=pan, release=0.8)
            else:
                g.n("celesta", m, ts, 1.4, vel=v, gain=0.45, pan=pan, release=1.0)
    # пол: пространство, в котором всё это происходит
    g.n("cb_sus", 38, g_start + 6.0, g_end - g_start - 4.0, vel=0.25, gain=0.35, attack=6.0, release=3.0)
    # «совокупность»: все 21 звука сразу
    tt = g_end + 0.3
    for j, m in enumerate(scale):
        inst = "cb_pizz" if j < 4 else "vc_pizz" if j < 7 else "harp" if j < 14 else "celesta"
        g.n(inst, m, tt + 0.01 * j, 4.0, vel=0.62, gain=0.5, pan=-0.6 + 1.2 * j / 20, release=2.5)
        g.n("harp", m, tt + 0.01 * j, 4.0, vel=0.5, gain=0.35, pan=-0.6 + 1.2 * j / 20, release=3.0)
    g.p.chord("vln_sus", [74, 76, 78, 81], tt, 5.0, vel=0.35, gain=0.3, attack=0.4, release=2.5)
    g.p.chord("vla_sus", [62, 64, 66, 69], tt, 5.0, vel=0.35, gain=0.3, attack=0.4, release=2.5)
    g.p.chord("vc_sus", [50, 54, 57], tt, 5.0, vel=0.35, gain=0.3, attack=0.4, release=2.5)


def sachverhalte(g, t0, t1):
    """2: семь предметов; конфигурация меняется ровно на один предмет за шаг"""
    t = g.motto(2, t0 + 0.4)
    flips = [0, 3, 5, 1, 6, 2, 4, 0, 5, 3, 6, 1, 2]  # путь по 7-мерному кубу (код Грея): соседи различаются в 1 бите
    start = t + 0.4
    step = (t1 - 1.5 - start) / len(flips)
    on = {}
    rng = random.Random(2027)
    for k, b in enumerate(flips):
        ts = start + k * step
        if b in on:
            t_in = on.pop(b)
            inst, m = OBJECTS[b]
            sachverhalt(g, inst, m, t_in, ts - t_in, b, rng)
        else:
            on[b] = ts
    for b, t_in in on.items():
        inst, m = OBJECTS[b]
        sachverhalt(g, inst, m, t_in, t1 + 0.6 - t_in, b, rng)
    # каждое изменение отмечено лёгким ударом арфы — тем самым предметом, что вошёл или вышел
    for k, b in enumerate(flips):
        g.n("harp", OBJECTS[b][1] + (12 if OBJECTS[b][1] < 50 else 0), start + k * step, 2.0, vel=0.35, gain=0.35,
            pan=-0.5 + b / 6, release=1.5)


def sachverhalt(g, inst, m, t, d, b, rng):
    if d <= 0.5:
        return
    gain = {"cb_sus": 0.45, "vc_sus": 0.4, "vla_sus": 0.38, "hn_sus": 0.32, "vln_sus": 0.32, "fl_sus": 0.32,
            "vln_harm": 0.3}[inst]
    g.n(inst, m, t, d, vel=0.32 + 0.08 * rng.random(), gain=gain, attack=1.2, release=1.4, pan=-0.6 + 0.2 * b)


def bild(g, t0, t1):
    """3: факт и его картины — мензуральный канон"""
    t = g.motto(3, t0 + 0.4)
    fact = [(50, 1), (53, 0.5), (57, 0.5), (55, 1), (60, 1.5), (59, 0.5), (53, 1), (52, 1), (50, 2)]  # 9 долей
    L = sum(b for _, b in fact) * BEAT

    def play(inst, tt, f, scale_t=1.0, transp=0, invert=None, **kw):
        for m, b in fact:
            mm = (2 * invert - m) if invert is not None else m
            d = b * BEAT * scale_t
            g.n(inst, mm + transp, tt, d * 0.95, **kw)
            tt += d
        return tt

    s = t + 0.6
    pedal = dict(vel=0.22, gain=0.32, attack=3.0, release=3.0)
    g.n("cb_sus", 38, s, t1 - s - 1.0, **pedal)
    # факт
    for k in range(7):
        play("bsn_sus", s + k * L, None, vel=0.5, gain=0.55, attack=0.05, release=0.6, pan=0.0)
    # картина 1: ускорение ×2, двумя октавами выше
    for k in range(2, 14):
        play("celesta", s + L + k * L / 2 - L, None, scale_t=0.5, transp=24, vel=0.4, gain=0.42, release=0.8,
             pan=0.45)
    # картина 2: обращение (дорийский лад симметричен относительно D — форма сохраняется)
    for k in range(2, 7):
        play("harp", s + k * L + L / 4, None, invert=62, vel=0.45, gain=0.45, release=1.2, pan=-0.45)
    # картина 3: растяжение ×2, флажолеты
    for k in (3, 5):
        play("vln_harm", s + k * L, None, scale_t=2.0, transp=19, vel=0.35, gain=0.35, attack=0.6, release=1.5,
             pan=0.2)
    # итог: факта больше нет — остаётся картина (обращение, медленно, в флажолетах и арфе)
    end_ = s + 7 * L + 0.3
    sc = max(0.5, (t1 - 0.6 - end_) / L)
    play("harp", end_, None, scale_t=sc, invert=62, vel=0.35, gain=0.4, release=1.6, pan=-0.3)
    play("vln_harm", end_, None, scale_t=sc, invert=62, transp=12, vel=0.25, gain=0.25, attack=0.3, release=1.5,
         pan=0.3)


def satz(g, t0, t1):
    """4: одна фраза — один смысл; истинна или ложна относительно бурдона"""
    t = g.motto(4, t0 + 0.4)
    s = t + 0.5
    g.n("org_quiet", 50, t0 + 0.2, t1 - t0 - 0.5, vel=0.45, gain=0.4, attack=3.0, release=2.5)
    g.n("org_quiet", 38, t0 + 2.0, t1 - t0 - 2.5, vel=0.45, gain=0.38, attack=4.0, release=2.5)
    phrase = [(69, 1), (71, 0.5), (73, 0.5), (74, 1.5), (None, 0.5), (76, 1), (74, 0.5), (71, 0.5), (73, 1)]
    # конец: D — истинно (W); E♭ / G♯ — ложно (F); последняя — без конца
    plan = [("ob_sus", 0, "W"), ("eh_sus", -12, "Fes"), ("tpt_mute", -12, "W"), ("fl_sus", 0, "Fgis"),
            ("hn_sus", -24, "Fes"), ("ob_sus", 0, "W"), ("eh_sus", -12, None)]
    span = (t1 - 1.5 - s) / len(plan)
    for k, (inst, tr, end) in enumerate(plan):
        tt = s + k * span
        kw = dict(vel=0.5, gain={"ob_sus": 0.45, "eh_sus": 0.5, "tpt_mute": 0.45, "fl_sus": 0.45,
                                 "hn_sus": 0.45}[inst], attack=0.06, release=0.6, pan=(-0.3, 0.3)[k % 2])
        for m, b in phrase:
            d = b * BEAT
            if m is not None:
                g.n(inst, m + tr, tt, d * 0.94, **kw)
            tt += d
        if end is None:  # последняя фраза повисает на ми — без ответа
            g.n(inst, 76 + tr, tt, 3.0, **dict(kw, release=0.3))
            continue
        g.n(inst, {"W": 74, "Fes": 75, "Fgis": 68}[end] + tr, tt, 2.2, **dict(kw, release=1.0))
        if end == "W":  # действительность «отвечает»: тот же звук в струнных
            g.p.chord("vla_sus", [62, 66, 69], tt + 0.05, 2.4, vel=0.3, gain=0.3, attack=0.5, release=1.5)
            g.n("vc_sus", 50, tt + 0.05, 2.4, vel=0.3, gain=0.35, attack=0.5, release=1.5)


def wahrheit(g, t0, t_coda, t1):
    """5: таблица истинности; 5.6 — сужение в унисон"""
    g.motto(5, t0 + 0.4)
    bar0 = t_coda - 16 * 4 * BEAT
    for f, func in enumerate(FUNCS):
        tb = bar0 + f * 4 * BEAT
        g.p.mark(tb, f"{func} {NAMES[func]}")
        for r, (p, q) in enumerate(ROWS):
            tt = tb + r * BEAT
            if p:
                g.n("cb_pizz", 38, tt, 0.5, vel=0.7, gain=0.55, pan=-0.35)
                g.n("vc_pizz", 50, tt, 0.5, vel=0.6, gain=0.45, pan=-0.3)
            if q:
                g.n("xylo", 81, tt + 0.002, 0.4, vel=0.5, gain=0.3, pan=0.35)
            if func[r] == "W":
                v = 0.62 + 0.15 * f / 15
                g.p.chord("tbn_stac", [50, 57], tt + 0.004, 0.32, vel=v, gain=0.4, pan=0.0, spread=0.004)
                g.p.chord("hn_stac", [62, 66], tt + 0.004, 0.32, vel=v, gain=0.38, pan=0.1, spread=0.004)
                g.p.chord("tpt_stac", [69, 74], tt + 0.004, 0.3, vel=v, gain=0.17, pan=0.15, spread=0.004)
    # тихий счёт тактов: маримба на первой доле — только чтобы слышать «строки»
    for f in range(16):
        g.n("marimba", 74, bar0 + f * 4 * BEAT, 0.4, vel=0.22, gain=0.22, pan=0.5)
    # 5.6: Die Grenzen meiner Sprache — поле (квинтовая цепь) стягивается в унисон D4
    lanes = [("cb_sus", 38), ("vc_sus", 45), ("vla_sus", 52), ("vla_sus", 59), ("vln_sus", 66), ("vln_sus", 73),
             ("vln_harm", 80)]
    d = t1 - t_coda - 0.6
    for j, (inst, m) in enumerate(lanes):
        tgt = 62 if inst not in ("cb_sus",) else 50
        if inst == "vln_harm":
            tgt = 74
        g.n(inst, m, t_coda + 0.05 * j, d, vel=0.42, gain=0.36, attack=0.8, release=1.6, bend=tgt - m,
            pan=-0.6 + 0.2 * j)


def form(g, t0, t_out, t_myst, t_ladder, t_cut):
    """6: [p̄, ξ̄, N(ξ̄)] — отрицание как дополнение; вне мира; мистическое; лестница"""
    t = g.motto(6, t0 + 0.4)
    # формула: три удара — p̄, ξ̄, N(ξ̄)
    fifths = [2, 9, 4, 11, 6, 1, 8, 3, 10, 5, 0, 7]  # D A E B F♯ C♯ | G♯ D♯ A♯ F C G
    hits = [[2], [2, 9, 4], [8, 3, 10, 5, 0, 7]]
    for k, pcs in enumerate(hits):
        tt = t + 0.3 + k * 1.1 * 1.0
        voiced = [38 + ((pc - 2) % 12) + 12 * (i % 3) for i, pc in enumerate(pcs)]
        g.n("org_loud", 26, tt, 0.9, vel=0.6, gain=0.3, release=1.2)
        g.p.chord("org_quiet", voiced, tt, 0.8, vel=0.6, gain=0.35, release=1.0, spread=0.0)
        g.n("timp", 38, tt, 1.5, vel=0.55 + 0.1 * k, gain=0.5)
    s = t + 4.2
    span = (t_out - 1.2 - s) / 6
    for k in range(1, 7):
        x = (k - 1) / 5
        tk = s + (k - 1) * span
        xi, neg = fifths[:k], fifths[k:]
        dx, dn = span * 0.38, span * 0.62
        vel_x, vel_n = 0.35 + 0.35 * x, 0.4 + 0.45 * x
        # ξ: хор и деревянные — тесно, в середине
        xv = sorted(60 + ((pc - 2) % 12) for pc in xi)
        g.p.chord("choir", xv, tk, dx + 0.4, vel=vel_x, gain=0.45, attack=0.25, release=0.6)
        for m in xv:
            g.n("cl_sus" if m < 70 else "fl_sus", m + (0 if m < 70 else 0), tk, dx + 0.3, vel=vel_x, gain=0.28,
                attack=0.15, release=0.5)
        # N(ξ): дополнение — разложено по всему регистру: медь, струнные, орган
        tn = tk + dx
        for i, pc in enumerate(neg):
            m = 36 + ((pc - 2) % 12) + 12 * (i % 4) + 2
            m = max(38, m)
            inst = ("tbn_sus" if m < 55 else "hn_sus") if i % 2 == 0 else ("vc_sus" if m < 55 else "vln_sus")
            if inst == "hn_sus" and m > 74:
                inst = "tpt_sus"
            g.n(inst, m, tn + 0.01 * i, dn - 0.1, vel=vel_n, gain=0.32, attack=0.12, release=0.5, pan=-0.6 + 0.1 * i)
            g.n("org_quiet", m, tn, dn - 0.1, vel=vel_n, gain=0.18 + 0.12 * x, attack=0.1, release=0.6)
        g.n("cb_sus", 38 if k % 2 else 37, tn, dn - 0.1, vel=vel_n, gain=0.45, attack=0.2, release=0.6)
        if k == 6:  # 6+6 — равновесие, кульминация
            g.n("org_loud", 26, tn, dn - 0.1, vel=0.8, gain=0.35, release=0.8)
            g.n("timp_roll", 38, tn, dn - 0.2, vel=0.75, gain=0.45, release=0.4)
            g.n("crotales", 98, tn, 3.0, vel=0.6, gain=0.35)
    # 6.41: вне мира — четверть тона над D5, одна флейта и флажолеты, в пустоте
    g.n("afl_sus", 74, t_out, t_myst - t_out + 0.8, vel=0.38, gain=0.5, attack=1.2, release=1.5, detune=0.5,
        art="+¼")
    g.n("vln_harm", 86, t_out + 1.5, t_myst - t_out - 2.0, vel=0.25, gain=0.25, attack=2.0, release=1.5, detune=0.5,
        art="+¼")
    # 6.44: мистическое — не как, а что: ре мажор, тихо, без движения
    dm = t_ladder - t_myst
    g.p.chord("choir", [62, 66, 69, 74], t_myst, dm + 1.0, vel=0.28, gain=0.4, attack=1.2, release=2.5)
    g.p.chord("vln_sus", [74, 78, 81], t_myst + 0.5, dm + 0.5, vel=0.25, gain=0.28, attack=3.0, release=2.5)
    g.p.chord("vla_sus", [57, 62, 66], t_myst + 0.5, dm + 0.5, vel=0.25, gain=0.28, attack=3.0, release=2.5)
    g.n("vc_sus", 50, t_myst, dm + 1.0, vel=0.28, gain=0.32, attack=3.0, release=2.5)
    g.n("cb_sus", 38, t_myst, dm + 1.0, vel=0.28, gain=0.36, attack=3.0, release=2.5)
    for j, (m, dt) in enumerate([(86, 1.5), (81, 4.0), (90, 6.5), (78, 8.6)]):
        g.n("celesta", m, t_myst + dt, 2.5, vel=0.3, gain=0.42, release=2.0, pan=0.4 - 0.25 * j)
    # 6.54: лестница — ступень за ступенью вверх, всё быстрее; бесконечный подъём органа; обрыв
    insts = ["cb_sus", "vc_sus", "bsn_sus", "vla_sus", "cl_sus", "hn_sus", "ob_sus", "vln_sus", "tpt_sus", "fl_sus",
             "vln_sus", "fl_sus", "vln_sus", "picc_sus"]
    steps = [38 + o * 12 + iv for o in range(5) for iv in IONIAN]
    tt, d = t_ladder, 1.2
    i = 0
    while tt < t_cut - 0.1 and i < len(steps):
        m = steps[i]
        inst = insts[min(len(insts) - 1, i * len(insts) // len(steps))]
        lo = {"cb_sus": 28, "vc_sus": 36, "bsn_sus": 34, "vla_sus": 48, "cl_sus": 50, "hn_sus": 34, "ob_sus": 58,
              "vln_sus": 55, "tpt_sus": 54, "fl_sus": 60, "picc_sus": 74}[inst]
        hi = {"cb_sus": 60, "vc_sus": 76, "bsn_sus": 72, "vla_sus": 84, "cl_sus": 88, "hn_sus": 74, "ob_sus": 88,
              "vln_sus": 100, "tpt_sus": 82, "fl_sus": 96, "picc_sus": 100}[inst]
        if not lo <= m <= hi:
            inst = "vln_sus" if m >= 55 else "vc_sus"
        x = (tt - t_ladder) / (t_cut - t_ladder)
        g.n(inst, m, tt, min(t_cut - tt, d * 2.5), vel=0.35 + 0.45 * x,
            gain=0.06 if inst == "picc_sus" else 0.38, attack=0.05, release=0.08, pan=-0.6 + 1.2 * (i % 7) / 6)
        tt += d
        d = max(0.22, d * 0.9)
        i += 1
    g.c.shepard(t_ladder, t_cut - 1.2, up=True, gain=0.3, period=6.0)
    g.n("timp_roll", 38, t_cut - 6.0, 5.95, vel=0.5, gain=0.4, release=0.05)


def schweigen(g, t0, t_sil):
    """7: «Wovon…» — и молчание"""
    t = g.motto(7, t0 + 0.6, vel=0.42, gain=0.5)
    g.n("vln_harm", 86, t + 0.1, t_sil - t - 1.5, vel=0.2, gain=0.22, attack=1.5, release=2.5)


def build(ctx):
    g = T(ctx)
    t = g.t
    welt(g, 0.0, t("2 Sachverhalte"))
    sachverhalte(g, t("2 Sachverhalte"), t("3 Das Bild"))
    bild(g, t("3 Das Bild"), t("4 Der Satz"))
    satz(g, t("4 Der Satz"), t("5 Wahrheitsfunktion"))
    wahrheit(g, t("5 Wahrheitsfunktion"), t("5.6 Grenzen"), t("6 Die allgemeine Form"))
    form(g, t("6 Die allgemeine Form"), t("6.41 außerhalb"), t("6.44 Das Mystische"), t("6.54 Leiter"),
         t("Leiter weg"))
    schweigen(g, t("7 Schweigen"), t("Schweigen"))
    # измерено `--parts` на эскизе (LUFS каждой партии отдельно): кларнет −23, контрабасы −52, альты −48,
    # скрипки −45, челеста −41 — поднять до «пола» и «красок» (SKILL §5)
    # второе измерение (вся пьеса): гобой −35, англ. рожок −34, тромбон −48, ксилофон (q!) −48, орган −34
    g.p.balance({"Basses": +16, "Violas": +12, "Violins": +11, "Celesta": +11, "Cellos": +8, "Horn": +6,
                 "Flute": +6, "Marimba": +2, "Oboe": +10, "English horn": +9, "Trombone": +14, "Xylophone": +16,
                 "Crotales": +10, "Timpani": +8, "Organ": +6, "Alto flute": +5, "Choir": -4, "Piccolo": -4})
    return g.p
