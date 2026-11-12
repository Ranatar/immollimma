"""Контрапункт фуги: тональности, перенос темы по ступеням, гармонический план, поиск свободных голосов,
проверка голосоведения.

Время — в долях (четверть = 1). Нота — (t, d, midi). Голос — список нот по времени.
"""
import math

NAT_MINOR = (0, 2, 3, 5, 7, 8, 10)
MAJOR = (0, 2, 4, 5, 7, 9, 11)


class Key:
    def __init__(self, tonic, mode="minor"):
        self.tonic, self.mode = tonic % 12, mode
        self.scale = NAT_MINOR if mode == "minor" else MAJOR

    def pcs(self):
        """допустимые звуки лада: в миноре — натуральный плюс повышенные VI и VII"""
        s = {(self.tonic + x) % 12 for x in self.scale}
        if self.mode == "minor":
            s |= {(self.tonic + 9) % 12, (self.tonic + 11) % 12}
        return s

    def degree(self, m):
        """midi → (абсолютная ступень, альтерация) относительно натурального лада"""
        rel = m - self.tonic
        octv, r = divmod(rel, 12)
        best = min(range(7), key=lambda k: (abs(r - self.scale[k]), -self.scale[k]))
        alt = r - self.scale[best]
        return octv * 7 + best, alt

    def pitch(self, deg, alt=0):
        octv, k = divmod(deg, 7)
        return self.tonic + 12 * octv + self.scale[k] + alt


def dmap(m, src, dst, shift=0):
    """перенос высоты по ступеням из лада src в лад dst; shift — сдвиг на ступени (октавы и пр.).
    Повышенные VI/VII минора в мажоре становятся натуральными VI/VII, натуральная VII минора — тоже"""
    deg, alt = src.degree(m)
    k = deg % 7
    if dst.mode == "major" and src.mode == "minor" and k in (5, 6):
        alt = 0
    elif dst.mode == "minor" and src.mode == "major" and k == 6:
        alt = 1  # вводный тон
    return dst.pitch(deg + shift, alt)


def tmap(notes, src, dst, shift=0, dt=0.0, scale_t=1.0):
    return [(dt + t * scale_t, d * scale_t, dmap(m, src, dst, shift)) for t, d, m in notes]


def transpose(notes, semis, dt=0.0, scale_t=1.0):
    return [(dt + t * scale_t, d * scale_t, m + semis) for t, d, m in notes]


# ---------------------------------------------------------------- гармония
QUAL = {"m": (0, 3, 7), "M": (0, 4, 7), "d": (0, 3, 6), "7": (0, 4, 7, 10), "d7": (0, 3, 6, 9),
        "m7": (0, 3, 7, 10), "hd7": (0, 3, 6, 10), "M7": (0, 4, 7, 11)}


class Chord:
    def __init__(self, root, qual, bass=None):
        self.root, self.qual = root % 12, qual
        self.pcs = {(root + x) % 12 for x in QUAL[qual]}
        self.bass = None if bass is None else bass % 12

    def __repr__(self):
        names = "C C# D Eb E F F# G Ab A Bb B".split()
        return names[self.root] + self.qual + ("" if self.bass is None else "/" + names[self.bass])


def ch(key, deg, qual, inv=0):
    """аккорд на ступени deg (0..6) лада key; V и VII в миноре берутся от повышенной VII"""
    if key.mode == "minor" and deg == 6 and qual in ("d", "d7", "hd7"):
        root = (key.tonic + 11) % 12
    else:
        root = (key.tonic + key.scale[deg % 7]) % 12
    c = Chord(root, qual)
    if inv:
        c.bass = (root + QUAL[qual][inv]) % 12
    return c


class Harmony:
    """отрезки [(t, Chord, Key)] — аккорд действует до следующего"""

    def __init__(self):
        self.seg = []

    def add(self, t, chord, key):
        self.seg.append((t, chord, key))
        self.seg.sort(key=lambda x: x[0])

    def at(self, t):
        cur = None
        for s in self.seg:
            if s[0] <= t + 1e-9:
                cur = s
            else:
                break
        return cur

    def extend(self, other_seg):
        for s in other_seg:
            self.add(*s)


# ---------------------------------------------------------------- голоса
def sounding(voice, t):
    for n in voice:
        if n[0] <= t + 1e-9 < n[0] + n[1] - 1e-9:
            return n[2]
    return None


