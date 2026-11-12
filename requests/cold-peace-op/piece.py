#!/usr/bin/env python3
"""«Холодный мир» — опенинг аниме, TV-size 1:30 (152 уд/мин, 57 тактов). Раскадровка — storyboard.md.

Вторая редакция (первая звучала «детским приключением»): всё в миноре, тяжёлый полутемп поверх мотора
шестнадцатых низких струнных, удары как у тайко вместо бита ударной установки, низкая медь, туба, мужской хор,
орган; без ксилофона и колокольчиков.

Форма: интро (туман 1944, шкатулка, коронация) → заставка → куплет A (одна тема мира в четырёх обликах:
СССР — мужской хор и валторны; Панамерика — засурдиненная труба над «телеграфом»; Япония — альтовая флейта в
мияко-бусими; Рейх — расстроенная шкатулка над увеличенными созвучиями, обрыв) → предприпев B (педаль F#,
четыре мотива-флага) → припев, си минор: i–♭VI–iv–V | i–♭II–iv–V → война: полтона вверх (до минор) → доминанта
не разрешается → крушение → шкатулка (си минор, как в начале) → удар на титр.

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
DOR = [0, 2, 3, 5, 7, 9, 10]
PHRYG = [0, 1, 3, 5, 7, 8, 10]

# тема мира (куплет, 4 такта): (доля, длительность, ступень)
THEME = [(0, .5, 4), (.5, .5, 4), (1, .5, 3), (1.5, 1, 4), (2.5, 1.5, 2),
         (4, .5, 1), (4.5, .5, 2), (5, .5, 4), (5.5, 1, 7), (6.5, 1.5, 6),
         (8, .5, 5), (8.5, .5, 4), (9, .5, 2), (9.5, 1, 4), (10.5, 1.5, 3),
         (12, .5, 2), (12.5, .5, 1), (13, 3, 0)]
# японский облик — вручную в ладу мияко-бусими на B (B C E F# G): тот же контур
JAPAN = [78, 78, 76, 78, 76, 72, 76, 78, 83, 79, 79, 78, 76, 78, 76, 76, 72, 71]

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
    o.c.music_box(o.t(0, 0.5), tune, step=0.36, slow=0.012, flat=0.02, inst="celesta", double=None, gain=0.42)
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


def motor(o, bar, notes, beats=4, inst="vc_spic", vel=0.6, gain=0.35):
    """шестнадцатые низких струнных — мотор тревоги (без «гитарных» восьмых)"""
    for j in range(int(beats * 4)):
        m = notes[j % len(notes)]
        o.n(inst, m, bar, j * 0.25, 0.22, vel=vel + (0.12 if j % 4 == 0 else 0), gain=gain, release=0.08)


def heavy(o, bar, gain=1.0, fill=False, tam=False):
    """тяжёлый полутемп, как тайко: большой барабан на 1 и «и» второй, литавры и малый — на 3"""
    o.drum("bd", bar, 0, gain=0.5 * gain)
    o.drum("bd", bar, 1.5, gain=0.3 * gain)
    o.drum("snare", bar, 2, gain=0.22 * gain)
    o.drum("bd", bar, 2, gain=0.35 * gain)
    if fill:
        for b in (3, 3.25, 3.5, 3.75):
            o.drum("bd", bar, b, gain=(0.25 + 0.08 * (b - 3) * 4) * gain)
    if tam:
        o.drum("tamtam", bar, 0, gain=0.18 * gain)


def verse_ussr(o, bar):
    """СССР: протяжный эолийский облик — виолончели и валторны, мужской хор, низкие колокола, полутемп"""
    mel = theme(AEOL, B0)  # B3…
    o.line("hn_sus", mel, bar, vel=0.6, gain=0.5, attack=0.05)
    o.line("vc_sus", mel, bar, vel=0.55, gain=0.4, attack=0.05)
    o.line("choir", [(b, d, m - 12) for b, d, m in mel], bar, vel=0.5, gain=0.35, attack=0.1, legato=0.97)
    chords = [(47, [54, 59, 62]), (43, [55, 59, 62]), (40, [55, 59, 64]), (47, [54, 59, 62])]
    for k, (r, up) in enumerate(chords):
        o.n("cb_sus", r - 12, bar + k, 0, 4, vel=0.6, gain=0.45, release=0.3)
        o.n("tba_sus", r - 12 if r - 12 >= 28 else r, bar + k, 0, 3.8, vel=0.5, gain=0.25, release=0.3)
        o.ch("tbn_sus", [x - 12 for x in up[:2]], bar + k, 0, 3.8, vel=0.45, gain=0.28, release=0.3)
        o.n("tubular", 64 if k % 2 == 0 else 66, bar + k, 0, 3, vel=0.4, gain=0.3, release=2.0)
        o.n("timp", r if r >= 40 else r + 12, bar + k, 0, 1, vel=0.65, gain=0.4)
        o.n("timp", r if r >= 40 else r + 12, bar + k, 2, 1, vel=0.5, gain=0.3)
        heavy(o, bar + k, gain=0.7)


def verse_pan(o, bar):
    """Панамерика: холодный расчёт — засурдиненная труба (дорийский лад), тикающее спиккато, удары низкой меди"""
    mel = theme(DOR, B0 + 12)  # B4…
    o.line("tpt_mute", mel, bar, vel=0.65, gain=0.5, attack=0.02, legato=0.85)
    roots = [47, 40, 42, 47]
    tri = [[50, 54, 59], [52, 56, 59], [49, 54, 57], [50, 54, 59]]  # Bm | E | F#m | Bm
    for k in range(4):
        for j in range(16):  # тикающий телеграф: одна высота шестнадцатыми
            o.n("vln_spic", 78, bar + k, j * 0.25, 0.2, vel=0.4 + (0.15 if j % 4 == 0 else 0), gain=0.22, release=0.05)
        motor(o, bar + k, [roots[k], roots[k] + 12, roots[k] + 7, roots[k] + 12], vel=0.55, gain=0.3)
        o.n("cb_sus", roots[k] - 12, bar + k, 0, 4, vel=0.6, gain=0.45, release=0.2)
        for b in (0, 1.5, 3):  # удары низкой меди по синкопам
            o.ch("tbn_stac", tri[k], bar + k, b, 0.5, vel=0.7, gain=0.32)
        heavy(o, bar + k, gain=0.85, fill=(k == 3))


def verse_japan(o, bar):
    """Япония: мияко-бусими, альтовая флейта с подъездами, кото-арфа с малой секундой, «тайко»"""
    for (b, d, _), m in zip(THEME, JAPAN):
        bend, mm = 0.0, m - 12
        if d >= 1.5:
            mm, bend = m - 13, 1.0  # мери → кари: подъезд снизу
        o.n("afl_sus", mm + 12, bar, b, d * 0.95, vel=0.6, gain=0.55, attack=0.04, bend=bend, release=0.2)
        o.n("vla_sus", m - 12, bar, b, d * 0.9, vel=0.45, gain=0.2, attack=0.03)
    fifths = [(35, 42), (36, 43), (40, 47), (35, 42)]
    koto = [[59, 60, 64, 66], [60, 64, 67, 71], [64, 66, 67, 71], [59, 60, 64, 66]]
    for k in range(4):
        lo, hi = fifths[k]
        o.ch("cb_sus", [lo], bar + k, 0, 4, vel=0.65, gain=0.45, release=0.2)
        o.ch("vc_trem", [lo + 12, hi + 12], bar + k, 0, 4, vel=0.5, gain=0.3, release=0.2)
        o.ch("vln_trem", [hi + 24, lo + 37], bar + k, 0, 4, vel=0.35, gain=0.14, release=0.2)  # секунда наверху
        for b, g in ((0, 0.55), (0.75, 0.3), (1.5, 0.45), (2, 0.35), (3, 0.5), (3.5, 0.4)):
            o.drum("bd", bar + k, b, gain=g * 0.85)
        for b in (0, 1.5, 3, 3.5):
            o.n("timp", lo + 12 if lo + 12 <= 49 else lo, bar + k, b, 0.5, vel=0.7, gain=0.4)
        for j in range(8):
            o.n("harp", koto[k][j % 4] + (12 if j >= 4 else 0), bar + k, j * 0.5, 0.8, vel=0.5, gain=0.35,
                release=0.8, pan=0.35)


def verse_reich(o, bar):
    """Рейх: шкатулка с расстройкой, хор мальчиков на увеличенных созвучиях, орган; фраза обрывается вверх"""
    mel = theme(HARM, B0 + 24)
    cut = 13.0
    for j, (b, d, m) in enumerate(mel):
        if b >= cut:
            continue
        o.n("celesta", m, bar, b, d, vel=0.55, gain=0.5, release=0.8, detune=-0.02 * j)
        o.n("vln_harm", m, bar, b, d * 0.9, vel=0.3, gain=0.18, attack=0.05)
    chords = [[59, 62, 66], [58, 62, 66], [59, 63, 67], [61, 64, 66, 70]]  # Bm | D+ | G+ | F#7
    for k in range(4):
        dur = 4 if k < 3 else 2
        o.ch("org_quiet", [x - 12 for x in chords[k]], bar + k, 0, dur, vel=0.5, gain=0.35, release=0.1)
        o.ch("choir", [x + 12 for x in chords[k]], bar + k, 0, dur, vel=0.4, gain=0.35, attack=0.4, release=0.15)
        o.n("org_quiet", 47, bar + k, 0, dur, vel=0.5, gain=0.3, release=0.1)
        for j in range(int(dur * 2)):
            o.n("vla_pizz", chords[k][j % len(chords[k])], bar + k, j * 0.5, 0.4, vel=0.45, gain=0.25)
    t_cut = o.t(bar + 3, 2)
    o.c.fx("glock_up", t_cut, gain=0.18, pan=0.2, bus="perc")
    for j, m in enumerate(range(71, 108, 3)):
        o.p.note("harp", m, t_cut + 0.035 * j, 0.6, vel=0.4, gain=0.22, release=0.8, pan=0.4)


def prechorus(o, bar):
    """B: космодром — педаль F# в моторе низких струнных, гармония сползает над ней; четыре мотива по очереди"""
    prog = [[55, 59, 62], [55, 59, 64], [54, 59, 62], [55, 60, 64], [55, 59, 62], [55, 59, 64], [55, 60, 64],
            [54, 58, 61]]  # G/F# | Em/F# | Bm/F# | C/F# | G | Em | C | F#
    for k, tri in enumerate(prog):
        b = bar + k
        motor(o, b, [42, 54, 42, 49], vel=0.55 + 0.03 * k, gain=0.33)
        o.n("cb_sus", 42, b, 0, 4, vel=0.55 + 0.04 * k, gain=0.45, release=0.2)
        o.ch("vla_sus", tri, b, 0, 4, vel=0.4 + 0.04 * k, gain=0.22, release=0.2)
        o.ch("vln_sus", [x + 12 for x in tri], b, 0, 4, vel=0.35 + 0.05 * k, gain=0.18, release=0.2)
        o.drum("bd", b, 0, gain=0.35 + 0.03 * k)
        o.drum("bd", b, 2, gain=0.25 + 0.03 * k)
    head = THEME[:10]
    flags = [("hn_sus", 59, 0.55), ("tpt_mute", 71, 0.45), ("afl_sus", 71, 0.5), ("celesta", 83, 0.5)]
    for i, (inst, tonic, g) in enumerate(flags):
        b = bar + 2 * i
        o.drum("tamtam" if i == 0 else "clash", b, 0, gain=0.12 + 0.04 * i)
        o.line(inst, [(x, d, deg(s, AEOL, tonic)) for x, d, s in head], b, vel=0.62, gain=g, attack=0.03)
        if inst == "celesta":
            o.ch("choir", [x + 12 for x in prog[6]], b, 0, 4, vel=0.5, gain=0.35, attack=0.4)
            o.ch("choir", [x + 12 for x in prog[7]], b + 1, 0, 4, vel=0.55, gain=0.38, attack=0.2)
        for kk in range(2 * i + 2, 8):  # «флаг» остаётся: долгий тон
            if inst != "celesta":
                o.n(inst, prog[kk][i % 3] + (0 if inst == "hn_sus" else 12), bar + kk, 0, 4, vel=0.45, gain=g * 0.5,
                    attack=0.2, release=0.2)
    o.roll("snare_soft", bar + 6, bar + 7, 0.03, 0.12)
    o.roll("snare", bar + 7, bar + 8, 0.12, 0.4)
    o.c.shepard(o.t(bar + 4), o.t(bar + 8) - 0.15, up=True, gain=0.22, period=3.0)
    o.n("timp_roll", 42, bar + 6, 0, 8, vel=0.55, gain=0.35, attack=2.0, release=0.05)


