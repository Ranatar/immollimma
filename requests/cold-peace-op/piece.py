#!/usr/bin/env python3
"""«Холодный мир» — опенинг аниме, TV-size 1:30 (152 уд/мин, 57 тактов). Раскадровка — storyboard.md.

Форма песни без голоса: интро → заставка → куплет A (одна тема мира в четырёх обликах — по лидерам) →
предприпев B (космодром: четыре мотива вступают по очереди, как четыре флага) → припев (D мажор, «королевский
путь» IV–V–iii–vi) → война: модуляция на тон (E мажор), кадансы ♭VI–♭VII–I → крушение → кода (шкатулка
кончает завод, E минор) → финальный удар на титр.

Сквозное: детская шкатулка (тема Рейха) — первый и последний звук опенинга; у Рейха фраза каждый раз
обрывается, не дойдя до тоники (правитель исчезает в 16 лет).

    python3 -m kit run requests/cold-peace-op/piece.py --sketch --parts
    python3 -m kit run requests/cold-peace-op/piece.py --parts
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from kit.devices import Composer  # noqa: E402
from kit.events import Piece  # noqa: E402

BPM = 152
SPB = 60.0 / BPM
B0 = 59  # B3 — тоника куплета

AEOL = [0, 2, 3, 5, 7, 8, 10]
MIXO = [0, 2, 4, 5, 7, 9, 10]
HARM = [0, 2, 3, 5, 7, 8, 11]
MAJ = [0, 2, 4, 5, 7, 9, 11]
PHRYG = [0, 1, 3, 5, 7, 8, 10]

# тема мира (куплет, 4 такта): (доля, длительность, ступень)
THEME = [(0, .5, 4), (.5, .5, 4), (1, .5, 3), (1.5, 1, 4), (2.5, 1.5, 2),
         (4, .5, 1), (4.5, .5, 2), (5, .5, 4), (5.5, 1, 7), (6.5, 1.5, 6),
         (8, .5, 5), (8.5, .5, 4), (9, .5, 2), (9.5, 1, 4), (10.5, 1.5, 3),
         (12, .5, 2), (12.5, .5, 1), (13, 3, 0)]
# японский облик — вручную в ладу мияко-бусими на B (B C E F# G): тот же контур
JAPAN = [78, 78, 76, 78, 76, 72, 76, 78, 83, 79, 79, 78, 76, 78, 76, 76, 72, 71]

# припев (D мажор, ступени от D4): 8 тактов
CHORUS = [(0, 1, 5), (1, .5, 4), (1.5, .5, 5), (2, 1, 7), (3, 1, 8),
          (4, 1.5, 6), (5.5, .5, 5), (6, 1, 4), (7, 1, 1),
          (8, .5, 2), (8.5, .5, 4), (9, 1, 6), (10, 1.5, 8), (11.5, .5, 7),
          (12, 1, 7), (13, .5, 6), (13.5, 2.5, 5),
          (16, .5, 5), (16.5, .5, 7), (17, 1, 8), (18, 1, 9), (19, .5, 8), (19.5, .5, 7),
          (20, 1, 6), (21, 1, 8), (22, 2, 11),
          (24, 1.5, 9), (25.5, .5, 8), (26, 2, 7),
          (28, 1, 7), (30, .5, 4), (30.5, .5, 5), (31, .5, 6), (31.5, .5, 7)]


def deg(d, mode, tonic):
    o, k = divmod(d, 7)
    return tonic + 12 * o + mode[k]


class Op:
    def __init__(self, ctx):
        self.p = Piece("Холодный мир — опенинг", bpm=BPM, meter=(4, 4), key="B minor", seed=1944)
        self.p.meta["subtitle"] = "TV-size, 1:30"
        self.p.meta["sends"] = {"strings": 0.3, "brass": 0.25, "winds": 0.3, "perc": 0.2, "choir": 0.45, "organ": 0.4,
                                "harp": 0.4, "keys": 0.3}
        self.c = Composer(self.p, lib="vsco", seed=152)
        for cue in ctx.cues["cues"]:
            if cue["kind"] in ("section", "hit"):
                tq = round(cue["t"] / SPB * 4) / 4 * SPB  # на сетку долей (иначе MusicXML ломается)
                self.p.mark(tq, cue["label"][:24])

    @staticmethod
    def t(bar, beat=0.0):
        return (bar * 4 + beat) * SPB

    # уровень по разделам (множитель): куплет тише, припев — подъём, война — ещё выше
    LEVELS = [(0, 1.0), (6, 0.7), (22, 0.8), (30, 1.0), (38, 1.05), (40, 1.12), (50, 0.9), (56, 1.15)]
    full = False  # удар-заставка — без понижения

    def level(self, bar, beat=0.0):
        if self.full:
            return 1.0
        x = bar + beat / 4
        g = 1.0
        for b, v in self.LEVELS:
            if x >= b - 1e-9:
                g = v
        return g

    def n(self, inst, m, bar, beat, beats, **kw):
        kw.setdefault("release", 0.25)
        kw["gain"] = kw.get("gain", 1.0) * self.level(bar, beat)
        return self.p.note(inst, m, self.t(bar, beat), beats * SPB, **kw)

    def ch(self, inst, ms, bar, beat, beats, **kw):
        for m in ms:
            self.n(inst, m, bar, beat, beats, **kw)

    def line(self, inst, notes, bar, *, legato=0.92, **kw):
        """notes: [(доля от начала такта bar, длительность, midi)]"""
        for b, d, m in notes:
            if m is not None:
                self.n(inst, m, bar, b, d * legato, **kw)

    def drum(self, kind, bar, beat, gain=0.3, pan=0.0, **kw):
        return self.c.fx(kind, self.t(bar, beat), gain=gain * self.level(bar, beat), pan=pan, bus="perc", **kw)

    def roll(self, kind, bar0, bar1, g0=0.05, g1=0.35, step=0.125):
        b = bar0 * 4
        while b < bar1 * 4 - 1e-9:
            x = (b - bar0 * 4) / ((bar1 - bar0) * 4)
            self.drum(kind, 0, b, gain=g0 + (g1 - g0) * x ** 1.5, pan=0.1)
            b += step


def theme(mode, tonic, oct_=0):
    return [(b, d, deg(s, mode, tonic) + 12 * oct_) for b, d, s in THEME]


def chorus_mel(tonic):
    return [(b, d, deg(s, MAJ, tonic)) for b, d, s in CHORUS]


# ------------------------------------------------------------------------------------------------------------
def intro(o):
    """0:00 туман 1944 и шкатулка → коронация → взлёт к звёздам"""
    # химический туман: низкий кластер, расстроенный, и дыхание противогазов
    o.n("vc_sus", 47, 0, 0, 8, vel=0.35, gain=0.35, attack=1.5, release=1.0, detune=0.15)
    o.n("vc_sus", 48, 0, 0.5, 7.5, vel=0.32, gain=0.3, attack=1.5, release=1.0, detune=-0.2)
    o.n("cb_sus", 35, 0, 0, 8, vel=0.35, gain=0.4, attack=1.5, release=1.0)
    o.n("vla_trem", 61, 0, 1, 7, vel=0.25, gain=0.18, attack=1.2, release=0.8)
    o.n("vla_trem", 62, 0, 1.5, 6.5, vel=0.25, gain=0.16, attack=1.2, release=0.8, detune=0.25)
    o.c.breath(o.t(0, 0.5), 2.6, gain=0.18)
    o.c.breath(o.t(1, 1.0), 2.6, gain=0.15)
    # шкатулка: тема Рейха (гармонический минор), заводная, чуть плывёт
    tune = [m + 12 for _, _, m in theme(HARM, 71)[:10]]
    o.c.music_box(o.t(0, 0.5), tune, step=0.36, slow=0.01, flat=0.012, inst="celesta", double=None, gain=0.42)
    # коронация: удар «тайко», открытая квинта, флейта-сякухати с подтяжкой, кото
    for b in (2, 3):
        o.drum("bd", b, 0, gain=0.35)
        o.n("timp", 40, b, 0, 1.5, vel=0.6, gain=0.45)
    o.drum("gong_roll", 2, 0, gain=0.12)
    o.ch("vc_sus", [47, 54], 2, 0, 8, vel=0.45, gain=0.38, attack=0.6, release=0.8)
    o.n("cb_sus", 35, 2, 0, 8, vel=0.45, gain=0.42, attack=0.6, release=0.8)
    o.n("fl_sus", 71, 2, 1, 3, vel=0.5, gain=0.45, attack=0.3, bend=1.0, release=0.4)       # B4 → C5
    o.n("fl_sus", 76, 3, 0.5, 1.5, vel=0.5, gain=0.45, attack=0.1, release=0.4)
    o.n("fl_sus", 72, 3, 2, 2, vel=0.5, gain=0.42, attack=0.1, bend=-1.0, release=0.5)        # C5 → B4
    for j, m in enumerate([47, 54, 59, 60, 64, 66, 71]):
        o.n("harp", m, 2, 0.25 + 0.12 * j, 3, vel=0.5, gain=0.45, release=1.5, pan=0.3)
    # взлёт: дробь малого барабана, литавровое тремоло, скрипки ползут вверх, бесконечный подъём органа
    o.roll("snare_soft", 4, 5, 0.03, 0.12)
    o.roll("snare", 5, 6, 0.12, 0.38)
    o.n("timp_roll", 42, 4, 0, 8, vel=0.4, gain=0.25, attack=1.5, release=0.1)
    o.ch("vln_sus", [66, 71], 4, 0, 8, vel=0.5, gain=0.35, attack=1.0, bend=12.0, release=0.1)
    o.ch("vla_sus", [59, 62], 4, 0, 8, vel=0.5, gain=0.3, attack=1.0, bend=12.0, release=0.1)
    o.c.shepard(o.t(4), o.t(6) - 0.2, up=True, gain=0.22, period=2.5)


def title_hit(o, bar):
    """удар-заставка: тутти си минор"""
    o.full = True
    o.ch("tbn_stac", [47, 54, 59], bar, 0, 1, vel=0.85, gain=0.5)
    o.ch("hn_stac", [59, 62, 66], bar, 0, 1, vel=0.85, gain=0.45)
    o.ch("tpt_stac", [71, 74, 78], bar, 0, 1, vel=0.85, gain=0.4)
    o.ch("vln_sus", [74, 78, 83], bar, 0, 3, vel=0.7, gain=0.4, release=0.6)
    o.n("cb_sus", 35, bar, 0, 3, vel=0.8, gain=0.5, release=0.5)
    o.n("timp", 47, bar, 0, 2, vel=0.9, gain=0.55)
    o.drum("clash", bar, 0, gain=0.35)
    o.drum("bd", bar, 0, gain=0.5)
    o.full = False


def bass8(o, bar, root, beats=4, insts=(("cb_pizz", 0.5), ("vc_spic", 0.42)), pattern=(0, 0, 12, 0, 0, 12, 0, 7),
          vel=0.62):
    for k in range(int(beats * 2)):
        for inst, g in insts:
            m = root + pattern[k % len(pattern)]
            if inst.startswith("cb"):
                m = root
            o.n(inst, m, bar, k * 0.5, 0.45, vel=vel + (0.1 if k % 2 == 0 else 0), gain=g, release=0.15)


def rock(o, bar, *, half=False, fill=False, gain=1.0):
    """«ударная установка» из оркестровых: большой барабан + малый + тарелки"""
    if half:
        o.drum("bd", bar, 0, gain=0.42 * gain)
        o.drum("snare", bar, 2, gain=0.25 * gain)
        return
    for b in (0, 1.5, 2.5):
        o.drum("bd", bar, b, gain=0.42 * gain)
    for b in (1, 3):
        o.drum("snare", bar, b, gain=0.3 * gain)
    for b in (0.5, 1.5, 2.5, 3.5):
        o.drum("snare_soft", bar, b, gain=0.07 * gain)
    if fill:
        for b in (3, 3.25, 3.5, 3.75):
            o.drum("snare", bar, b, gain=0.22 * gain)


def verse_ussr(o, bar):
    """СССР: протяжный эолийский облик, валторны с виолончелью, колокола, тяжёлый полутемп"""
    mel = theme(AEOL, B0)  # B3…
    o.line("hn_sus", mel, bar, vel=0.65, gain=0.55, attack=0.05)
    o.line("vc_sus", mel, bar, vel=0.55, gain=0.35, attack=0.05)
    # подголосок терцией ниже (протяжная песня)
    sub = [(b, d, deg(s - 2, AEOL, B0)) for b, d, s in THEME]
    o.line("bsn_sus", sub, bar, vel=0.5, gain=0.4, attack=0.05)
    chords = [(47, [54, 59, 62]), (43, [55, 59, 62]), (40, [55, 59, 64]), (47, [54, 59, 62])]
    for k, (r, up) in enumerate(chords):
        o.n("cb_sus", r - 12, bar + k, 0, 4, vel=0.6, gain=0.45, release=0.3)
        o.ch("tbn_sus", up[:2], bar + k, 0, 3.8, vel=0.45, gain=0.3, release=0.3)
        o.ch("vla_sus", [x + 12 for x in up], bar + k, 0, 3.8, vel=0.4, gain=0.25, release=0.3)
        o.n("tubular", 71 if k % 2 == 0 else 66, bar + k, 0, 3, vel=0.55, gain=0.4, release=2.0)
        o.n("timp", r if r >= 40 else r + 12, bar + k, 0, 1, vel=0.6, gain=0.35)
        rock(o, bar + k, half=True, gain=0.9)
    o.drum("clash", bar, 0, gain=0.2)


def verse_pan(o, bar):
    """Панамерика: миксолидийская фанфара, синкопы, трубы и ксилофон, I–♭VII–IV–I"""
    mel = theme(MIXO, B0 + 12)  # B4…
    o.line("tpt_sus", mel, bar, vel=0.7, gain=0.5, attack=0.03, legato=0.85)
    o.line("xylo", mel, bar, vel=0.55, gain=0.22, legato=0.5)
    roots = [47, 45, 40, 47]
    triads = [[63, 66, 71], [61, 64, 69], [59, 64, 68], [63, 66, 71]]
    for k in range(4):
        bass8(o, bar + k, roots[k] if roots[k] >= 40 else roots[k] + 12)
        for b in (0.5, 1.5, 2.5, 3.5):  # синкопированные стаккато медных
            o.ch("hn_stac", [x - 12 for x in triads[k]], bar + k, b, 0.4, vel=0.6, gain=0.28)
        o.ch("vla_spic", triads[k], bar + k, 2.5, 0.4, vel=0.6, gain=0.3)
        rock(o, bar + k, fill=(k == 3))
    o.drum("clash", bar, 0, gain=0.3)


def verse_japan(o, bar):
    """Япония: мияко-бусими, флейта с подтяжками, кото-арфа, «тайко» — большой барабан и литавры"""
    for (b, d, _), m in zip(THEME, JAPAN):
        bend = 0.0
        mm = m
        if d >= 1.5:
            mm, bend = m - 1, 1.0  # мери → кари: подъезд снизу
        o.n("fl_sus", mm, bar, b, d * 0.95, vel=0.6, gain=0.5, attack=0.04, bend=bend, release=0.2)
        o.n("vln_sus", m - 12, bar, b, d * 0.9, vel=0.45, gain=0.2, attack=0.03)
    fifths = [(35, 42), (36, 43), (40, 47), (35, 42)]
    koto = [[59, 60, 64, 66], [60, 64, 67, 71], [64, 66, 67, 71], [59, 60, 64, 66]]
    for k in range(4):
        lo, hi = fifths[k]
        o.ch("cb_sus", [lo], bar + k, 0, 4, vel=0.65, gain=0.45, release=0.2)
        o.ch("vc_trem", [lo + 12, hi + 12], bar + k, 0, 4, vel=0.5, gain=0.3, release=0.2)
        o.ch("vln_trem", [hi + 24, lo + 36], bar + k, 0, 4, vel=0.4, gain=0.18, release=0.2)
        # тайко: ⓪ . ⓪ ⓪ | ③ ③ .
        for b, g in ((0, 0.55), (0.75, 0.3), (1.5, 0.45), (2, 0.35), (3, 0.5), (3.5, 0.4)):
            o.drum("bd", bar + k, b, gain=g * 0.85)
        for b in (0, 1.5, 3, 3.5):
            o.n("timp", lo + 12 if lo + 12 <= 49 else lo, bar + k, b, 0.5, vel=0.7, gain=0.4)
        for j in range(8):  # кото: шестнадцатые по звукам лада
            o.n("harp", koto[k][j % 4] + (12 if j >= 4 else 0), bar + k, j * 0.5, 0.8, vel=0.5, gain=0.35,
                release=0.8, pan=0.35)
        o.drum("woodblocks", bar + k, 3.75, gain=0.12, pan=-0.3)


def verse_reich(o, bar):
    """Рейх: шкатулка (челеста + колокольчики), хор мальчиков, орган; фраза обрывается и улетает вверх"""
    mel = theme(HARM, B0 + 24)  # B5…
    cut = 13 * 1.0  # в четвёртом такте: «D C#» — и обрыв (доли 12–13)
    for b, d, m in mel:
        if b >= cut:
            continue
        o.n("celesta", m, bar, b, d, vel=0.55, gain=0.5, release=0.8)
        o.n("glock", m + 12 if m + 12 <= 108 else m, bar, b, d, vel=0.4, gain=0.22, release=0.6)
    chords = [[59, 62, 66], [61, 66, 70], [59, 64, 67], [61, 64, 66, 70]]
    for k in range(4):
        dur = 4 if k < 3 else 2
        o.ch("org_quiet", [x - 12 for x in chords[k]], bar + k, 0, dur, vel=0.5, gain=0.35, release=0.1)
        o.ch("choir", chords[k], bar + k, 0, dur, vel=0.45, gain=0.4, attack=0.3, release=0.15)
        for j in range(int(dur * 2)):
            o.n("vln_pizz", chords[k][j % len(chords[k])] + 12, bar + k, j * 0.5, 0.4, vel=0.45, gain=0.25)
        root = [35, 42, 40, 42][k]
        o.n("cb_pizz", root + 12, bar + k, 0, 1, vel=0.6, gain=0.45)
        o.n("cb_pizz", root + 12, bar + k, 2, 1, vel=0.55, gain=0.4) if dur == 4 else None
    # обрыв на доле 2 последнего такта: колокольчики уносятся вверх
    t_cut = o.t(bar + 3, 2)
    o.c.fx("glock_up", t_cut, gain=0.3, pan=0.2, bus="perc")
    for j, m in enumerate(range(71, 108, 3)):
        o.p.note("harp", m, t_cut + 0.035 * j, 0.6, vel=0.4, gain=0.25, release=0.8, pan=0.4)


def prechorus(o, bar):
    """B: космодром — спиккато шестнадцатыми, четыре мотива вступают по очереди (четыре флага)"""
    prog = [(43, [55, 59, 62]), (45, [57, 61, 64]), (42, [54, 57, 61]), (47, [54, 59, 62]),
            (43, [55, 59, 62]), (45, [57, 61, 64]), (46, [53, 58, 62]), (45, [55, 57, 61, 64])]
    for k, (r, tri) in enumerate(prog):
        b = bar + k
        bass8(o, b, r, insts=(("cb_pizz", 0.45), ("vc_spic", 0.4)), pattern=(0, 0, 0, 0, 0, 0, 0, 0), vel=0.55 + 0.03 * k)
        arp = sorted(tri + [x + 12 for x in tri])
        for j in range(16):
            o.n("vln_spic", arp[j % len(arp)] + 12 * (k >= 4), b, j * 0.25, 0.22, vel=0.45 + 0.04 * k, gain=0.28,
                release=0.08)
        o.drum("bd", b, 0, gain=0.35)
        o.drum("snare_soft", b, 2, gain=0.15)
    head = THEME[:10]
    # флаги: валторны (СССР), трубы (Панамерика), флейта (Япония), челеста + хор (Рейх)
    flags = [("hn_sus", MIXO, 55, 0.55), ("tpt_sus", PHRYG, 66, 0.45), ("fl_sus", MIXO, 79, 0.5),
             ("celesta", HARM, 79, 0.5)]
    for i, (inst, mode, tonic, g) in enumerate(flags):
        b = bar + 2 * i
        o.drum("clash" if i else "susp", b, 0, gain=0.12 + 0.05 * i)
        o.line(inst, [(x, d, deg(s, mode, tonic)) for x, d, s in head], b, vel=0.62, gain=g, attack=0.03)
        if inst == "celesta":
            o.ch("choir", [62, 65, 70], b, 0, 4, vel=0.5, gain=0.35, attack=0.4)
            o.ch("choir", [61, 64, 69], b + 1, 0, 4, vel=0.55, gain=0.38, attack=0.2)
        # после своего мотива «флаг» остаётся: долгий тон в гармонии
        for kk in range(2 * i + 2, 8):
            tri = prog[kk][1]
            m = tri[i % 3] + {0: 0, 1: 12, 2: 12, 3: 12}[i]
            if inst != "celesta":
                o.n(inst, m, bar + kk, 0, 4, vel=0.45, gain=g * 0.5, attack=0.2, release=0.2)
    # обратный отсчёт: дробь, подъём, вдох
    o.roll("snare_soft", bar + 6, bar + 7, 0.03, 0.12)
    o.roll("snare", bar + 7, bar + 8, 0.12, 0.42)
    o.c.shepard(o.t(bar + 4), o.t(bar + 8) - 0.15, up=True, gain=0.22, period=3.0)
    o.n("timp_roll", 45, bar + 6, 0, 8, vel=0.55, gain=0.35, attack=2.0, release=0.05)


def chorus(o, bar, tonic, war=False):
    """припев: тема у скрипок (8va) + валторн + хора; IV–V–iii–vi | IV–V–I–I (на войне: IV–V–iii–vi | ♭VI–♭VII–I)"""
    mel = chorus_mel(tonic)
    if war:  # последняя строка: ♭VI–♭VII → I
        mel = [x for x in mel if x[0] < 24] + [(24, 1.5, tonic + 15), (25.5, .5, tonic + 12), (26, 2, tonic + 8),
                                                (28, 1, tonic + 17), (29, 1, tonic + 14), (30, 1, tonic + 10),
                                                (31, 1, tonic + 14)]
    o.line("vln_sus", [(b, d, m + 12) for b, d, m in mel], bar, vel=0.75, gain=0.45, attack=0.03)
    o.line("hn_sus", [(b, d, m - 12) for b, d, m in mel], bar, vel=0.75, gain=0.5, attack=0.03)
    o.line("choir", mel, bar, vel=0.7, gain=0.45, attack=0.08, legato=0.97)
    if war:
        o.line("tbn_sus", [(b, d, m - 12) for b, d, m in mel], bar, vel=0.75, gain=0.35, attack=0.03)
        o.line("glock", [(b, d, m + 24) for b, d, m in mel if d >= 1], bar, vel=0.5, gain=0.15, legato=0.6)
    else:
        o.line("fl_sus", [(b, d, m + 12) for b, d, m in mel], bar, vel=0.6, gain=0.3, attack=0.03)
    s = tonic
    prog = [(s + 5, "M"), (s + 7, "M"), (s + 4, "m"), (s + 9, "m"), (s + 5, "M"), (s + 7, "M"),
            (s, "M"), (s, "M")]
    if war:
        prog[6:] = [(s + 8, "M"), (s + 10, "M")]
    for k, (r, q) in enumerate(prog):
        b = bar + k
        rr = r % 12 + 36 if r % 12 + 36 >= 40 else r % 12 + 48
        third = 4 if q == "M" else 3
        tri = [rr + 12, rr + 12 + third, rr + 19]
        bass8(o, b, rr, vel=0.68)
        if war:
            o.n("bsn_sus", rr, b, 0, 4, vel=0.6, gain=0.3)
        for x in (0.5, 1.5, 2.5, 3.5):  # «гитара»: восьмые аккорды спиккато на слабых долях
            o.ch("vla_spic", [m + 12 for m in tri[:2]], b, x, 0.35, vel=0.6, gain=0.25)
        o.ch("tbn_sus", [m for m in tri], b, 0, 3.8, vel=0.55, gain=0.22, release=0.2)
        o.n("timp", rr if rr <= 49 else rr - 12, b, 0, 1, vel=0.7, gain=0.35)
        rock(o, b, fill=(k == 7), gain=1.15 if war else 1.0)
        if k in (0, 4):
            o.drum("clash", b, 0, gain=0.32)
        # контрмелодия труб во второй половине: синкопированное арпеджио (фанфара)
        if k >= 4:
            for x, m in zip((0.5, 1, 1.5, 3), (tri[0] + 12, tri[1] + 12, tri[2] + 12, tri[1] + 12)):
                o.n("tpt_stac", m, b, x, 0.4, vel=0.65, gain=0.25)


def war_bridge(o, bar):
    """станция взрывается: удары меди, химическое облако (кластер, сползающий вниз), модуляция B7 → E"""
    o.drum("gong_hit", bar, 0, gain=0.4)
    o.drum("bd", bar, 0, gain=0.55)
    o.drum("clash", bar, 0, gain=0.35)
    o.n("timp", 47, bar, 0, 1, vel=0.9, gain=0.55)
    o.ch("tbn_stac", [47, 50, 54], bar, 0, 1, vel=0.9, gain=0.45)
    for j, m in enumerate([86, 85, 84, 83, 81, 80]):
        o.n("vln_sus", m, bar, 0.5, 6, vel=0.55, gain=0.2, attack=0.1, bend=-14.0, detune=0.1 * j, pan=-0.5 + 0.2 * j)
    for b, ch in ((1.5, [48, 52, 55]), (2.5, [48, 52, 55]), (3.5, [48, 52, 55]), (4, [47, 51, 54, 57]),
                  (5, [47, 51, 54, 57]), (5.5, [47, 51, 54, 57]), (6.5, [47, 51, 54, 57]), (7, [47, 51, 54, 57])):
        o.ch("hn_stac", [x + 12 for x in ch], bar, b, 0.45, vel=0.75, gain=0.35)
        o.ch("tbn_stac", ch, bar, b, 0.45, vel=0.75, gain=0.35)
        o.drum("snare", bar, b, gain=0.28)
    bass8(o, bar, 48, beats=4, pattern=(0,) * 8, vel=0.7)
    bass8(o, bar + 1, 47, beats=4, pattern=(0,) * 8, vel=0.75)
    o.roll("snare", bar + 1, bar + 2, 0.12, 0.4)
    o.n("timp_roll", 47, bar + 1, 0, 4, vel=0.6, gain=0.4, release=0.05)


def climax(o, bar):
    """четверо лицом к лицу: E мажор держится, хор в полный голос — и обрыв (крушение)"""
    top = [(0, 1, 76), (1, 1, 80), (2, 2, 83), (4, 4, 83)]
    o.line("vln_sus", [(b, d, m + 12) for b, d, m in top], bar, vel=0.85, gain=0.45, legato=0.98)
    o.line("hn_sus", [(b, d, m - 12) for b, d, m in top], bar, vel=0.85, gain=0.5, legato=0.98)
    o.ch("choir", [64, 68, 71, 76, 80], bar, 0, 7.9, vel=0.8, gain=0.4, attack=0.1, release=0.1)
    o.ch("tbn_sus", [52, 56, 59], bar, 0, 7.9, vel=0.75, gain=0.3, release=0.1)
    o.n("org_loud", 28, bar, 0, 7.9, vel=0.7, gain=0.3, release=0.1)
    o.n("cb_sus", 40, bar, 0, 7.9, vel=0.8, gain=0.5, release=0.1)
    o.n("timp_roll", 40, bar, 0, 7.9, vel=0.7, gain=0.45, release=0.05)
    o.roll("snare", bar + 1, bar + 2, 0.15, 0.45)
    o.drum("clash", bar, 0, gain=0.4)
    for k in range(2):
        o.drum("bd", bar + k, 0, gain=0.5)


def coda(o, bar, final_bar):
    """крушение → тишина → шкатулка кончает завод (E минор) → удар на титр"""
    o.c.fx("glass", o.t(bar, 0), gain=0.25, pan=0.0, bus="fx")
    o.drum("tamtam", bar, 0, gain=0.25)
    tune = [m + 5 for _, _, m in theme(HARM, 71 + 12)[:14]]  # E минор, гармонический
    o.c.music_box(o.t(bar, 1.0), tune, step=0.42, slow=0.03, flat=0.03, inst="celesta", double=None, gain=0.45)
    for b in (bar, bar + 2, bar + 4):
        o.n("tubular", 64, b, 0.5, 4, vel=0.45, gain=0.3, release=2.5)
    o.ch("vln_harm", [76, 83], bar, 0.5, 18, vel=0.3, gain=0.2, attack=2.0, release=0.5)
    o.n("cb_sus", 40, bar + 1, 0, 16, vel=0.3, gain=0.35, attack=2.0, release=0.3)
    o.n("vc_sus", 47, bar + 2, 0, 12, vel=0.3, gain=0.3, attack=2.0, release=0.3)
    # подъём к удару: дробь и литавры
    o.roll("snare_soft", final_bar - 1, final_bar, 0.02, 0.2)
    o.n("timp_roll", 40, final_bar - 1, 0, 3.95, vel=0.5, gain=0.4, attack=1.5, release=0.05)
    o.c.swell(o.t(final_bar), inst="org_quiet", midi_=64, dur=2.4, gain=0.3)
    # удар на титр: тутти E минор + гонг, звенит до конца
    fb = final_bar
    o.ch("tbn_stac", [40, 47, 52], fb, 0, 1, vel=0.95, gain=0.5)
    o.ch("tbn_sus", [52, 55, 59], fb, 0, 3, vel=0.85, gain=0.35, release=0.5)
    o.ch("hn_sus", [59, 64, 67], fb, 0, 3, vel=0.85, gain=0.45, release=0.5)
    o.ch("tpt_stac", [71, 76, 79], fb, 0, 1, vel=0.95, gain=0.4)
    o.ch("vln_sus", [76, 79, 83, 88], fb, 0, 3, vel=0.8, gain=0.4, release=0.5)
    o.ch("choir", [52, 59, 64, 67, 71], fb, 0, 3, vel=0.8, gain=0.4, release=0.5)
    o.n("cb_sus", 28, fb, 0, 3, vel=0.9, gain=0.55, release=0.5)
    o.n("org_loud", 28, fb, 0, 3, vel=0.8, gain=0.35, release=0.5)
    o.n("timp", 40, fb, 0, 2, vel=0.95, gain=0.6)
    o.drum("gong_hit", fb, 0, gain=0.45, dur=1.5, fade=0.4)
    o.drum("clash", fb, 0, gain=0.4, dur=1.4, fade=0.4)
    o.drum("bd", fb, 0, gain=0.55)
    o.n("tubular", 64, fb, 0, 3, vel=0.7, gain=0.4, release=0.6)


def build(ctx):
    o = Op(ctx)
    intro(o)
    title_hit(o, 6)
    verse_ussr(o, 6)
    verse_pan(o, 10)
    verse_japan(o, 14)
    verse_reich(o, 18)
    prechorus(o, 22)
    title_hit(o, 30)
    chorus(o, 30, 62)        # D мажор
    war_bridge(o, 38)
    chorus(o, 40, 64, war=True)  # E мажор
    climax(o, 48)
    coda(o, 50, 56)
    # эскиз `--parts` (LUFS каждой партии отдельно): трубы −17 и флейта −21 выпирали, а ведущая челеста Рейха
    # (−38), колокола (−49), тромбоны (−45), контрабасы (−37) тонули; выравниваем: ведущие ≈ −22…−25, бас — вровень
    o.p.balance({"Trumpet": -7, "Flute": -3, "Horn": +3, "Basses": +9, "Violins": +7, "Celesta": +13,
                 "Timpani": +6, "Trombone": +10, "Xylophone": +8, "Glockenspiel": +9, "Tubular bells": +12,
                 "Violas": +3, "Organ": +5, "Bassoon": -2})
    return o.p