def onset_at(voice, t):
    return any(abs(n[0] - t) < 1e-9 for n in voice)


def strength(t):
    f = t - math.floor(t + 1e-9)
    if f < 1e-6:
        return 2 if int(round(t)) % 2 == 0 else 1.5
    if abs(f - 0.5) < 1e-6:
        return 0.5
    return 0.0


DISS = {1, 2, 10, 11}


def melodic_cost(a, b):
    d = abs(b - a)
    return {0: 5.0, 1: 0.0, 2: 0.0, 3: 1.2, 4: 1.5, 5: 2.0, 6: 40.0, 7: 2.5, 8: 5.0, 9: 5.5, 10: 40.0, 11: 40.0,
            12: 4.0}.get(d, 60.0)


def generate(slots, harm, fixed, lo, hi, *, role="upper", above=(), below=(), start=None, end=None, center=None,
             invertible_with=None, strict=True, prev=None, pedals=()):
    """поиск линии по слотам [(t, d)] — динамическое программирование по парам (пред., тек.)
    fixed: все уже записанные голоса; above/below: голоса, которые должны быть выше/ниже этого
    start/end: множества допустимых высот (или None); invertible_with: голос, с которым избегать квинт на долях"""
    center = (lo + hi) / 2 if center is None else center
    cands = []
    for t, d in slots:
        h = harm.at(t)
        chord, key = h[1], h[2]
        allowed = key.pcs() | chord.pcs
        cands.append([m for m in range(lo, hi + 1) if m % 12 in allowed])
    INF = 1e18
    onsets = [sorted(n[0] for n in v) for v in fixed]
    ped_ons = [sorted(n[0] for n in v) for v in pedals]

    def held_clash(i, m):
        """звук держится, а другой голос берёт новую ноту на доле"""
        t, d = slots[i]
        c = 0.0
        for v, ons in zip(fixed, onsets):
            for tau in ons:
                if t + 1e-9 < tau < t + d - 1e-9 and strength(tau) >= 1:
                    f = sounding(v, tau)
                    hh = harm.at(tau)
                    if f is None or hh is None:
                        continue
                    iv = abs(m - f) % 12
                    if iv in DISS and f % 12 in hh[1].pcs and m % 12 not in hh[1].pcs:
                        c += 40
                    elif iv in DISS and m % 12 not in hh[1].pcs:
                        c += 12
        return c

    def local(i, m):
        t, d = slots[i]
        h = harm.at(t)
        chord, key = h[1], h[2]
        s = strength(t)
        c = 0.05 * abs(m - center)
        nct = m % 12 not in chord.pcs
        if nct and s >= 1.5:
            c += 60
        elif nct and s >= 1:
            c += 25
        elif nct and s >= 0.5:
            c += 3
        lowest = True
        present = set()
        for v in fixed:
            f = sounding(v, t)
            if f is None:
                continue
            present.add(f % 12)
            if f < m:
                lowest = False
            iv = abs(m - f) % 12
            if iv in DISS:
                f_nct = f % 12 not in chord.pcs
                if s >= 1 and not f_nct:
                    c += 50 if not nct else 30
                elif s >= 0.5 and not (nct or f_nct):
                    c += 15
            if iv == 6 and s >= 1 and not (chord.qual in ("7", "d", "d7", "hd7")):
                c += 12
            if m == f:
                c += 6
        for v in above:
            f = sounding(v, t)
            if f is not None and m >= f:
                c += 40
        for v in below:
            f = sounding(v, t)
            if f is not None and m <= f:
                c += 40
        if role == "bass":
            if s >= 1:
                want = chord.bass if chord.bass is not None else chord.root
                if m % 12 != want:
                    c += 30 if m % 12 in chord.pcs else 60
        else:
            for v in fixed:
                f = sounding(v, t)
                if f is not None and s >= 1 and abs(m - f) % 12 == 5 and f < m and all(
                        (sounding(w, t) is None or sounding(w, t) >= f) for w in fixed) and lowest is False:
                    # кварта с басом на доле
                    if f == min(x for x in (sounding(w, t) for w in fixed) if x is not None):
                        c += 18
            if s >= 1 and not nct and m % 12 not in present:
                c -= 2.5
        if invertible_with is not None:
            f = sounding(invertible_with, t)
            if f is not None and s >= 1 and abs(m - f) % 12 == 7:
                c += 25
        if key.mode == "minor" and m % 12 == (key.tonic + 11) % 12 and m % 12 in present:
            c += 15  # удвоение вводного тона
        c += held_clash(i, m)
        if start is not None and i == 0 and m not in start:
            c += 1000
        if end is not None and i == len(slots) - 1 and m not in end:
            c += 1000
        return c

    def trans(i, a, b):
        """переход от слота i-1 (высота a) к слоту i (высота b)"""
        c = melodic_cost(a, b)
        t0, t1 = slots[i - 1][0], slots[i][0]
        h0, h1 = harm.at(t0), harm.at(t1)
        a_nct = a % 12 not in h0[1].pcs
        b_nct = b % 12 not in h1[1].pcs
        if a_nct and abs(b - a) > 2:
            c += 40
        if b_nct and abs(b - a) > 2:
            c += 40
        if a_nct and a == b:
            c += 20
        k = h0[2]
        if k.mode == "minor" and a % 12 == (k.tonic + 11) % 12 and b % 12 != k.tonic and h0[1].root == (k.tonic + 7) % 12:
            c += 8
        for v, ons in zip(list(fixed) + list(pedals), onsets + ped_ons):
            tl = max([t0] + [x for x in ons if t0 - 1e-9 <= x < t1 - 1e-9])
            fa, fb = sounding(v, tl), sounding(v, t1)
            if fa is None or fb is None or fa == fb or a == b:
                continue
            ia, ib = abs(a - fa) % 12, abs(b - fb) % 12
            if ia == ib and ia in (0, 7) and (b - a) * (fb - fa) > 0:
                c += 80
            if ia in (0, 7) and ib in (0, 7) and ia != ib:
                pass
        return c

    def trans3(i, p, a, b):
        c = 0.0
        if b == p and slots[i][1] < 1:
            c += 1.5  # возврат к тому же звуку через один (трель-топтание)
        if abs(a - p) >= 5 and (abs(b - a) > 2 or (b - a) * (a - p) > 0):
            c += 4
        if abs(a - p) >= 3 and abs(b - a) >= 3 and (b - a) * (a - p) > 0 and abs(b - p) > 12:
            c += 30
        return c

    n = len(slots)
    if n == 0:
        return []
    # состояние: (пред, тек)
    best = {}
    for m in cands[0]:
        c0 = local(0, m)
        if prev is not None:
            pt, pm = prev
            c0 += melodic_cost(pm, m)
            for v, ons in zip(list(fixed) + list(pedals), onsets + [sorted(n[0] for n in p) for p in pedals]):
                tl = max([pt] + [x for x in ons if pt - 1e-9 <= x < slots[0][0] - 1e-9])
                fa, fb = sounding(v, tl), sounding(v, slots[0][0])
                if fa is None or fb is None or fa == fb or pm == m:
                    continue
                ia, ib = abs(pm - fa) % 12, abs(m - fb) % 12
                if ia == ib and ia in (0, 7) and (m - pm) * (fb - fa) > 0:
                    c0 += 80
        best[(None if prev is None else prev[1], m)] = (c0, None)
    layers = [best]
    for i in range(1, n):
        nb = {}
        lc = {m: local(i, m) for m in cands[i]}
        for (p, a), (cost, _) in layers[-1].items():
            if cost >= INF:
                continue
            for b in cands[i]:
                c = cost + lc[b] + trans(i, a, b) + (trans3(i, p, a, b) if p is not None else 0)
                key_ = (a, b)
                if key_ not in nb or c < nb[key_][0]:
                    nb[key_] = (c, (p, a))
        # отсечение
        if len(nb) > 1500:
            items = sorted(nb.items(), key=lambda x: x[1][0])[:1500]
            nb = dict(items)
        layers.append(nb)
    state = min(layers[-1], key=lambda k: layers[-1][k][0])
    total = layers[-1][state][0]
    seq = []
    for i in range(n - 1, -1, -1):
        seq.append(state[1])
        prev = layers[i][state][1]
        state = prev
    seq.reverse()
    line = [(t, d, m) for (t, d), m in zip(slots, seq)]
    return merge_repeats(line) if not strict else line, total


