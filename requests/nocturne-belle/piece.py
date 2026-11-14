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
    def melody(self, bar, notes, k, part="Piano RH", vel=0.5, oct=0, double=False, level=0, sc=None, nxt=None,
               trill=False):
        """мелодия такта; rubato Шопена — правая рука чуть позже левой на сильных долях.
        level — сколько «бриллиантового» убранства (stile brillante): 0 — как есть; 1 — опевания сверху и
        заполненные скачки; 2 — ещё группетто на долгих нотах; 3 — фиоритуры: долгая нота рассыпается каскадом
        вверх и вниз 32-ми. sc — звукоряд (классы высот) для украшений; nxt — первая нота следующего такта.
        trill — последняя долгая нота такта трелится"""
        b0 = bar * BAR
        sc = sc if sc is not None else {(2 + k + x) % 12 for x in (0, 2, 3, 5, 7, 8, 11)}
        src = [(b, d, m + k + oct) for b, d, m in notes]
        out = self.ornament(src, sc, level, None if nxt is None else nxt + k + oct, trill)
        for b, d, m, kind in out:
            main = kind == "main"
            late = ((0.035 if b == 0 and d >= 1 else 0.012 if d >= 1 else 0.0) + 0.008 * self.rng.random()) if main else 0
            v = vel + (0.05 if d >= 1.5 else 0) - (0.07 if d < 0.5 and main else 0) - (0.1 if not main else 0)
            if kind == "run":  # пассаж: лёгкое крещендо-диминуэндо по дуге
                v += 0.03
            self.note(m, b0 + b, d, v, part, late=late)
            if double and main:
                self.note(m - 12, b0 + b, d, v - 0.08, part, late=late + 0.01)

    @staticmethod
    def step(m, sc, direction):
        x = m + direction
        while x % 12 not in sc:
            x += direction
        return x

    def ornament(self, notes, sc, level, nxt, trill):
        out = []
        longest = max(range(len(notes)), key=lambda i: (notes[i][1], i)) if notes else -1
        for i, (b, d, m) in enumerate(notes):
            n2 = notes[i + 1][2] if i + 1 < len(notes) else nxt
            seg = []
            bb, dd = b, d
            if trill and i == longest and d >= 1.5:  # трель с верхней, 32-ми, кончается группетто
                up, lo = self.step(m, sc, 1), self.step(m, sc, -1)
                cnt = int((d - 0.5) * 8)
                seg += [(b + j / 8, 1 / 8, up if j % 2 == 0 else m, "orn") for j in range(cnt)]
                seg += [(b + cnt / 8, 1 / 8, lo, "orn"), (b + cnt / 8 + 1 / 8, 1 / 8, m, "orn")]
                bb, dd = b + cnt / 8 + 0.25, d - cnt / 8 - 0.25
            elif (level >= 2 and d >= 2) or (level >= 3 and d >= 1.5):  # группетто секстолью
                up, lo = self.step(m, sc, 1), self.step(m, sc, -1)
                seg += [(b, 1 / 8, m, "main"), (b + 1 / 8, 1 / 8, up, "orn"), (b + 2 / 8, 1 / 8, m, "orn"),
                        (b + 3 / 8, 1 / 8, lo, "orn")]
                bb, dd = b + 0.5, d - 0.5
            elif level >= 1 and d >= 1.5:  # опевание сверху (короткий форшлаг на долю)
                seg += [(b, 1 / 8, self.step(m, sc, 1), "orn")]
                bb, dd = b + 1 / 8, d - 1 / 8
            tail = []
            if level >= 3 and dd >= 1.75 and n2 is not None:  # фиоритура: держать, затем каскад к следующей ноте
                hold = 0.75 if seg else 1.0
                rest = dd - hold
                cnt = int(rest * 8)
                up = [m]
                while up[-1] < min(m + 12, 100):
                    up.append(self.step(self.step(up[-1], sc, 1), sc, 1))  # вверх терциями
                down = [up[-1]]
                while down[-1] > n2 + 2 and len(up) + len(down) < cnt:
                    down.append(self.step(down[-1], sc, -1))
                path = (up[1:] + down)[:cnt]
                hold = dd - len(path) / 8  # каскад кончается вплотную к следующей ноте, лишнее — держать
                tail = [(bb + hold + j / 8, 1 / 8, x, "run") for j, x in enumerate(path)]
                dd = hold
            elif level >= 1 and n2 is not None and abs(n2 - m) >= 5 and dd >= 1:  # заполнить скачок
                direction = 1 if n2 > m else -1
                x, path = m, []
                for _ in range(3):
                    x = self.step(x, sc, direction)
                    path.append(x)
                tail = [(bb + dd - 3 / 8 + j / 8, 1 / 8, x, "orn") for j, x in enumerate(path)]
                dd -= 3 / 8
            seg = [z for z in seg]
            if dd > 0.02:
                seg.append((bb, dd, m, "main"))
            out += seg + tail
        return out

    def cascade(self, beat, beats, top, bottom, part="Piano RH", vel=0.4, chromatic=True, sc=None):
        """хроматический (или по звукоряду) каскад вниз 32-ми — шопеновский спуск из вершины"""
        cnt = int(beats * 8)
        pcs = set(range(12)) if chromatic else sc
        path = [x for x in range(top, bottom - 1, -1) if x % 12 in pcs][:cnt]
        for j, x in enumerate(path):
            self.note(x, beat + j / 8, 1 / 8, vel - 0.003 * j, part)

    def fioritura(self, beat, top, bottom, k, part="Piano RH", vel=0.42):
        """пассаж вниз по гамме за одну долю (шопеновская фиоритура в конце фразы)"""
        sc = sorted(x for x in range(bottom, top + 1) if x % 12 in {(2 + k + y) % 12 for y in (0, 2, 3, 5, 7, 8, 11)})
        run = sc[::-1][:8]
        for i, m in enumerate(run):
            self.note(m, beat + i / 8, 1 / 8, vel - 0.004 * i, part)

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
def hm(t):
    """гармонический минор от класса t"""
    return {(t + x) % 12 for x in (0, 2, 3, 5, 7, 8, 11)}


