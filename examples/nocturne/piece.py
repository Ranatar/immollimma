#!/usr/bin/env python3
"""Nocturne — a reference piece for the 'impressionist' card (≈ 45 s).

Planing major-ninth chords (the chord keeps its shape and slides), a pentatonic alto-flute line over a
pedal, celesta and harp arpeggios, string harmonics as haze, vibraphone doubling the long notes; a whole-tone
shift in the middle, back to E for the end. Uses Sonatina-only colours (celesta, alto flute, vibraphone,
harmonics) next to VSCO: the hybrid case of the 'auto' library.

    python3 -m kit run examples/nocturne/piece.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from kit.devices import Composer  # noqa: E402
from kit.events import Piece  # noqa: E402
from kit.harmony import MAJ9, in_range  # noqa: E402

E = 4
# roots of the planing chords, a bar each (major ninths sliding): E D C D | E F# G# F# | E E
ROOTS = [4, 2, 0, 2, 4, 6, 8, 6, 4, 4]
# the alto flute: E-major pentatonic (E F# G# B C#), (midi, beats)
TUNE = [(None, 4), (71, 1.5), (73, 0.5), (76, 2), (75, 2), (73, 1), (71, 1), (68, 2), (None, 2), (66, 1), (68, 1),
        (71, 3), (73, 1), (76, 2), (78, 2), (80, 3), (78, 1), (76, 4), (73, 1.5), (71, 0.5), (68, 2), (71, 6)]


def build(ctx):
    p = Piece("Ноктюрн", bpm=54, meter=(4, 4), key="E")
    p.meta["sends"] = {"strings": 0.55, "winds": 0.5, "harp": 0.6, "keys": 0.5}
    c = Composer(p, lib="sso")
    bar = p.b(4)
    p.mark(0, "A")
    p.mark(4 * bar, "B (целотон)")
    p.mark(8 * bar, "A′")
    # pedal: double bass E1 and cello harmonics, the whole piece
    total = len(ROOTS) * bar
    p.note("cb_sus", 28, 0, total, vel=0.25, gain=0.35, attack=3.0, release=4.0)
    prev = None
    for i, r in enumerate(ROOTS):
        t = i * bar
        # the planing chord on muted-sounding strings: same shape, sliding root
        base = in_range(r, 48, 59, 52 if prev is None else prev)
        prev = base
        shape = [base + x for x in (0, 7, 11, 14, 16)]  # root, fifth, seventh, ninth, tenth: open, airy
        for k, m in enumerate(shape):
            inst = "vc_sus" if k == 0 else "vla_sus" if k < 3 else "vln_sus"
            p.note(inst, m, t, bar * 1.02, vel=0.22, gain=0.3, pan=-0.4 + 0.2 * k, attack=0.9, release=1.8)
        # harmonics haze on the ninth and the tenth, every other bar
        if i % 2 == 0:
            p.note("vln_harm", shape[3] + 24, t + 0.3, bar * 1.6, vel=0.3, gain=0.3, pan=0.4, attack=1.2, release=2.0)
        # celesta: a falling figure in the chord, off the beat
        if i in (1, 3, 5, 7, 9):
            fig = sorted({in_range(m % 12, 79, 91) for m in shape}, reverse=True)
            for j, m in enumerate(fig):
                p.note("celesta", m, t + p.b(1.5) + j * p.b(0.25), p.b(1.5), vel=0.4, gain=0.35, pan=0.35)
        # harp: an upward sweep into bars 1, 5 and 9
        if i in (0, 4, 8):
            c.arpeggio(t + 0.05, (r, (0, 7, 11, 14, 16)), n=10, step=0.07, lo=40, gain=0.4, vel=0.4, ring=3.0)
    # the tune on the alto flute, vibraphone doubling the long notes
    t = 0.0
    for m, beats in TUNE:
        d = p.b(beats)
        if m is not None:
            p.note("afl_sus", m, t, d * 0.96, vel=0.42, gain=0.5, pan=0.1, attack=0.18, release=0.8)
            if beats >= 3:
                p.note("vibes", m + 12, t, d, vel=0.32, gain=0.3, pan=0.25)
        t += d
    # the end: a whole-tone celesta descent over the last chord, harmonics fading
    end = 9 * bar
    for j, m in enumerate([92, 90, 88, 86, 84, 82, 80]):
        p.note("celesta", m, end + p.b(1) + j * p.b(0.5), p.b(1), vel=0.3, gain=0.3, pan=0.3 - 0.1 * j)
    p.note("vln_harm", 88, end, bar * 1.5, vel=0.25, gain=0.25, pan=-0.3, attack=1.0, release=3.0)
    # balance by part (dB); measured 2026-11-12: celesta 15, vibraphone 28, the pedal 26 dB under the alto flute — the colours were lost
    p.balance({"Celesta": 11, "Vibraphone": 16, "Basses": 15, "Cellos": 7, "Violas": 7, "Violins": 4})
    return p
