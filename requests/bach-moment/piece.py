#!/usr/bin/env python3
"""Praeludium es-moll — Музыкальный момент № 2 Рахманинова (op. 16, 1896), каким его написал бы Бах (клавесин, ≈ 3:00).

Сохранено: настроение (суровая мелодия сквозь непрерывный вихрь), «сюжет» (вихрь с начала до конца → мелодия
проступает → нарастание → кульминация, мелодия «громадными аккордами» → буря стихает → Adagio: четыре аккорда,
плагальный каданс), ми-бемоль минор. Всё остальное — баховское:

  секстоли         → 12/8, сплошные шестнадцатые: фигура разложенного аккорда со скрытым многоголосием (Brechung)
  мелодия          → cantus в долгих нотах против мотора (как Гольдберг-вариация 26, прелюдия e-moll ХТК I);
                     патетика по-баховски: вздох полутоном, уменьшённая кварта, увеличенная секунда
  развитие          → перестановка голосов (cantus сверху, мотор снизу) и проведение в параллельном мажоре;
                     секвенции по квинтовому кругу с имитацией головы cantus; ламенто-бас (es–d–des–c–ces–b)
  крещендо          → у клавесина нет громкости: густеет фактура (2 → 3 → 4 голоса), органный пункт на доминанте,
                     мелодия аккордами; уменьшённый септаккорд с ферматой и выписанная каденция (как прелюдия c-moll)
  затихание         → мотор вдвое медленнее над тоническим пунктом; Adagio — четыре аккорда, плагально,
                     с пикардийской терцией (баховская норма конца минорной пьесы)

    python3 -m kit run requests/bach-moment/piece.py --backend sso --parts
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from kit.events import Piece  # noqa: E402

BEAT = 1.0  # пунктирная четверть = 60
SIX = BEAT / 6

NAMES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
QUAL = {"": (0, 4, 7), "m": (0, 3, 7), "7": (0, 4, 7, 10), "dim7": (0, 3, 6, 9), "dim": (0, 3, 6),
        "hd7": (0, 3, 6, 10), "m6": (0, 3, 7, 9)}


def chord(name):
    """'Ebm', 'Bb7', 'Cb', 'Adim7', 'Ebm/Bb' → (множество pc, бас pc)"""
    name, _, bass = name.partition("/")
    root = NAMES[name[0]]
    i = 1
    while i < len(name) and name[i] in "b#":
        root += -1 if name[i] == "b" else 1
        i += 1
    pcs = {(root + x) % 12 for x in QUAL[name[i:]]}
    b = root % 12
    if bass:
        b = NAMES[bass[0]] + sum(-1 if c == "b" else 1 for c in bass[1:])
    return pcs, b % 12


# --- cantus (ми-бемоль минор, 8 тактов по 4 доли): (доля, длительность, midi) — в теноре (A) или сопрано (B)
CANTUS = [(0, 1, 63), (1, 1, 70), (2, 1, 71), (3, 1, 70),          # es  b  ces b   — квинта вверх и вздох
          (4, 1, 68), (5, 1, 66), (6, 2, 65),                      # as  ges f
          (8, 1, 66), (9, 1, 73), (10, 1, 75), (11, 1, 73),        # ges des' es' des' — секвенция на терцию выше
          (12, 1, 71), (13, 1, 70), (14, 2, 68),                   # ces b   as
          (16, 1, 70), (17, 1, 71), (18, 1, 69), (19, 1, 70),      # b   ces a   b    — вводный тон к b-moll
          (20, 1, 73), (21, 1, 72), (22, 1, 66), (23, 1, 69),      # des c   ges a    — ум. кварта, ув. секунда
          (24, 1, 70), (25, 1, 75), (26, 1, 72), (27, 1, 69),      # b   es  c   a
          (28, 4, 70)]                                             # b — каданс в b-moll
HARM_A = ["Ebm", "Ebm", "Cb", "Bb",  "Abm", "Ebm/Gb", "Bb", "Bb7",
          "Cb", "Gb", "Abm", "Db7",  "Abm", "Gb", "Bb7", "Bb7",
          "Ebm", "Cb", "F7", "Bbm",  "Bbm", "F7", "Ebm/Gb", "F7",
          "Bbm", "Ebm", "Cdim", "F7",  "Bbm", "Bbm", "Bbm", "Bbm"]
# B: то же в параллельном мажоре (по ступеням es-moll → Ges-dur; гармония переносится тем же способом)
HARM_B = ["Gb", "Gb", "Ebm", "Db",  "Cb", "Gb/Bb", "Db", "Db7",
          "Ebm", "Bbm", "Cb", "Fhd7",  "Cb", "Bbm", "Db7", "Db7",
          "Gb", "Ebm", "Ab7", "Db",  "Db", "Ab7", "Gb/Bb", "Ab7",
          "Db", "Gb", "Abm", "Ab7",  "Db", "Db", "Db", "Db7"]
ES_MOLL = [3, 5, 6, 8, 10, 11, 13]   # es f ges as b ces des (от C=0, со сдвигом октавы)
GES_DUR = [6, 8, 10, 11, 13, 15, 17]


def to_ges(m):
    """по ступеням: es-moll → Ges-dur (повышенные ступени сохраняют повышение)"""
    rel = m - 3
    o, r = divmod(rel, 12)
    base = [0, 2, 3, 5, 7, 8, 10]
    k = min(range(7), key=lambda j: (abs(r - base[j]), base[j]))
    alt = r - base[k]
    if k in (5, 6):
        alt = 0  # повышенные VI–VII минора — натуральные в мажоре
    return 6 + 12 * o + [0, 2, 4, 5, 7, 9, 11][k] + alt


# C: секвенции (по 2 доли на аккорд) и ламенто
HARM_C1 = ["Gb", "Gb", "Cb", "Cb",  "Fhd7", "Fhd7", "Bb7", "Bb7",  "Ebm", "Ebm", "Abm", "Abm",
           "Db7", "Db7", "Gb", "Gb",  "Cb", "Cb", "Fhd7", "Fhd7",  "Bb7", "Bb7", "Ebm", "Eb7"]
# ламенто: i – V6 (vii°7) – v6 (III6/4) – IV6 (vii°7/C) – iv6 (VI) – V; бас — по такту на ступень
HARM_C2 = ["Ebm", "Ebm", "Abm/Eb", "Abm/Eb",  "Bb/D", "Bb/D", "Ddim7", "Ddim7",  "Bbm/Db", "Bbm/Db", "Gb/Db", "Gb/Db",
           "Ab/C", "Ab/C", "Adim7/C", "Adim7/C",  "Abm/Cb", "Abm/Cb", "Cb", "Cb",  "Bb7", "Bb7", "Bb7", "Bb7"]
# D: органный пункт b; мелодия аккордами
HARM_D = ["Ebm/Bb", "Ebm/Bb", "Cb/Bb", "Bb7",  "Abm/Bb", "Ebm/Bb", "Bb7", "Bb7",
          "Ebm/Bb", "Abm/Bb", "Ebm/Bb", "Bb7",  "Adim7/Bb", "Adim7/Bb", "Adim7/Bb", "Adim7/Bb"]
HEAD = [(0, 1, 0), (1, 1, 7), (2, 1, 8), (3, 1, 7)]  # голова cantus: 1–5–♭6–5 (от тоники)


class Bach:
    def __init__(self):
        self.p = Piece("Praeludium es-moll", bpm=90, meter=(12, 8), key="E-flat minor", seed=1896)
        self.p.meta["subtitle"] = "Музыкальный момент № 2 Рахманинова, как его написал бы Бах"
        self.p.meta["sends"] = {"keys": 0.3}
        self.prev = {"RH": None, "LH": None}
        self.slow = []  # [(доля начала, доля конца, множитель)] — исполнение медленнее записанного

    # --- время: записанные доли → секунды исполнения (фермата, каденция, Adagio)
    def perf(self, beat):
        s = 0.0
        pts = sorted(self.slow)
        for b0, b1, f in pts:
            if beat <= b0:
                break
            s += (min(beat, b1) - b0) * (f - 1)
        return beat * BEAT + s

    def n(self, m, beat, dur, hand, vel=0.6, late=0.0):
        t0, t1 = self.perf(beat), self.perf(beat + dur)
        e = self.p.note("hpsd", m, t0 + late, max(0.05, (t1 - t0) * 0.92), vel=vel, gain=0.5, release=0.25,
                        pan=(m - 62) / 80, part=f"Harpsichord {hand}")
        e["wt"], e["wdur"] = beat * BEAT, dur * BEAT
        return e

    def voicing(self, harm, lo, hi, hand, size=4):
        """ближайшее к прежнему расположение аккорда: size звуков подряд по звукам аккорда"""
        pcs, _ = chord(harm)
        cands = []
        for start in range(lo, hi - 12):
            if start % 12 not in pcs:
                continue
            v = [start]
            m = start
            while len(v) < size:
                m += 1
                if m % 12 in pcs:
                    v.append(m)
            if v[-1] <= hi:
                cands.append(v)
        prev = self.prev[hand]
        if prev is None:
            best = cands[len(cands) // 2]
        else:
            best = min(cands, key=lambda v: sum(abs(a - b) for a, b in zip(v, prev)))
        self.prev[hand] = best
        return best

    def motor(self, beat, harm, hand, lo, hi, pattern=(0, 1, 2, 3, 2, 1), vel=0.55, speed=6):
        """фигура на одну долю: шестнадцатые (speed=6) или восьмые (speed=3)"""
        v = self.voicing(harm, lo, hi, hand)
        step = 1 / speed
        pat = pattern if speed == 6 else (0, 2, 3)
        for j, k in enumerate(pat):
            self.n(v[k], beat + j * step, step, hand, vel=vel + (0.06 if j == 0 else 0))

    def line(self, notes, beat0, hand, shift=0, vel=0.66, chordal=None):
        """cantus; chordal=список гармоний по долям — мелодия аккордами: два ближайших звука аккорда ниже"""
        for b, d, m in notes:
            self.n(m + shift, beat0 + b, d, hand, vel=vel)
            if chordal:
                pcs, _ = chord(chordal[int(b)])
                below = [x for x in range(m + shift - 1, m + shift - 13, -1) if x % 12 in pcs][:2]
                for x in below:
                    self.n(x, beat0 + b, d, hand, vel=vel - 0.08)

    def bass(self, beat, m, dur, vel=0.62):
        self.n(m, beat, dur, "LH", vel=vel)


def build(ctx):
    s = Bach()
    # исполнение: фермата на ум. септаккорде, каденция свободнее, затихание, Adagio
    s.slow += [(124, 128, 1.8), (128, 132, 1.25), (140, 148, 1.15), (148, 156, 2.4)]
    marks = [(0, "A: cantus в теноре"), (32, "B: перестановка, Ges-dur"), (64, "C: секвенции"),
             (88, "Ламенто-бас"), (112, "D: пункт на доминанте"), (124, "Фермата, каденция"),
             (132, "Затихание"), (148, "Adagio")]
    # --- A (такты 1–8): мотор в правой руке, cantus в левой (тенор)
    for k, h in enumerate(HARM_A):
        s.motor(k, h, "RH", 67, 88)
    s.line(CANTUS, 0, "LH", shift=-12)
    # --- B (9–16): перестановка голосов, Ges-dur; cantus сверху, мотор в левой; бас на сильных долях
    cant_b = [(b, d, to_ges(m)) for b, d, m in CANTUS]
    for k, h in enumerate(HARM_B):
        s.motor(32 + k, h, "LH", 48, 66)
        if k % 2 == 0:
            _, bp = chord(h)
            s.bass(32 + k, 36 + (bp - 36) % 12, 2, vel=0.55)
    s.line(cant_b, 32, "RH", shift=0)
    # --- C1 (17–22): секвенции по квинтам; мотор переходит из руки в руку по тактам, голова cantus в имитации
    for k, h in enumerate(HARM_C1):
        beat = 64 + k
        bar = k // 4
        hand = "RH" if bar % 2 == 0 else "LH"
        s.motor(beat, h, hand, 67 if hand == "RH" else 46, 88 if hand == "RH" else 64)
        if k % 4 == 0:  # голова cantus (1–5–♭6–5) — в другой руке; «♭6» — ближайший звук следующего аккорда
            pcs, root = chord(HARM_C1[k])
            pcs2, _ = chord(HARM_C1[k + 2])
            base = (54 if hand == "RH" else 70) + (root - (54 if hand == "RH" else 70)) % 12
            fifth = base + 7
            six = next(x for x in range(fifth + 1, fifth + 6) if x % 12 in pcs2)
            back = min((x for x in range(fifth - 3, fifth + 4) if x % 12 in pcs2), key=lambda x: abs(x - fifth))
            other = "LH" if hand == "RH" else "RH"
            s.line([(0, 1, base), (1, 1, fifth), (2, 1, six), (3, 1, back)], beat, other, vel=0.64)
    # --- C2 (23–28): ламенто-бас es–d–des–c–ces–b; мотор в правой, вздохи cantus в теноре
    lament = [51, 50, 49, 48, 47, 46]
    for k, h in enumerate(HARM_C2):
        s.motor(88 + k, h, "RH", 65, 88)
    for j, m in enumerate(lament):
        s.bass(88 + 4 * j, m - 12, 4, vel=0.62)
    sighs = [(0, 1, 68), (1, 1, 66), (2, 2, 63), (4, 1, 67), (5, 1, 65), (6, 2, 65), (8, 1, 66), (9, 1, 65),
             (10, 2, 66), (12, 1, 65), (13, 1, 63), (14, 2, 63), (16, 1, 64), (17, 1, 63), (18, 2, 63),
             (20, 2, 62), (22, 2, 62)]  # вздохи: задержание на доле — разрешение на секунду вниз
    s.line(sighs, 88, "LH", shift=0, vel=0.6)
    # --- D (29–32): органный пункт b; мотор в левой над пунктом, мелодия аккордами (голова cantus, расширенная)
    for k, h in enumerate(HARM_D):
        beat = 112 + k
        s.motor(beat, h, "LH", 46, 64, vel=0.6)
        if k % 4 == 0:
            s.bass(beat, 34, 4, vel=0.68)
    climax = [(0, 1, 75), (1, 1, 82), (2, 1, 83), (3, 1, 82),          # es' b' ces'' b' — голова, октавой выше
              (4, 1, 80), (5, 1, 78), (6, 2, 77),
              (8, 1, 78), (9, 1, 80), (10, 1, 82), (11, 1, 86),
              (12, 4, 81)]                                               # a' — уменьшённый септаккорд, фермата
    s.line(climax, 112, "RH", chordal=HARM_D)
    # фермата и выписанная каденция (т. 32–33): тридцатьвторые вниз по ум. септаккорду, затем вверх к доминанте
    run = [81, 78, 75, 72, 69, 66, 63, 60, 57, 54, 51, 48]
    for j, m in enumerate(run):
        s.n(m, 128 + j / 6, 1 / 6, "RH" if m >= 60 else "LH", vel=0.6)
    up = [46, 50, 53, 56, 58, 62, 65, 68, 70, 74, 77, 80]
    for j, m in enumerate(up):
        s.n(m, 130 + j / 6, 1 / 6, "RH" if m >= 60 else "LH", vel=0.62)
    # --- E (34–37): буря стихает — мотор восьмыми над тоническим пунктом, голова cantus в последний раз
    s.prev["RH"] = None
    harm_e = ["Ebm", "Ebm", "Cb/Eb", "Ebm", "Abm/Eb", "Abm/Eb", "Bb7/Eb", "Bb7/Eb",
              "Ebm", "Ebm", "Cb/Eb", "Ebm", "Abm/Eb", "Abm/Eb", "Ebm", "Ebm"]
    for k, h in enumerate(harm_e):
        s.motor(132 + k, h, "RH", 63, 84, speed=3 if k < 12 else 3, vel=0.52)
        if k % 4 == 0:
            s.bass(132 + k, 39, 4, vel=0.55)
    s.line([(b, d, 63 - 12 + iv) for b, d, iv in HEAD] + [(4, 2, 59), (6, 2, 58)], 132, "LH", vel=0.6)
    s.line([(8, 1, 63), (9, 1, 58), (10, 1, 59), (11, 1, 58), (12, 2, 59), (14, 2, 58)], 132, "LH", vel=0.55)
    # --- Adagio (38–39): четыре аккорда, плагально; последний — с пикардийской терцией; арпеджато, как на клавесине
    finals = [[39, 51, 56, 59, 63, 68], [39, 51, 54, 58, 63, 66], [39, 51, 56, 59, 63, 65], [39, 51, 55, 58, 63, 67]]
    for j, ch_ in enumerate(finals):
        b = 148 + 2 * j
        for i, m in enumerate(ch_):
            m = max(29, m)
            s.n(m, b, 2 if j < 3 else 4, "RH" if m >= 60 else "LH", vel=0.62, late=0.045 * i)
    for b, label in marks:
        s.p.mark(s.perf(b), label)["wt"] = b * BEAT
    return s.p