def maj(t):
    return {(t + x) % 12 for x in (0, 2, 4, 5, 7, 9, 11)}


def nxt_of(seq, i, after=None):
    return seq[i + 1][0][2] if i + 1 < len(seq) and seq[i + 1] else after


def refr_scale(i, k):
    """припев: первые четыре такта — минор терцией ниже куплета, потом — одноимённый мажор куплета"""
    return hm(11 + k) if i < 4 else maj(2 + k)


def strophe_quasimodo(o, bar):
    """d-moll: мелодия в середине; первая фраза — как есть, вторая смелее (опевания, заполненные скачки);
    припев — с группетто к концу"""
    for i in range(8):
        o.arpeggio(bar + i, VERSE_H[i], 0, vel=0.27)
        o.melody(bar + i, VERSE[i], 0, vel=0.44 + 0.03 * (i in (2, 5)), level=0 if i < 4 else 1,
                 nxt=nxt_of(VERSE, i, REFR[0][0][2]), sc=hm(2))
    for i in range(6):
        o.arpeggio(bar + 8 + i, REFR_H[i], 0, vel=0.3)
        o.melody(bar + 8 + i, REFR[i], 0, vel=0.5 + 0.02 * i, level=1 if i < 4 else 2,
                 nxt=nxt_of(REFR, i, LINK[0][0][2]), sc=refr_scale(i, 0), trill=(i == 3))
    return bar + 14


def link(o, bar, k, vel=0.45):
    """связка: долгая тоника мажора рассыпается фиоритурой; затем C7 — к куплету на терцию выше"""
    for i in range(2):
        o.arpeggio(bar + i, LINK_H[i], k, vel=0.28)
        o.melody(bar + i, LINK[i], k, vel=vel, level=3 if i == 0 else 1, nxt=nxt_of(LINK, i, VERSE[0][0][2] + 3),
                 sc=maj(2 + k) if i == 0 else maj(5 + k) | {(10 + k) % 12})
    return bar + 2


def strophe_frollo(o, bar):
    """f-moll: мелодия в левой руке (баритон), над ней бьющиеся аккорды — без украшений, тяжело; конец куплета —
    тёмный хроматический спуск в правой; припев — октавами, с опеваниями"""
    k = 3
    for i in range(8):
        o.throb(bar + i, VERSE_H_FROLLO[i], k, vel=0.34 + 0.02 * (i in (3, 4, 5, 6)))
        o.melody(bar + i, VERSE[i], k, part="Piano LH", vel=0.56, oct=-12)
    o.cascade((bar + 7) * BAR + 1, 3, 87, 64, vel=0.4)
    for i in range(6):
        o.throb(bar + 8 + i, REFR_H[i], k, vel=0.42, lo=57, hi=72)
        o.melody(bar + 8 + i, REFR[i], k, vel=0.66 + 0.01 * i, oct=12, double=True, level=1,
                 nxt=nxt_of(REFR, i, LINK[0][0][2]), sc=refr_scale(i, k))
    return bar + 14


def strophe_phoebus(o, bar):
    """gis-moll: высоко и блестяще — группетто, фиоритуры-каскады, трели; лёгкий аккомпанемент"""
    k = 6
    for i in range(8):
        o.salon(bar + i, VERSE_H[i], k, vel=0.27)
        notes = VERSE[i]
        if i in (3, 7):  # конец фразы — пассаж вместо последней доли
            notes = [x for x in notes if x[0] < 3]
        o.melody(bar + i, notes, k, vel=0.46, oct=12, level=2 if i < 4 else 3, nxt=nxt_of(VERSE, i, REFR[0][0][2]),
                 sc=hm(2 + k))
        if i == 3:
            o.fioritura((bar + i) * BAR + 3, 2 + k + 12 * 7 - 12, 2 + k + 12 * 5, k)
        if i == 7:
            o.fioritura((bar + i) * BAR + 3, 2 + k + 12 * 7, 2 + k + 12 * 5 + 7, k)
    for i in range(6):
        o.salon(bar + 8 + i, REFR_H[i], k, vel=0.3)
        o.melody(bar + 8 + i, REFR[i], k, vel=0.52 + 0.015 * i, level=3, nxt=nxt_of(REFR, i, REFR[0][0][2]),
                 sc=refr_scale(i, k), trill=(i == 3))
    return bar + 14


