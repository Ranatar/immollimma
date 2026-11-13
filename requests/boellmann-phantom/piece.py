#!/usr/bin/env python3
"""Toccata «Le Fantôme» pour grand orgue — «Призрак Оперы», каким его написал бы Боэльман (≈ 2:30).

Модель — Toccata из «Готической сюиты» Боэльмана: вечное движение шестнадцатыми в мануалах, аккорды каждую долю,
неподвижный минор «дрожит» на полутон (у Боэльмана — нижний сосед квинты), тема гремит в педали, в кульминации —
та же тема в увеличении, в конце пикардийская терция. От «Призрака» — ре минор, стук неподвижного баса, каждый
куплет выше прежнего (d → g, затем a). Тема своя — та же, что в баховском Praeludium d-moll: пара пьес.

  вступление        токката одна; «дрожь»: обе руки поднимают квинту к верхнему соседу — вздох a–b
  тема в педали     d → g, полный орган
  голос в тишине    тихий регистр: тема наверху, шестнадцатые в левой, педаль пульсирует восьмыми (g → c)
  тема в педали     на тон выше: a → d
  разработка        голова темы в педали всё выше (g – a – b – c), от тихого к полному; пункт на A, ум. септаккорд,
                    фермата, пассаж вниз
  тема в увеличении кульминация: тема вдвое медленнее под полными аккордами
  кода              каданс, тоническая педаль, плагальный оборот, ре мажор

    python3 -m kit run requests/boellmann-phantom/piece.py --parts
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from kit.events import Piece  # noqa: E402

BPM = 126
SPB = 60 / BPM
NAMES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
QUAL = {"": (0, 4, 7), "m": (0, 3, 7), "7": (0, 4, 7, 10), "dim7": (0, 3, 6, 9), "dim": (0, 3, 6)}
MINOR = (0, 2, 3, 5, 7, 8, 10)


def chord(name, k=0):
    """'Dm', 'A7', 'C#dim7', 'G/B' → (pcs, bass pc, root pc, quality), транспонировано на k"""
    name, _, bass = name.partition("/")
    root = NAMES[name[0]]
    i = 1
    while i < len(name) and name[i] in "b#":
        root += -1 if name[i] == "b" else 1
        i += 1
    q = name[i:]
    pcs = {(root + k + x) % 12 for x in QUAL[q]}
    b = root
    if bass:
        b = NAMES[bass[0]] + sum(-1 if c == "b" else 1 for c in bass[1:])
    return pcs, (b + k) % 12, (root + k) % 12, q


# ===================================================================== тема (своя; та же, что в Praeludium)
# в педали: на три октавы ниже сопрановой записи (a = A1); гармония — под бас (бас каждой доли = звук темы)
SONG = [(-1, .5, 69), (-.5, .5, 69),
        (0, 1.5, 74), (1.5, .5, 73), (2, 1, 74), (3, 1, 76),
        (4, 2, 77), (6, 1, 76), (7, 1, 74),
        (8, 1.5, 72), (9.5, .5, 70), (10, 1, 69), (11, 1, 67),
        (12, 3, 69)]
SEQ = [(-1, .5, 72), (-.5, .5, 72),
       (0, 1.5, 77), (1.5, .5, 76), (2, 1, 77), (3, 1, 79),
       (4, 2, 81), (6, 1, 79), (7, 1, 77),
       (8, 1.5, 79), (9.5, .5, 78), (10, 1, 79), (11, 1, 81),
       (12, 2, 82), (14, 1, 81), (15, 1, 79)]
# каданс темы в басу: es d c b | a b c d(2) | es(2) d(2) | g — в g-moll (относительно d)
PCAD = [(0, 1, 75), (1, 1, 74), (2, 1, 72), (3, 1, 70),
        (4, 1, 69), (5, 1, 70), (6, 1, 72), (7, 1, 74),
        (8, 2, 75), (10, 2, 74),
        (12, 4, 67)]
PSONG_H = ["Dm", "Dm", "Dm", "C/E", "F", "F", "C/E", "Dm", "C", "C7", "F/A", "Gm", "A", "A", "A", "C7"]
PSEQ_H = ["F", "F", "F", "C7/G", "F/A", "F/A", "C7/G", "F", "Gm", "Gm", "Gm", "D7/A", "Gm/Bb", "Gm/Bb", "D/A", "Gm"]
PCAD_H = ["Cm/Eb", "Gm/D", "Cm", "Gm/Bb", "D7/A", "Gm/Bb", "Cm", "D", "Cm/Eb", "Cm/Eb", "D7", "D7", "Gm", "Gm", "Gm", "Gm"]
# та же тема наверху (голос в тишине): гармония — под мелодию (как в Praeludium)
CAD = [(0, 1, 75), (1, 1, 74), (2, 1, 72), (3, 1, 70),
       (4, 1, 69), (5, .5, 70), (5.5, .5, 72), (6, 2, 74),
       (8, 2, 70), (10, 2, 69),
       (12, 4, 67)]
SONG_H = ["Dm", "Dm", "Dm", "A7", "Bb", "Bb", "C", "Gm", "C", "C7", "F", "Gm/Bb", "A", "A", "A", "C7"]
SEQ_H = ["F", "F", "F", "C7", "F", "F", "C", "F", "Gm", "Gm", "Gm", "D7", "Gm", "Gm", "D7", "Gm"]
CAD_H = ["Cm", "Gm", "Cm", "Gm/Bb", "D7", "Gm", "D7", "D7", "Gm/D", "Gm/D", "D7", "D7", "Gm", "Gm", "Gm", "Gm"]


class Org:
    def __init__(self):
        self.p = Piece("Toccata «Le Fantôme»", bpm=BPM, meter=(4, 4),
                       key="D minor", seed=1895)
        self.p.meta["subtitle"] = "pour grand orgue — «Призрак Оперы», как написал бы Боэльман"
        self.p.meta["sends"] = {"organ": 0.5}
        self.prev = {}
        self.slow = []

    def perf(self, beat):
        s = 0.0
        for b0, b1, f in sorted(self.slow):
            if beat <= b0:
                break
            s += (min(beat, b1) - b0) * (f - 1)
        return (beat + s) * SPB

    def n(self, m, beat, dur, staff, reg="org_loud", vel=0.6, legato=0.92, gain=0.5):
        if reg == "org_quiet" and m < 36:
            reg = "org_loud"
        t0, t1 = self.perf(beat), self.perf(beat + dur)
        e = self.p.note(reg, m, t0, max(0.05, (t1 - t0) * legato), vel=vel, gain=gain, release=0.35,
                        pan={"RH": 0.2, "LH": -0.15, "Ped": 0.0}[staff],
                        part=f"Organ {staff}" if staff != "Ped" else "Organ Pedal")
        e["wt"], e["wdur"] = beat * SPB, dur * SPB
        return e

    def voicing(self, harm, k, lo, hi, key, size=3):
        pcs = chord(harm, k)[0]
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

    def toccata(self, beat0, harms, k, tonic, staff="RH", lo=72, hi=88, reg="org_loud", gain=0.5, chords=True,
                clo=53, chi=67, creg=None):
        """вечное движение: на каждую долю — верхний звук аккорда и два нижних (верх, низ, середина, низ).
        На неподвижной гармонии сверху квинта, а на третьей доле обе руки вместе поднимают её к верхнему соседу по
        гамме — вздох a–b над ре минором (у Боэльмана наоборот: нижний сосед, соль–фа-диез–соль).
        chords: аккорды левой руки каждую долю"""
        scale = {(tonic + 2 + x) % 12 for x in MINOR}
        for j, h in enumerate(harms):
            b = beat0 + j
            bar = (j // 4) * 4
            pcs, _, root, q = chord(h, k)
            static = bar + 3 < len(harms) and all(harms[bar + i] == h for i in range(4)) and not q.startswith("dim")
            fifth = (root + 7) % 12
            if static:  # на неподвижной гармонии сверху — квинта, под ней два ближайших звука аккорда
                top = max(m for m in range(lo + 5, hi + 1) if m % 12 == fifth)
                low = [m for m in range(top - 1, top - 13, -1) if m % 12 in pcs][:2][::-1]
                v = low + [top]
            else:
                v = self.voicing(h, k, lo, hi, staff + "fig" + reg, 3)
            sigh = static and j % 4 == 2
            # верхний сосед квинты: у минорного — полутон (вздох a–b), у мажорного — тон, у септаккорда — по гамме
            nb = (fifth + 1) % 12 if q == "m" else (fifth + 2) % 12 if q == "" else \
                next(x for x in range(fifth + 1, fifth + 3) if x % 12 in scale) % 12
            top = v[2] + ((nb - fifth) % 12 if sigh else 0)
            for i, m in enumerate((top, v[0], v[1], v[0])):
                self.n(m, b + i / 4, 0.25, staff, reg, 0.62, legato=0.9, gain=gain * (1.08 if i == 0 else 1.0))
            if chords:
                c = self.voicing(h, k, clo, chi, "LHch" + (creg or reg), 3)
                if sigh:  # вздох в обеих руках вместе: квинта поднимается к своему верхнему соседу
                    c = [m + (nb - fifth) % 12 if m % 12 == fifth else m for m in c]
                for m in c:
                    self.n(m, b, 1, "LH", creg or reg, 0.6, legato=0.55, gain=gain * 0.95)

    def theme(self, notes, beat0, k, staff="Ped", reg="org_loud", oct=-36, aug=1, gain=0.55, legato=0.9):
        for b, d, m in notes:
            self.n(m + k + oct, beat0 + b * aug, d * aug, staff, reg, 0.7, legato=legato, gain=gain)

    def pulse(self, beat0, harms, k, lo=38, hi=50, reg="org_quiet", gain=0.45):
        """педаль-пульс восьмыми на басу гармонии — тень неподвижного баса «Призрака»"""
        prev = (lo + hi) // 2
        for j, h in enumerate(harms):
            b = chord(h, k)[1]
            m = min((x for x in range(lo, hi + 1) if x % 12 == b), key=lambda x: abs(x - prev))
            prev = m
            for i in range(2):
                self.n(m, beat0 + j + i / 2, 0.5, "Ped", reg, 0.6, legato=0.6, gain=gain * (1.1 if i == 0 else 1.0))


def per_beat(h, n):
    return [h] * n


# ===================================================================== разделы
def intro(o, b0):
    """4 такта: токката одна; Dm, Dm, Gm/D, A7 — последний такт — затакт темы в педали"""
    harms = per_beat("Dm", 8) + per_beat("Gm/D", 4) + per_beat("A7", 4)
    o.toccata(b0, harms, 0, 0)
    return b0 + 16


def pedal_theme(o, b0, k, tonic, gain=0.5):
    """12 тактов: тема в педали d → g (относительно k); над ней токката и аккорды"""
    harms = PSONG_H + PSEQ_H + PCAD_H
    o.theme([x for x in SONG if x[0] < 0], b0, k)  # затакт — в последней доле предыдущего раздела
    o.theme([x for x in SONG if x[0] >= 0], b0, k)
    o.theme(SEQ, b0 + 16, k)
    o.theme(PCAD, b0 + 32, k)
    o.toccata(b0, harms[:16], k, tonic=k, gain=gain)
    o.toccata(b0 + 16, harms[16:], k, tonic=k + 5, gain=gain)
    return b0 + 48


def link(o, b0, harm, k, tonic, reg="org_loud", gain=0.5, pedal=None):
    o.toccata(b0, per_beat(harm, 8), k, tonic, reg=reg, gain=gain)
    if pedal is not None:
        o.n(pedal, b0, 7, "Ped", reg if pedal >= 36 else "org_loud", 0.6, gain=gain * 0.9)
    return b0 + 8


def quiet_voice(o, b0, k):
    """12 тактов, тихий регистр: тема наверху (g), шестнадцатые — в левой руке, педаль пульсирует восьмыми"""
    mel = SONG + [(16 + b, d, m) for b, d, m in SEQ] + [(32 + b, d, m) for b, d, m in CAD]
    harms = SONG_H + SEQ_H + CAD_H
    o.theme(mel, b0, k, staff="RH", reg="org_quiet", oct=0, gain=0.62, legato=0.95)
    o.toccata(b0, harms[:16], k, tonic=k, staff="LH", lo=55, hi=70, reg="org_quiet", gain=0.42, chords=False)
    o.toccata(b0 + 16, harms[16:], k, tonic=k + 5, staff="LH", lo=55, hi=70, reg="org_quiet", gain=0.42, chords=False)
    o.pulse(b0, harms, k)
    return b0 + 48


def development(o, b0):
    """голова темы в педали всё выше: g, a, b, c (по 2 такта), от тихого к полному; пункт на A; фермата"""
    keys = [5, 7, 8, 10]
    head = [x for x in SONG if 0 <= x[0] < 4]
    pick = [x for x in SONG if x[0] < 0]
    o.theme(pick, b0, keys[0], reg="org_quiet", gain=0.5)  # затакт — в последней доле предыдущего раздела
    for u, kk in enumerate(keys):
        st = b0 + 8 * u
        reg = "org_quiet" if u < 2 else "org_loud"
        g = 0.44 + 0.04 * u
        o.theme(head, st, kk, reg=reg, gain=g + 0.06)
        dom = min(x for x in range(36, 48) if x % 12 == (9 + kk) % 12)
        o.n(dom, st + 4, 3 if u + 1 < len(keys) else 4, "Ped", reg, 0.62, gain=g + 0.06)
        o.toccata(st, ["Dm", "Dm", "Dm", "A7/E"] + ["A7"] * 3, kk, tonic=kk, reg=reg, gain=g)
        if u + 1 < len(keys):  # последняя доля — уже доминанта следующей тональности, в педали — затакт
            nxt = keys[u + 1]
            o.toccata(st + 7, ["A7"], nxt, tonic=nxt, reg=reg, gain=g)
            o.theme(pick, st + 8, nxt, reg="org_quiet" if u + 1 < 2 else "org_loud", gain=g + 0.06)
        else:
            o.toccata(st + 7, ["A7"], kk, tonic=kk, reg=reg, gain=g)
    # органный пункт на A: C#dim7 / A7, верх фигурации выше каждый такт
    st = b0 + 32
    for u in range(4):
        h = "C#dim7" if u % 2 == 0 else "A7"
        o.toccata(st + 4 * u, per_beat(h, 4), 0, 0, lo=72 + 2 * u, hi=90 + 2 * u, gain=0.56, clo=52, chi=67)
    o.n(33, st, 16, "Ped", "org_loud", 0.7, gain=0.6)
    o.n(45, st, 16, "Ped", "org_loud", 0.7, gain=0.45)
    # фермата на ум. септаккорде и пассаж вниз по нему, в конце — затакт темы в увеличении
    sf = st + 16
    for m in (33, 45, 52, 55, 58, 61, 64, 67, 70, 73, 76):
        o.n(m, sf, 4, "Ped" if m < 50 else ("LH" if m < 62 else "RH"), "org_loud", 0.72, legato=0.97, gain=0.5)
    run = [x for x in range(94, 57, -1) if x % 12 in (1, 4, 7, 10)][:8]
    for j, m in enumerate(run):
        o.n(m, sf + 4 + j / 4, 0.25, "RH" if m >= 62 else "LH", "org_loud", 0.66, gain=0.55)
    return sf + 8


def augmented(o, b0):
    """8 тактов: тема в педали вдвое медленнее (d), над ней токката и полные аккорды — кульминация"""
    harms = [h for h in PSONG_H for _ in range(2)]
    harms[-2:] = ["A7", "A7"]
    harms[3] = "A/C#"  # проходящее cis в увеличении длится долю — под ним V6
    o.theme([x for x in SONG if x[0] < 0], b0, 0, aug=2, gain=0.62)
    o.theme([x for x in SONG if x[0] >= 0], b0, 0, aug=2, gain=0.62)
    o.toccata(b0, harms, 0, 0, gain=0.58, clo=55, chi=69)
    return b0 + 32


def coda(o, b0):
    """каданс, тоническая педаль, плагальный оборот (g/d – D), пикардийская терция, последний аккорд — широко"""
    bars = ["Dm", "Bb", "Gm/Bb", "A7", "Dm", "Gm/D", "D"]
    peds = [38, 34, 34, 33, 26, 26, 26]
    harms = [h for h in bars for _ in range(4)]
    o.toccata(b0, harms[:16], 0, 0, gain=0.6, clo=55, chi=69)
    o.toccata(b0 + 16, harms[16:24], 0, 0, gain=0.6, clo=55, chi=69)
    # ре мажор: та же фигура в мажоре (верхний сосед — си натуральное: тоника D мажора)
    o.toccata(b0 + 24, harms[24:], 0, 0, gain=0.62, clo=54, chi=69)
    for j, m in enumerate(peds):
        o.n(m, b0 + 4 * j, 4, "Ped", "org_loud", 0.7, legato=0.97 if j >= 4 else 0.9, gain=0.62)
    fin = b0 + 28
    for m in (26, 38, 50, 57, 62, 66, 69, 74, 78, 81, 86):
        o.n(m, fin, 4, "Ped" if m < 50 else ("LH" if m < 62 else "RH"), "org_loud", 0.74, legato=0.98, gain=0.5)
    return fin + 4


def build(ctx):
    o = Org()
    # исполнение задаётся до нот (по нему считаются времена): фермата разработки, расширение в конце
    SF = 16 + 48 + 8 + 48 + 8 + 48 + 48      # фермата на ум. септаккорде (доли)
    FIN = SF + 8 + 32 + 28                    # последний аккорд
    o.slow += [(SF, SF + 4, 1.9), (SF + 4, SF + 8, 1.15), (FIN - 4, FIN, 1.15), (FIN, FIN + 4, 2.0)]
    plan = []
    b = 0
    plan.append((b, "Вступление")); b = intro(o, b)
    plan.append((b, "Тема в педали (d → g)")); b = pedal_theme(o, b, 0, 0)
    plan.append((b, "Связка")); b = link(o, b, "Dm", 5, 5, reg="org_quiet", gain=0.45)
    plan.append((b, "Голос в тишине (g → c)")); b = quiet_voice(o, b, 5)
    plan.append((b, "Связка к a-moll")); b = link(o, b, "A7", 7, 7, gain=0.52, pedal=40)
    plan.append((b, "Тема в педали (a → d)")); b = pedal_theme(o, b, 7, 7, gain=0.54)
    plan.append((b, "Разработка")); b = development(o, b)
    plan.append((b, "Тема в увеличении (d)")); b = augmented(o, b)
    plan.append((b, "Кода")); b = coda(o, b)
    for bt, label in plan:
        o.p.mark(o.perf(bt), label)["wt"] = bt * SPB
    o.p.meta["beats"] = b
    # замер `--parts` без баланса: педаль −26.9, левая −35.7, правая −39.0 LUFS — токката тонула под темой
    o.p.balance({"Organ RH": +10, "Organ LH": +7, "Organ Pedal": -1})
    return o.p
