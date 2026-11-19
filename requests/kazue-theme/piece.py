#!/usr/bin/env python3
"""«Холодный мир» — тема Кадзуэ (≈ 1:50). Инвариант персонажа (форма А — портрет, без событий сюжета): точность на
службе чужой веры. Чистая рассчитанная линия инженера, которой цель задают другие; её благие намерения — всякий раз
звено беды; искупление, которое некому принять.

Материал — одна дуга-траектория в ладу мияко-бусими на си (си – до – ми – фа# – соль) — ладу императора из японского
облика опенинга: её вера заимствована. Подъём квартами, вершина с поправкой курса на полутон (до → си), спуск точно в
цель. Полутон над тоникой в этом ладу — до, тоника войны (до минор во втором припеве опенинга и в пророчестве Гернота):
поправка курса си → до и есть шаг в войну — война лежит в ладу императора на расстоянии полутона.

Флейта Кадзуэ — без вибрато, нота в ноту; у императора альтовая флейта с подъездами, их она не перенимает.
Крючок — педаль фа#, которую нельзя отпустить: альтовая флейта (император) в унисон с флажолетами скрипок (Гернот,
его тембр из его темы) — тайну знают трое. Фа# — тон речитации культа в теме Гернота и голова темы мира.

Форма: расчёт (флейта одна над педалью си) — вера (император поёт дугу с подъездами октавой ниже, она повторяет её
прямо; рабочий шаг спиккато; гармония по полутактам: си5 | до – си5 | ми5 – до | си5) — крючок (входит педаль фа#;
дуга трижды застревает на фа#; под ней до против фа# — тритон, задуманный) — наведение (фугато: вступления через
шесть долей октавами вниз, басы — увеличением; поправка не возвращается: цель — до; приход в до минор под педалью
фа#) — обрыв, тишина — не попасть (флейта одна, медленнее; спуск останавливается на до, си звучит в басу, но она
в него не попадает; обрыв).

    python3 -m kit run requests/kazue-theme/piece.py --parts
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from kit.devices import Composer  # noqa: E402
from kit.events import Piece  # noqa: E402

BPM = 88
SPB = 60.0 / BPM

# мияко-бусими на си: си до ми фа# соль; флейта — от си первой октавы (71)
B, C, E, Fs, G = 71, 72, 76, 78, 79
# дуга (доля, длительность, midi), 16 долей, 16-я пуста
ARC = [(0, 1, B), (1, .5, E), (1.5, .5, Fs), (2, 2, B + 12),
       (4, .5, C + 12), (4.5, .5, B + 12), (5, 1, G), (6, 1.5, Fs), (7.5, .5, G),
       (8, 1.5, E), (9.5, .5, Fs), (10, 1, E), (11, 1, C), (12, 3, B)]
# та же дуга, но поправка не возвращается: после до — снова до, цель сдвинута на полутон
ARC_WAR = ARC[:-2] + [(11, 4, C)]
# гармония дуги по полутактам (доля, длительность, звуки ниже темы): си5 | до – си5 | ми5 – до | си5
HARM = [(0, 4, (47, 54)), (4, 2, (48, 55)), (6, 2, (47, 54)), (8, 2, (52, 59)), (10, 2, (48, 52, 55)),
        (12, 4, (47, 54))]
PED = 78  # крючок: фа# второй октавы


def tr(notes, semis=0, dt=0.0, scale=1.0):
    return [(dt + b * scale, d * scale, m + semis) for b, d, m in notes]


class K:
    def __init__(self):
        self.p = Piece("«Холодный мир» — тема Кадзуэ", bpm=BPM, meter=(4, 4), key="B minor", seed=28)
        self.p.meta["subtitle"] = "дуга и крючок"
        self.p.meta["sends"] = {"strings": 0.4, "brass": 0.35, "winds": 0.32, "perc": 0.35, "keys": 0.4}
        self.c = Composer(self.p, lib="vsco", seed=27)
        self.slow = []       # (доля0, доля1, множитель длительности)
        self.cut = None      # (доля0, доля1): всё, что звучит внутри, срезается
        self.level = 1.0

    def perf(self, beat):
        s = 0.0
        for b0, b1, f in sorted(self.slow):
            if beat <= b0:
                break
            s += (min(beat, b1) - b0) * (f - 1)
        return (beat + s) * SPB

    def n(self, inst, m, beat, dur, part, legato=None, **kw):
        if legato is None:  # долгие звуки (педали, приход) держатся до конца, иначе педаль кончается раньше метки
            legato = 1.0 if dur >= 3 else 0.95
        if self.cut is not None:
            lo, hi = self.cut
            if lo <= beat < hi:
                return None
            if beat < lo < beat + dur:
                dur = lo - beat
                kw["release"] = 0.12
                legato = 1.0
        kw.setdefault("release", 0.4)
        kw["gain"] = kw.get("gain", 1.0) * self.level
        t0, t1 = self.perf(beat), self.perf(beat + dur)
        e = self.p.note(inst, m, t0, max(0.06, (t1 - t0) * legato), part=part, **kw)
        e["wt"], e["wdur"] = beat * SPB, dur * SPB
        return e

    def line(self, inst, notes, part, vel, gain, accent=0.06, **kw):
        """прямая линия: каждая нота ровно, сильные доли чуть твёрже — без подъездов и вибрато"""
        for b, d, m in notes:
            acc = accent if abs(b - round(b)) < 1e-6 else 0.0
            self.n(inst, m, b, d, part, vel=vel + acc, gain=gain * (1 + acc), **kw)

    def fx(self, kind, beat, **kw):
        return self.c.fx(kind, self.perf(beat), bus="perc", **kw)


# ===================================================================== голоса

def kazue(o, notes, vel=0.5, gain=0.45, **kw):
    o.line("fl_sus", notes, "Flauto (Kazue)", vel=vel, gain=gain, attack=0.03, **kw)


def emperor(o, notes, vel=0.52, gain=0.5):
    """альтовая флейта с подъездами: длинные звуки берутся снизу на полутон (мери → кари), как в опенинге"""
    for b, d, m in notes:
        bend = 1.0 if d >= 1.5 else 0.0
        o.n("afl_sus", m - (1 if bend else 0), b, d, "Flauto alto (imperatore)", vel=vel, gain=gain, attack=0.05,
            bend=bend, release=0.3)


def hook(o, b0, b1, gain=1.0):
    """крючок: фа#, который нельзя отпустить, — император (альтовая флейта) и Гернот (флажолеты на октаву выше)"""
    o.n("afl_sus", PED, b0, b1 - b0, "Gancio (fa#)", vel=0.36, gain=0.2 * gain, attack=2.0, release=0.12)
    o.n("vln_harm", PED + 12, b0 + 0.5, b1 - b0 - 0.5, "Gancio (fa#)", vel=0.34, gain=0.16 * gain, attack=2.5,
        release=0.12)


