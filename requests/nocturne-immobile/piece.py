#!/usr/bin/env python3
"""Неподвижный ноктюрн (ре-бемоль мажор, 3/4, Lent, ≈ 3:00) — стиль «неподвижное бельканто» (Шопен × Сати).

Правило стиля — «жест без следствия»: шопеновская поющая линия, густая гармония, украшения, нарастание — но
развитие, разрешение и взрыв удержаны; сатиевская неподвижность (маятник двух аккордов, почти дословный повтор)
наполнена внутренней жизнью голосов.

  0:00  маятник: левая рука одна (бас — дуга децимами — неподвижный звук)
  0:06  A: мелодия a (8 т.), конец прерванный — на си-бемоль миноре; a′ — почти дословно, одно украшение,
        конец на квинте
  0:54  B: ля мажор (на полтона вниз — без подготовки), хорал параллельных нонаккордов вверху, мелодия в теноре;
        набухание до mp — и такт тишины (1:42)
  1:45  A′: реприза вычитанием — мелодия теряет ноты; единственный пассаж — вниз, в тишину (2:24)
  2:33  кода: маятник, обрывки мелодии, аккорд с секстой и ноной

    python3 -m kit run requests/nocturne-immobile/piece.py --backend sso --parts
"""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from kit.events import Piece  # noqa: E402

BEAT = 1.0  # 60 уд/мин
BAR = 3

# --- A: левая рука по тактам (бас, дуга1, дуга2, неподвижный звук) и мелодия a / a′
LH_A = [(37, 44, 53, 60), (37, 46, 54, 65), (37, 44, 53, 60), (34, 41, 49, 60),      # Db△7 | Gb△7/Db | Db△7 | Bbm9
        (39, 46, 54, 61), (32, 42, 48, 53), (33, 39, 48, 53), (34, 41, 49, 60)]      # Ebm7 | Ab13 | F7/A | Bbm(9)
LH_A2 = LH_A[:5] + [(32, 39, 48, 54), (30, 37, 46, 53), (32, 37, 44, 51)]           # … | Ab7 | Gb△7 | Db/Ab(9)
# мелодия: такт → [(доля, длительность, midi)]
MEL_A = [[(1, 2, 77)],
         [(0, 1.5, 75), (1.5, .5, 77), (2, 1, 78)],
         [(0, 2, 77), (2, 1, 72)],
         [(0, 1.5, 73), (1.5, .25, 75), (1.75, .25, 73), (2, 1, 70)],
         [(0, 2, 75), (2, 1, 78)],
         [(0, 1, 77), (1, .5, 75), (1.5, .5, 72), (2, 1, 68)],
         [(0, 1.5, 69), (1.5, .5, 72), (2, 1, 75)],
         [(0, 3, 73)]]
MEL_A2 = MEL_A[:5] + [[(0, .5, 77), (.5, .25, 78), (.75, .25, 77), (1, .5, 75), (1.5, .25, 74), (1.75, .25, 75),
                        (2, 1, 72)],                                                  # одно украшение
                       [(0, 1.5, 70), (1.5, .5, 68), (2, 1, 70)],
                       [(0, 3, 68)]]                                                  # конец на квинте

# --- B: ля мажор; нонаккорды планируют (одна форма скользит), мелодия в теноре
B_CH = [(33, 9, "maj"), (30, 6, "min"), (38, 2, "maj"), (40, 4, "sus"), (33, 9, "maj"), (36, 0, "maj"),
        (34, 10, "maj"), (32, 8, "b9")]
SHAPE = {"maj": (4, 11, 14), "min": (3, 10, 14), "sus": (5, 10, 14), "b9": (4, 10, 13)}
B_MEL = [[(0, 2, 61), (2, 1, 59)], [(0, 3, 57)],
         [(0, 1, 57), (1, 1, 59), (2, 1, 61)], [(0, 3, 61)],
         [(0, 2, 66), (2, 1, 64)], [(0, 1.5, 62), (1.5, .5, 61), (2, 1, 57)],
         [(0, 3, 59)], [(0, 2, 57), (2, 1, 59)],
         [(0, 2, 61), (2, 1, 64)], [(0, 3, 69)],                                      # набухание
         [(0, 2, 67), (2, 1, 64)], [(0, 1, 59), (1, 2, 60)],
         [(0, 2, 57), (2, 1, 62)], [(0, 3, 65)],
         [(0, 1.5, 66), (1.5, .5, 65), (2, 1, 63)], [(0, 3, 60)]]

