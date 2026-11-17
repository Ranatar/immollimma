#!/usr/bin/env python3
"""«Холодный мир» — тема СССР (≈ 2:50). Мелодия — заказчика (MIDI, 8 тактов, e-moll, натуральный минор);
оркестровка и драматургия — по образу СССР из опенинга (requests/cold-peace-op/storyboard.md): старик у окна,
снег, красное; ветеран химической войны 1944 года, подобравший на ней шкатулку; держава, которая устала быть
великой. Тон — по правилу 7 taste.md: тяжесть и память, не ликование.

  снег         низкий колокол E, флажолеты скрипок пустой квинтой, арфа роняет звуки
  старик       тема у виолончели соло, тихо, с подголоском валторны (поёт, когда тема стоит)
  хор          тема у мужского хора с валторнами; подголоски альтов терциями и сextами (русская
               подголосочная полифония); колокола на сильные доли
  1944         память: голова темы у тромбонов и тубы в увеличении над педалью E, гармония сползает на
               полутон (e – f, туман), тремоло-кластер скрипок, дыхание противогаза, дальняя дробь;
               сквозь туман — шкатулка (тема мира из опенинга на челесте, расстроенная), обрыв
  держава      тема у труб, валторн и хора октавами, хорал тромбонов, литавры и большой барабан на каждую долю,
               тремоло струнных — величие без мажора: каданс v – i (h-moll – e-moll)
  снег         последняя фраза у валторны издалека, шкатулка закрывается на полуслове, колокол E

    python3 -m kit run requests/ussr-theme/piece.py --parts
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from kit.devices import Composer  # noqa: E402
from kit.events import Piece  # noqa: E402

BPM = 72
SPB = 60.0 / BPM
NAMES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
QUAL = {"": (0, 4, 7), "m": (0, 3, 7), "7": (0, 4, 7, 10), "m7": (0, 3, 7, 10)}

# тема заказчика: (доля, длительность, midi) — 8 тактов по 4 доли
THEME = [(0, 1, 71), (1, 1, 71), (2, 1, 72), (3, .5, 71), (3.5, .5, 69),
         (4, 1, 67), (5, 1, 69), (6, 1, 67), (7, 1, 64),
         (8, 1, 71), (9, 1, 71), (10, 1, 76), (11, 1, 76),
         (12, .5, 74), (12.5, .5, 76), (13, .5, 74), (13.5, .5, 72), (14, .5, 71), (14.5, .5, 72), (15, 1, 74),
         (16, 1, 76), (17, 1, 76), (18, 1, 72), (19, .5, 71), (19.5, .5, 69),
         (20, 1, 71), (21, 1, 69), (22, 1, 67), (23, 1, 64),
         (24, 1, 66), (25, .5, 67), (25.5, .5, 69), (26, .5, 67), (26.5, .5, 66), (27, 1, 64),
         (28, 1, 71), (29, 1, 69), (30, 2, 64)]
# гармония по полутактам (натуральный минор; каданс v – i, как в теме: си – ля – ми)
HARM = [["Em", "Am"], ["C", "Em"], ["Em", "C"], ["G", "Bm"], ["C", "Am"], ["Em", "C"], ["D", "Am7"], ["Bm7", "Em"]]

# тема мира из опенинга (шкатулка Рейха): ступени гармонического минора
BOX = [(0, .5, 4), (.5, .5, 4), (1, .5, 3), (1.5, 1, 4), (2.5, 1.5, 2), (4, .5, 1), (4.5, .5, 2), (5, .5, 4),
       (5.5, 1, 7), (6.5, 1.5, 6)]
HARM_MINOR = [0, 2, 3, 5, 7, 8, 11]


def chord(name, k=0):
    name, _, bass = name.partition("/")
    root, i = NAMES[name[0]], 1
    while i < len(name) and name[i] in "b#":
        root += -1 if name[i] == "b" else 1
        i += 1
    pcs = [(root + k + x) % 12 for x in QUAL[name[i:]]]
    b = root if not bass else NAMES[bass[0]]
    return pcs, (b + k) % 12


class U:
    def __init__(self):
        self.p = Piece("«Холодный мир» — тема СССР", bpm=BPM, meter=(4, 4), key="E minor", seed=1944)
        self.p.meta["subtitle"] = "мелодия заказчика; оркестровка по образу СССР из опенинга"
        self.p.meta["sends"] = {"strings": 0.35, "brass": 0.3, "winds": 0.3, "perc": 0.25, "choir": 0.5, "harp": 0.4,
                                "keys": 0.35}
        self.c = Composer(self.p, lib="vsco", seed=76)
        self.slow = []
        self.prev = {}

    def perf(self, beat):
        s = 0.0
        for b0, b1, f in sorted(self.slow):
            if beat <= b0:
                break
            s += (min(beat, b1) - b0) * (f - 1)
        return (beat + s) * SPB

    def n(self, inst, m, beat, dur, part=None, legato=0.95, **kw):
        kw.setdefault("release", 0.35)
        t0, t1 = self.perf(beat), self.perf(beat + dur)
        e = self.p.note(inst, m, t0, max(0.06, (t1 - t0) * legato), **kw)
        e["wt"], e["wdur"] = beat * SPB, dur * SPB
        if part:
            e["part"] = part
        return e

    def fx(self, kind, beat, **kw):
        return self.c.fx(kind, self.perf(beat), bus="perc", **kw)

    def theme(self, inst, beat0, k=0, oct_=0, part=None, notes=THEME, **kw):
        for b, d, m in notes:
            self.n(inst, m + k + 12 * oct_, beat0 + b, d, part=part, **kw)

    def voicing(self, h, lo, hi, key, size=3):
        pcs = chord(h)[0]
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

    def bass(self, h, lo=28, hi=40):
        b = chord(h)[1]
        return next(x for x in range(lo, hi + 1) if x % 12 == b)

    def counter(self, inst, beat0, lo, hi, part=None, **kw):
        """подголосок: звук аккорда на каждый полутакт, ближайший к прежнему; вступает со второй доли
        полутакта, когда тема движется — держит, на долгих нотах темы делает шаг"""
        prev = (lo + hi) // 2
        for bar, hs in enumerate(HARM):
            for j, h in enumerate(hs):
                pcs = chord(h)[0]
                m = min((x for x in range(lo, hi + 1) if x % 12 in pcs and x != prev), key=lambda x: (abs(x - prev), x))
                b = beat0 + bar * 4 + j * 2
                self.n(inst, m, b + 0.5 if (bar + j) % 2 else b, 1.5 if (bar + j) % 2 else 2, part=part, **kw)
                prev = m


# ===================================================================== разделы
def snow(o, b0, bars=4, final=False):
    """снег: низкий колокол E на каждый такт, пустая квинта флажолетов, арфа роняет звуки"""
    for i in range(bars):
        o.n("tubular", 52 if i % 2 == 0 else 59, b0 + 4 * i, 4, vel=0.45, gain=0.38, release=3.0)
        o.n("cb_sus", 28, b0 + 4 * i, 4, vel=0.4, gain=0.35, attack=1.0, release=1.0)
    o.n("vln_harm", 76, b0, 4 * bars, vel=0.35, gain=0.2, attack=2.0, release=2.0)
    o.n("vla_harm", 71, b0, 4 * bars, vel=0.35, gain=0.18, attack=2.0, release=2.0)
    flakes = [88, 83, 79, 76, 83, 79, 74, 71, 79, 76, 71, 67]
    for j, m in enumerate(flakes[: bars * 3]):
        o.n("harp", m, b0 + 1 + j * 4 / 3, 1.5, vel=0.32, gain=0.28, release=2.5, pan=0.35)
    if not final:
        o.c.breath(o.perf(b0 + 4 * bars - 4), 3.0, gain=0.14)


def old_man(o, b0):
    """тема у виолончели соло, тихо; подголосок валторны; гармония — низкие струнные аккордами по полутактам"""
    o.theme("vc_leg", b0, oct_=-1, vel=0.55, gain=0.62, attack=0.06, part="Violoncello solo")
    o.counter("hn_sus", b0, 52, 62, vel=0.45, gain=0.3, attack=0.25, part="Horns")
    for bar, hs in enumerate(HARM):
        for j, h in enumerate(hs):
            b = b0 + bar * 4 + j * 2
            o.n("cb_sus", o.bass(h), b, 2, vel=0.45, gain=0.42, attack=0.3, part="Contrabassi")
            for m in o.voicing(h, 55, 67, "vla", 2):
                o.n("vla_sus", m, b, 2, vel=0.4, gain=0.22, attack=0.4, part="Viole")


def choir_hymn(o, b0):
    """тема у мужского хора с валторнами; подголоски альтов и вторых скрипок терциями/секстами (подголосочная
    полифония); колокола на сильные доли, литавры тихо"""
    o.theme("choir", b0, oct_=-1, vel=0.55, gain=0.5, attack=0.12, part="Coro (uomini)")
    o.theme("hn_sus", b0, oct_=-1, vel=0.55, gain=0.38, attack=0.05, part="Horns")
    # подголосок: тема терцией/секстой ниже по ладу — где созвучие с аккордом
    for b, d, m in THEME:
        bar = int(b // 4)
        h = HARM[bar][int((b % 4) // 2)]
        pcs = chord(h)[0]
        low = next((x for x in (m - 3, m - 4, m - 8, m - 9) if x % 12 in pcs), None)
        if low is not None:
            o.n("vla_leg", low, b0 + b, d, vel=0.45, gain=0.3, attack=0.05, part="Viole")
    for bar, hs in enumerate(HARM):
        for j, h in enumerate(hs):
            b = b0 + bar * 4 + j * 2
            bs = o.bass(h)
            o.n("cb_sus", bs, b, 2, vel=0.55, gain=0.5, attack=0.2, part="Contrabassi")
            o.n("vc_sus", bs + 12, b, 2, vel=0.5, gain=0.35, attack=0.2, part="Violoncelli")
            for m in o.voicing(h, 59, 74, "vln2", 3):
                o.n("vln_sus", m, b, 2, vel=0.42, gain=0.18, attack=0.4, part="Violini")
        o.n("tubular", 52 if bar % 2 == 0 else 59, b0 + bar * 4, 4, vel=0.5, gain=0.35, release=3.0, part="Campane")
        o.n("timp", 40, b0 + bar * 4, 1, vel=0.45, gain=0.3, part="Timpani")


def memory_1944(o, b0):
    """8 тактов: педаль E, голова темы у тромбонов и тубы в увеличении, гармония сползает e – f (туман);
    тремоло-кластер скрипок ползёт вверх; дыхание противогаза; дальняя дробь; шкатулка сквозь туман; обрыв"""
    head = [(b, d, m) for b, d, m in THEME if b < 8]
    for rep in range(2):  # голова темы дважды, вдвое медленнее, второй раз — на полутон выше (туман)
        for b, d, m in head:
            for inst, sh, g in (("tbn_sus", -12, 0.42), ("tba_sus", -24, 0.32), ("bsn_sus", -12, 0.25)):
                o.n(inst, m + sh + rep, b0 + rep * 16 + 2 * b, 2 * d, vel=0.55 + 0.05 * rep, gain=g, attack=0.08,
                    part={"tbn_sus": "Tromboni", "tba_sus": "Tuba", "bsn_sus": "Fagotti"}[inst])
    o.n("cb_sus", 28, b0, 32, vel=0.5, gain=0.45, attack=1.5, part="Contrabassi")
    o.n("timp_roll", 40, b0, 32, vel=0.35, gain=0.18, attack=3.0, part="Timpani")
    # туман: тремоло скрипок кластером, по полутону выше каждые 2 такта
    for k in range(4):
        for m in (64 + k, 65 + k, 67 + k):
            o.n("vln_trem", m, b0 + 8 * k, 8, vel=0.3 + 0.04 * k, gain=0.12 + 0.02 * k, attack=1.5, part="Violini")
    for k in range(3):
        o.c.breath(o.perf(b0 + 6 + 9 * k), 2.8, gain=0.2)
    # дальняя дробь, как сквозь стену
    t = b0 + 8
    while t < b0 + 30:
        o.fx("snare_soft", t, gain=0.05 + 0.06 * (t - b0) / 30, pan=0.3)
        t += 0.25 if int(t) % 4 < 2 else 0.5
    # шкатулка, расстроенная, сквозь туман — тема мира в гармоническом миноре (e), обрывается
    tune = [64 + 12 + HARM_MINOR[s % 7] + 12 * (s // 7) for _, _, s in BOX]
    o.c.music_box(o.perf(b0 + 20), tune[:8], step=0.42, slow=0.03, flat=0.03, inst="celesta", double=None, gain=0.32)
    # обрыв: удар там-тама и тишина в последнем такте
    o.fx("gong_hit", b0 + 30, gain=0.3)


def power(o, b0):
    """держава: тема у труб, валторн и хора октавами, хорал тромбонов на каждую долю, литавры и большой барабан,
    тремоло струнных; каданс v – i, без мажора"""
    o.theme("tpt_sus", b0, vel=0.68, gain=0.42, attack=0.03, part="Trombe")
    o.theme("hns_sus", b0, oct_=-1, vel=0.68, gain=0.45, attack=0.03, part="Horns")
    o.theme("choir", b0, oct_=-1, vel=0.65, gain=0.5, attack=0.08, part="Coro")
    o.theme("vln_sus", b0, oct_=1, vel=0.6, gain=0.3, attack=0.05, part="Violini")
    for bar, hs in enumerate(HARM):
        for j, h in enumerate(hs):
            b = b0 + bar * 4 + j * 2
            bs = o.bass(h)
            for q in range(2):  # хорал на каждую долю
                for m in o.voicing(h, 50, 64, "tbn", 3):
                    o.n("tbn_sus", m, b + q, 1, vel=0.62, gain=0.3, legato=0.85, part="Tromboni")
                o.n("tba_sus", bs, b + q, 1, vel=0.62, gain=0.4, legato=0.85, part="Tuba")
                o.n("cb_sus", bs, b + q, 1, vel=0.6, gain=0.45, legato=0.85, part="Contrabassi")
                o.n("timp", next(x for x in range(40, 52) if x % 12 == chord(h)[1]), b + q, 1,
                    vel=0.62 if q == 0 else 0.5, gain=0.4, part="Timpani")
                o.fx("bd", b + q, gain=0.22 if q == 0 else 0.14)
            for m in o.voicing(h, 64, 79, "vtrem", 3):
                o.n("vla_trem", m - 12, b, 2, vel=0.45, gain=0.16, part="Viole")
        o.n("tubular", 52 if bar % 2 == 0 else 59, b0 + bar * 4, 4, vel=0.65, gain=0.45, release=3.0, part="Campane")
    o.fx("clash", b0, gain=0.3)
    o.fx("tamtam", b0 + 28, gain=0.35)


def coda(o, b0):
    """снег: последняя фраза у валторны издалека; шкатулка закрывается на полуслове; колокол E"""
    snow(o, b0, bars=4, final=True)
    last = [(b - 24, d, m) for b, d, m in THEME if b >= 24]
    o.theme("hn_sus", b0, notes=last, oct_=-1, vel=0.42, gain=0.32, attack=0.1, part="Horns")
    tune = [64 + 12 + HARM_MINOR[s % 7] + 12 * (s // 7) for _, _, s in BOX]
    o.c.music_box(o.perf(b0 + 9), tune[:4], step=0.5, slow=0.08, flat=0.05, inst="celesta", double=None, gain=0.26)
    o.n("cb_sus", 28, b0 + 8, 8, vel=0.4, gain=0.38, attack=0.5, release=2.0)
    o.n("tubular", 40, b0 + 12, 4, vel=0.5, gain=0.4, release=4.0, part="Campane")


def build(ctx):
    o = U()
    # разделы (в долях): снег 0–16 | старик 16–48 | хор 48–80 | 1944 80–112 | держава 112–144 | снег 144–160
    o.slow += [(0, 16, 1.1), (80, 112, 0.92), (112, 144, 1.12), (140, 144, 1.25), (144, 160, 1.3), (156, 160, 1.4)]
    plan = [(0, "Снег"), (16, "Старик"), (48, "Хор"), (80, "1944"), (112, "Держава"), (144, "Снег")]
    snow(o, 0)
    old_man(o, 16)
    choir_hymn(o, 48)
    memory_1944(o, 80)
    power(o, 112)
    coda(o, 144)
    for bt, label in plan:
        o.p.mark(o.perf(bt), label)["wt"] = bt * SPB
    o.p.meta["beats"] = 160
    # замер `--parts` без баланса: фаготы −19.7 (громче всех), трубы −21.7, хор −24.6, виолончель соло −27.7,
    # мужской хор −28.8, валторны −33.0, контрабасы −36.5, альты −39.6, скрипки −40.9, туба −41.0,
    # тромбоны −42.4, литавры −49.7 LUFS — медь хорала и бас тонули, фаготы торчали
    o.p.balance({"Fagotti": -12, "Tromboni": +12, "Tuba": +10, "Contrabassi": +8, "Violoncelli": +6, "Horns": +5,
                 "Timpani": +12, "Viole": +4, "Violini": +4, "Harp": +4, "Coro (uomini)": +3})
    o.p.meta["length"] = o.perf(160) + 5
    return o.p