def harmony(o, t0, vel=0.38, gain=0.22, bass=True, pulse=False):
    """гармония дуги по полутактам: альты и виолончели держат созвучие ниже темы, бас — основной тон"""
    for b, d, ch in HARM:
        for m in ch:
            o.n("vla_sus" if m >= 52 else "vc_sus", m, t0 + b, d, "Archi", vel=vel, gain=gain, attack=0.25,
                release=0.4)
        if bass:
            o.n("cb_sus", ch[0] - 12, t0 + b, d, "Bassi", vel=vel + 0.04, gain=gain * 1.2, attack=0.2, release=0.4)
        if pulse:  # рабочий шаг: восьмые спиккато по звукам созвучия
            for j in range(int(d * 2)):
                m = ch[j % len(ch)] + 12
                o.n("vla_spic", m, t0 + b + j * 0.5, 0.4, "Spiccato", vel=0.42 + (0.06 if j % 2 == 0 else 0),
                    gain=0.2, release=0.15)


# ===================================================================== разделы

def calculation(o, t0):
    """расчёт: флейта одна; низкие струнные пустыми квинтами по гармонии дуги (неподвижная педаль си спорила бы с до
    на сильной доле); дуга приходит точно в цель"""
    kazue(o, tr(ARC, 0, t0), vel=0.46, gain=0.42)
    for b, d, ch in HARM:
        o.n("cb_sus", ch[0] - 12, t0 + b, d, "Bassi", vel=0.36, gain=0.3, attack=0.8 if b else 1.5, release=0.6)
        o.n("vc_sus", ch[0] + 7 if ch[0] + 7 in ch else ch[1], t0 + b, d, "Archi", vel=0.34, gain=0.2,
            attack=0.8 if b else 1.8, release=0.6)


def faith(o, t0):
    """вера: император поёт дугу с подъездами (октавой ниже), затем она повторяет её прямо; под ними рабочий шаг
    спиккато и гармония по полутактам; бас пиццикато на сильных долях"""
    emperor(o, tr(ARC, -12, t0))
    kazue(o, tr(ARC, 0, t0 + 16), vel=0.52, gain=0.46)
    # пока она поёт, он держит снизу верхний звук гармонии (си – соль – си – фа# … ) — ведёт её, не споря с ней
    for b, d, ch in HARM:
        o.n("afl_sus", ch[-1] + 12, t0 + 16 + b, d, "Flauto alto (imperatore)", vel=0.36, gain=0.22,
            attack=0.6, release=0.5)
    for k in (0, 16):
        harmony(o, t0 + k, vel=0.38, gain=0.2, bass=False, pulse=True)
        for b, d, ch in HARM:
            for bb in range(int(b), int(b + d), 2):
                o.n("cb_pizz", ch[0] - 12, t0 + k + bb, 1, "Bassi", vel=0.55, gain=0.5, release=0.7)
                o.n("vc_pizz", ch[0], t0 + k + bb, 1, "Bassi", vel=0.45, gain=0.25, release=0.6)