# --- A′: вычитание — те же такты, часть нот заменена паузами; единственный пассаж
MEL_A3 = [[(1, 2, 77)],
          [(1.5, .5, 77), (2, 1, 78)],
          [(0, 2, 77)],
          [(0, 1.5, 73), (2, 1, 70)],
          [(0, 2, 75)],
          [(0, 1, 77), (2, 1, 68)],
          [(0, 1.5, 69)],
          [(0, 3, 73)],
          [(1, 2, 77)],
          [(0, 1.5, 75), (2, 1, 78)],
          [(0, 2, 77), (2, 1, 72)],
          [(0, 1.5, 73), (2, 1, 70)],
          [(0, 2, 75), (2, 1, 78)],
          # пассаж: секстоли вниз от верхнего ре-бемоля к фа
          [(0, .5, 85)] + [(0.5 + j / 6, 1 / 6, m) for j, m in enumerate([84, 82, 80, 78, 77, 75, 73, 72, 70, 68,
                                                                          67, 65, 63, 61, 60, 58])][:12]
          + [(2.5, .5, 65)],
          [(0, 1.5, 70), (2, 1, 70)],
          [(0, 3, 72)]]                                                                # конец — не на тонике
LH_A3 = LH_A + LH_A[:5] + [(32, 39, 48, 54), (30, 37, 46, 53), (34, 41, 49, 60)]

# --- кода
CODA_LH = [(37, 44, 53, 60), (37, 46, 54, 65)] * 3
CODA_MEL = [[(0, 3, 77)], [(0, 3, 75)], [(0, 1, 77), (1, 2, 72)], [], [(0, 3, 73)], []]
FINAL = [25, 37, 44, 53, 58, 63, 68, 77]  # Db6/9: Db Db Ab F Bb Eb Ab F — арпеджио вверх


# рубато: множитель длительности доли (больше 1 — медленнее) по записанным долям; ноты пишутся ровно (wt, wdur)
def tempo_factor(beat):
    bar, x = divmod(beat, BAR)
    f = 1.0
    if bar in (9, 17, 50):                      # концы фраз — оттяжка
        f = 1.0 + 0.35 * (x / BAR) ** 1.5
    elif bar == 33:                             # перед тишиной
        f = 1.0 + 0.5 * (x / BAR) ** 1.5
    elif bar in (6, 7, 14, 15, 39, 40, 43, 44):  # середина фразы — чуть вперёд
        f = 0.95
    elif bar == 48:                             # пассаж — дыхание шире
        f = 1.12
    elif bar in (26, 27):                       # набухание середины
        f = 0.97
    elif bar >= 55:                             # кода затихает
        f = 1.12 + 0.12 * (bar - 55) + 0.1 * x / BAR
    return f


STEP = 1 / 24
_CUM = [0.0]
for _i in range(int(62 * BAR / STEP)):
    _CUM.append(_CUM[-1] + STEP * tempo_factor(_i * STEP))


def perf(beat):
    """записанная доля → секунда исполнения"""
    i = beat / STEP
    k = min(int(i), len(_CUM) - 2)
    return _CUM[k] + (_CUM[k + 1] - _CUM[k]) * (i - k)


MARKS = [(0, "Маятник"), (2, "A: пение"), (10, "a′"), (18, "B: тенор под хоралом"), (26, "Набухание"),
         (34, "Тишина"), (35, "A′: вычитание"), (48, "Пассаж"), (51, "Кода")]