def trio(o, bar):
    """припев в f-moll втроём: октавы наверху (Фролло), линия Квазимодо в середине, бас — триоли агитато;
    расширение Des – C7 и каденция: арпеджио вверх, хроматический каскад вниз, фермата"""
    k = 6
    harms = REFR_H[:5] + [["G", "F#7"]]  # (+6) → Db | C7
    for i in range(6):
        o.agitato(bar + i, harms[i], k, vel=0.42 + 0.02 * i)
        o.melody(bar + i, REFR[i] if i < 5 else [(0, 2, 71), (2, 2, 70)], k, vel=0.74, double=True, level=1,
                 nxt=nxt_of(REFR, i, 71) if i < 4 else None, sc=refr_scale(i, k))
    for i in range(1, 6):
        o.inner(bar + i, harms[i], k, vel=0.36)
    b = bar + 6
    o.agitato(b, ["G"], k, vel=0.5)  # (+6) → Db
    o.melody(b, [(0, 1, 80), (1, 1, 79), (2, 2, 77)], 0, vel=0.78, double=True)
    t = (b + 1) * BAR  # каденция на C7
    o.ped(t)
    for m in (36, 48, 55, 58, 64):
        o.note(m, t, 4, 0.5, "Piano LH")
    up = [x for x in range(60, 95) if x % 12 in (0, 4, 7, 10)][:8]
    for j, m in enumerate(up):
        o.note(m, t + j / 8, 1 / 8, 0.48 + 0.01 * j, "Piano RH")
    o.cascade(t + 1, 2.5, 94, 70, vel=0.56)
    o.note(76, t + 3.5, 0.5, 0.4, "Piano RH")
    return bar + 8


def coda(o, bar):
    """C7 → d-moll: тема Квазимодо внизу, обрывками; наверху — последняя фиоритура и мерцание D-dur (leggierissimo);
    последний аккорд — D-dur, pp"""
    o.arpeggio(bar, ["Dm"], 0, vel=0.24)
    o.melody(bar, VERSE[0], 0, vel=0.38, oct=-12, part="Piano LH")
    o.arpeggio(bar + 1, ["A7"], 0, vel=0.22)
    o.melody(bar + 1, VERSE[1], 0, vel=0.34, oct=-12, part="Piano LH")
    o.arpeggio(bar + 2, ["Gm", "A7"], 0, vel=0.22)
    o.melody(bar + 2, [(0, 2, 70), (2, 2, 69)], 0, vel=0.34, level=2, sc=hm(2))
    o.arpeggio(bar + 3, ["Dm"], 0, vel=0.2)
    o.melody(bar + 3, [(0, 4, 74)], 0, vel=0.3, oct=12, level=3, nxt=74, sc=hm(2))
    # мерцание: D-dur арпеджио вверх-вниз секстолями в высоком регистре над тоникой
    t = (bar + 4) * BAR
    o.ped(t)
    o.note(38, t, 4, 0.22, "Piano LH")
    o.note(50, t, 4, 0.18, "Piano LH")
    tones = [x for x in range(74, 99) if x % 12 in (2, 6, 9)]
    fig = tones + tones[-2:0:-1]
    for j in range(32):
        o.note(fig[j % len(fig)], t + j / 8, 1 / 8, 0.32 - 0.003 * j, "Piano RH")
    t = (bar + 5) * BAR
    o.ped(t)
    for j, m in enumerate((26, 38, 45, 50, 54, 57, 62, 66, 74)):  # D-dur, арпеджато снизу
        o.note(m, t, 8, 0.32 + (0.04 if m == 74 else 0), "Piano LH" if m < 60 else "Piano RH", late=0.09 * j)
    return bar + 7


def build(ctx):
    o = Noct()
    plan = [(0, "Вступление"), (2, "I. Квазимодо: d-moll"), (10, "припев: h → D"), (16, "Связка"),
            (18, "II. Фролло: f-moll"), (26, "припев: d → F"), (32, "Связка"), (34, "III. Фебюс: gis-moll"),
            (42, "припев: f → As"), (48, "Трио: f-moll"), (54, "Каденция"), (56, "Кода: d-moll")]
    # рубато: концы фраз оттянуты, трио рвётся вперёд, каденция и кода — широко
    for bb in (5, 9, 15, 21, 25, 31, 37, 41, 47):
        o.slow.append((bb * BAR + 2, bb * BAR + 4, 1.0, 1.35))
    o.slow += [(48 * BAR, 53 * BAR, 0.9, 0.9), (54 * BAR, 55 * BAR, 1.2, 1.5), (55 * BAR, 56 * BAR, 1.4, 2.2),
               (59 * BAR, 61 * BAR, 1.1, 1.5), (61 * BAR, 63 * BAR, 1.8, 2.0)]
    o.p.meta["notation_divisors"] = [[8, 3], [4, 3], [4]]  # фиоритуры — 32-е, речевые триоли — триоли
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