# припев — минор, широкие длинные ноты над мотором: i | ♭VI | iv | V | i | ♭II | iv | V
CH_MEL = [(0, 2, 66), (2, .5, 67), (2.5, .5, 66), (3, 1, 62),
          (4, 2, 71), (6, 1, 69), (7, 1, 67),
          (8, 1.5, 67), (9.5, .5, 66), (10, 1, 64), (11, 1, 71),
          (12, 2, 70), (14, 2, 73),
          (16, 2, 74), (18, 1, 73), (19, 1, 71),
          (20, 2, 76), (22, 1, 74), (23, 1, 72),
          (24, 1.5, 71), (25.5, .5, 67), (26, 2, 64),
          (28, 2, 66), (30, 1, 70), (31, 1, 73)]
CH_PROG = [(47, "m"), (43, "M"), (40, "m"), (42, "M"), (47, "m"), (48, "M"), (40, "m"), (42, "M")]


def chorus(o, bar, shift=0, war=False):
    """припев: тема у валторн + скрипок 8va + хора; на войне — на полтона выше, мелодия ещё и у тромбонов и тубы"""
    mel = [(b, d, m + shift) for b, d, m in CH_MEL]
    o.line("hn_sus", mel, bar, vel=0.75, gain=0.5, attack=0.03, legato=0.97)
    o.line("vln_sus", [(b, d, m + 12) for b, d, m in mel], bar, vel=0.75, gain=0.42, attack=0.03, legato=0.97)
    o.line("choir", mel, bar, vel=0.7, gain=0.45, attack=0.08, legato=0.98)
    if war:
        o.line("tbn_sus", [(b, d, m - 12) for b, d, m in mel], bar, vel=0.75, gain=0.35, attack=0.03)
    for k, (r, q) in enumerate(CH_PROG):
        b = bar + k
        rr = r + shift
        third = 4 if q == "M" else 3
        tri = [rr + 12, rr + 12 + third, rr + 19]
        motor(o, b, [rr, rr + 12, rr + 7, rr + 12], vel=0.62, gain=0.34)
        motor(o, b, [tri[1] + 12, tri[2], tri[1] + 12, tri[2] + 5], inst="vla_spic", vel=0.5, gain=0.18)
        o.n("cb_sus", rr - 12 if rr - 12 >= 28 else rr, b, 0, 4, vel=0.75, gain=0.5, release=0.2)
        o.n("tba_sus", rr - 12 if rr - 12 >= 28 else rr, b, 0, 3.8, vel=0.6, gain=0.3, release=0.2)
        o.ch("tbn_sus", tri, b, 0, 3.8, vel=0.6, gain=0.25, release=0.2)
        o.n("timp", rr if 38 <= rr <= 53 else (rr - 12 if rr > 53 else rr + 12), b, 0, 1, vel=0.75, gain=0.4)
        o.n("timp", rr if 38 <= rr <= 53 else (rr - 12 if rr > 53 else rr + 12), b, 2, 1, vel=0.6, gain=0.3)
        heavy(o, b, gain=1.15 if war else 1.0, fill=(k == 7), tam=(k % 4 == 0))
        if k % 4 == 0:
            o.drum("clash", b, 0, gain=0.3)
        if war:
            o.n("org_loud", rr - 12 if rr - 12 >= 24 else rr, b, 0, 3.9, vel=0.6, gain=0.22, release=0.2)


