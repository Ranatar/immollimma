#!/usr/bin/env python3
"""Phase — a reference piece for the 'minimalism' card (≈ 50 s).

Two marimbas play the same twelve-note figure; the second has one extra note in its cycle (13), so the two
drift apart and meet again — a phase process written as arithmetic. Over it: clarinet long tones that change
every eight bars, a pizzicato pulse, and an additive glockenspiel line (one more note each round).

    python3 -m kit run examples/phase/piece.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from kit.events import Piece  # noqa: E402

FIG = [64, 66, 71, 73, 74, 66, 64, 73, 71, 66, 74, 73]  # twelve semiquavers, E dorian-ish
EXTRA = 69  # the thirteenth note of the second marimba
CLAR = [(52, 57), (54, 59), (50, 57), (52, 59), (52, 57)]  # clarinet pairs, one per eight bars of 3/4
GLOCK = [76, 78, 81, 83, 85, 83, 81]


def build(ctx):
    p = Piece("Фаза", bpm=126, meter=(3, 4), key="E dorian")
    p.meta["sends"] = {"harp": 0.35, "winds": 0.4, "strings": 0.3}
    s16 = p.b(0.25)
    total_bars = 26
    n = total_bars * 12
    p.mark(0, "унисон")
    p.mark(p.bar(8), "расхождение")
    p.mark(p.bar(16), "встреча")
    for k in range(n):
        t = k * s16
        acc = 0.55 if k % 3 == 0 else 0.4
        p.note("marimba", FIG[k % 12], t, s16 * 2, vel=acc, gain=0.4, pan=-0.45)
        fig2 = FIG + [EXTRA]
        if k >= 4 * 12:  # the second marimba enters after four bars, one note longer per cycle
            j = k - 4 * 12
            p.note("marimba", fig2[j % 13], t, s16 * 2, vel=acc * 0.95, gain=0.38, pan=0.45)
    # the pulse: violins and violas pizzicato on every beat, a bass on the bar
    for b in range(total_bars * 3):
        t = p.b(b)
        p.note("vla_pizz", 52 if (b // 24) % 2 == 0 else 54, t, 0.2, vel=0.4, gain=0.35, pan=-0.1)
        if b % 3 == 0:
            p.note("cb_pizz", 40 if (b // 24) % 2 == 0 else 38, t, 0.3, vel=0.55, gain=0.45, pan=-0.2)
    # clarinet long tones, a pair every eight bars
    for i, (lo, hi) in enumerate(CLAR):
        t = p.bar(4 + 4 * i)
        if t >= p.bar(total_bars - 2):
            break
        for m, pan in ((lo, -0.2), (hi, 0.2)):
            p.note("cl_sus", m + 12, t, p.bar(4) * 0.98, vel=0.35, gain=0.35, pan=pan, attack=0.6, release=1.0)
    # additive glockenspiel: round r plays the first r notes of the line
    t = p.bar(10)
    for r in range(1, len(GLOCK) + 1):
        for m in GLOCK[:r]:
            p.note("glock", m + 12, t, p.b(1), vel=0.35, gain=0.3, pan=0.3)
            t += p.b(0.5)
        t += p.b(1)
        if t > p.bar(total_bars - 1):
            break
    # last bar: everything on E, held
    end = p.bar(total_bars)
    for m, inst in ((40, "cb_sus"), (52, "vc_sus"), (64, "cl_sus"), (76, "marimba")):
        p.note(inst, m, end, p.bar(2), vel=0.45, gain=0.4, attack=0.05, release=2.0)
    return p