class N:
    def __init__(self):
        self.p = Piece("Неподвижный ноктюрн", bpm=60, meter=(3, 4), key="D-flat major", seed=1849)
        self.p.meta["subtitle"] = "Шопен × Сати"
        self.p.meta["sends"] = {"keys": 0.42}
        self.rng = random.Random(1866)
        self.pedal = []  # моменты смены педали (секунды исполнения)
        self.hand = "Piano RH"

    def t(self, bar, beat=0.0):
        """записанное время (доли); исполнение — perf()"""
        return (bar * BAR + beat) * BEAT

    def note(self, m, t, d, vel, late=0.0, part=None, wdur=None):
        """t, d — записанные; правая рука — верхний нотоносец, левая — нижний"""
        t0, t1 = perf(t), perf(t + d)
        part = part or ("Piano RH" if m >= 60 else "Piano LH")
        e = self.p.note("piano", m, t0 + late, t1 - t0, vel=vel, gain=0.5, release=0.35, pan=(m - 64) / 90,
                        part=part)
        e["wt"], e["wdur"] = t, d if wdur is None else wdur
        return e

    def lh(self, bar, chord, vel=0.32, thin=False):
        bass, a, b, c = chord
        self.pedal.append(perf(self.t(bar)))
        self.note(bass, self.t(bar), 3, vel + 0.06, part="Piano LH", wdur=1)
        if not thin:
            self.note(a, self.t(bar, 1), 0.5, vel - 0.04, part="Piano LH")
            self.note(b, self.t(bar, 1.5), 0.5, vel - 0.02, part="Piano LH")
        self.note(c, self.t(bar, 2), 1, vel - 0.03, part="Piano LH")

    def mel(self, bar, notes, base=0.5, arch=0.0):
        """правая рука: лёгкое отставание от левой на сильных долях (рубато Шопена — микросдвиги, в пределах сетки)"""
        for b, d, m in notes:
            late = (0.03 if b == 0 and d >= 1 else 0.012 if d >= 1 else 0.0) + 0.006 * self.rng.random()
            v = base + arch + (0.04 if d >= 1.5 else 0) - (0.06 if d < 0.5 else 0)
            self.note(m, self.t(bar, b), d, v, late=late, part=self.hand)

    def apply_pedal(self, end):
        """педаль меняется с каждой гармонией: звук держится до смены педали (но не короче написанного)"""
        ch = sorted(set(self.pedal)) + [end]
        for e in self.p.events:
            if e["kind"] != "note":
                continue
            nxt = next((x for x in ch if x > e["t"] + 0.05), end)
            hold = nxt - e["t"] - 0.04
            if e["dur"] < 0.45:  # украшения и пассаж не копятся под педалью в кашу
                hold = min(hold, e["dur"] + 0.6)
            e["dur"] = max(e["dur"], hold)


def build(ctx):
    n = N()
    for bar, label in MARKS:  # метки — на такт (записанное время), в звуке — исполненное
        n.p.mark(perf(bar * BAR), label)["wt"] = bar * BAR
    # маятник
    for k, chord in enumerate([LH_A[0], LH_A[1]]):
        n.lh(k, chord, vel=0.3)
    # A: a и a′ (фразы: арка громкости к 5–6-му такту)
    arch = [0, .02, .04, .05, .07, .06, .03, 0]
    for k in range(8):
        n.lh(2 + k, LH_A[k])
        n.mel(2 + k, MEL_A[k], arch=arch[k])
    for k in range(8):
        n.lh(10 + k, LH_A2[k], vel=0.3)
        n.mel(10 + k, MEL_A2[k], base=0.48, arch=arch[k])
    # B: бас, тенор, хорал нонаккордов вверху (pp); набухание в тактах 26–27
    for k in range(16):
        bar = 18 + k
        bass, root, q = B_CH[k // 2]
        sw = 0.08 if bar in (26, 27) else 0.04 if bar in (25, 28) else 0.0
        n.pedal.append(perf(n.t(bar)))  # педаль — каждый такт: тенор поёт поступенно, без мути
        if k % 2 == 0:
            n.note(bass, n.t(bar), 6, 0.36 + sw, part="Piano LH", wdur=3)
            n.note(bass + 12, n.t(bar), 6, 0.26 + sw, part="Piano LH", wdur=3, late=0.02)
        top = [72 + ((root + x) % 12) if 72 + ((root + x) % 12) <= 83 else 60 + ((root + x) % 12) for x in SHAPE[q]]
        for j, m in enumerate(sorted(top)):
            n.note(m, n.t(bar, 0.25) if k % 2 == 0 else n.t(bar, 1.0), 2.5 if k % 2 == 0 else 2,
                   0.2 + sw * 0.6 - (0.04 if k % 2 else 0), late=0.04 * j, part="Piano RH")
        n.hand = "Piano LH"  # мелодия середины — в теноре, левой рукой
        n.mel(bar, B_MEL[k], base=0.42 + sw)
        n.hand = "Piano RH"
    # такт тишины (34): педаль снята
    n.pedal.append(perf(n.t(34)) - 0.3)
    # A′: вычитание
    for k in range(16):
        n.lh(35 + k, LH_A3[k], vel=0.28 if k < 8 else 0.3, thin=(k < 4))
        n.mel(35 + k, MEL_A3[k], base=0.44, arch=arch[k % 8] * 0.7)
    # кода
    for k, chord in enumerate(CODA_LH):
        n.lh(51 + k, chord, vel=0.26 - 0.015 * k)
        n.mel(51 + k, CODA_MEL[k], base=0.38 - 0.02 * k)
    t_fin = n.t(57)
    n.pedal.append(perf(t_fin))
    for j, m in enumerate(FINAL):  # аккорд берётся арпеджато снизу вверх (в нотах — аккорд)
        n.note(m, t_fin, 6, 0.3 + (0.04 if m == 77 else 0), late=0.11 * j)
    n.apply_pedal(perf(t_fin) + 7.5)
    return n.p