def the_hook(o, t0):
    """крючок: педаль фа# входит и больше не уходит; дуга трижды застревает на фа#; под второй попыткой — до против
    фа# (тритон, задуманный: война против тайны)"""
    hook(o, t0, 112 + 16)  # держится до конца наведения
    tries = [
        [(0, 1, B), (1, .5, E), (1.5, .5, Fs), (2, 5, Fs)],
        [(8, .5, E), (8.5, .5, Fs), (9, 2, B + 12), (11, .5, C + 12), (11.5, .5, B + 12), (12, 1, G), (13, 3, Fs)],
        [(16, 1, B), (17, .5, E), (17.5, .5, Fs), (18, 2, B + 12), (20, .5, C + 12), (20.5, .5, B + 12), (21, 1, G),
         (22, 1.5, Fs), (23.5, .5, G), (24, 8, Fs)],
    ]
    for k, tr_ in enumerate(tries):
        kazue(o, tr(tr_, 0, t0), vel=0.46 + 0.04 * k, gain=0.4 + 0.04 * k)
    low = [(0, 8, (35, 42)), (8, 4, (35, 42)), (12, 4, (36, 43)), (16, 4, (35, 42)), (20, 4, (36, 43)),
           (24, 8, (35, 42))]
    for b, d, (r, f) in low:
        o.n("cb_sus", r, t0 + b, d, "Bassi", vel=0.36, gain=0.3, attack=0.6, release=0.5)
        o.n("vc_sus", f, t0 + b, d, "Archi", vel=0.34, gain=0.2, attack=0.6, release=0.5)
        o.n("vc_sus", r + 12, t0 + b, d, "Archi", vel=0.32, gain=0.16, attack=0.6, release=0.5)
    # кларнет в низком регистре — медленная линия под застреваниями: си – до – си (поправка, которую она не делает)
    for b, d, m in [(4, 4, 59), (12, 4, 60), (20, 4, 60), (24, 8, 59)]:
        o.n("cl_sus", m, t0 + b, d, "Clarinetto", vel=0.36, gain=0.24, attack=0.5, release=0.6)


def heavy(o, b0, gain=1.0, root=(47, 42)):
    """тяжёлый пульс, как «тайко» опенинга: большой барабан на 1, «и» второй и 3; литавры на основном тоне и квинте"""
    for b, g in ((0, 0.5), (1.5, 0.3), (2, 0.38), (3, 0.42)):
        o.fx("bd", b0 + b, gain=g * gain)
    o.n("timp", root[0], b0, 0.5, "Timpani", vel=0.66, gain=0.36 * gain, release=0.6)
    o.n("timp", root[1], b0 + 2, 0.5, "Timpani", vel=0.6, gain=0.3 * gain, release=0.6)


