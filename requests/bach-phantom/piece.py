#!/usr/bin/env python3
"""Praeludium d-moll für die Orgel — «Призрак Оперы» (заглавный дуэт), каким его написал бы Бах (≈ 3:40).

Схема — по MIDI дуэта (♩=125, 127 т.): органное вступление (трезвучия хроматически вниз над пульсирующим басом),
куплеты i–iv–VII–i — каждый в новой, более высокой тональности, между ними — снова вступление; дуэт; финальный
вокализ всё выше по целым тонам. У Баха это ритурнельная форма для органа:

  ритурнель (R)   органное вступление: tirata вниз по трезвучию, «барабанный бас» (Trommelbass — повторяющиеся
                  восьмые: барочный двойник рокового баса), хроматический бас ламенто d–cis–c–h под цепью
                  секстаккордов, VI – V с задержанием 4–3
  эпизод 1        «Кристина»: песенная тема (своя: затакт повторяющимися нотами, долгие ноты, нисхождение) в
                  сопрано на тихом регистре, ходящий бас в педали; секвенция; каданс в g-moll
  R в g-moll      ритурнель в новой тональности (как каждый новый куплет — выше)
  эпизод 2        «Призрак»: та же тема в теноре на язычковом регистре, над ней фигурация шестнадцатыми; каданс в a-moll
  R в a-moll
  эпизод 3        «дуэт»: тема в теноре, затем в сопрано, затем вместе параллельными децимами
  кульминация      «монте» (C7–F, D7–g, E7–a): токкатные пассажи всё выше — двойник вокализа; органный пункт на
                  доминанте, ум. септаккорд с ферматой, каденция
  R в d-moll      возврат, плагальный каданс, пикардийская терция (у Уэббера конец в ля миноре)

Мелодия «Призрака» не цитируется.

    python3 -m kit run requests/bach-phantom/piece.py --parts
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from kit.events import Piece  # noqa: E402

SPB = 60 / 84
NAMES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
QUAL = {"": (0, 4, 7), "m": (0, 3, 7), "7": (0, 4, 7, 10), "dim7": (0, 3, 6, 9), "dim": (0, 3, 6)}
NOTE = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]


def chord(name, k=0):
    """'Dm', 'A7', 'C#dim7', 'G/B' → (pcs, bass pc), транспонировано на k"""
    name, _, bass = name.partition("/")
    root = NAMES[name[0]]
    i = 1
    while i < len(name) and name[i] in "b#":
        root += -1 if name[i] == "b" else 1
        i += 1
    pcs = {(root + k + x) % 12 for x in QUAL[name[i:]]}
    b = root
    if bass:
        b = NAMES[bass[0]] + sum(-1 if c == "b" else 1 for c in bass[1:])
    return pcs, (b + k) % 12


def near(pc, ref):
    """высота с данным pc, ближайшая к ref"""
    return min((m for m in range(ref - 6, ref + 7) if m % 12 == pc), key=lambda m: abs(m - ref))


class Org:
    def __init__(self):
        self.p = Piece("Praeludium d-moll (Призрак Оперы, как написал бы Бах)", bpm=84, meter=(4, 4), key="D minor",
                       seed=1986)
        self.p.meta["subtitle"] = "für die Orgel"
        self.p.meta["sends"] = {"organ": 0.45}
        self.prev = {}
        self.slow = []

    def perf(self, beat):
        s = 0.0
        for b0, b1, f in sorted(self.slow):
            if beat <= b0:
                break
            s += (min(beat, b1) - b0) * (f - 1)
        return (beat + s) * SPB

    def n(self, m, beat, dur, staff, reg="org_quiet", vel=0.6, late=0.0, legato=0.92):
        if reg == "org_quiet" and m < 36:
            reg = "org_loud"
        t0, t1 = self.perf(beat), self.perf(beat + dur)
        e = self.p.note(reg, m, t0 + late, max(0.05, (t1 - t0) * legato), vel=vel, gain=0.5, release=0.3,
                        pan={"RH": 0.2, "LH": -0.1, "Ped": 0.0}[staff], part=f"Organ {staff}" if staff != "Ped" else "Organ Pedal")
        e["wt"], e["wdur"] = beat * SPB, dur * SPB
        return e

    def voicing(self, harm, k, lo, hi, key, size=3):
        pcs, _ = chord(harm, k)
        cands = []
        for start in range(lo, hi):
            if start % 12 not in pcs:
                continue
            v, m = [start], start
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

    def ch(self, harm, k, beat, dur, staff, lo, hi, reg="org_quiet", vel=0.55, size=3):
        for m in self.voicing(harm, k, lo, hi, staff + reg, size):
            self.n(m, beat, dur, staff, reg, vel)

    def line(self, notes, beat0, staff, reg, k=0, vel=0.66, trill_at=None):
        for b, d, m in notes:
            if trill_at is not None and abs(b - trill_at) < 1e-9:
                steps = int(d * 8) - 1
                for j in range(steps):
                    self.n(m + k + (2 if j % 2 == 0 else 0) - (1 if (m + k) % 12 in (1, 4, 6, 9, 11) and j % 2 == 0 else 0),
                           beat0 + b + j / 8, 1 / 8, staff, reg, vel - 0.05, legato=0.95)
                self.n(m + k, beat0 + b + steps / 8, 1 / 8, staff, reg, vel)
            else:
                self.n(m + k, beat0 + b, d, staff, reg, vel)

    def walk(self, beat0, harms, k, tonic=None, lo=36, hi=55, reg="org_quiet", vel=0.55):
        """ходящий бас педали четвертями: на смене гармонии — бас аккорда, на остальных долях — другой звук того же
        аккорда (ближайший); восьмая-проходящая — только диатоническая (натуральный минор от tonic) и не на
        полутон от звуков аккорда, когда до следующего звука терция"""
        tonic = k if tonic is None else tonic
        scale = {(tonic + 2 + x) % 12 for x in (0, 2, 3, 5, 7, 8, 10)}  # d-moll = тоника D (pc 2)
        seq = []
        prev = None
        for j, h in enumerate(harms):
            pcs, b = chord(h, k)
            ref = prev if prev is not None else (lo + hi) // 2
            if j == 0 or harms[j - 1] != h:
                m = min((x for x in range(lo, hi + 1) if x % 12 == b), key=lambda x: abs(x - ref))
            else:  # та же гармония: шаг к другому звуку трезвучия (септима в бас не идёт), не повторяя предыдущий
                tri, _ = chord(h.split("/")[0].replace("7", ""), k)
                m = min((x for x in range(lo, hi + 1) if x % 12 in tri and x != ref), key=lambda x: (abs(x - ref), x))
            seq.append((m, pcs))
            prev = m
        for j, (m, pcs) in enumerate(seq):
            nxt = seq[j + 1][0] if j + 1 < len(seq) else None
            pas = None
            if nxt is not None and abs(nxt - m) in (3, 4):
                d = 1 if nxt > m else -1
                for x in range(m + d, nxt, d):
                    if x % 12 in scale and all(min((x - p) % 12, (p - x) % 12) != 1 for p in pcs):
                        pas = x
                        break
            if pas is None:
                self.n(m, beat0 + j, 1, "Ped", reg, vel + 0.05, legato=0.85)
            else:
                self.n(m, beat0 + j, 0.5, "Ped", reg, vel + 0.05)
                self.n(pas, beat0 + j + 0.5, 0.5, "Ped", reg, vel)

    def accomp(self, beat0, harms, k, melody, lo=53, hi=67, reg="org_quiet", vel=0.5):
        """средние голоса левой руки: аккорд меняется вместе с гармонией; где мелодия держит долгую ноту, левая рука
        отвечает восьмыми (комплементарный ритм), где мелодия движется — держит"""
        onsets = {round(b * 2) / 2 for b, d, m in melody}
        j = 0
        while j < len(harms):
            e = j + 1
            while e < len(harms) and harms[e] == harms[j]:
                e += 1
            v = self.voicing(harms[j], k, lo, hi, "acc" + reg, 2)
            t = j
            while t < e:  # по долям внутри гармонии
                if t not in onsets:  # мелодия держит — ответ восьмыми
                    self.n(v[0], beat0 + t, 0.5, "LH", reg, vel)
                    self.n(v[1], beat0 + t + 0.5, 0.5, "LH", reg, vel)
                    t += 1
                    continue
                # мелодия ударяет: аккорд держится до следующей доли-ответа или конца гармонии
                u = t + 1
                while u < e and u in onsets:
                    u += 1
                for m in v:
                    self.n(m, beat0 + t, u - t, "LH", reg, vel)
                t = u
            j = e


# ===================================================================== ритурнель
def ritornello(o, b0, k, end="tonic", full=True):
    """4 такта: tirata вниз и аккорд над барабанным басом; ламенто d–cis–c–h; VI – V (4–3); конец"""
    reg = "org_loud" if full else "org_quiet"
    D = 62 + k  # D4
    # такт 1: tirata — шестнадцатые вниз по трезвучию от D6, затем аккорд
    tir = [D + 24, D + 19, D + 15, D + 12, D + 7, D + 3, D, D - 5]
    for j, m in enumerate(tir):
        o.n(m, b0 + j / 4 * 1, 0.25, "RH", reg, 0.7)
    o.ch("Dm", k, b0 + 2, 2, "RH", 62, 82, reg, 0.68)
    for j in range(8):  # Trommelbass
        o.n(D - 12, b0 + j * 0.5, 0.5, "LH", reg, 0.62 + (0.06 if j % 2 == 0 else 0), legato=0.7)
    o.n(D - 24, b0, 4, "Ped", "org_loud", 0.7)
    # такт 2: ламенто под секстаккордами (7–6 в верхнем голосе)
    lam = [("Dm", 0), ("A/C#", -1), ("Am/C", -2), ("G/B", -3)]
    for j, (h, sh) in enumerate(lam):
        o.n(D - 24 + sh + 12, b0 + 4 + j, 1, "Ped", "org_loud", 0.68)
        o.ch(h, k, b0 + 4 + j, 1, "LH", 50 + k, 64 + k, reg, 0.6)
    o.n(D + 19, b0 + 4, 3, "RH", reg, 0.66)   # a'' держится над спуском баса — и уступает g''
    o.n(D + 17, b0 + 7, 1, "RH", reg, 0.66)
    # такт 3: VI – V с задержанием 4–3
    o.n(D - 24 + 8, b0 + 8, 2, "Ped", "org_loud", 0.7)
    o.n(D - 24 + 7, b0 + 10, 2, "Ped", "org_loud", 0.7)
    o.ch("Bb", k, b0 + 8, 2, "LH", 53 + k, 66 + k, reg, 0.6)
    o.ch("A", k, b0 + 10, 2, "LH", 52 + k, 66 + k, reg, 0.6)
    for b, d, m in [(8, 1, D + 15), (9, 1, D + 12), (10, 1, D + 12), (11, 1, D + 11)]:  # f d | d cis (4–3)
        o.n(m, b0 + b, d, "RH", reg, 0.66)
    # такт 4
    if end == "tonic":
        o.ch("Dm", k, b0 + 12, 4, "RH", 62 + k, 80 + k, reg, 0.66)
        o.n(D - 24, b0 + 12, 4, "Ped", "org_loud", 0.7)
        for j in range(8):
            o.n(D - 12, b0 + 12 + j * 0.5, 0.5, "LH", reg, 0.6, legato=0.7)
    else:  # к песне: доминанта и затакт
        o.ch("A7", k, b0 + 12, 3, "RH", 61 + k, 79 + k, reg, 0.64)
        o.n(D - 24 + 7, b0 + 12, 3, "Ped", "org_loud", 0.68)
        for j in range(6):
            o.n(D - 12 - 5, b0 + 12 + j * 0.5, 0.5, "LH", reg, 0.58, legato=0.7)


# ===================================================================== песня
# своя тема в манере куплета: затакт повторяющимися нотами, долгие ноты, нисхождение; d-moll, 4 такта:
# i – V | VI – VII – iv | VII7 – III – iv6 | V  (гармония следует за каждой долей мелодии)
SONG = [(-1, .5, 69), (-.5, .5, 69),
        (0, 1.5, 74), (1.5, .5, 73), (2, 1, 74), (3, 1, 76),
        (4, 2, 77), (6, 1, 76), (7, 1, 74),
        (8, 1.5, 72), (9.5, .5, 70), (10, 1, 69), (11, 1, 67),
        (12, 3, 69)]
SONG_H = ["Dm", "Dm", "Dm", "A7", "Bb", "Bb", "C", "Gm", "C", "C7", "F", "Gm/Bb", "A", "A", "A", "A7"]
# продолжение: секвенция головы (по терции вверх) и каданс в субдоминанте (g-moll)
SEQ = [(-1, .5, 72), (-.5, .5, 72),
       (0, 1.5, 77), (1.5, .5, 76), (2, 1, 77), (3, 1, 79),
       (4, 2, 81), (6, 1, 79), (7, 1, 77),
       (8, 1.5, 79), (9.5, .5, 78), (10, 1, 79), (11, 1, 81),
       (12, 2, 82), (14, 1, 81), (15, 1, 79)]
SEQ_H = ["F", "F", "F", "C7", "F", "F", "C", "F", "Gm", "Gm", "Gm", "D7", "Gm", "Gm", "D7", "Gm"]
CAD = [(0, 1, 75), (1, 1, 74), (2, 1, 72), (3, 1, 70),
       (4, 1, 69), (5, .5, 70), (5.5, .5, 72), (6, 2, 74),
       (8, 2, 70), (10, 2, 69),
       (12, 4, 67)]
CAD_H = ["Cm", "Gm", "Cm", "Gm/Bb", "D7", "Gm", "D7", "D7", "Gm/D", "Gm/D", "D7", "D7", "Gm", "Gm", "Gm", "Gm"]


def episode(o, b0, k, voice="S"):
    """12 тактов: песня, секвенция, каданс (в тональности на кварту выше — как у куплетов «Призрака»)"""
    melody = SONG + [(16 + b, d, m) for b, d, m in SEQ] + [(32 + b, d, m) for b, d, m in CAD]
    harms = SONG_H + SEQ_H + CAD_H
    if voice == "S":  # «Кристина»: сопрано на тихом регистре, левая рука — средние голоса, педаль ходит
        o.line(melody, b0, "RH", "org_quiet", k=k, vel=0.68, trill_at=42)
        o.accomp(b0, harms, k, melody)
    else:  # «Призрак»: тенор на язычковом регистре, над ним фигурация шестнадцатыми
        o.line(melody, b0, "LH", "org_reed", k=k - 12, vel=0.7, trill_at=42)
        for j, h in enumerate(harms):
            v = o.voicing(h, k, 74, 93, "fig", 4)
            for i, kk in enumerate((0, 1, 2, 3)):
                o.n(v[kk], b0 + j + i / 4, 0.25, "RH", "org_quiet", 0.5 + (0.06 if i == 0 else 0))
    o.walk(b0, harms[:16], k, k)
    o.walk(b0 + 16, harms[16:], k, k + 5)  # секвенция и каданс — уже в g-moll (относительно k)


def duet(o, b0, k):
    """дуэт: песня в теноре (язычок), ответ — в сопрано, затем оба параллельными децимами; к органному пункту"""
    o.line(SONG, b0, "LH", "org_reed", k=k - 12, vel=0.7)
    for j, h in enumerate(SONG_H):
        v = o.voicing(h, k, 74, 93, "fig", 3)
        o.n(v[j % 3], b0 + j, 1, "RH", "org_quiet", 0.48)
    o.walk(b0, SONG_H, k)
    # ответ сопрано — тема из d-moll в a-moll на квинту выше уже позади; теперь тема в d-moll (возврат к тонике)
    o.line(SONG, b0 + 16, "RH", "org_quiet", k=0, vel=0.7)
    o.accomp(b0 + 16, SONG_H, 0, SONG)
    o.walk(b0 + 16, SONG_H, 0)
    # вместе: голова песни в сопрано и децимой ниже в теноре, секвенция вверх по ступеням к доминанте
    # вместе — в октаву (как герои поют вместе в кульминации дуэта); голова песни всё выше: d – g – a
    for st, kk in ((0, 0), (4, 5), (8, 7)):
        hd = [(b, d, m) for b, d, m in SONG if 0 <= b < 4]
        o.line(hd, b0 + 32 + st, "RH", "org_quiet", k=kk, vel=0.7)
        o.line(hd, b0 + 32 + st, "LH", "org_reed", k=kk - 12, vel=0.66)
        o.walk(b0 + 32 + st, SONG_H[:4], kk, kk)
    # связка: доминанта к фа мажору — первая ступень «монте»
    o.ch("C7", 0, b0 + 44, 4, "RH", 64, 80, "org_quiet", 0.6, size=4)
    o.n(36, b0 + 44, 4, "Ped", "org_quiet", 0.62)


def climax(o, b0):
    """«монте» (C7–F, D7–g, E7–a): токкатные пассажи всё выше; органный пункт на доминанте; ум. септаккорд с ферматой,
    каденция; → ритурнель"""
    units = [("C7", "F", 0), ("D7", "Gm", 1), ("E7", "Am", 2)]
    for u, (h1, h2, i) in enumerate(units):
        for j, h in enumerate((h1, h2)):
            st = b0 + 8 * u + 4 * j
            pcs, b = chord(h)
            tones = [m for m in range(60 + 3 * i, 90) if m % 12 in pcs]
            run = tones[: 16]
            for q in range(16):
                o.n(run[q % len(run)], st + q / 4, 0.25, "RH", "org_loud", 0.62 + (0.06 if q % 4 == 0 else 0))
            o.ch(h, 0, st, 2, "LH", 50, 64, "org_loud", 0.6)
            o.ch(h, 0, st + 2, 2, "LH", 50, 64, "org_loud", 0.6)
            o.n(near(b, 38), st, 4, "Ped", "org_loud", 0.68)
    # органный пункт на A: ум. септаккорд и A7 по очереди, вершина выше на целый тон каждые два такта
    st = b0 + 24
    tops = [86, 88, 89]
    for u in range(3):
        for j, h in enumerate(("C#dim7", "A7")):
            sb = st + 8 * u + 4 * j
            pcs, _ = chord(h)
            tones = [m for m in range(64, tops[u] + 1) if m % 12 in pcs]
            seq = tones[-8:] + tones[-8:][::-1]
            for q in range(16):
                o.n(seq[q], sb + q / 4, 0.25, "RH", "org_loud", 0.64 + (0.06 if q % 4 == 0 else 0))
            o.ch(h, 0, sb, 4, "LH", 52, 66, "org_loud", 0.62, size=4)
        o.n(33, st + 8 * u, 8, "Ped", "org_loud", 0.72)
    # фермата на уменьшённом септаккорде и каденция вниз
    sf = st + 24
    for m in (37, 49, 55, 58, 61, 64, 67, 70, 73):
        o.n(m, sf, 4, "RH" if m >= 60 else ("LH" if m >= 45 else "Ped"), "org_loud", 0.72)
    run = [89, 85, 82, 79, 76, 73, 70, 67, 64, 61, 58, 55, 52, 49, 45, 43]
    for j, m in enumerate(run):
        o.n(m, sf + 4 + j / 4, 0.25, "RH" if m >= 60 else "LH", "org_loud", 0.64)
    return sf + 8


def finale(o, b0):
    """ритурнель в d-moll и конец: плагально (g/d – D) с пикардийской терцией над педалью d"""
    ritornello(o, b0, 0, end="tonic")
    b = b0 + 16
    o.n(26, b, 8, "Ped", "org_loud", 0.75)
    o.ch("Gm/D", 0, b, 4, "RH", 62, 82, "org_loud", 0.7, size=4)
    o.ch("Gm", 0, b, 4, "LH", 50, 62, "org_loud", 0.66, size=2)
    o.ch("D", 0, b + 4, 4, "RH", 62, 82, "org_loud", 0.72, size=4)
    o.ch("D", 0, b + 4, 4, "LH", 50, 62, "org_loud", 0.68, size=2)
    return b + 8


def build(ctx):
    o = Org()
    plan = []
    b = 0
    # исполнение: фермата перед каденцией, широкий конец
    CLIM = 4 * (8 + 12 + 4 + 12 + 4 + 12)   # начало кульминации (доли)
    FERM = CLIM + 4 * (6 + 6)
    END = FERM + 8 + 16
    o.slow += [(FERM, FERM + 4, 1.8), (FERM + 4, FERM + 8, 1.25), (END + 4, END + 8, 1.8), (END + 6, END + 8, 1.3)]
    plan.append((b, "R: ритурнель")); ritornello(o, b, 0, end="tonic"); b += 16
    ritornello(o, b, 0, end="dominant"); b += 16
    plan.append((b, "Эпизод 1: «Кристина»")); episode(o, b, 0, "S"); b += 48
    plan.append((b, "R в g-moll")); ritornello(o, b, 5, end="dominant"); b += 16
    plan.append((b, "Эпизод 2: «Призрак»")); episode(o, b, 5, "T"); b += 48
    plan.append((b, "R в a-moll")); ritornello(o, b, 7, end="dominant"); b += 16
    plan.append((b, "Эпизод 3: дуэт")); duet(o, b, 7); b += 48
    plan.append((b, "Кульминация: монте")); b = climax(o, b)
    plan.append((b, "R в d-moll, конец")); b = finale(o, b)
    for bt, label in plan:
        o.p.mark(o.perf(bt), label)["wt"] = bt * SPB
    o.p.meta["beats"] = b
    # замер `--parts`: правая рука (мелодия, фигурация) −38.6 LUFS тонула под педалью (−30.2) и левой (−32.4)
    o.p.balance({"Organ RH": +8, "Organ LH": +2, "Organ Pedal": -2})
    return o.p