def war_bridge(o, bar):
    """станция взрывается: удары меди, химическое облако (кластер, сползающий вниз), ♭VI → V7 до минора"""
    o.drum("gong_hit", bar, 0, gain=0.4)
    o.drum("bd", bar, 0, gain=0.55)
    o.drum("clash", bar, 0, gain=0.35)
    o.n("timp", 47, bar, 0, 1, vel=0.9, gain=0.55)
    o.ch("tbn_stac", [47, 50, 54], bar, 0, 1, vel=0.9, gain=0.45)
    for j, m in enumerate([86, 85, 84, 83, 81, 80]):
        o.n("vln_sus", m, bar, 0.5, 6, vel=0.55, gain=0.2, attack=0.1, bend=-14.0, detune=0.1 * j, pan=-0.5 + 0.2 * j)
    for b, ch in ((1.5, [44, 48, 51]), (2.5, [44, 48, 51]), (3.5, [44, 48, 51]), (4, [43, 47, 50, 53]),
                  (5, [43, 47, 50, 53]), (5.5, [43, 47, 50, 53]), (6.5, [43, 47, 50, 53]), (7, [43, 47, 50, 53])):
        o.ch("hn_stac", [x + 12 for x in ch], bar, b, 0.45, vel=0.75, gain=0.35)
        o.ch("tbn_stac", ch, bar, b, 0.45, vel=0.75, gain=0.35)
        o.drum("bd", bar, b, gain=0.3)
    motor(o, bar, [44, 56, 44, 51], vel=0.7, gain=0.36)
    motor(o, bar + 1, [43, 55, 43, 50], vel=0.75, gain=0.38)
    o.n("cb_sus", 32, bar, 0, 4, vel=0.8, gain=0.5)
    o.n("cb_sus", 31, bar + 1, 0, 4, vel=0.8, gain=0.5)
    o.roll("snare", bar + 1, bar + 2, 0.12, 0.4)
    o.n("timp_roll", 43, bar + 1, 0, 4, vel=0.6, gain=0.4, release=0.05)


