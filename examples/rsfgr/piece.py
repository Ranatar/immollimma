#!/usr/bin/env python3
"""R.S.F.G.R. 1920–2000 — the score of the archive video (second edition), ported onto the kit.

Every event of the scenario is a cue (cues.json, exported from the video's frame plan): t = change of
borders, fly = start of the camera flight, hold = the document on screen; mood picks the music. Through the
century a 'madness index' m grows 0 → 1 and rots the Union's harmony (out-of-tune doubles sinking lower);
the awake stay in tune; on the last lamp of 1997 the rot collapses into a perfect unison.

    python3 -m kit run examples/rsfgr/piece.py            (≈ 1 min; out/ next to this file)

Differences from the original (music/score_rsfgr.py of the future_borders project):
  * timpani sit where they should (D2–F3, the drums' real pitches from VSCO's own SFZ); the original took
    the drum pitches from pYIN, which hears timpani an octave low;
  * nothing else changed: same moods, same devices, same numbers.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from kit import fx as fxcat  # noqa: E402
from kit.devices import Composer  # noqa: E402
from kit.events import Piece  # noqa: E402
from kit.harmony import FIFTH, MAJ, MIN, in_range  # noqa: E402

D = 2
GROWTH_PROG = [(2, MIN), (10, MAJ), (7, MIN), (9, MAJ), (5, MAJ), (0, MAJ), (2, MIN), (3, MAJ)]
AWAKE_PROG = [(0, MAJ), (7, MAJ), (9, MIN), (5, MAJ)]
REPRESS_PROG = [(7, MIN), (2, MIN), (3, MAJ), (9, (0, 3, 6))]


def rot(m):
    """the rot of a string chord at madness m: an out-of-tune double, sinking"""
    det = 0.05 + 0.32 * m
    return dict(detune=det if det > 0.06 else 0.0, drift=-0.06 - 0.45 * m, double_gain=0.35 + 0.4 * m)


def mrot(m):
    """the rot of a motif: doubled out of tune once m is high enough, long notes sinking"""
    return dict(detune=0.05 + 0.32 * m, drift=-0.06 - 0.45 * m, double_gain=0.5 * m)


def lullaby(c, t, m):
    """Lenin's lullaby on the flute, each note sinking as it is held"""
    c.melody(t, [(77, 1.0), (74, 0.8), (72, 0.8), (69, 2.2)], inst="fl_sus", vel=0.4, gain=0.4, pan=0.25, attack=0.15,
             bend=-0.4 * m - 0.1, detune_double=0.15 + 0.3 * m)