def merge_repeats(line):
    out = []
    for n in line:
        if out and out[-1][2] == n[2] and abs(out[-1][0] + out[-1][1] - n[0]) < 1e-9 and strength(n[0]) < 1.5:
            out[-1] = (out[-1][0], out[-1][1] + n[1], n[2])
        else:
            out.append(n)
    return out


def slots_between(t0, t1, voices, busy_div=0.5, calm_div=1.0):
    """ритм свободного голоса: восьмые там, где остальные стоят, четверти — где движутся"""
    out, t = [], t0
    while t < t1 - 1e-9:
        moving = sum(1 for v in voices for n in v if t + 1e-9 < n[0] < t + 1 - 1e-9)
        step = busy_div if moving == 0 else calm_div
        step = min(step, t1 - t)
        k = int(round(1 / step)) if step < 1 else 1
        for j in range(k):
            if t + j * step < t1 - 1e-9:
                out.append((t + j * step, min(step, t1 - t - j * step)))
        t += step * k
    return out


# ---------------------------------------------------------------- проверка
NAMES = "C C# D Eb E F F# G Ab A Bb B".split()


def nm(m):
    return f"{NAMES[m % 12]}{m // 12 - 1}"


def check(voices, harm, t0=None, t1=None, verbose=True):
    """параллельные квинты/октавы, диссонансы на сильных долях (без опоры в гармонии), перекрещивания"""
    times = sorted({n[0] for v in voices.values() for n in v})
    if t0 is not None:
        times = [t for t in times if t0 - 1e-9 <= t < t1]
    problems = []
    names = list(voices)
    for i in range(len(times)):
        t = times[i]
        h = harm.at(t)
        for a in range(len(names)):
            for b in range(a + 1, len(names)):
                va, vb = voices[names[a]], voices[names[b]]
                ma, mb = sounding(va, t), sounding(vb, t)
                if ma is None or mb is None:
                    continue
                if i > 0:
                    tp = times[i - 1]
                    pa, pb = sounding(va, tp), sounding(vb, tp)
                    if pa is not None and pb is not None and pa != ma and pb != mb:
                        ip, ic = abs(pa - pb) % 12, abs(ma - mb) % 12
                        if ip == ic and ic in (0, 7) and (ma - pa) * (mb - pb) > 0:
                            problems.append((t, f"парал. {'октавы' if ic == 0 else 'квинты'} {names[a]}-{names[b]} "
                                                f"{nm(pa)}/{nm(pb)} → {nm(ma)}/{nm(mb)}"))
                s = strength(t)
                iv = abs(ma - mb) % 12
                if s >= 1 and iv in DISS and h is not None and (onset_at(va, t) or onset_at(vb, t)):
                    if ma % 12 in h[1].pcs and mb % 12 in h[1].pcs:
                        continue  # септаккорд
                    problems.append((t, f"диссонанс на доле {names[a]}-{names[b]} {nm(ma)}/{nm(mb)} ({h[1]})"))
    if verbose:
        for t, p in problems:
            print(f"  {t:7.2f}  {p}")
    return problems