def climax(o, bar):
    """четверо лицом к лицу: доминанта до минора держится, не разрешаясь — и обрыв (крушение)"""
    top = [(0, 1, 67), (1, 1, 71), (2, 2, 74), (4, 4, 77)]
    o.line("vln_sus", [(b, d, m + 12) for b, d, m in top], bar, vel=0.85, gain=0.45, legato=0.98)
    o.line("hn_sus", top, bar, vel=0.85, gain=0.5, legato=0.98)
    o.ch("choir", [55, 59, 62, 65, 67], bar, 0, 7.9, vel=0.8, gain=0.4, attack=0.1, release=0.1)
    o.ch("tbn_sus", [43, 47, 53], bar, 0, 7.9, vel=0.75, gain=0.3, release=0.1)
    o.n("org_loud", 31, bar, 0, 7.9, vel=0.7, gain=0.3, release=0.1)
    o.n("cb_sus", 31, bar, 0, 7.9, vel=0.8, gain=0.5, release=0.1)
    o.n("tba_sus", 31, bar, 0, 7.9, vel=0.7, gain=0.3, release=0.1)
    motor(o, bar, [43, 55, 43, 50], vel=0.75, gain=0.36)
    motor(o, bar + 1, [43, 55, 43, 50], vel=0.8, gain=0.38)
    o.n("timp_roll", 43, bar, 0, 7.9, vel=0.7, gain=0.45, release=0.05)
    o.roll("snare", bar + 1, bar + 2, 0.15, 0.45)
    o.drum("clash", bar, 0, gain=0.4)
    o.drum("tamtam", bar, 0, gain=0.3)
    for k in range(2):
        o.drum("bd", bar + k, 0, gain=0.5)