def guidance(o, t0):
    """наведение: фугато на дуге с целью до — флейта, кларнет (октавой ниже, через 6 долей), альты и виолончели
    (двумя октавами ниже, через 12), тромбоны и туба — увеличением подъёма и вершины (через 16); мотор спиккато
    восьмыми, тяжёлый пульс; с доли 32 — приход в до минор под педалью фа#, флейта застывает на до"""
    kazue(o, tr(ARC_WAR, 0, t0), vel=0.56, gain=0.5)
    o.line("cl_sus", tr(ARC_WAR, -12, t0 + 6), "Clarinetto", vel=0.52, gain=0.42, attack=0.03)
    o.line("vla_sus", tr(ARC_WAR, -12, t0 + 12), "Archi", vel=0.5, gain=0.2, attack=0.05)  # альты не берут си малой
    o.line("vc_sus", tr(ARC_WAR, -24, t0 + 12), "Archi", vel=0.55, gain=0.3, attack=0.05)
    aug = tr(ARC[:7], 0, t0 + 16, scale=2.0)
    o.line("tbn_sus", tr(aug, -24), "Ottoni", vel=0.6, gain=0.34, attack=0.06, accent=0.0)
    o.line("tba_sus", tr(aug, -36), "Ottoni", vel=0.6, gain=0.3, attack=0.06, accent=0.0)
    # бас и мотор: педаль си до прихода (16 + 16 долей), затем до
    for bar in range(8):
        b = t0 + 4 * bar
        heavy(o, b, gain=0.8 + 0.04 * bar)
        o.n("cb_sus", 35, b, 4, "Bassi", vel=0.5, gain=0.4, attack=0.1, release=0.3)
        for j in range(8):
            o.n("vln_spic", (71, 78)[j % 2], b + j * 0.5, 0.4, "Spiccato", vel=0.48 + (0.08 if j % 2 == 0 else 0),
                gain=0.2, release=0.15)
    # приход: до минор (до – ми♭ – соль) — чужая ладу императора терция; флейта на до третьей октавы
    t1 = t0 + 32
    cm = [(36, "Bassi", "cb_sus"), (48, "Ottoni", "tbn_sus"), (51, "Ottoni", "tbn_sus"), (55, "Ottoni", "hn_sus"),
          (60, "Archi", "vla_sus"), (63, "Archi", "vla_sus"), (48, "Archi", "vc_sus"), (55, "Archi", "vc_sus"),
          (36, "Ottoni", "tba_sus")]
    for m, part, inst in cm:
        # замер окна 76–88 с: медь прихода на 13 дБ ниже флейты — до минор не слышен как удар; медь ×1.8 (≈ +5 дБ)
        o.n(inst, m, t1, 16, part, vel=0.6, gain=0.3 * (1.8 if part == "Ottoni" else 1.0), attack=1.2, release=0.12)
    kazue(o, [(t1, 16, C + 12)], vel=0.62, gain=0.5)
    o.n("cl_sus", 72, t1 + 2, 14, "Clarinetto", vel=0.5, gain=0.34, attack=0.8, release=0.12)
    for bar in range(4):
        b = t1 + 4 * bar
        heavy(o, b, gain=1.0 + 0.1 * bar, root=(48, 43))
        for j in range(8):
            o.n("vln_spic", (72, 79)[j % 2], b + j * 0.5, 0.4, "Spiccato", vel=0.55 + (0.08 if j % 2 == 0 else 0),
                gain=0.22 + 0.02 * bar, release=0.15)
    o.fx("tamtam", t1, gain=0.12)


def miss(o, t0):
    """не попасть: флейта одна, медленнее; спуск останавливается на до. Педаль фа# — только альтовая флейта,
    тихо; на последнем такте в басу звучит си — цель есть, она в неё не попадает. Обрыв."""
    mel = tr(ARC_WAR, 0, t0, scale=1.25)
    *body, (b, d, m) = mel
    kazue(o, body, vel=0.44, gain=0.4)
    o.n("fl_sus", m, b, 24 - b + t0, "Flauto (Kazue)", vel=0.4, gain=0.38, attack=0.04, release=0.1)
    o.n("afl_sus", PED, t0, 24, "Gancio (fa#)", vel=0.32, gain=0.16, attack=1.5, release=0.1)
    o.n("cb_pizz", 35, t0 + 16, 1, "Bassi", vel=0.45, gain=0.42, release=1.2)
    o.n("cb_sus", 35, t0 + 18, 6, "Bassi", vel=0.34, gain=0.28, attack=1.5, release=0.1)


# замер `--parts` без баланса: флейта −20.8, струнные −23.7, альтовая флейта −26.3, кларнет −28.1, спиккато −37.7,
# медь −40.8, крючок −42.1, литавры −45.1, басы −46.2 LUFS — бас на 25 дБ ниже темы, крючок и медь не слышны
BAL = {"Bassi": +20, "Gancio (fa#)": +11, "Spiccato": +7, "Ottoni": +14, "Timpani": +12, "Archi": -2,
       "Clarinetto": +3, "Flauto alto (imperatore)": +3}


def build(ctx):
    o = K()
    # доли: расчёт 0–16 | вера 16–48 | крючок 48–80 | наведение 80–128 | тишина 128–132 | не попасть 132–156
    o.slow += [(148, 156, 1.25)]  # медленнее только последний спуск: метки разделов стоят ровно на тактах
    plan = [(0, "Расчёт"), (16, "Вера"), (48, "Крючок"), (80, "Наведение"), (128, "Обрыв"), (132, "Не попасть")]
    calculation(o, 0)
    faith(o, 16)
    o.cut = (128, 132)
    the_hook(o, 48)
    guidance(o, 80)
    o.cut = None
    o.level = 0.7
    miss(o, 132)
    o.p.balance(BAL)
    for bt, label in plan:
        o.p.mark(o.perf(bt), label)["wt"] = bt * SPB
    o.p.meta["beats"] = 156
    o.p.meta["length"] = o.perf(156) + 1.2
    return o.p
