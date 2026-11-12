#!/usr/bin/env python3
"""Chorale prelude in D minor — a reference piece for the 'baroque' card (≈ 50 s, metrical, notation-ready).

A chorale tune (original, written here) in long notes on the oboe, harmonised a chord per half note;
violas spin continuous quavers from the chord tones with passing notes; the bass walks in crotchets
(cellos, bassoon, later the organ pedal); the harpsichord plays the continuo on the beats. Terraced
dynamics: phrase 1 p, phrase 2 mf with bassoon, phrase 3 f with organ and horn; a held final chord.

    python3 -m kit run examples/chorale_prelude/piece.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from kit.devices import Composer  # noqa: E402
from kit.events import Piece  # noqa: E402
from kit.harmony import SCALES, chord_pcs, in_range, roman  # noqa: E402

KEY = 2  # D
# a chord per half note, three phrases of four bars
PROG = ["i", "V", "i", "iv", "VII", "III", "iv", "V",
        "i", "VI", "ii°", "V", "i", "iv", "V", "i",
        "III", "VII", "III", "VI", "iv", "V", "i", "i"]
# the tune's contour: where the soprano wants to be (it takes the nearest chord tone, avoiding repeats)
CONTOUR = [74, 73, 74, 74, 76, 77, 79, 76, 74, 77, 79, 76, 77, 74, 73, 74, 77, 79, 81, 79, 77, 76, 74, 74]


def chord(n):
    return roman(KEY, n, "harmonic_minor" if n in ("V", "ii°") else "minor")


def scale_step(m, up):
    sc = [(KEY + x) % 12 for x in SCALES["harmonic_minor"]]
    k = m + (1 if up else -1)
    while k % 12 not in sc:
        k += 1 if up else -1
    return k


def build(ctx):
    p = Piece("Хоральная прелюдия ре минор", bpm=66, meter=(4, 4), key="D minor")
    p.meta["sends"] = {"strings": 0.3, "winds": 0.3, "keys": 0.25, "organ": 0.4}
    c = Composer(p)
    half = p.b(2)
    chords = [chord(n) for n in PROG]
    # soprano: the chorale tune
    sop, prev = [], None
    for ch, want in zip(chords, CONTOUR):
        cands = [m for m in range(64, 84) if m % 12 in chord_pcs(ch)]
        cands.sort(key=lambda m: (abs(m - want), m == prev))
        prev = cands[0]
        sop.append(prev)
    for ph in range(3):
        p.mark(p.bar(4 * ph), ["Фраза 1", "Фраза 2", "Фраза 3"][ph])
    for i, (ch, s) in enumerate(zip(chords, sop)):
        t = i * half
        ph = i // 8
        last = i == len(chords) - 1
        dur = half * (3 if last else 1)
        vel = [0.4, 0.55, 0.72][ph]
        # the tune
        p.note("ob_sus", s, t, dur * 0.97, vel=vel, gain=0.55, pan=0.1, attack=0.04, release=0.5)
        if ph == 2:
            p.note("hn_sus", s - 12, t, dur * 0.97, vel=vel * 0.8, gain=0.3, pan=-0.3, attack=0.05)
        # inner voices: alto and tenor as viola quavers from chord tones and passing notes
        pcs = chord_pcs(ch)
        tones = sorted(m for m in range(55, 68) if m % 12 in pcs)
        nxt = chord_pcs(chords[i + 1])[0] if i + 1 < len(chords) else pcs[0]
        up = i % 2 == 0
        fig = tones[:3] if up else tones[-3:][::-1]
        target = in_range(nxt, 55, 67, fig[-1])
        fig = fig + [scale_step(fig[-1], target > fig[-1]) if target != fig[-1] else fig[-1]]
        if not last:
            for j, m in enumerate(fig):
                p.note("vla_sus", m, t + j * half / 4, half / 4 * 0.9, vel=vel * 0.8, gain=0.4, pan=0.25, attack=0.02,
                       release=0.25)
        else:
            p.chord("vla_sus", tones[:2], t, dur, vel=vel * 0.7, gain=0.35, pan=0.25)
        # bass: root on the beat, a passing note toward the next root
        root = in_range(ch[0], 38, 50, 44)
        nroot = in_range(chords[i + 1][0], 38, 50, root) if i + 1 < len(chords) else root
        walk = [root, root if nroot == root else scale_step(root, nroot > root)]
        for j, m in enumerate(walk if not last else [root]):
            d = half / 2 * 0.92 if not last else dur
            p.note("vc_sus", m, t + j * half / 2, d, vel=vel, gain=0.45, pan=-0.25, attack=0.02, release=0.3)
            p.note("cb_pizz" if ph == 0 else "cb_sus", m - 12, t + j * half / 2, d, vel=vel * 0.8, gain=0.35, pan=-0.35,
                   release=0.3)
            if ph >= 1:
                p.note("bsn_sus", m, t + j * half / 2, d, vel=vel * 0.8, gain=0.3, pan=-0.1, release=0.3)
        if ph == 2:
            p.note("org_quiet", root - 12, t, dur, vel=0.5, gain=0.35, attack=0.05, release=1.0)
        # continuo: harpsichord chord on each beat of the half note (only the downbeat at the end)
        voicing = sorted(m for m in range(50, 70) if m % 12 in pcs)[:4]
        for j in range(1 if last else 2):
            p.chord("hpsd", voicing, t + j * half / 2, half / 2 * 0.8, vel=0.5 + 0.1 * ph, gain=0.45, pan=-0.05,
                    spread=0.006)
    end = len(chords) * half + 2 * half
    c.arpeggio(end - 2 * half - 0.05, chords[-1], n=6, step=0.07, inst="hpsd", lo=50, gain=0.4, ring=2.0)
    return p
