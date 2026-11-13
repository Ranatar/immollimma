#!/usr/bin/env python3
"""Praeludium es-moll — Музыкальный момент № 2 Рахманинова (op. 16, 1896), каким его написал бы Бах (клавесин, ≈ 3:10).

Вторая редакция — по MIDI оригинала (присланному пользователем; в репозиторий не кладётся): 133 такта 2/4,
четверть = 92, секстоли шестнадцатыми. Взята схема ведения такт в такт (такт оригинала = половина такта 12/8):

  т. 1–16    фраза, повтор фразы, продолжение и каданс в es-moll         → A: P, P, Q (каданс с трелью)
  т. 17–40   фраза; она же на кварту выше; хроматические «вздохи»;      → A′: P; P в as-moll; цепь 7–6 над
             хроматический спуск в двух октавах                            хроматическим басом; спуск по цепи
                                                                           септаккордов, во второй раз — в теноре
  т. 41–44   тоника, мотор один, в теноре a–b                            → то же
  т. 45–76   уменьшённые и доминантсептаккорды над органными пунктами   → фантазия: пункты es–f–ges–fes–g–a,
             es → f → ges → fes → g → a; развороты арпеджио                пары V7 / vii°7, голос b–h–c; развороты
  фермата    на уменьшённом над a                                         → то же
  т. 77–84   каскады: Es-dur, c-moll, es-moll, Ces-dur                    → каскады вниз в тех же гармониях
  т. 85–124  дословная реприза т. 1–40                                    → реприза с перестановкой голосов
                                                                           (мелодия в теноре, мотор наверху)
  т. 125–133 тоника, вздохи a–b; Adagio, сопрано ges–f–fes–es,          → то же; vii°7 – V7 – неаполитанский –
             неаполитанский перед концом                                   I с пикардийской терцией

Своё (баховское): мелодия не цитируется — сохранён её жест (кружение вокруг доминанты, скачок, хроматическое
ламенто к вводному тону), синкопы оригинала стали задержаниями; секстоли — фигура разложенного аккорда с басом
на первой шестнадцатой (Brechung); романтические параллельные септаккорды — цепи 7–6 и квинтовые цепи; трели на
кадансах; реприза — с перестановкой голосов (двойной контрапункт), а не дословно.

    python3 -m kit run requests/bach-moment/piece.py --backend sso --parts
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from kit.events import Piece  # noqa: E402

BEAT = 60 / 88  # пунктирная четверть = 88 (четверть оригинала = 92)
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


class Bach:
    def __init__(self):
        self.p = Piece("Praeludium es-moll", bpm=132, meter=(12, 8), key="E-flat minor", seed=1896)
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



    # --- фигура с басом (Brechung): бас — первая шестнадцатая доли, дальше дуга по звукам аккорда
    def figure(self, beat, harm, bass, ceiling, pattern=(0, 1, 2, 3, 2, 1), vel=0.55, speed=6, floor=None):
        pcs, _ = chord(harm)
        ups = []
        m = max(bass + 3, floor or 0)
        while len(ups) < 3:
            m += 1
            if m % 12 in pcs:
                ups.append(m)
        if ups[-1] > ceiling:  # не залезать на мелодию: сдвинуть дугу вниз на октаву, но не ниже баса
            ups = [u - 12 if u - 12 > bass else u for u in ups]
            ups.sort()
        v = [bass] + ups
        step = 1 / speed
        pat = pattern if speed == 6 else (0, 2, 3)
        for j, k in enumerate(pat):
            mm = v[k]
            self.n(mm, beat + j * step, step, "LH", vel=vel + (0.07 if j == 0 else 0))  # мотор — левая рука целиком

    def upper_figure(self, beat, harm, floor, ceiling=86, pattern=(0, 1, 2, 3, 2, 1), vel=0.55):
        """мотор над мелодией (при перестановке голосов)"""
        pcs, _ = chord(harm)
        v, m = [], floor
        while len(v) < 4:
            m += 1
            if m % 12 in pcs:
                v.append(m)
        if v[-1] > ceiling:
            v = [x - 12 for x in v]
        for j, k in enumerate(pattern):
            self.n(v[k], beat + j / 6, 1 / 6, "RH", vel=vel + (0.07 if j == 0 else 0))

    def trill(self, beat, m, upper, beats, hand):
        """трель с верхней вспомогательной, окончание — на основном звуке"""
        k = int(beats * 12) - 2
        for j in range(k):
            self.n(upper if j % 2 == 0 else m, beat + j / 12, 1 / 12, hand, vel=0.55)
        self.n(m, beat + k / 12, 2 / 12, hand, vel=0.58)

    def melody(self, notes, beat0, hand, shift=0, vel=0.66, trill_at=None):
        for b, d, m in notes:
            if trill_at is not None and abs(b - trill_at) < 1e-9:
                self.trill(beat0 + b, m + shift, m + shift + 1, d, hand)
            else:
                self.n(m + shift, beat0 + b, d, hand, vel=vel)

    def sweep(self, beat, harm, lo, hi, up=True, vel=0.55):
        """фантазия: арпеджио через две руки на две доли (12 шестнадцатых)"""
        pcs, _ = chord(harm)
        tones = [m for m in range(lo, hi + 1) if m % 12 in pcs]
        k = max(1, len(tones) // 12)
        seq = tones[::k][:12] if up else tones[::-1][::k][:12]
        for j, m in enumerate(seq):
            self.n(m, beat + j / 6, 1 / 6, "RH" if m >= 60 else "LH", vel=vel + (0.05 if j % 6 == 0 else 0))


# ======================================================================================== материал
# Фраза P (2 такта 12/8 = 4 такта оригинала): кружение вокруг доминанты (b ces a b — circulatio) и скачок с
# хроматическим ламенто вниз к вводному тону (es ges f fes es d). Синкопы — как задержания: звук входит на
# середине доли и переходит через долю (как у Рахманинова — мелодия на слабой восьмой).
P_MEL = [(0, .5, 70), (.5, 1, 71), (1.5, 1, 69), (2.5, 1.5, 70),
         (4, .5, 75), (4.5, 1, 78), (5.5, .5, 77), (6, .5, 76), (6.5, .5, 75), (7, 1, 74)]
P_CH = ["Bb", "Cb", "Bb", "Bb7", "Ebm", "Ebm", "C7", "Bb7"]
P_BASS = [50, 51, 53, 56, 54, 54, 52, 50]                       # d es f as | ges ges e d
# Q (4 такта = 8 оригинала): секвенция хвоста вниз по ступеням и каданс в es-moll с трелью
Q_MEL = [(0, 1, 78), (1, .5, 77), (1.5, .5, 76), (2, .5, 75), (2.5, 1.5, 72),
         (4, 1, 77), (5, .5, 75), (5.5, .5, 74), (6, .5, 73), (6.5, 1.5, 70),
         (8, 1, 75), (9, .5, 73), (9.5, .5, 72), (10, .5, 71), (10.5, 1.5, 68),
         (12, 1, 68), (13, 1, 66), (14, 1, 65), (15, 1, 63)]
Q_CH = ["Ebm", "Bb7", "Abm", "F7", "Bb7", "Ebm", "Gb", "Ebm", "Cb", "Db7", "Abm", "Abm", "Abm", "Ebm", "Bb7", "Ebm"]
Q_BASS = [51, 50, 47, 45, 46, 42, 46, 39, 47, 49, 47, 44, 44, 46, 46, 39]
# спуск по цепи септаккордов (т. 33–40 оригинала): септима одного — терция следующего, полутонами вниз
D_CH = ["F7", "Bb7", "Eb7", "Abm", "Db7", "Gb", "Adim7", "Bb7"]
D_SOP = [75, 74, 73, 71, 71, 70, 69, 70]
D_BASS = [41, 46, 39, 44, 49, 42, 45, 46]


def tr(chs, k):
    """транспонировать имена аккордов на k полутонов"""
    names = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "Cb"]
    out = []
    for c in chs:
        root = c[0] + (c[1] if len(c) > 1 and c[1] in "b#" else "")
        q = c[len(root):]
        pcs_root = (NAMES[root[0]] + (-1 if root.endswith("b") else 0)) % 12
        out.append(names[(pcs_root + k) % 12] + q)
    return out


def section_A(s, b0, swap=False):
    """т. 1–16 оригинала: P, P, Q (8 тактов 12/8); swap — реприза с перестановкой голосов"""
    for rep in range(2):
        st = b0 + 8 * rep
        if not swap:
            s.melody(P_MEL, st, "RH")
            for k in range(8):
                s.figure(st + k, P_CH[k], P_BASS[k], 66, pattern=(0, 1, 2, 3, 2, 1) if rep == 0 else (0, 2, 1, 3, 1, 2))
        else:
            s.melody(P_MEL, st, "LH", shift=-12)
            for k in range(8):
                s.upper_figure(st + k, P_CH[k], 66)
                s.bass(st + k, P_BASS[k] - 12, 0.5, vel=0.58)
    st = b0 + 16
    if not swap:
        s.melody(Q_MEL, st, "RH", trill_at=14)
        for k in range(16):
            s.figure(st + k, Q_CH[k], Q_BASS[k], 62)
    else:
        s.melody(Q_MEL, st, "LH", shift=-12, trill_at=14)
        for k in range(16):
            s.upper_figure(st + k, Q_CH[k], 66)
            s.bass(st + k, Q_BASS[k] - 12 if Q_BASS[k] - 12 >= 29 else Q_BASS[k], 0.5, vel=0.58)


def section_A2(s, b0, swap=False):
    """т. 17–40 оригинала: P; P на кварту выше; цепь вздохов над хроматическим басом; спуск по септаккордам"""
    if not swap:
        s.melody(P_MEL, b0, "RH")
        for k in range(8):
            s.figure(b0 + k, P_CH[k], P_BASS[k], 66)
    else:
        s.melody(P_MEL, b0, "LH", shift=-12)
        for k in range(8):
            s.upper_figure(b0 + k, P_CH[k], 66)
            s.bass(b0 + k, P_BASS[k] - 12, 0.5, vel=0.58)
    # P на кварту выше (as-moll)
    st = b0 + 8
    s.melody(P_MEL, st, "RH", shift=5)
    for k, c in enumerate(tr(P_CH, 5)):
        s.figure(st + k, c, P_BASS[k] + 5 - 12 if P_BASS[k] + 5 > 58 else P_BASS[k] + 5, 70)
    # вздохи 7–6 над хроматическим басом as–g–ges–f–fes–es–d–des (по 2 доли)
    st = b0 + 16
    bass = [56, 55, 54, 53, 52, 51, 50, 49]
    for k, b in enumerate(bass):
        third = 3 if k % 2 == 0 else 4
        t = st + 2 * k
        sop7, sop6 = b + 10 + 12, b + 9 + 12
        if k == 0:
            s.n(sop6 + 1, t - 0.5, 0.5, "RH", vel=0.6)  # приготовление
        s.n(sop7, t, 0.5, "RH", vel=0.66)                # задержание (септима) на доле
        s.n(sop6, t + 0.5, 1.5, "RH", vel=0.6)           # разрешение в сексту
        for j in range(2):
            ups = [b + third + 12 * 0, b + 9, b + 12]
            v = [b - 12] + sorted(u if u > b - 12 else u + 12 for u in ups)
            for i, kk in enumerate((0, 1, 2, 3, 2, 1)):
                mm = v[kk]
                s.n(mm, t + j + i / 6, 1 / 6, "LH", vel=0.55 + (0.07 if i == 0 else 0))
    # спуск по цепи септаккордов, затем то же октавой ниже — мелодия уходит в тенор, мотор — наверх
    st = b0 + 32
    for half in range(2):
        for k in range(8):
            t = st + 8 * half + k
            sop = D_SOP[k] - 12 * half
            s.n(sop, t - 0.5, 1, "RH" if half == 0 else "LH", vel=0.66)
            if half == 0:
                s.figure(t, D_CH[k], D_BASS[k], 66)
            else:
                s.upper_figure(t, D_CH[k], 66)
                s.bass(t, D_BASS[k], 0.5, vel=0.6)
    # каданс в es-moll (трель на вводном тоне d)
    s.trill(st + 15.5, 62, 63, 0.5, "LH")


def link(s, b0, beats=8, slow_motor=False):
    """т. 41–44 оригинала: тоника, мотор один; в теноре — вздохи a–b"""
    for k in range(beats):
        t = b0 + k
        if k % 4 == 0:
            s.bass(t, 39, 4, vel=0.6)
        c = "Ebm" if (k % 2 == 0 or not slow_motor) else "Adim7"
        s.upper_figure(t, c, 63, pattern=(0, 1, 2, 3, 2, 1))
        if k % 2 == 0:
            s.n(57, t, 0.5, "LH", vel=0.6)
            s.n(58, t + 0.5, 1.5, "LH", vel=0.62)


# середина: органные пункты и пары аккордов (доминантсептаккорд / уменьшённый) — маршрут оригинала
B_UNITS = [(39, "Bb7", "Adim7"),       # es: V7 / vii°7 V над тоникой
           (41, "F7", "Fhd7"),         # f
           (42, "Db7", "Adim7"),       # ges
           (40, "E7", "Ehd7"),         # fes (= e): неаполитанская область
           (43, "D7", "Dbdim7"),       # g
           (45, "F7", "Adim7")]        # a — вводный к b: кульминация


def middle(s, b0):
    """т. 45–76 оригинала: фантазия над органными пунктами, хроматически восходящий голос, развороты-арпеджио"""
    t = b0
    for i, (ped, X, Y) in enumerate(B_UNITS):
        # пункт держится 8 долей; голос: r – r+1 – r+2 (b–h–c оригинала), r ∈ X, r+2 ∈ Y
        px, _ = chord(X)
        py, _ = chord(Y)
        r = next((m for m in range(55, 67) if m % 12 in px and (m + 2) % 12 in py), 58)
        s.bass(t, ped, 8, vel=0.66)
        s.bass(t, ped + 12, 8, vel=0.5)
        for j in range(8):
            c = X if (j // 2) % 2 == 0 else Y
            s.upper_figure(t + j, c, 66 if i < 5 else 70, pattern=(0, 1, 2, 3, 2, 1) if j % 2 == 0 else (3, 2, 1, 0, 1, 2),
                           vel=0.56 + 0.02 * i)
        s.melody([(0, 1, r), (1, 1, r + 1), (2, 2, r + 2), (4, 1, r), (5, 1, r + 1), (6, 2, r + 2)], t, "LH",
                 vel=0.64)
        t += 8
        if i in (0, 2):  # развороты по уменьшённому септаккорду (т. 49–52, 61–62 оригинала)
            for j in range(0, 8 if i == 0 else 4, 2):
                s.sweep(t + j, Y, 48 + 2 * j, 84 + j // 2, up=(j // 2) % 2 == 0)
            if i == 0:
                s.bass(t, ped, 8, vel=0.6)
            t += 8 if i == 0 else 4
    return t


def cascade(s, b0):
    """т. 77–84 оригинала: после ферматы — каскады вниз: Es-dur, c-moll, es-moll, Ces-dur"""
    plan = [("Eb", 39), ("Cm", 36), ("Cm", 36), ("Cm", 36), ("Ebm", 39), ("Ebm", 39), ("Cb", 35), ("Cb", 35)]
    for k, (c, b) in enumerate(plan):
        t = b0 + 2 * k
        s.bass(t, b, 2, vel=0.68)
        s.bass(t, b + 12, 2, vel=0.55)
        s.sweep(t, c, 48, 89, up=False, vel=0.6)


def coda(s, b0):
    """т. 125–133: тоника и вздохи; Adagio — сопрано ges–f–fes–es: vii°7, V7, неаполитанский, I (пикардийская терция)"""
    link(s, b0, 8)
    link(s, b0 + 8, 4, slow_motor=True)
    t = b0 + 12
    finals = [([39, 51, 57, 60, 63, 66], 1), ([39, 50, 56, 58, 62, 65], 1), ([44, 52, 56, 59, 64], 1),
              ([39, 51, 55, 58, 63, 67], 3)]
    for j, (ch_, d) in enumerate(finals):
        for i, m in enumerate(ch_):
            s.n(m, t, d, "RH" if m >= 60 else "LH", vel=0.62, late=0.05 * i)
        t += d


def build(ctx):
    s = Bach()
    # исполнение: фермата перед каскадами, каскады свободнее, Adagio
    B_END = 32 + 48 + 8 + 6 * 8 + 8 + 4      # конец середины (доли)
    ADAGIO = B_END + 16 + 80 + 12
    s.slow += [(B_END - 2, B_END, 2.0), (B_END, B_END + 16, 1.12), (ADAGIO - 2, ADAGIO, 1.3), (ADAGIO, ADAGIO + 6, 2.4)]
    b = 0
    marks = []
    marks.append((b, "A: фраза, фраза, каданс")); section_A(s, b); b += 32
    marks.append((b, "A′: на кварту выше, вздохи, спуск")); section_A2(s, b); b += 48
    marks.append((b, "Тоника")); link(s, b); b += 8
    marks.append((b, "B: фантазия над пунктами")); b_end = middle(s, b)
    # фермата на уменьшённом септаккорде над пунктом a
    for i, m in enumerate([45, 57, 60, 63, 66, 69, 72]):
        s.n(m, b_end - 2, 2, "RH" if m >= 60 else "LH", vel=0.66, late=0.04 * i)
    b = b_end
    marks.append((b, "Каскады")); cascade(s, b); b += 16
    marks.append((b, "Реприза: голоса переставлены")); section_A(s, b, swap=True); b += 32
    section_A2(s, b, swap=True); b += 48
    marks.append((b, "Кода, Adagio")); coda(s, b); b += 18
    for bt, label in marks:
        s.p.mark(s.perf(bt), label)["wt"] = bt * BEAT
    s.p.meta["beats"] = b
    return s.p
