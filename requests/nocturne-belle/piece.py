#!/usr/bin/env python3
"""Nocturne à trois — драматургия «Belle» (Кочанте), каким её написал бы Шопен (≈ 4:20).

Из «Belle» — только схема: три куплета, три характера на одну мелодию, каждый куплет на малую терцию выше
(d → f → as — по звукам одного уменьшённого септаккорда), припев каждый раз начинается в миноре терцией ниже
куплета и выходит в одноимённый мажор куплета; в конце все трое — один припев, ff, в f-moll. Тема — своя.

  вступление    левая рука одна, d-moll
  I  Квазимодо  d-moll, мелодия в середине, простая, с повторами; припев h-moll → D-dur
  II Фролло     f-moll, мелодия в левой руке (баритон) под мерно бьющимися аккордами — хорал-наваждение;
                припев d-moll → F-dur — октавами, ff
  III Фебюс     gis-moll (у Кочанте as-moll), мелодия наверху, в фиоритурах, лёгкий «салонный» аккомпанемент; припев f-moll → As-dur
  трио          припев в f-moll: мелодия октавами наверху, тема Квазимодо в середине, хроматика Фролло в басу,
                агитато триолями; каденция на C7, фермата
  кода          C7 → d-moll: обрывок темы Квазимодо внизу, ре-мажорный аккорд pp

    python3 -m kit run requests/nocturne-belle/piece.py --backend sso --parts
"""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from kit.events import Piece  # noqa: E402

BPM = 58
SPB = 60 / BPM
BAR = 4
NAMES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
QUAL = {"": (0, 4, 7), "m": (0, 3, 7), "7": (0, 4, 7, 10), "m7": (0, 3, 7, 10), "dim7": (0, 3, 6, 9),
        "m7b5": (0, 3, 6, 10), "6": (0, 4, 7, 9), "m6": (0, 3, 7, 9)}


def chord(name, k=0):
    """'Dm', 'A7', 'Gm/Bb' → (pcs, bass pc), транспонировано на k"""
    name, _, bass = name.partition("/")
    root, i = NAMES[name[0]], 1
    while i < len(name) and name[i] in "b#":
        root += -1 if name[i] == "b" else 1
        i += 1
    pcs = {(root + k + x) % 12 for x in QUAL[name[i:]]}
    b = root if not bass else NAMES[bass[0]] + sum(-1 if c == "b" else 1 for c in bass[1:])
    return pcs, (b + k) % 12


# ===================================================================== тема (своя), в d-moll; такт → [(доля, длит., midi)]
T3 = 1 / 3
VERSE = [
    [(0, 1.5, 69), (1.5, .5, 67), (2, 1, 65), (3, 1, 64)],                                  # Dm — вздох с квинты
    [(0, 1.5, 64), (1.5, .25, 65), (1.75, .25, 64), (2, 2, 61)],                            # A7
    [(0, 1, 62), (1, T3, 65), (1 + T3, T3, 69), (1 + 2 * T3, T3, 74), (2, 1.5, 76), (3.5, .5, 74)],  # Dm — надежда
    [(0, 1.5, 72), (1.5, .5, 70), (2, 1, 69), (3, 1, 67)],                                  # Gm | A7
    [(0, 2, 65), (2, .5, 64), (2.5, .5, 65), (3, 1, 69)],                                   # Dm
    [(0, 2, 74), (2, 1, 72), (3, 1, 70)],                                                   # Bb
    [(0, 1, 70), (1, .5, 69), (1.5, .5, 67), (2, 1, 64), (3, 1, 61)],                       # Gm | A7
    [(0, 3, 62)],                                                                           # Dm
]
VERSE_H = [["Dm"], ["A7"], ["Dm"], ["Gm", "A7"], ["Dm"], ["Bb"], ["Gm", "A7"], ["Dm"]]
# припев: h-moll → D-dur (на малую терцию ниже куплета, выход в одноимённый мажор куплета)
REFR = [
    [(0, 1, 71), (1, 1, 74), (2, 1.5, 78), (3.5, .5, 76)],                                  # Bm
    [(0, 2, 74), (2, 1, 71), (3, 1, 67)],                                                   # Em7
    [(0, 1, 70), (1, T3, 73), (1 + T3, T3, 76), (1 + 2 * T3, T3, 79), (2, 1, 78), (3, .5, 76), (3.5, .5, 73)],  # F#7
    [(0, 1, 74), (1, 2, 71), (3, 1, 66)],                                                   # Bm
    [(0, 1, 67), (1, 1, 71), (2, 1, 74), (3, 1, 79)],                                       # G
    [(0, 1.5, 78), (1.5, .5, 76), (2, 1, 73), (3, 1, 69)],                                  # A7
]
REFR_H = [["Bm"], ["Em7"], ["F#7"], ["Bm"], ["G"], ["A7"]]
LINK = [[(0, 3.5, 74)], [(0, 1.5, 76), (1.5, .5, 74), (2, 2, 72)]]                            # D | C7 (→ на терцию выше)
LINK_H = [["D"], ["C7"]]
# варианты гармонии: Фролло темнее (неаполитанский, уменьшённый), Фебюс — как есть
VERSE_H_FROLLO = [["Dm"], ["A7"], ["Dm"], ["Gm6", "A7"], ["Dm"], ["Bb7"], ["Em7b5", "A7"], ["Dm"]]