def coda(o, bar, final_bar):
    """крушение → тишина → шкатулка кончает завод (E минор) → удар на титр"""
    o.c.fx("glass", o.t(bar, 0), gain=0.25, pan=0.0, bus="fx")
    o.drum("tamtam", bar, 0, gain=0.25)
    tune = [m for _, _, m in theme(HARM, 71 + 12)[:14]]  # си минор — та же шкатулка, что в начале
    o.c.music_box(o.t(bar, 1.0), tune, step=0.42, slow=0.03, flat=0.03, inst="celesta", double=None, gain=0.45)
    for b in (bar, bar + 2, bar + 4):
        o.n("tubular", 66, b, 0.5, 4, vel=0.4, gain=0.28, release=2.5)
    o.ch("vln_harm", [78, 83], bar, 0.5, 18, vel=0.3, gain=0.2, attack=2.0, release=0.5)
    o.n("cb_sus", 35, bar + 1, 0, 16, vel=0.3, gain=0.35, attack=2.0, release=0.3)
    o.n("vc_sus", 47, bar + 2, 0, 12, vel=0.3, gain=0.3, attack=2.0, release=0.3)
    o.n("vc_sus", 48, bar + 3, 0, 8, vel=0.25, gain=0.22, attack=2.0, release=0.3)  # си и до — туман возвращается
    # подъём к удару: дробь и литавры
    o.roll("snare_soft", final_bar - 1, final_bar, 0.02, 0.2)
    o.n("timp_roll", 47, final_bar - 1, 0, 3.95, vel=0.5, gain=0.4, attack=1.5, release=0.05)
    o.c.swell(o.t(final_bar), inst="org_quiet", midi_=59, dur=2.4, gain=0.3)
    # удар на титр: тутти си минор + низкое до (туман), гонг
    fb = final_bar
    o.ch("tbn_stac", [35 + 12, 42 + 12, 47 + 12], fb, 0, 1, vel=0.95, gain=0.5)
    o.ch("tbn_sus", [47, 50, 54], fb, 0, 3, vel=0.85, gain=0.35, release=0.5)
    o.ch("hn_sus", [59, 62, 66], fb, 0, 3, vel=0.85, gain=0.45, release=0.5)
    o.ch("tpt_stac", [71, 74, 78], fb, 0, 1, vel=0.95, gain=0.35)
    o.ch("vln_sus", [74, 78, 83, 86], fb, 0, 3, vel=0.8, gain=0.4, release=0.5)
    o.ch("choir", [47, 54, 59, 62, 66], fb, 0, 3, vel=0.8, gain=0.4, release=0.5)
    o.n("cb_sus", 35, fb, 0, 3, vel=0.9, gain=0.55, release=0.5)
    o.n("cb_sus", 36, fb, 0, 3, vel=0.7, gain=0.3, release=0.5)
    o.n("tba_sus", 35, fb, 0, 3, vel=0.8, gain=0.35, release=0.5)
    o.n("org_loud", 35, fb, 0, 3, vel=0.8, gain=0.35, release=0.5)
    o.n("timp", 47, fb, 0, 2, vel=0.95, gain=0.6)
    o.drum("gong_hit", fb, 0, gain=0.45, dur=1.5, fade=0.4)
    o.drum("tamtam", fb, 0, gain=0.35, dur=1.5, fade=0.4)
    o.drum("bd", fb, 0, gain=0.55)


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
    chorus(o, 30)                 # си минор
    war_bridge(o, 38)
    chorus(o, 40, 1, war=True)    # до минор
    climax(o, 48)
    coda(o, 50, 56)
    # замер `--parts` (LUFS каждой партии отдельно): засурдиненная труба −13 выпирала и топила всё остальное;
    # мотор и низы (виолончели −34, контрабасы −36, тромбоны −38, туба −44) должны быть опорой, а не фоном
    o.p.balance({"Trumpet": -10, "Choir": -2, "Flute": +3, "Violins": +6, "Cellos": +8, "Violas": +4, "Organ": +5,
                 "Timpani": +6, "Basses": +11, "Trombone": +11, "Celesta": +14, "Tuba": +12, "Tubular bells": +16,
                 "Alto flute": +1})
    return o.p