# ---------------------------------------------------------------- автоматическая гармонизация по нотам
def candidates(key):
    """аккорды лада по ступеням с предпочтением (меньше — лучше)"""
    out = []
    if key.mode == "minor":
        spec = [(0, "m", 0), (4, "M", 0), (3, "m", 1), (5, "M", 1), (2, "M", 2), (6, "d7", 2), (4, "7", 1),
                (1, "d", 3), (1, "hd7", 3), (6, "M", 3), (3, "M", 3), (4, "m", 4), (0, "M", 4), (0, "7", 4)]
    else:
        spec = [(0, "M", 0), (4, "M", 0), (3, "M", 0), (5, "m", 1), (1, "m", 1), (4, "7", 1), (2, "m", 2),
                (6, "d", 3), (1, "m7", 2)]
    for deg, q, pref in spec:
        out.append((ch(key, deg, q), pref))
    return out


def auto_harmony(lines, key, t0, t1, step=1.0, prefer=None):
    """для каждой доли — аккорд, содержащий звуки, взятые на этой доле (и звучащие в ней); → [(t, Chord, key)]"""
    res, t = [], t0
    prev = None
    while t < t1 - 1e-9:
        pcs_on = set()
        for v in lines:
            m = sounding(v, t)
            if m is not None:
                pcs_on.add(m % 12)
        best, bc = None, 1e9
        for c, pref in candidates(key):
            miss = len(pcs_on - c.pcs)
            cost = miss * 10 + pref + (0.5 if prev is not None and c.pcs == prev.pcs else 0)
            if prefer and c.root in prefer:
                cost -= 1
            if cost < bc:
                best, bc = c, cost
        res.append((t, best, key, bc))
        prev = best
        t += step
    return res