class Noct:
    def __init__(self):
        self.p = Piece("Nocturne à trois", bpm=BPM, meter=(4, 4), key="D minor", seed=1998)
        self.p.meta["subtitle"] = "«Belle», как написал бы Шопен"
        self.p.meta["sends"] = {"keys": 0.42}
        self.rng = random.Random(1830)
        self.pedal = []
        self.slow = []
        self.prev = {}

    # ---------------------------------------------------------------- время: записанное → исполненное
    def perf(self, beat):
        s = 0.0
        for b0, b1, f0, f1 in sorted(self.slow):
            if beat <= b0:
                break
            x = min(beat, b1)
            # множитель меняется линейно f0 → f1 на отрезке; интеграл (f−1)
            L = b1 - b0
            u = (x - b0) / L
            s += L * (u * (f0 - 1) + 0.5 * u * u * (f1 - f0))
        return (beat + s) * SPB

    def note(self, m, beat, dur, vel, part, late=0.0, wdur=None):
        t0, t1 = self.perf(beat), self.perf(beat + dur)
        e = self.p.note("piano", m, t0 + late, max(0.05, t1 - t0), vel=max(0.08, min(0.95, vel)), gain=0.5,
                        release=0.35, pan=(m - 64) / 90, part=part)
        e["wt"], e["wdur"] = beat * SPB, dur * SPB if wdur is None else wdur * SPB
        return e

    def ped(self, beat):
        self.pedal.append(self.perf(beat))

    # ---------------------------------------------------------------- голоса
    def melody(self, bar, notes, k, part="Piano RH", vel=0.5, oct=0, double=False, orn=False):
        """мелодия такта; rubato Шопена — правая рука чуть позже левой на сильных долях.
        orn: фиоритуры Фебюса — долгие ноты опеваются группеттой, концы фраз — пассажем"""
        b0 = bar * BAR
        for b, d, m in notes:
            m = m + k + oct
            late = (0.035 if b == 0 and d >= 1 else 0.012 if d >= 1 else 0.0) + 0.008 * self.rng.random()
            v = vel + (0.05 if d >= 1.5 else 0) - (0.07 if d < 0.5 else 0)
            if orn and d >= 1.5:  # группетто: верхний — сам — нижний — сам, затем держать
                sc = self.scale_near(m, k)
                up, lo = sc[0], sc[1]
                for i, x in enumerate((m, up, m, lo)):
                    self.note(x, b0 + b + i / 8, 1 / 8, v - 0.08, part, late=late if i == 0 else 0)
                self.note(m, b0 + b + 0.5, d - 0.5, v, part)
                continue
            self.note(m, b0 + b, d, v, part, late=late)
            if double:
                self.note(m - 12, b0 + b, d, v - 0.08, part, late=late + 0.01)

    def scale_near(self, m, k):
        """верхний и нижний соседи по гармоническому минору тональности куплета (k — сдвиг от d-moll)"""
        sc = {(2 + k + x) % 12 for x in (0, 2, 3, 5, 7, 8, 11)}
        up = next(x for x in range(m + 1, m + 3) if x % 12 in sc)
        lo = next(x for x in range(m - 1, m - 4, -1) if x % 12 in sc)
        return up, lo

    def fioritura(self, beat, top, bottom, k, part="Piano RH", vel=0.42):
        """пассаж вниз по гамме за одну долю (шопеновская фиоритура в конце фразы)"""
        sc = sorted(x for x in range(bottom, top + 1) if x % 12 in {(2 + k + y) % 12 for y in (0, 2, 3, 5, 7, 8, 11)})
        run = sc[::-1][:12]
        for i, m in enumerate(run):
            self.note(m, beat + i / len(run), 1 / len(run), vel - 0.004 * i, part)

    def voicing(self, h, k, lo, hi, key, size=3):
        pcs = chord(h, k)[0]
        cands = []
        for s in range(lo, hi):
            if s % 12 not in pcs:
                continue
            v, m = [s], s
            while len(v) < size:
                m += 1
                if m % 12 in pcs:
                    v.append(m)
            if v[-1] <= hi:
                cands.append(v)
        prev = self.prev.get(key)
        best = cands[len(cands) // 2] if prev is None else min(cands, key=lambda v: sum(abs(a - b) for a, b in zip(v, prev)))
        self.prev[key] = best
        return best

    def bass_of(self, h, k, lo=34, hi=46):
        return next(x for x in range(lo, hi + 1) if x % 12 == chord(h, k)[1])

    # ---------------------------------------------------------------- аккомпанементы
    def arpeggio(self, bar, harms, k, vel=0.3, wide=True):
        """ноктюрн: бас на сильную долю, широкая ломаная восьмыми вверх и обратно (поверх полутора октав)"""
        b0 = bar * BAR
        span = BAR / len(harms)
        for i, h in enumerate(harms):
            t = b0 + i * span
            self.ped(t)
            pcs = chord(h, k)[0]
            bs = self.bass_of(h, k)
            up = [x for x in range(bs + 7, bs + 26) if x % 12 in pcs][:4 if wide else 3]
            figure = [bs] + up + up[-2:0:-1] if span == 4 else [bs] + up[:3]
            n = int(span * 2)
            for j in range(n):
                m = figure[j % len(figure)]
                self.note(m, t + j / 2, 0.5, vel + (0.07 if j == 0 else 0) - 0.01 * (j % 4), "Piano LH",
                          wdur=span if j == 0 else 0.5)

    def throb(self, bar, harms, k, vel=0.36, lo=67, hi=82):
        """Фролло: правая рука — мерно бьющиеся аккорды восьмыми (наваждение), голоса ведутся по ближайшему"""
        b0 = bar * BAR
        span = BAR / len(harms)
        for i, h in enumerate(harms):
            t = b0 + i * span
            self.ped(t)
            v = self.voicing(h, k, lo, hi, "throb%d" % lo, 3)
            for j in range(int(span * 2)):
                for m in v:
                    self.note(m, t + j / 2, 0.5, vel + (0.05 if j % 2 == 0 else 0), "Piano RH")
            self.note(self.bass_of(h, k, 29, 41), t, span, vel + 0.1, "Piano LH")

    def salon(self, bar, harms, k, vel=0.28):
        """Фебюс: лёгкий аккомпанемент — бас на 1 и 3, аккорды на 2 и 4 (стаккато под педалью)"""
        b0 = bar * BAR
        span = BAR / len(harms)
        for i, h in enumerate(harms):
            t = b0 + i * span
            self.ped(t)
            for q in range(int(span)):
                beat = t + q
                if (beat - b0) % 2 == 0:
                    bs = self.bass_of(h, k, 36, 48)
                    self.note(bs, beat, 1, vel + 0.06, "Piano LH")
                else:
                    for m in self.voicing(h, k, 53, 66, "salon", 3):
                        self.note(m, beat, 0.5, vel - 0.03, "Piano LH")

    def agitato(self, bar, harms, k, vel=0.42):
        """трио: бас октавой и триоли восьмыми вверх-вниз; в басу — хроматика Фролло (через бас аккорда)"""
        b0 = bar * BAR
        span = BAR / len(harms)
        for i, h in enumerate(harms):
            t = b0 + i * span
            self.ped(t)
            pcs = chord(h, k)[0]
            bs = self.bass_of(h, k, 31, 43)
            self.note(bs, t, span, vel + 0.12, "Piano LH")
            self.note(bs + 12, t, span, vel + 0.05, "Piano LH")
            up = [x for x in range(bs + 12 + 1, bs + 30) if x % 12 in pcs][:4]
            fig = up + up[-2:0:-1]
            for j in range(int(span * 3)):
                if j == 0:
                    continue
                self.note(fig[j % len(fig)], t + j / 3, 1 / 3, vel - 0.02, "Piano LH")

    def inner(self, bar, harms, k, vel=0.34, lo=58, hi=70):
        """средний голос трио — линия Квазимодо: по половинной на гармонию, ближайший звук аккорда (терция/септима),
        с триольным затактом, как его «речь» в первом куплете"""
        b0 = bar * BAR
        span = BAR / len(harms)
        for i, h in enumerate(harms):
            pcs, bs = chord(h, k)
            cand = [x for x in range(lo, hi + 1) if x % 12 in pcs and x % 12 != bs]
            prev = self.prev.get("inner", (lo + hi) // 2)
            m = min(cand, key=lambda x: (abs(x - prev), x))
            self.prev["inner"] = m
            self.note(m, b0 + i * span, span - T3 if span >= 2 else span, vel, "Piano RH")
            if span >= 2:
                self.note(m, b0 + i * span + span - T3, T3, vel - 0.05, "Piano RH")

    def apply_pedal(self, end):
        ch = sorted(set(self.pedal)) + [end]
        for e in self.p.events:
            if e["kind"] != "note":
                continue
            nxt = next((x for x in ch if x > e["t"] + 0.05), end)
            hold = nxt - e["t"] - 0.04
            if e["dur"] < 0.3:  # фиоритуры и группетто не копятся в кашу
                hold = min(hold, e["dur"] + 0.4)
            e["dur"] = max(e["dur"], hold)


# ===================================================================== строфы
def strophe_quasimodo(o, bar):
    """d-moll: мелодия в середине (как поёт тот, кто не привык петь), ровная ломаная в басу"""
    for i in range(8):
        o.arpeggio(bar + i, VERSE_H[i], 0, vel=0.27)
        o.melody(bar + i, VERSE[i], 0, vel=0.44 + 0.03 * (i in (2, 5)))
    for i in range(6):  # припев: h-moll → D, громче, мелодия октавой выше не уходит — остаётся в середине
        o.arpeggio(bar + 8 + i, REFR_H[i], 0, vel=0.3)
        o.melody(bar + 8 + i, REFR[i], 0, vel=0.5 + 0.02 * i)
    return bar + 14


def link(o, bar, k, vel=0.45):
    for i in range(2):
        o.arpeggio(bar + i, LINK_H[i], k, vel=0.28)
        o.melody(bar + i, LINK[i], k, vel=vel)
    return bar + 2


def strophe_frollo(o, bar):
    """f-moll: мелодия в левой руке (баритон), над ней бьющиеся аккорды; гармония темнее; припев — октавами, ff"""
    k = 3
    for i in range(8):
        o.throb(bar + i, VERSE_H_FROLLO[i], k, vel=0.34 + 0.02 * (i in (3, 4, 5, 6)))
        o.melody(bar + i, VERSE[i], k, part="Piano LH", vel=0.56, oct=-12)
    for i in range(6):  # припев d-moll → F: мелодия октавами наверху, аккорды бьются в середине
        o.throb(bar + 8 + i, REFR_H[i], k, vel=0.42, lo=57, hi=72)
        o.melody(bar + 8 + i, REFR[i], k, vel=0.66 + 0.01 * i, oct=12, double=True)
    return bar + 14


def strophe_phoebus(o, bar):
    """as-moll: высоко, в фиоритурах, лёгкий аккомпанемент; концы фраз — пассажи"""
    k = 6
    for i in range(8):
        o.salon(bar + i, VERSE_H[i], k, vel=0.27)
        notes = VERSE[i]
        if i in (3, 7):  # конец фразы — пассаж вместо последней доли
            notes = [x for x in notes if x[0] < 3]
        o.melody(bar + i, notes, k, vel=0.46, oct=12, orn=True)
        if i == 3:
            o.fioritura((bar + i) * BAR + 3, 2 + k + 12 * 7 - 12, 2 + k + 12 * 5, k)
        if i == 7:
            o.fioritura((bar + i) * BAR + 3, 2 + k + 12 * 7, 2 + k + 12 * 5 + 7, k)
    for i in range(6):
        o.salon(bar + 8 + i, REFR_H[i], k, vel=0.3)
        o.melody(bar + 8 + i, REFR[i], k, vel=0.52 + 0.015 * i, orn=True)
    return bar + 14


def trio(o, bar):
    """припев в f-moll втроём: октавы наверху (Фролло), тема Квазимодо в середине, бас — триоли агитато;
    два такта расширения и каденция на C7"""
    k = 6
    harms = REFR_H[:5] + [["G", "F#7"]]  # (+6) → Db | C7
    for i in range(6):
        o.agitato(bar + i, harms[i], k, vel=0.42 + 0.02 * i)
        o.melody(bar + i, REFR[i] if i < 5 else [(0, 2, 77 - 6), (2, 2, 76 - 6)], k, vel=0.74, oct=0, double=True)
    # линия Квазимодо в середине, под октавами — со второго такта
    for i in range(1, 6):
        o.inner(bar + i, harms[i], k, vel=0.36)
    # расширение: Db | C7 — каденция (пассаж вниз и вверх), фермата
    b = bar + 6
    o.agitato(b, ["G"], k, vel=0.5)  # (+6) → Db
    o.melody(b, [(0, 1, 80 - 6 + 6), (1, 1, 79), (2, 2, 77)], 0, vel=0.78, double=True)
    o.ped((b + 1) * BAR)
    for m in (36, 48, 55, 58, 64):
        o.note(m, (b + 1) * BAR, 4, 0.5, "Piano LH")
    run = [x for x in range(96, 59, -1) if x % 12 in (0, 4, 7, 10)]
    for i, m in enumerate(run):
        o.note(m, (b + 1) * BAR + i * 3 / len(run), 3 / len(run), 0.55 - 0.006 * i, "Piano RH")
    o.note(64, (b + 1) * BAR + 3, 1, 0.4, "Piano RH")
    return bar + 8


def coda(o, bar):
    """C7 → d-moll: тема Квазимодо внизу, обрывками; последний аккорд — D-dur, pp"""
    o.arpeggio(bar, ["Dm"], 0, vel=0.24)
    o.melody(bar, VERSE[0], 0, vel=0.38, oct=-12, part="Piano LH")
    o.arpeggio(bar + 1, ["A7"], 0, vel=0.22)
    o.melody(bar + 1, VERSE[1], 0, vel=0.34, oct=-12, part="Piano LH")
    o.arpeggio(bar + 2, ["Gm", "A7"], 0, vel=0.22)
    o.melody(bar + 2, [(0, 2, 70), (2, 2, 69)], 0, vel=0.34)
    o.arpeggio(bar + 3, ["Dm"], 0, vel=0.2)
    o.melody(bar + 3, [(0, 4, 74)], 0, vel=0.3)
    t = (bar + 4) * BAR
    o.ped(t)
    for j, m in enumerate((26, 38, 45, 50, 54, 57, 62, 66, 74)):  # D-dur, арпеджато снизу
        o.note(m, t, 8, 0.26 + (0.04 if m == 74 else 0), "Piano LH" if m < 60 else "Piano RH", late=0.09 * j)
    return bar + 6


def build(ctx):
    o = Noct()
    plan = [(0, "Вступление"), (2, "I. Квазимодо: d-moll"), (10, "припев: h → D"), (16, "Связка"),
            (18, "II. Фролло: f-moll"), (26, "припев: d → F"), (32, "Связка"), (34, "III. Фебюс: gis-moll"),
            (42, "припев: f → As"), (48, "Трио: f-moll"), (54, "Каденция"), (56, "Кода: d-moll")]
    # рубато: концы фраз оттянуты, трио рвётся вперёд, каденция и кода — широко
    for bb in (5, 9, 15, 21, 25, 31, 37, 41, 47):
        o.slow.append((bb * BAR + 2, bb * BAR + 4, 1.0, 1.35))
    o.slow += [(48 * BAR, 53 * BAR, 0.9, 0.9), (54 * BAR, 55 * BAR, 1.2, 1.5), (55 * BAR, 56 * BAR, 1.4, 2.2),
               (58 * BAR, 60 * BAR, 1.15, 1.6), (60 * BAR, 62 * BAR, 1.8, 2.0)]
    # вступление: левая рука одна
    o.arpeggio(0, ["Dm"], 0, vel=0.25)
    o.arpeggio(1, ["A7"], 0, vel=0.25)
    b = strophe_quasimodo(o, 2)
    b = link(o, b, 0)
    b = strophe_frollo(o, b)
    b = link(o, b, 3, vel=0.6)
    b = strophe_phoebus(o, b)
    b = trio(o, b)
    end = coda(o, b)
    # смена ключевых знаков, как писал бы Шопен: Фебюс — gis-moll (диезы), его припев и трио — f-moll (бемоли)
    o.p.meta["keys"] = [[b_ * BAR * SPB, k_] for b_, k_ in
                        ((10, "B minor"), (18, "F minor"), (26, "D minor"), (34, "G-sharp minor"), (42, "F minor"),
                         (56, "D minor"))]
    for bt, label in plan:
        o.p.mark(o.perf(bt * BAR), label)["wt"] = bt * BAR * SPB
    o.apply_pedal(o.perf(end * BAR) + 2)
    o.p.meta["beats"] = end * BAR
    return o.p