def build(ctx):
    cues = ctx.cues
    cs = cues["cues"]
    INTRO, OUTRO = cues["intro"], cues["outro"]
    p = Piece("Р.С.Ф.Г.Р. 1920–2000", bpm=60, meter=(4, 4), key="D minor")
    p.meta["sends"] = {}
    for e in cs:
        p.mark(e["t"], e["label"])
    c = Composer(p, lib="vsco")
    a, _ = INTRO
    b = cs[0]["t"] + 0.3
    p.note("org_quiet", 38, a, b - a + 1.0, vel=0.5, gain=0.4, bus="organ", attack=1.5, release=2.0)
    p.note("cb_trem", 38, a + 0.5, b - a, vel=0.4, gain=0.35, pan=-0.3, bus="strings", attack=2.5)
    c.breath(a, b - a + 1.0, gain=0.45)
    c.fx("alien", a + 1.0, gain=0.25, shift=-5, bus="deep", attack=1.0)
    c.fx("glock_down", a + 2.5, gain=0.25, shift=-3, bus="harp")
    c.motif(a + 3.0, (D, MIN), inst="hn_mute", vel=0.35, gain=0.35)
    c.heartbeat(a + 4.0, cs[1]["t"], gain=0.3)
    gi = ai = ri = 0
    for k in range(1, len(cs) + 1):
        e = cs[k - 1]
        eid = e.get("id")
        mood = e["mood"]
        m = max(0.0, min(1.0, (e["year"] - 1920) / 77.0))
        t_fly, t_tr, t_hold = e["fly"], e["t"], e["hold"]
        t_end = cs[k]["t"] + 0.3 if k < len(cs) else OUTRO[0] + 0.5
        has_doc, big, vortex = e["has_doc"], e["big"], e["vortex"]

        if mood in ("growth", "feast"):
            ch = GROWTH_PROG[gi % len(GROWTH_PROG)]
            gi += 1
            c.pad(t_tr, t_end + 0.6, ch, vel=0.5, gain=0.45, **rot(m))
            c.motif(t_tr, ch, inst="hn_sus" if gi % 2 else "tbn_sus", vel=0.62, **mrot(m))
            c.timp(t_tr, ch[0], vel=0.75)
            p.note("tba_sus", in_range(ch[0], 29, 40), t_tr, 2.2, vel=0.5, gain=0.4, bus="brass", release=0.8)
            c.spores(t_tr + 0.05, 4.0, density=28 + 25 * m, gain=0.2)
            c.heartbeat(t_tr + 1.0, t_end, gain=0.25)
            if mood == "feast":
                key = [10, 3, 5, 0][gi % 4]
                c.fx("clash", t_hold, gain=0.3, pan=0.3, bus="perc")
                c.march(t_hold + 0.1, t_end, key=key, gain=0.42, sour=0.25 * m, detune=0.12 + 0.35 * m)
            elif has_doc:
                c.arpeggio(t_hold + 0.2, ch, vel=0.45, gain=0.45)
        elif mood == "lamp":
            ch = (5, MAJ)
            c.pad(t_tr, t_end + 0.6, ch, vel=0.4, gain=0.38, **rot(m))
            p.note("org_quiet", in_range(ch[0], 41, 52), t_tr, t_end - t_tr + 0.5, vel=0.4, gain=0.3, bus="organ",
                   attack=1.0)
            for j in range(14):  # lamps lighting one by one, each a little out of tune
                p.note("glock", in_range([0, 4, 7, 9][j % 4] + 5, 79, 96), t_tr + 0.2 + j * 0.37, 1.5, vel=0.45,
                       gain=0.28, pan=-0.7 + 0.1 * j, bus="harp", detune=c.rng.uniform(-0.3, 0.3))
            p.grains(fxcat.files("glass"), t_tr + 0.5, t_hold + 1.5, 12, gain=0.06, bus="spores", pitch=[12, 17, 19, 24])
            c.march(t_hold + 0.2, t_end, key=5, bpm=104, gain=0.36, sour=0.0, detune=0.45)
        elif mood == "sleeper":
            dur = t_end - t_fly + 0.4
            p.note("org_loud" if vortex else "org_quiet", 26, t_fly, dur, vel=0.6, gain=0.45, bus="organ",
                   attack=1.2, release=2.2, bend=-0.3 * m)
            p.note("cb_trem", 38, t_fly + 0.2, dur, vel=0.6, gain=0.5, pan=-0.3, bus="strings", attack=1.6)
            p.note("vc_trem", 51, t_tr, t_end - t_tr + 0.6, vel=0.45, gain=0.3, pan=-0.05, bus="strings", attack=1.2,
                   bend=-0.5 * m)
            p.note("vla_trem", 52, t_tr + 0.3, t_end - t_tr + 0.4, vel=0.35, gain=0.22, pan=0.2, bus="strings",
                   attack=1.5, detune=0.3 * m)
            c.breath(t_fly + 0.3, min(7.0, dur), gain=0.5)
            c.fx("alien", t_tr + 0.4, gain=0.22, shift=-7 + 2 * (k % 3), pan=0.3, bus="deep", attack=0.6)
            if vortex:
                c.shepard(t_tr - 0.5, t_end, gain=0.3)
                c.timp(t_tr, D, vel=0.85, roll=t_hold - t_tr + 0.4)
                c.fx("gong_roll", t_tr - 0.3, gain=0.35, bus="perc", shift=-5, dur=t_hold - t_tr + 2.0)
                p.note("tba_sus", 26, t_tr + 0.2, 3.0, vel=0.7, gain=0.45, bus="brass", bend=-1.0)
                p.note("tbn_sus", 39, t_tr + 0.4, 2.6, vel=0.6, gain=0.35, bus="brass", bend=-1.5)
            if eid == "alarm":
                for j in range(3):
                    c.fx("siren", t_tr + 0.3 + 1.6 * j, gain=0.22, pan=-0.6 + 0.6 * j, shift=-2 * j, bus="fx")
            if eid == "kara":
                c.fx("bubbles", t_tr + 0.6, gain=0.4, shift=-9, bus="deep")
                c.fx("bubbles", t_hold + 0.5, gain=0.3, shift=-12, bus="deep")
            if eid == "chamber":
                c.fx("brick", t_tr, gain=0.35, pan=-0.2, bus="fx")
            if eid == "cylinder":
                p.note("org_quiet", 62, t_tr - 2.0, 2.2, vel=0.5, gain=0.3, bus="organ", reverse=True)
                c.fx("gong_scrape", t_hold + 0.4, gain=0.3, bus="fx")
            if eid == "protocol":
                c.fx("chain", t_tr, gain=0.3, pan=0.3, bus="fx", dur=3.0)
                c.fx("timpsnare", t_hold, gain=0.45, bus="perc")
            if eid in ("lenin_sleeps", "sprouted", "chamber"):
                lullaby(c, t_hold + 0.4, m)
            if eid == "sprouted":  # the voice in the lamps: a trombone wavering without words
                tt = t_hold + 1.0
                for j, d_ in enumerate([0.9, 0.5, 1.4, 0.7, 1.8]):
                    p.note("tbn_sus", [45, 46, 44, 45, 43][j], tt, d_, vel=0.4, gain=0.3, pan=-0.3, bus="brass",
                           bend=c.rng.uniform(-0.8, 0.5), attack=0.1)
                    tt += d_ + [0.4, 1.1, 0.4, 4.0][j % 4] * 0.3
                c.spores(t_tr, 5.0, density=18, gain=0.16)
            if has_doc:
                p.note("glock", 86, t_hold + 0.2, 2.0, vel=0.3, gain=0.18, pan=0.4, bus="harp", detune=-0.3)
                p.note("glock", 87, t_hold + 1.4, 2.0, vel=0.25, gain=0.15, pan=0.4, bus="harp", detune=0.2)
        elif mood == "repress":
            ch = REPRESS_PROG[ri % len(REPRESS_PROG)]
            ri += 1
            c.pad(t_tr, t_end + 0.5, ch, vel=0.3, gain=0.32, bass_only=True, **rot(m))
            root = in_range(ch[0], 43, 54)
            pat = [0, 7, 12, 7, 3 if 3 in ch[1] else 4]  # five to the bar: the step that is one too many
            beat = 60 / 132 / 2
            t, j = t_tr, 0
            while t < t_end - 0.1:
                p.note("vc_pizz" if j % 10 < 5 else "vla_pizz", root + pat[j % 5], t, 0.25,
                       vel=0.55 if j % 5 == 0 else 0.35, gain=0.42, pan=-0.1 if j % 2 else 0.1, bus="strings",
                       release=0.3)
                if j % 5 == 0:
                    c.fx("claves", t, gain=0.12, pan=0.5, bus="perc")
                t += beat
                j += 1
            p.note("tpt_mute", in_range(ch[0] + 1, 62, 73), t_tr, 0.9, vel=0.55, gain=0.3, pan=0.25, bus="brass")
            p.note("bsn_sus", in_range(ch[0], 34, 45), t_tr, t_end - t_tr, vel=0.4, gain=0.3, pan=0.1, bus="winds",
                   attack=0.4, bend=-0.3)
            c.fx("metal", t_tr, gain=0.25, pan=-0.4, bus="fx")
            if eid in ("case1147", "case427"):
                c.fx("chain", t_tr + 0.5, gain=0.22, pan=0.4, bus="fx", dur=4.0)
            if eid == "case611":
                c.fx("guiro", t_hold, gain=0.3, bus="fx")
            if has_doc:
                c.fx("timpsnare", t_hold, gain=0.4, bus="perc")
                c.fx("susp_scrape", t_hold + 0.5, gain=0.18, bus="fx", dur=3.0)
        elif mood == "school":
            ch = (5, MAJ)
            c.pad(t_tr, t_end + 0.5, ch, vel=0.3, gain=0.28, **rot(m))
            tune = [77, 77, 84, 84, 86, 86, 84, 82, 82, 81, 81, 79, 79, 77]  # the alphabet song, in F
            for j, n_ in enumerate(tune):  # a music box running down: slower, flatter
                tt = t_tr + sum(0.38 + 0.025 * i for i in range(j))
                p.note("glock", n_ + 12 if n_ + 12 <= 96 else n_, tt, 0.7, vel=0.4, gain=0.3, pan=0.3, bus="harp",
                       detune=-0.04 * j)
                p.note("vln_pizz", n_ - 12, tt, 0.3, vel=0.35, gain=0.3, pan=-0.2, bus="strings", detune=-0.03 * j)
            p.note("cl_sus", 64, t_end - 2.5, 2.4, vel=0.3, gain=0.25, bus="winds", bend=-0.6)
        elif mood == "hymn":
            prog = [(D, MIN), (10, MAJ), (7, MIN), (9, MAJ), (D, MIN)]
            seg = (t_end - t_tr) / len(prog)
            c.fx("snare", t_tr - 0.25, gain=0.35, bus="perc")
            for j, ch in enumerate(prog):
                tt = t_tr + j * seg
                c.pad(tt, tt + seg + 0.4, ch, vel=0.75, gain=0.55, attack=0.25, **rot(m))
                pcs = [(ch[0] + i) % 12 for i in ch[1]]
                for lane, (lo, hi, pc, art) in enumerate([(29, 40, ch[0], "tba_sus"), (40, 52, pcs[2], "tbn_sus"),
                                                         (50, 62, pcs[0], "tbn_sus"), (55, 67, pcs[1], "hn_sus"),
                                                         (60, 70, pcs[2], "hn_sus")]):
                    p.note(art, in_range(pc, lo, hi), tt, seg * 0.96, vel=0.72, gain=0.42, pan=-0.3 + 0.15 * lane,
                           bus="brass", attack=0.05, release=0.6)
                c.timp(tt, ch[0], vel=0.8 if j in (0, len(prog) - 1) else 0.55)
            c.motif(t_tr, (D, MIN), inst="tpt_sus", vel=0.7, gain=0.4, octave=62,
                       steps=(0, 7, 8, 7, 5, 3, 1, 0), durs=[seg / 2] * 8, **mrot(m))
            c.fx("clash", t_end - seg, gain=0.35, bus="perc")
            c.spores(t_end - seg, 4.0, density=35, gain=0.2)
        elif mood == "awake":
            ch = AWAKE_PROG[ai % len(AWAKE_PROG)]
            ai += 1
            c.pad(t_tr, t_end + 0.6, ch, vel=0.3, gain=0.25, attack=1.2)
            root = ch[0]
            pcs = [(root + i) % 12 for i in ch[1]]
            p.note("hn_sus", in_range(root, 41, 52), t_tr, t_end - t_tr, vel=0.45, gain=0.32, pan=-0.25,
                   bus="brass", attack=0.6)
            p.note("hn_sus", in_range(root + 7, 48, 59), t_tr + 0.1, t_end - t_tr, vel=0.45, gain=0.3, pan=-0.15,
                   bus="brass", attack=0.6)
            tt = t_tr + 0.4
            for j, pc in enumerate([pcs[0], pcs[1], pcs[2], pcs[1]]):
                d_ = 1.1 if j < 3 else 2.4
                p.note("cl_sus", in_range(pc, 60, 71), tt, d_, vel=0.45, gain=0.4, pan=0.1, bus="winds", attack=0.1)
                p.note("fl_sus", in_range(pc + (4 if 4 in ch[1] else 3), 72, 83), tt, d_, vel=0.4, gain=0.3,
                       pan=0.3, bus="winds", attack=0.1)
                tt += d_
            # reason keeps time: a steady metronome on the claves, and a clean triangle
            t, j = t_tr, 0
            while t < t_end - 0.2:
                c.fx("claves", t, gain=0.1 if j % 4 else 0.16, pan=0.5, bus="perc")
                t += 0.6
                j += 1
            c.fx("triangle", t_tr, gain=0.25, pan=0.4, bus="perc")
            if eid in ("budapest", "pannonia", "bohemia"):  # the spell breaks
                c.fx("glass", t_tr - 0.05, gain=0.35, pan=0.2, bus="fx")
            if has_doc:
                c.arpeggio(t_hold + 0.3, ch, n=6, step=0.11, vel=0.4, lo=55, gain=0.4)
        elif mood == "heresy":
            wt = [D, 4, 6, 8, 10, 0]
            ch = (D, (0, 4, 8))
            c.pad(t_tr, t_end + 0.5, ch, vel=0.35, gain=0.35, bass_only=True, **rot(m))
            c.buzz(t_tr, t_end - t_tr, gain=0.28)
            for j in range(2):
                c.fx("alien", t_tr + 0.3 + 2.5 * j, gain=0.25, shift=3 - 4 * j, pan=-0.5 + j, bus="deep")
            if eid in ("urga", "altai"):
                for j in range(4):
                    c.fx("nepal", t_tr + 0.4 + 1.3 * j, gain=0.3, pan=0.4 - 0.25 * j, bus="harp")
            tt = t_tr + 0.6
            for j in range(8):
                p.note("glock", in_range(wt[(5 - j) % 6], 84, 96), tt, 1.6, vel=0.45, gain=0.3, pan=0.5 - 0.12 * j,
                       bus="harp", detune=0.5 if j % 2 else 0.0)
                tt += 0.38 + 0.08 * (j % 3)
            if eid == "exodus":  # the flight: a reversed swell and a glissando upward
                p.note("org_quiet", 74, t_tr - 2.2, 2.3, vel=0.5, gain=0.3, bus="organ", reverse=True)
                c.fx("glock_up", t_hold, gain=0.3, bus="harp")
                c.shepard(t_hold, t_end, up=True, gain=0.2, period=5.0)
            if big:
                c.timp(t_tr, 8, vel=0.5)
            if has_doc:
                c.arpeggio(t_hold + 0.2, ch, n=9, step=0.06, vel=0.35, lo=62, gain=0.35)
        elif mood == "dry":
            ch = (D, FIFTH)
            c.pad(t_tr, t_end + 0.4, ch, vel=0.3, gain=0.42, bass_only=True, attack=1.5)
            t = t_tr
            while t < t_end - 0.3:
                p.note("cb_pizz", in_range(D, 26, 38), t, 0.4, vel=0.6, gain=0.7, pan=-0.2, bus="strings")
                t += 1.6
            c.fx("guiro", t_tr + 0.2, gain=0.25, pan=0.3, bus="fx")
            c.fx("ambience", t_tr, gain=0.25, bus="deep", dur=t_end - t_tr, attack=1.5)
            p.note("fl_sus", 69, t_tr + 0.8, 2.6, vel=0.3, gain=0.3, pan=0.3, bus="winds", attack=0.3)
            p.note("fl_sus", 64, t_tr + 3.6, 2.6, vel=0.25, gain=0.25, pan=0.3, bus="winds", attack=0.3)
            if eid == "salt":  # salt crystals: high glass grains
                p.grains(fxcat.files("glass"), t_tr + 0.3, t_end - 0.5, 9, gain=0.07, bus="spores",
                              pitch=[12, 14, 17, 19, 24])
            if eid == "dry":
                c.fx("brick", t_hold, gain=0.25, bus="fx")
            c.timp(t_tr, D, vel=0.35)
        elif mood == "final":
            # gather: a rising endless glissando, snare and timpani rolls, a cymbal scraped to the breaking point
            c.shepard(t_fly, t_tr + 0.5, up=True, gain=0.35, period=3.5)
            c.timp(t_fly + 0.3, 9, vel=0.7, roll=t_tr - t_fly - 0.2)
            c.fx("susp_scrape", t_fly, gain=0.25, bus="fx", dur=t_tr - t_fly)
            for lane, (art, mm) in enumerate([("cb_trem", 33), ("vc_trem", 45), ("vla_trem", 57), ("vln_trem", 64)]):
                p.note(art, mm, t_fly, t_tr - t_fly + 0.3, vel=0.6, gain=0.35, pan=-0.3 + 0.2 * lane, bus="strings",
                       attack=t_tr - t_fly)
                p.note(art, mm, t_fly, t_tr - t_fly + 0.3, vel=0.6, gain=0.25, pan=0.3 - 0.2 * lane, bus="strings",
                       attack=t_tr - t_fly, detune=0.4)
            prog = [(10, MAJ), (7, MIN), (9, MAJ)]
            seg = (t_hold - t_tr) / len(prog)
            for j, ch in enumerate(prog):  # the chorale at its most out of tune
                tt = t_tr + j * seg
                c.pad(tt, tt + seg + 0.4, ch, vel=0.7, gain=0.55, attack=0.3, **rot(m))
                pcs = [(ch[0] + i) % 12 for i in ch[1]]
                for lane, (lo, hi, pc, art) in enumerate([(29, 40, ch[0], "tba_sus"), (43, 54, pcs[2], "tbn_sus"),
                                                         (52, 62, pcs[1], "hn_sus"), (57, 68, pcs[0], "hn_sus")]):
                    p.note(art, in_range(pc, lo, hi), tt, seg * 0.97, vel=0.7, gain=0.42, pan=-0.3 + 0.2 * lane,
                           bus="brass", attack=0.05)
                    p.note(art, in_range(pc, lo, hi), tt, seg * 0.97, vel=0.6, gain=0.3, pan=0.3 - 0.2 * lane,
                           bus="brass", attack=0.05, detune=0.45, bend=-0.4)
            # the last lamp: D major, everyone — and for the first time in the century, perfectly in tune
            m = 0.0
            ch = (D, MAJ)
            dur = t_end - t_hold + 2.0
            c.pad(t_hold, t_hold + dur, ch, vel=0.85, gain=0.6, attack=0.05)
            for lane, (lo, hi, pc, art) in enumerate([(26, 38, D, "tba_sus"), (38, 50, D, "tbn_sus"),
                                                     (45, 57, 9, "tbn_sus"), (54, 66, 6, "hn_sus"),
                                                     (57, 69, 9, "hn_sus"), (62, 74, D, "tpt_sus"),
                                                     (66, 78, 6, "tpt_sus")]):
                p.note(art, in_range(pc, lo, hi), t_hold, min(dur, 7.0), vel=0.8, gain=0.4, pan=-0.35 + 0.1 * lane,
                       bus="brass", attack=0.03, release=1.5)
            for n_, g_ in [(26, 0.45), (50, 0.3), (54, 0.28), (57, 0.28)]:
                p.note("org_loud", n_, t_hold, dur + 3, vel=0.8, gain=g_, bus="organ", release=3.0)
            c.timp(t_hold, D, vel=0.95)
            c.timp(t_hold + 0.02, 9, vel=0.6)
            c.fx("gong_hit", t_hold, gain=0.45, bus="perc")
            c.fx("clash", t_hold, gain=0.4, bus="perc")
            for j, n_ in enumerate([86, 90, 93, 98, 93, 90, 86]):
                p.note("glock", n_, t_hold + 0.25 + j * 0.3, 2.5, vel=0.45, gain=0.25, pan=0.4 - 0.1 * j, bus="harp")
            c.spores(t_hold + 0.1, 6.0, density=60, gain=0.18)
            c.march(t_hold + 2.0, t_end, key=D, bpm=120, gain=0.4, sour=0.0, detune=0.0)
    # outro: the one mycelium, held, dying away; the heartbeat goes on, slower
    a, b = OUTRO
    m = 0.0
    c.pad(a, b + 1.0, (D, MAJ), vel=0.4, gain=0.4, attack=1.5)
    p.note("org_quiet", 38, a, b - a + 2.0, vel=0.5, gain=0.4, bus="organ", attack=1.0, release=3.0)
    p.note("org_quiet", 54, a + 0.5, b - a, vel=0.4, gain=0.25, bus="organ", attack=1.5, release=3.0)
    c.arpeggio(a + 1.0, (D, MAJ), n=10, step=0.12, vel=0.35, lo=50, gain=0.35)
    c.motif(a + 3.5, (D, MAJ), inst="hn_mute", vel=0.3, gain=0.3, steps=(0, 7, 9, 7), durs=(0.8, 0.8, 0.8, 3.5))
    c.heartbeat(a + 1.0, b - 1.0, gain=0.22)
    c.fx("alien", a + 4.0, gain=0.12, shift=-9, bus="deep", attack=2.0)
    return p
