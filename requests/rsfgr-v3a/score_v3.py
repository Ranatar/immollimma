"""Р.С.Ф.Г.Р. 1920–2000, третья редакция — общая партитура двух вариантов.

    variant "A": идеи 1, 2, 4, 5 — разум = контрапункт (канон, растущий от события к событию), Грибница =
                 унисон; три лейтмотива с превращениями (гимн Грибницы, колыбельная Ленина, тема Ми-Го);
                 архив стареет наоборот (граммофон 1920-х → полное стерео 1990-х → моно на последней лампе);
                 шесть частей видео = шесть актов со своим ведущим тембром.
    variant "B": всё это плюс 3 (Интернационал как cantus firmus, гниющий на четверть тона), 6 (быт:
                 вальс 1947 → 5/8, фокстрот 1930, позывной радио 1977, пионерский горн 1931) и 7 (нечеловеческие
                 тембры: скользящие кластеры хора, удары низа рояля, контрфагот и бас-кларнет, флажолеты).

Сквозные процессы: индекс безумия m = (год − 1920)/77 гноит строй Союза; ключ Союза оседает на полутон с
каждым актом (d → cis → c → h → b) и в последнем акте возвращается в d; число голосов разума растёт 1 → 4;
архив молодеет. Все времена — из cues.json.
"""
import os
import sys

import numpy as np

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
sys.path.insert(0, ROOT)
from kit import fx as fxcat  # noqa: E402
from kit.devices import Composer  # noqa: E402
from kit.events import Piece  # noqa: E402
from kit.harmony import FIFTH, MAJ, MIN, in_range  # noqa: E402
from kit.instruments import INSTR  # noqa: E402

D = 2
DOM7 = (0, 4, 7, 10)

# -- acts ---------------------------------------------------------------------------------------------------
ACT_START = {"II": "elbe", "III": "drought", "IV": "pannonia", "V": "receiver", "VI": "dry"}  # by the fly
ACT_SHIFT = {"I": 0, "II": -1, "III": -2, "IV": -3, "V": -4, "VI": 0}  # the Union's key sinks act by act
ACT_NAME = {"I": "I · медь и литавры", "II": "II · пиццикато и сухие шумы", "III": "III · хор и орган",
            "IV": "IV · деревянные и контрапункт", "V": "V · челеста и колокола", "VI": "VI · все"}

# -- leitmotif 1: the hymn of the Mycelium (D minor, offsets from D4, beats; chords per half bar) -------------
HYMN = [[(0, 1), (7, 1), (8, 1.5), (7, .5)], [(5, 1), (3, 1), (2, 2)], [(3, 1), (5, 1), (7, 1.5), (12, .5)],
        [(10, 2), (7, 2)], [(8, 1), (5, .5), (3, .5), (5, 1.5), (3, .5)], [(2, 1), (5, 1), (7, 2)],
        [(12, 1.5), (10, .5), (8, 1.5), (7, .5)], [(5, 1), (2, 1), (0, 2)]]
HYMN_CH = [[(2, MIN), (10, MAJ)], [(7, MIN), (9, MAJ)], [(5, MAJ), (2, MIN)], [(0, MAJ), (5, MAJ)],
           [(10, MAJ), (7, MIN)], [(9, DOM7), (9, MAJ)], [(2, MIN), (7, MIN)], [(9, DOM7), (2, MIN)]]
# the second phrase in D major — the only time in the century it is sung in tune
HYMN_B_MAJ = [[(9, 1), (5, .5), (4, .5), (5, 1.5), (4, .5)], [(2, 1), (5, 1), (7, 2)],
              [(12, 1.5), (11, .5), (9, 1.5), (7, .5)], [(5, 1), (2, 1), (0, 2)]]
HYMN_B_MAJ_CH = [[(7, MAJ), (4, MIN)], [(9, DOM7), (9, MAJ)], [(2, MAJ), (7, MAJ)], [(9, DOM7), (2, MAJ)]]

# -- leitmotif 2: Lenin's lullaby (F5 D5 C5 A4 Bb4 A4, seconds) ---------------------------------------------
LULLABY = [(77, 1.0), (74, 0.8), (72, 0.8), (69, 2.2), (70, 0.9), (69, 2.0)]

# -- leitmotif 3: the Mi-Go (quarter tones, seconds) ---------------------------------------------------------
MIGO = [(86, .6), (86.5, .6), (89.5, .9), (92, .4), (94.5, 1.4), (88, 2.0)]

# -- reason: a round in C (offsets from the tonic, beats); every beat a tone of the tonic triad -------------
ROUND = [[(0, 1), (4, 1), (7, 1), (12, 1)], [(7, .5), (9, .5), (7, .5), (5, .5), (4, 1), (7, 1)],
         [(16, .5), (14, .5), (12, 1), (7, 1), (4, 1)], [(0, 1.5), (2, .5), (4, 1), (0, 1)]]
ROUND_VOICES = {  # (instrument, octave) per act — the order of entries
    "II": [("vln_solo", 12), ("cl_sus", 0)],
    "III": [("ob_sus", 12), ("cl_sus", 0)],
    "IV": [("fl_sus", 12), ("ob_sus", 0), ("cl_sus", -12), ("bsn_sus", -24)],
    "V": [("fl_sus", 12), ("cl_sus", 0), ("vln_solo", 12), ("bsn_sus", -24)],
    "VI": [("fl_sus", 12), ("ob_sus", 0), ("cl_sus", -12), ("bsn_sus", -24)],
}
VOICES = {"sweden": 1, "kremnev": 2, "budapest": 2, "pannonia": 3, "gotland": 3, "waite": 4, "euclid": 4,
          "bohemia": 4}
ROUND_KEY = {"sweden": 0, "kremnev": 7, "budapest": 5, "pannonia": 10, "gotland": 7, "waite": 9, "euclid": 4,
             "bohemia": 2}

# -- idea 3: the Internationale (P. Degeyter, 1888; public domain), in C, offsets from C4, beats -------------
INTER_UP = [(7, 1)]
INTER = [[(12, 1.5), (11, .5), (14, 1), (12, 1)], [(7, 1), (4, 1), (9, 1), (5, 1)],
         [(14, 1.5), (12, .5), (11, 1), (9, 1)], [(7, 1), (5, 1), (4, 2)]]
INTER_CH = [[(0, MAJ), (0, MAJ)], [(0, MAJ), (5, MAJ)], [(7, MAJ), (7, MAJ)], [(7, DOM7), (0, MAJ)]]

# -- the leading timbres of the hymn per act: (instrument, octave, gain) -------------------------------------
LEADS = {
    "I": [("hn_sus", 0, .42), ("tpt_sus", 0, .26), ("tbn_sus", -12, .36)],
    "II": [("vln_pizz", 0, .55), ("vla_pizz", -12, .45), ("xylo", 12, .2)],
    "III": [("choir", 0, .5), ("org_quiet", -12, .26)],
    "IV": [("ob_sus", 0, .42), ("cl_sus", -12, .4), ("fl_sus", 12, .2)],
    "V": [("celesta", 12, .5), ("glock", 24, .16), ("tubular", 0, .28)],
    "VI": [("hn_sus", 0, .34), ("tpt_sus", 0, .22), ("choir", 0, .36), ("ob_sus", 0, .24), ("vln_sus", 0, .3),
           ("tbn_sus", -12, .3), ("vc_sus", -12, .26)],
}
PLUCKED = {"vln_pizz", "vla_pizz", "vc_pizz", "cb_pizz", "xylo", "celesta", "glock", "tubular", "harp", "marimba"}

GROWTH_REPRESS = [(7, MIN), (2, MIN), (3, MAJ), (9, MIN)]


def rot(m):
    det = 0.05 + 0.32 * m
    return dict(detune=det if det > 0.06 else 0.0, drift=-0.06 - 0.45 * m, double_gain=0.35 + 0.4 * m)


def tch(ch, tr):
    return ((ch[0] + tr) % 12, ch[1])


def pcs_of(ch):
    return [(ch[0] + i) % 12 for i in ch[1]]


class Tune:
    """notes [(pos, offset, beats)], chords [(pos, chord)], built from 4-beat bars (+ an upbeat)"""

    def __init__(self, bars, chords=None, upbeat=None, upbeat_chord=None):
        self.notes, self.chords = [], []
        if upbeat:
            pos = -sum(d for _, d in upbeat)
            for off, d in upbeat:
                self.notes.append((pos, off, d))
                pos += d
            if upbeat_chord:
                self.chords.append((-sum(d for _, d in upbeat), upbeat_chord))
        for b, bar in enumerate(bars):
            pos = 4.0 * b
            for off, d in bar:
                self.notes.append((pos, off, d))
                pos += d
            assert abs(pos - 4.0 * (b + 1)) < 1e-6, bar
            if chords:
                self.chords.append((4.0 * b, chords[b][0]))
                self.chords.append((4.0 * b + 2, chords[b][1]))
        self.length = 4.0 * len(bars)
        self.start = min(n[0] for n in self.notes)


class TimeMap:
    """beats → seconds with a tempo per bar (seconds per beat; the upbeat takes the first bar's)"""

    def __init__(self, t0, spb):
        self.t0, self.spb = t0, list(spb)

    def sec(self, pos):
        if pos < 0:
            return self.t0 + pos * self.spb[0]
        t, b = self.t0, 0
        while pos >= 4.0 * (b + 1) - 1e-9:
            t += 4.0 * self.spb[min(b, len(self.spb) - 1)]
            b += 1
        return t + (pos - 4.0 * b) * self.spb[min(b, len(self.spb) - 1)]


class Score:
    def __init__(self, ctx, variant):
        self.full = variant == "B"
        self.cues = ctx.cues
        self.cs = self.cues["cues"]
        self.p = Piece("Р.С.Ф.Г.Р. 1920–2000 · третья редакция, вариант " + ("Б" if self.full else "А"), bpm=60,
                       meter=(4, 4), key="D minor")
        self.c = Composer(self.p, lib="vsco")
        self.ids = {e["id"]: e for e in self.cs}
        bounds = [("I", 0.0)] + [(a, self.ids[i]["fly"]) for a, i in ACT_START.items()]
        self.bounds = sorted(bounds, key=lambda x: x[1])

    # -- helpers -------------------------------------------------------------------------------------------
    def act(self, t):
        a = "I"
        for name, t0 in self.bounds:
            if t >= t0 - 1e-6:
                a = name
        return a

    def year_t(self, year):
        ys = np.array([e["year"] for e in self.cs], float)
        ts = np.array([e["t"] for e in self.cs], float)
        return float(np.interp(year, ys, ts))

    def n(self, inst, midi, t, dur, **kw):
        lo, hi = INSTR[inst]["range"]
        while midi < lo - 0.01:
            midi += 12
        while midi > hi + 0.01:
            midi -= 12
        return self.p.note(inst, midi, t, dur, **kw)

    # -- the leading voice: unison and octaves (the Mycelium sings with one voice) -------------------------
    def lead(self, notes, act, m, leads=None, vel=0.62, gain=1.0, rot_on=True):
        """notes: [(t, seconds, midi)]"""
        p = self.p
        leads = leads or LEADS[act]
        det = 0.05 + 0.32 * m
        drift = -0.06 - 0.45 * m
        for k, (inst, octv, g) in enumerate(leads):
            lo, hi = INSTR[inst]["range"]
            pan = -0.35 + 0.7 * k / max(1, len(leads) - 1)
            for t, d, mm in notes:
                pitch = mm + octv
                if inst == "tubular" and not 60 <= pitch <= 77:
                    continue
                if not lo <= pitch <= hi:
                    continue
                if inst in PLUCKED and inst not in ("tubular", "celesta", "glock") and d > 0.75:
                    k_ = max(1, int(round(d / 0.36)))  # a long note on a plucked instrument: struck again
                    for j in range(k_):
                        p.note(inst, pitch, t + j * d / k_, d / k_ * 0.9, vel=vel * (1 if j == 0 else 0.8),
                               gain=g * gain, pan=pan, release=0.4, detune=-0.04 * j * m)
                else:
                    p.note(inst, pitch, t, d * 0.96, vel=vel, gain=g * gain, pan=pan, attack=0.04, release=0.5,
                           bend=drift * 0.6 if d > 1.0 and rot_on else 0.0)
                if rot_on and k < 2 and m > 0.15:
                    p.note(inst, pitch, t + 0.03, d * 0.96, vel=vel * 0.8, gain=g * gain * 0.5 * m, pan=-pan,
                           attack=0.04, release=0.5, detune=det, bend=drift if d > 1.0 else 0.0)

    # -- the bed: harmony under every half bar, in the act's texture ----------------------------------------
    def bed(self, act, t0, t1, ch, m, spb, gain=1.0, rotted=True):
        c, p = self.c, self.p
        r = rot(m) if rotted else {}
        root = ch[0]
        pc = pcs_of(ch)
        if act == "I":
            c.pad(t0, t1 + 0.05, ch, vel=0.5, gain=0.42 * gain, attack=0.2, release=0.8, **r)
            p.note("tba_sus", in_range(root, 29, 40), t0, t1 - t0, vel=0.55, gain=0.45 * gain, bus="brass",
                   attack=0.05, release=0.6)
        elif act == "II":
            t, j = t0, 0
            while t < t1 - 0.05:
                if j % 2 == 0:
                    p.note("cb_pizz", in_range(root, 31, 43), t, 0.3, vel=0.6, gain=0.75 * gain, pan=-0.3,
                           release=0.3)
                    p.note("vc_pizz", in_range(pc[-1] if len(pc) > 2 else root, 43, 55), t, 0.3, vel=0.5,
                           gain=0.45 * gain, pan=-0.15, release=0.3)
                else:
                    for q, x in enumerate(pc[1:3]):
                        p.note("vla_pizz", in_range(x, 55, 66), t + 0.01 * q, 0.25, vel=0.4, gain=0.35 * gain,
                               pan=0.2, release=0.25, detune=(0.1 + 0.3 * m) * q if rotted else 0.0)
                    c.fx("wood_click", t, gain=0.08 * gain, pan=0.5, bus="perc")
                t += spb
                j += 1
        elif act == "III":
            for q, x in enumerate(pc[:3]):
                p.note("org_quiet", in_range(x, 50, 61), t0, t1 - t0 + 0.05, vel=0.45, gain=0.24 * gain,
                       pan=-0.2 + 0.2 * q, bus="organ", attack=0.15, release=0.8,
                       detune=(-0.15 * m * q) if rotted else 0.0)
            p.note("cb_sus", in_range(root, 28, 40), t0, t1 - t0 + 0.05, vel=0.55, gain=0.5 * gain, pan=-0.3,
                   attack=0.2, release=1.0, bend=r.get("drift", 0) * 0.5)
            p.note("vc_sus", in_range(pc[-1] if len(pc) > 2 else root, 43, 55), t0, t1 - t0 + 0.05, vel=0.45,
                   gain=0.3 * gain, pan=-0.1, attack=0.3, release=1.0)
        elif act == "IV":
            c.pad(t0, t1 + 0.05, ch, vel=0.35, gain=0.28 * gain, attack=0.35, release=0.8, **r)
            p.note("bsn_sus", in_range(root, 34, 46), t0, t1 - t0, vel=0.5, gain=0.45 * gain, pan=0.1,
                   bus="winds", attack=0.05, release=0.5)
        elif act == "V":
            c.arpeggio(t0, ch, n=5, step=0.08, vel=0.4, lo=50, gain=0.35 * gain, pan=-0.3, ring=max(0.5, t1 - t0))
            p.note("cb_sus", in_range(root, 28, 40), t0, t1 - t0 + 0.05, vel=0.45, gain=0.42 * gain, pan=-0.2,
                   attack=0.3, release=1.0)
            p.note("vibes", in_range(pc[1], 62, 73), t0, t1 - t0, vel=0.35, gain=0.22 * gain, pan=0.3,
                   release=1.5, detune=0.3 * m if rotted else 0.0)
        else:  # VI: everyone
            c.pad(t0, t1 + 0.05, ch, vel=0.6, gain=0.48 * gain, attack=0.15, release=0.8, **r)
            p.note("org_loud", in_range(root, 26, 37), t0, t1 - t0 + 0.05, vel=0.6, gain=0.3 * gain, bus="organ",
                   release=1.0)
            p.note("tba_sus", in_range(root, 29, 40), t0, t1 - t0, vel=0.6, gain=0.42 * gain, bus="brass",
                   release=0.6)

    def play_tune(self, tune, t0, spb, base, act, m, leads=None, bed=True, gain=1.0, rotted=True, cut=None,
                  lead_vel=0.62, chord_tr=0, bed_act=None):
        """the tune from t0 (bar 1, beat 1; the upbeat before) at spb seconds per beat (a number or a list
        per bar); base: the pitch of offset 0; chords transposed by chord_tr; returns the end time"""
        tm = TimeMap(t0, spb if isinstance(spb, (list, tuple)) else [spb])
        end = tm.sec(tune.length)
        cut = cut or end + 10
        notes = []
        for pos, off, d in tune.notes:
            a, b = tm.sec(pos), tm.sec(pos + d)
            if a >= cut:
                continue
            notes.append((a, min(b, cut) - a, base + off))
        self.lead(notes, act, m, leads=leads, gain=gain, rot_on=rotted, vel=lead_vel)
        if bed:
            for k, (pos, ch) in enumerate(tune.chords):
                nxt = tune.chords[k + 1][0] if k + 1 < len(tune.chords) else tune.length
                a, b = tm.sec(pos), tm.sec(nxt)
                if a >= cut:
                    continue
                sp = (b - a) / max(1e-6, nxt - pos)
                self.bed(bed_act or act, a, min(b, cut), tch(ch, chord_tr), m, sp, gain=gain, rotted=rotted)
        return min(end, cut)

    def hymn(self, bars, t0, spb, act, m, tr, **kw):
        tune = Tune([HYMN[b] for b in bars], [HYMN_CH[b] for b in bars])
        return self.play_tune(tune, t0, spb, 62 + tr, act, m, chord_tr=tr, **kw)

    def inter_tune(self, upbeat=True):
        return Tune(INTER, INTER_CH, upbeat=INTER_UP if upbeat else None, upbeat_chord=(7, MAJ) if upbeat else None)

    def internationale(self, t, spb, key, inst, m, gain=0.4, vel=0.6, sour=0.0, octave=0, pan=0.0, bars=4,
                       bus=None):
        """the Internationale as a single line (cantus firmus): degrees 3 and 7 sink by sour (≤ 0.5 semitone)"""
        tune = Tune(INTER[:bars], upbeat=INTER_UP)
        base = in_range(key, 55, 66) - 12 + octave
        tm = TimeMap(t, [spb])
        for pos, off, d in tune.notes:
            deg = off % 12
            flat = sour if deg in (4, 11) else 0.0
            a = tm.sec(pos)
            dur = d * spb
            self.n(inst, base + off - flat, a, dur * 0.95, vel=vel, gain=gain, pan=pan, attack=0.03, release=0.5,
                   bend=(-0.25 * sour if dur > 0.8 else 0.0), bus=bus)
            if sour > 0.15:
                self.n(inst, base + off - flat, a + 0.03, dur * 0.95, vel=vel * 0.8, gain=gain * 0.5, pan=-pan,
                       attack=0.03, release=0.5, detune=0.2 + sour * 0.5, bus=bus)
        return tm.sec(tune.length)

    def lullaby(self, t, notes, inst, m, gain=0.4, vel=0.4, pan=0.25, stretch=1.0, bus=None):
        return self.c.melody(t, [(n_, d_ * stretch) for n_, d_ in notes], inst=inst, vel=vel, gain=gain, pan=pan,
                             attack=0.15, bend=-0.4 * m - 0.1, detune_double=0.15 + 0.3 * m, bus=bus)

    def migo(self, t, inst="vln_harm", invert=False, stretch=1.0, rise=0.0, gain=0.32, transpose=0.0):
        p, c = self.p, self.c
        tt = t
        for j, (n_, d_) in enumerate(MIGO):
            pitch = (172 - n_ if invert else n_) + transpose
            d_ *= stretch
            p.note(inst, pitch, tt, d_ * 1.05, vel=0.45, gain=gain, pan=0.45 - 0.15 * j, attack=0.12, release=1.2,
                   bend=rise + (0.5 if j == 4 else 0.0))
            p.note(inst, pitch + 0.25, tt + 0.07, d_ * 0.9, vel=0.35, gain=gain * 0.4, pan=-0.3, attack=0.2,
                   release=1.0, ringmod=31.0)
            tt += d_
        # col legno ticks that keep no time: the clockwork of something that is not a clock
        t2 = t
        while t2 < tt:
            p.note("vc_colleg", 45 + c.rng.choice([0, 1, 5, 6]), t2, 0.15, vel=0.5, gain=0.3, pan=c.rng.uniform(-.5, .5),
                   release=0.2)
            t2 += c.rng.choice([0.13, 0.21, 0.34, 0.55, 0.89])
        return tt

    # -- archive ageing (idea 4) ----------------------------------------------------------------------------
    def archive(self):
        Y = self.year_t
        hold = self.ids["stars"]["hold"]
        pts = [dict(t=0.0, lp=3200, hp=120, width=0.1, crackle=0.55, hiss=-50),
               dict(t=Y(1930), lp=4200, hp=100, width=0.25, crackle=0.45, hiss=-53),
               dict(t=Y(1945), lp=6500, hp=75, width=0.5, crackle=0.28, hiss=-58),
               dict(t=Y(1960), lp=10000, hp=45, width=0.8, crackle=0.12, hiss=-64),
               dict(t=Y(1975), lp=16000, hp=30, width=1.0, crackle=0.04, hiss=-72),
               dict(t=Y(1995), lp=20000, hp=20, width=1.0, crackle=0.0, hiss=-110),
               dict(t=hold, lp=20000, hp=20, width=0.0, crackle=0.0, hiss=-110, step=True)]
        self.p.meta["post"] = [{"kind": "archive", "points": pts}]

    # -- the score -----------------------------------------------------------------------------------------
    def build(self):
        p, c, cs = self.p, self.c, self.cs
        p.meta["sends"] = {}
        for e in cs:
            p.mark(e["t"], e["label"])
        for name, t0 in self.bounds[1:]:
            p.mark(t0, "Акт " + ACT_NAME[name])
        if not os.environ.get("NO_ARCHIVE"):
            self.archive()
        self.intro()
        self.gi = self.ri = 0
        for k, e in enumerate(cs):
            nxt = cs[k + 1]["t"] + 0.3 if k + 1 < len(cs) else self.cues["outro"][0] + 0.5
            self.event(e, nxt)
        self.outro()
        # measured with --parts on the full render (first pass): colours and bass up to the tune
        p.balance({"Celesta": 11, "Violin solo": 8, "Tuba": 10, "Basses": 7, "Trombone": 9, "Xylophone": 6,
                   "Tubular bells": 10, "Vibraphone": 14, "Glockenspiel": 4, "Oboe": 5, "Bass clarinet": 5,
                   "Bassoon": -2, "Crotales": 15})
        p.balance({"Vibraphone": 8})  # second pass
        if self.full:
            p.balance({"Bass trombone": 14})
        self.p.meta["length"] = self.cues["duration_s"] + 1.0
        return p

    def intro(self):
        p, c, cs = self.p, self.c, self.cs
        a, _ = self.cues["intro"]
        b = cs[0]["t"] + 0.3
        p.note("org_quiet", 38, a, b - a + 1.0, vel=0.5, gain=0.4, bus="organ", attack=1.5, release=2.0)
        p.note("cb_trem", 38, a + 0.5, b - a, vel=0.4, gain=0.35, pan=-0.3, bus="strings", attack=2.5)
        c.breath(a, b - a + 1.0, gain=0.45)
        c.fx("alien", a + 1.0, gain=0.25, shift=-5, bus="deep", attack=1.0)
        c.fx("glock_down", a + 2.0, gain=0.25, shift=-3, bus="harp")
        # the hymn's first bar, far away, muted: the leitmotif is announced before anything happens
        self.lead([(a + 3.0 + x, d, 62 + o) for x, d, o in [(0, .7, 0), (.7, .7, 7), (1.4, 1.0, 8), (2.4, .9, 7)]],
                  "I", 0.0, leads=[("hn_mute", 0, .4)], rot_on=False, vel=0.4)
        c.heartbeat(a + 4.0, cs[1]["t"], gain=0.3)

    def event(self, e, t_end):
        mood, eid = e["mood"], e["id"]
        act = self.act(e["fly"] if eid in ACT_START.values() else e["t"])
        m = max(0.0, min(1.0, (e["year"] - 1920) / 77.0))
        tr = ACT_SHIFT[act]
        h = getattr(self, "ev_" + mood)
        h(e, t_end, act, m, tr)

    # growth / feast: a fragment of the hymn in the act's timbre over its own chords
    def ev_growth(self, e, t_end, act, m, tr, feast=False):
        p, c = self.p, self.c
        eid = e["id"]
        t0 = e["t"]
        gi = self.gi
        self.gi += 1
        if self.full and eid == "danube":
            return self.foxtrot(e, t_end, act, m, tr)
        if self.full and eid == "fruiting":
            return self.waltz(e, t_end, act, m, tr)
        stop = e["hold"] + 0.1 if feast else t_end
        bars = [(2 * gi) % 8, (2 * gi + 1) % 8]
        avail = stop - t0 - 0.3
        if feast:
            bars = bars[:1]
        beats = 4.0 * len(bars)
        spb = min(60 / 56, max(60 / 104, avail / beats))
        end = self.hymn(bars, t0, spb, act, m, tr, cut=stop)
        last = HYMN_CH[bars[-1]][1]
        if end < stop - 0.3 and not feast:  # the last chord held to the next event
            self.bed(act, end, stop - 0.3, tch(last, tr), m, spb, gain=0.8)
        c.timp(t0, (HYMN_CH[bars[0]][0][0] + tr) % 12, vel=0.75 if act in ("I", "VI") else 0.5)
        c.spores(t0 + 0.05, 4.0, density=28 + 25 * m, gain=0.2)
        if act in ("I", "III", "VI"):
            c.heartbeat(t0 + 1.0, t_end, gain=0.25)
        if act == "II":
            c.fx("slapstick", t0, gain=0.25, pan=0.3, bus="perc")
        if feast:
            key = [10, 3, 5, 0][gi % 4]
            c.fx("clash", e["hold"], gain=0.3, pan=0.3, bus="perc")
            if eid == "mekong":  # the hymn's head, made major, on marimba and celesta over a march going sour
                key = (5 + ACT_SHIFT[act]) % 12
                self.lead([(e["hold"] + 0.2 + 0.42 * j, 0.4, in_range(key, 60, 71) + o)
                           for j, o in enumerate([0, 7, 9, 7, 5, 4, 2, 0])],
                          act, m, leads=[("marimba", 0, .35), ("celesta", 12, .3)], rot_on=True)
            tune = None
            if self.full and eid == "union":
                tune = [(o, d) for o, d in INTER_UP + sum(INTER, [])] + [(None, 1)]
                key = 5
            if self.full and eid == "amazonia":
                key = 5
            c.march(e["hold"] + 0.1, t_end, key=key, gain=0.42, sour=0.25 * m, detune=0.12 + 0.35 * m, tune=tune)
            if self.full and eid == "amazonia":  # the Internationale, all brass, rotten to the bone
                self.internationale(e["hold"] + 0.1 + 60 / 116 * 2, 60 / 116, 5, "tbn_sus", m, gain=0.34,
                                    sour=0.5, octave=-12, pan=-0.3, bus="brass")
                self.internationale(e["hold"] + 0.1 + 60 / 116 * 2 + 0.03, 60 / 116, 5, "hn_sus", m, gain=0.3,
                                    sour=0.45, pan=0.3, bus="brass")


    def ev_feast(self, e, t_end, act, m, tr):
        return self.ev_growth(e, t_end, act, m, tr, feast=True)

    # idea 6: the hymn as a foxtrot (1930)
    def foxtrot(self, e, t_end, act, m, tr):
        p, c = self.p, self.c
        t0 = e["t"] + 0.2
        spb = 60 / 112
        tune = Tune([HYMN[b] for b in range(4)], [HYMN_CH[b] for b in range(4)])
        tm = TimeMap(t0, [spb])
        self.lead([(tm.sec(pos), d * spb, 62 + tr + off) for pos, off, d in tune.notes], act, m,
                  leads=[("tpt_mute", 0, .4), ("cl_sus", 0, .22)], vel=0.6)
        t, j = t0, 0
        end = min(t_end - 0.2, tm.sec(tune.length) + 2 * spb)
        while t < end:
            pos = (t - t0) / spb
            ch = HYMN_CH[min(3, int(pos // 4))][int(pos % 4 >= 2)]
            ch = tch(ch, tr)
            pc = pcs_of(ch)
            if j % 2 == 0:
                p.note("tba_stac", in_range(ch[0] if j % 4 == 0 else pc[2], 30, 42), t, spb * 0.7, vel=0.6,
                       gain=0.5, pan=-0.3, release=0.2)
            else:
                c.fx("snare_soft", t, gain=0.25, pan=0.2, bus="perc")
                for q, x in enumerate(pc):
                    p.note("vln_pizz" if q else "vla_pizz", in_range(x, 57, 69), t + 0.01 * q, 0.2, vel=0.45,
                           gain=0.3, pan=0.25, release=0.2)
            c.fx("wood_click", t + spb / 2, gain=0.06, pan=-0.5, bus="perc")
            t += spb
            j += 1
        c.fx("slapstick", e["t"], gain=0.25, pan=0.3, bus="perc")

    # idea 6: the Internationale as a waltz that loses a beat and becomes 5/8 (1947)
    def waltz(self, e, t_end, act, m, tr):
        p, c = self.p, self.c
        t0 = e["t"]
        # before the document: the choir's hymn head
        self.hymn([0], t0, (e["hold"] - t0) / 4.0, act, m, tr, cut=e["hold"])
        c.fx("clash", e["hold"], gain=0.3, pan=0.3, bus="perc")
        key = (5 + tr) % 12
        q = 60 / 152
        t = e["hold"] + 0.1
        round_ = 0
        while t < t_end - 1.0:
            # bars 1–2 in 3/4 (a 4-beat bar squeezed into 3), bars 3–4 in 5/8; the second round all in 5/8
            spb = [0.75 * q, 0.75 * q, 0.625 * q, 0.625 * q] if round_ == 0 else [0.625 * q] * 4
            tune = self.inter_tune()
            tm = TimeMap(t + q * 0.75, spb)
            base = in_range(key, 55, 66) - 12
            sour = 0.2 + 0.3 * round_
            notes = [(tm.sec(pos), d * spb[min(3, max(0, int(pos // 4)))], base + off) for pos, off, d in tune.notes]
            notes = [(a, d, x - (sour if (x - base) % 12 in (4, 11) else 0)) for a, d, x in notes if a < t_end - 0.3]
            self.lead(notes, act, m, leads=[("vln_sus", 12, .34), ("fl_sus", 12, .22), ("vc_sus", 0, .22)], vel=0.55)
            # oom-pah: waltz 1-2-3, then 5/8 grouped 2+3
            for b in range(4):
                bt0 = tm.sec(4.0 * b)
                bt1 = tm.sec(4.0 * (b + 1))
                if bt0 >= t_end - 0.3:
                    break
                fiveight = spb[b] < 0.7 * q
                hits = [0, 1, 2] if not fiveight else [0, 0.4, 0.8, 1.2, 1.6]  # in 3 quarters / 5 eighths
                strong = [0] if not fiveight else [0, 2]
                unit = (bt1 - bt0) / (3 if not fiveight else 5)
                for i in range(len(hits)):
                    tt = bt0 + i * unit
                    pos = 4.0 * b + (tt - bt0) / spb[b]
                    ch = tch(INTER_CH[b][int(pos % 4 >= 2)], key)
                    pc = pcs_of(ch)
                    if i in strong:
                        p.note("cb_pizz", in_range(ch[0], 31, 43), tt, 0.3, vel=0.6, gain=0.75, pan=-0.3, release=0.3)
                        c.fx("tamb", tt, gain=0.08, pan=0.4, bus="perc")
                    else:
                        for z, x in enumerate(pc[1:]):
                            p.note("vla_pizz", in_range(x, 55, 67), tt + 0.01 * z, 0.2, vel=0.42, gain=0.34,
                                   pan=0.25, release=0.2, detune=-0.1 * round_ * z)
            t = tm.sec(16.0) + q
            round_ += 1
        c.spores(e["hold"], 6.0, density=40, gain=0.2)

    # repress: the hymn's head as a rubber stamp, over a five-step ostinato in the act's timbre
    def ev_repress(self, e, t_end, act, m, tr):
        p, c = self.p, self.c
        eid, t0 = e["id"], e["t"]
        ch = tch(GROWTH_REPRESS[self.ri % 4], tr)
        self.ri += 1
        c.pad(t0, t_end + 0.5, ch, vel=0.3, gain=0.3, bass_only=True, **rot(m))
        root = in_range(ch[0], 43, 54)
        third = 3 if 3 in ch[1] else 4
        pat = [0, 7, 12, 7, third]
        beat = 60 / 132 / 2
        ost = {"I": ("tbn_stac", "tba_stac", -12), "II": ("vc_pizz", "vla_pizz", 0), "III": ("org_quiet", "bsn_stac", -12),
               "IV": ("ob_stac", "cl_stac", 12), "V": ("marimba", "vc_pizz", 0), "VI": ("vc_pizz", "tbn_stac", 0)}[act]
        t, j = t0, 0
        while t < t_end - 0.35:
            inst = ost[0] if j % 10 < 5 else ost[1]
            x = root + pat[j % 5] + (ost[2] if inst == ost[0] else 0)
            self.n(inst, x, t, 0.25 if inst != "org_quiet" else 0.2, vel=0.55 if j % 5 == 0 else 0.35,
                   gain=0.4 if inst != "org_quiet" else 0.25, pan=-0.1 if j % 2 else 0.1,
                   bus="organ" if inst == "org_quiet" else None, release=0.25)
            if act == "IV" and j % 5 == 0:
                self.n("bsn_stac", root - 12, t, 0.25, vel=0.55, gain=0.45, release=0.25)
            if j % 5 == 0:
                c.fx("claves" if act != "I" else "timpsnare", t, gain=0.12 if act != "I" else 0.2, pan=0.5, bus="perc")
            t += beat
            j += 1
        stamp = (0, 7, 8, 7) if 7 in ch[1] else (0, 6, 3, 0)
        stamp = tuple(9 if (s == 8 and 4 in ch[1]) else s for s in stamp)
        st_inst = {"I": "tpt_stac", "II": "tpt_mute", "III": "hn_mute", "IV": "ob_stac", "V": "xylo", "VI": "tpt_stac"}[act]
        for tt in (t0, e["hold"] + 0.05):
            for j, s in enumerate(stamp):
                self.n(st_inst, in_range(ch[0], 62, 73) + s, tt + j * beat, beat * 0.9, vel=0.6, gain=0.32, pan=0.25,
                       release=0.2)
        p.note("bsn_sus", in_range(ch[0], 34, 45), t0, t_end - t0, vel=0.4, gain=0.3, pan=0.1, bus="winds",
               attack=0.4, bend=-0.3)
        c.fx("metal", t0, gain=0.25, pan=-0.4, bus="fx")
        if act == "I":
            c.timp(t0, ch[0], vel=0.7)
        if eid in ("case1147", "case427"):
            c.fx("chain", t0 + 0.5, gain=0.22, pan=0.4, bus="fx", dur=4.0)
        if eid == "case611":
            c.fx("guiro", e["hold"], gain=0.3, bus="fx")
        if eid == "vessel":
            p.note("org_loud", in_range(ch[0], 24, 35), t0, t_end - t0, vel=0.5, gain=0.3, bus="organ", attack=0.8)
            c.fx("timpsnare", e["hold"], gain=0.45, bus="perc")
        if self.full and eid == "act1930":  # the Internationale's head, rotted to minor, in the bass trombone
            sp = beat * 5
            for j, o in enumerate([7, 12, 10, 7, 12]):
                self.n("btbn_sus", in_range(ch[0], 34, 45) + o - 12, t0 + 0.4 + j * sp, sp * 0.95, vel=0.6, gain=0.4,
                       pan=-0.2, attack=0.05, release=0.4, detune=-0.15 * m)
        if self.full and eid == "doctrine":
            self.piano_low(t0)
            self.piano_low(e["hold"])
        if e["has_doc"]:
            c.fx("timpsnare", e["hold"], gain=0.4, bus="perc")
            c.fx("susp_scrape", e["hold"] + 0.5, gain=0.18, bus="fx", dur=3.0)

    def piano_low(self, t, root=None):
        for j, x in enumerate((21, 22, 28) if root is None else (root, root + 1, root + 6)):
            self.p.note("piano", x, t + 0.01 * j, 3.0, vel=0.95, gain=0.45, pan=-0.3, release=2.5)

    # sleeper: the organ pedal, breathing, the lullaby transformed
    def ev_sleeper(self, e, t_end, act, m, tr):
        p, c = self.p, self.c
        eid, vortex = e["id"], e["vortex"]
        t_fly, t_tr, t_hold = e["fly"], e["t"], e["hold"]
        dur = t_end - t_fly + 0.4
        root = (D + tr) % 12
        if vortex:
            p.note("org_loud", in_range(root, 24, 35), t_fly, dur, vel=0.6, gain=0.45, bus="organ", attack=1.2,
                   release=2.2, bend=-0.3 * m)
        else:
            p.note("org_quiet", in_range(root, 36, 47), t_fly, dur, vel=0.55, gain=0.4, bus="organ", attack=1.2,
                   release=2.2, bend=-0.3 * m)
        p.note("cb_trem", in_range(root, 33, 44), t_fly + 0.2, dur, vel=0.6, gain=0.5, pan=-0.3, attack=1.6)
        if act == "IV" or (act == "V" and self.full):  # woodwinds where the act has them (B: the lowest ones)
            low = ("bcl_sus", "cbsn_sus") if self.full else ("bsn_sus", "cl_sus")
            p.note(low[0], in_range(root + 1, 37, 48), t_tr, t_end - t_tr + 0.6, vel=0.45, gain=0.32, pan=-0.05,
                   bus="winds", attack=1.0, bend=-0.5 * m)
            p.note(low[1], in_range(root, 26, 37) if self.full else in_range(root + 2, 52, 60), t_tr + 0.3,
                   t_end - t_tr + 0.4, vel=0.4, gain=0.3, pan=0.2, bus="winds", attack=1.4, detune=0.3 * m)
        else:
            p.note("vc_trem", in_range(root + 1, 47, 58), t_tr, t_end - t_tr + 0.6, vel=0.45, gain=0.3, pan=-0.05,
                   attack=1.2, bend=-0.5 * m)
            p.note("vla_trem", in_range(root + 2, 48, 59), t_tr + 0.3, t_end - t_tr + 0.4, vel=0.35, gain=0.22, pan=0.2,
                   attack=1.5, detune=0.3 * m)
        c.breath(t_fly + 0.3, min(7.0, dur), gain=0.5)
        c.fx("alien", t_tr + 0.4, gain=0.22, shift=-7 + 2 * (len(eid) % 3), pan=0.3, bus="deep", attack=0.6)
        if act == "V":  # low tubular bells, out of tune with the organ
            for j in range(3):
                p.note("tubular", 60 + [0, 1, 6][j], t_tr + 0.5 + 2.3 * j, 4.0, vel=0.5, gain=0.25, pan=-0.3 + 0.3 * j,
                       detune=-0.2 * j)
        if vortex:
            c.shepard(t_tr - 0.5, t_end, gain=0.3)
            c.timp(t_tr, root, vel=0.85, roll=t_hold - t_tr + 0.4)
            c.fx("gong_roll", t_tr - 0.3, gain=0.35, bus="perc", shift=-5, dur=t_hold - t_tr + 2.0)
            p.note("tba_sus", in_range(root, 26, 37), t_tr + 0.2, 3.0, vel=0.7, gain=0.45, bus="brass", bend=-1.0)
            p.note("tbn_sus", in_range(root + 1, 40, 51), t_tr + 0.4, 2.6, vel=0.6, gain=0.35, bus="brass", bend=-1.5)
            if self.full:
                self.choir_slide(t_tr + 0.3, min(6.0, t_end - t_tr), root, up=(eid == "kara"))
                for j in range(2):
                    p.note("vln_harm", 84 + 3 * j, t_tr + 0.8 + j, 4.5, vel=0.4, gain=0.18, pan=0.5 - j,
                           attack=1.0, bend=-5.0 + 9.0 * j, release=1.5)
        if eid == "alarm":
            for j in range(3):
                c.fx("siren", t_tr + 0.3 + 1.6 * j, gain=0.22, pan=-0.6 + 0.6 * j, shift=-2 * j, bus="fx")
        if eid == "kara":
            c.fx("bubbles", t_tr + 0.6, gain=0.4, shift=-9, bus="deep")
            c.fx("bubbles", t_hold + 0.5, gain=0.3, shift=-12, bus="deep")
        if eid == "chamber":
            c.fx("brick", t_tr, gain=0.35, pan=-0.2, bus="fx")
        if eid == "cylinder":
            p.note("org_quiet", in_range(root, 60, 71), t_tr - 2.0, 2.2, vel=0.5, gain=0.3, bus="organ", reverse=True)
            c.fx("gong_scrape", t_hold + 0.4, gain=0.3, bus="fx")
        if eid == "protocol":
            c.fx("chain", t_tr, gain=0.3, pan=0.3, bus="fx", dur=3.0)
            c.fx("timpsnare", t_hold, gain=0.45, bus="perc")
        if self.full and eid in ("chamber", "protocol"):
            self.piano_low(t_tr)
        # the lullaby, transformed
        L = [(n_ + tr, d_) for n_, d_ in LULLABY]
        if eid == "lenin_sleeps":
            self.lullaby(t_hold + 0.4, L, "fl_sus", m)
        elif eid == "voice":  # the choir hums it, slower, sinking
            self.lullaby(t_hold + 0.2, [(n_ - 12, d_) for n_, d_ in L], "choir", m, gain=0.4, stretch=1.25, bus="choir")
        elif eid == "chamber":  # the mirror: inverted around F, on the celesta
            inv = [(2 * (77 + tr) - n_, d_) for n_, d_ in L]
            self.lullaby(t_hold + 0.3, inv, "celesta", m, gain=0.42, vel=0.5)
        elif eid == "cylinder":  # backwards, in the bassoon
            self.lullaby(t_hold + 0.3, [(n_ - 24, d_) for n_, d_ in reversed(L)], "bsn_sus", m, gain=0.4, vel=0.45)
        elif eid == "protocol":  # a record stuck on its first three notes
            tt = t_hold + 0.2
            for j in range(4):
                tt = self.lullaby(tt, [(n_ - 0.12 * j, d_ * 0.8) for n_, d_ in L[:3]], "ob_sus", m, gain=0.36)
            if self.full:  # under it the Internationale crawls in the tuba, rotten
                self.internationale(t_tr + 0.2, 0.62, (5 + tr) % 12, "tba_sus", m, gain=0.42, sour=0.5, octave=-24,
                                    pan=-0.25, bars=2)
        elif eid == "sprouted":  # backwards in the bass clarinet, and the voice in the lamps
            self.lullaby(t_hold + 0.3, [(n_ - 24, d_) for n_, d_ in reversed(L)], "bcl_sus", m, gain=0.4, vel=0.45)
            tt = t_hold + 1.0
            for j, d_ in enumerate([0.9, 0.5, 1.4, 0.7, 1.8]):
                p.note("tbn_sus", [45, 46, 44, 45, 43][j] + tr, tt, d_, vel=0.4, gain=0.3, pan=-0.3, bus="brass",
                       bend=c.rng.uniform(-0.8, 0.5), attack=0.1)
                tt += d_ + [0.4, 1.1, 0.4, 4.0][j % 4] * 0.3
            c.spores(t_tr, 5.0, density=18, gain=0.16)
        if e["has_doc"] and eid not in ("chamber",):
            p.note("glock", 86 + tr, t_hold + 0.2, 2.0, vel=0.3, gain=0.18, pan=0.4, bus="harp", detune=-0.3)
            p.note("glock", 87 + tr, t_hold + 1.4, 2.0, vel=0.25, gain=0.15, pan=0.4, bus="harp", detune=0.2)

    def choir_slide(self, t, dur, root, up=False):
        """idea 7: a choir cluster whose voices slide apart, each its own way"""
        base = in_range(root, 52, 63)
        for j, off in enumerate([0, 1, 2, 3, 5, 6]):
            self.p.note("choir", base + off, t + 0.08 * j, dur, vel=0.5, gain=0.2, pan=-0.5 + 0.2 * j, attack=1.0,
                        release=1.5, bend=(1 if up else -1) * self.c.rng.uniform(1.0, 4.0) * (1 + j % 2))

    # reason: a round, voice by voice
    def ev_awake(self, e, t_end, act, m, tr):
        p, c = self.p, self.c
        eid, t0 = e["id"], e["t"]
        key = ROUND_KEY[eid]
        nv = VOICES[eid]
        bpm = 100
        spb = 60 / bpm
        self.round(t0 + 0.3, t_end - 0.2, key, nv, act, spb, stretto=(eid == "waite"))
        tonic = in_range(key, 33, 44)
        t, j = t0, 0
        while t < t_end - 0.2:
            c.fx("claves", t, gain=(0.1 if j % 4 else 0.16) * (1.4 if eid == "euclid" else 1.0), pan=0.5, bus="perc")
            if j % 2 == 0:
                p.note("cb_pizz" if j % 4 == 0 else "vc_pizz", tonic + (0 if j % 4 == 0 else 7) + (12 if j % 4 else 0),
                       t, 0.4, vel=0.55, gain=0.6, pan=-0.25, release=0.4)
            t += spb
            j += 1
        p.note("hn_sus", in_range(key, 41, 52), t0, t_end - t0, vel=0.4, gain=0.26, pan=-0.25, bus="brass", attack=0.8)
        p.note("hn_sus", in_range(key + 7, 48, 59), t0 + 0.1, t_end - t0, vel=0.4, gain=0.24, pan=-0.15, bus="brass",
               attack=0.8)
        c.fx("triangle", t0, gain=0.25, pan=0.4, bus="perc")
        if eid in ("budapest", "pannonia", "bohemia"):
            c.fx("glass", t0 - 0.05, gain=0.35, pan=0.2, bus="fx")
        if e["has_doc"]:
            c.arpeggio(e["hold"] + 0.3, (key, MAJ), n=6, step=0.11, vel=0.4, lo=55, gain=0.35)

    def round(self, t0, t1, key, nv, act, spb, stretto=False, until=None, glide_to=None):
        """the round in key; voice k enters k bars (stretto: k half bars) later; between cycles a breath of
        two beats. glide_to: {voice: (t_glide, target)} — the voice stops there and slides onto target."""
        p = self.p
        base = in_range(key, 55, 66)
        out = []
        voices = ROUND_VOICES[act][:nv]
        for k, (inst, octv) in enumerate(voices):
            lo, hi = INSTR[inst]["range"]
            o = octv
            while base + o < lo:
                o += 12
            while base + o + 16 > hi:
                o -= 12
            start = t0 + k * (2 if stretto else 4) * spb
            stop = t1 if not glide_to else glide_to[k][0]
            t, last = start, None
            g = {"fl_sus": .3, "vln_solo": .36, "ob_sus": .34, "cl_sus": .38, "bsn_sus": .42}.get(inst, .35)
            pan = [0.35, -0.3, 0.15, -0.1][k]
            flat = [(off, d) for bar in ROUND for off, d in bar] + [(None, 2)]  # a cycle, then two beats' breath
            i = 0
            while True:
                off, d = flat[i % len(flat)]
                if t + d * spb > stop + 0.01:
                    break
                if off is not None:
                    last = base + o + off
                    p.note(inst, last, t, d * spb * 0.92, vel=0.5, gain=g, pan=pan, attack=0.03, release=0.4)
                t += d * spb
                i += 1
            if glide_to and last is not None:
                tg, target = glide_to[k]
                p.note(inst, last, tg, t1 - tg, vel=0.55, gain=g * 1.1, pan=pan, attack=0.05, release=0.3,
                       bend=target - last)
            out.append((inst, o))
        if act == "V":  # the celesta doubles the first voice an octave up, the reason in the bells' act
            pass
        return out

    def ev_lamp(self, e, t_end, act, m, tr):
        p, c = self.p, self.c
        t0, hold = e["t"], e["hold"]
        key = (5 + tr) % 12
        ch = (key, MAJ)
        lit = hold + 0.3 if self.full else t_end + 0.5  # in B the call sign brings its own harmony
        p.note("org_quiet", in_range(key, 41, 52), t0, lit - t0, vel=0.4, gain=0.3, bus="organ", attack=1.0)
        for j in range(14):  # lamps lighting one by one, each a little out of tune
            p.note("glock", in_range([0, 4, 7, 9][j % 4] + key, 79, 96), t0 + 0.2 + j * 0.37, 1.5, vel=0.45,
                   gain=0.26, pan=-0.7 + 0.1 * j, bus="harp", detune=c.rng.uniform(-0.3, 0.3))
        p.grains(fxcat.files("glass"), t0 + 0.5, hold + 1.5, 12, gain=0.06, bus="spores", pitch=[12, 17, 19, 24])
        for j in range(2):
            p.note("tubular", in_range(key, 60, 71) + 7 * j, t0 + 0.05 + 1.1 * j, min(4.0, lit - t0 - 1.1 * j), vel=0.55,
                   gain=0.3, pan=0.2, release=0.8)
        if self.full:  # the radio call sign: the Internationale on the celesta, twice — the second time rotten
            spb = 60 / 132
            tune = self.inter_tune()
            for r_, start in enumerate([hold + 0.2, hold + 0.2 + 18 * spb]):
                if start > t_end - 1.0:
                    break
                tm = TimeMap(start + spb, [spb])
                base = in_range(key, 55, 66) - 12
                sour = 0.0 if r_ == 0 else 0.4
                notes = [(tm.sec(pos), d * spb, base + off - (sour if off % 12 in (4, 11) else 0))
                         for pos, off, d in tune.notes if tm.sec(pos) < t_end - 0.3]
                self.lead(notes, act, m, leads=[("celesta", 12, .5), ("glock", 24, .14)], rot_on=r_ > 0)
                for k, (pos, ch_) in enumerate(tune.chords):
                    a = tm.sec(pos)
                    nx = tune.chords[k + 1][0] if k + 1 < len(tune.chords) else tune.length
                    if a < t_end - 0.3:
                        b = min(tm.sec(nx), t_end)
                        c.arpeggio(a, tch(ch_, key), n=4, step=0.06, vel=0.35, lo=50, gain=0.28, pan=-0.3,
                                    ring=max(0.4, b - a))
                        p.note("cb_sus", in_range((ch_[0] + key) % 12, 28, 40), a, b - a + 0.1, vel=0.45, gain=0.4,
                               pan=-0.2, attack=0.1, release=0.6)
        else:
            c.pad(t0, t_end + 0.6, ch, vel=0.4, gain=0.34, **rot(m))
            # the Mycelium's call sign: the hymn's head on the celesta
            self.lead([(t0 + 0.4 + 0.45 * j, 0.42, 62 + tr + 3 + o) for j, o in enumerate([0, 7, 9, 7, 5, 4, 2])],
                      act, m, leads=[("celesta", 12, .45)], rot_on=False)
            c.march(hold + 0.2, t_end, key=key, bpm=104, gain=0.36, sour=0.0, detune=0.45)

    def ev_school(self, e, t_end, act, m, tr):
        p, c = self.p, self.c
        t0 = e["t"]
        key = (5 + tr) % 12
        start = t0
        if self.full:  # the pioneer bugle: sound the assembly
            b0 = in_range(key + 7, 55, 62)
            tt = t0
            for o, d in [(0, .22), (5, .22), (9, .22), (12, .5), (9, .22), (12, 1.2)]:
                p.note("tpt_sus", b0 + o, tt, d * 0.92, vel=0.7, gain=0.4, pan=-0.1, bus="brass", release=0.3)
                tt += d
            c.fx("snare", t0 - 0.2, gain=0.3, bus="perc")
            start = tt + 0.3
        self.bed(act, t0, t_end, (key, MAJ), m, 0.4, gain=0.6)
        tune = [77, 77, 84, 84, 86, 86, 84, 82, 82, 81, 81, 79, 79, 77]
        tune = [x + tr + (12 if x + tr + 12 <= 96 else 0) for x in tune]
        c.music_box(start, tune, step=0.38, slow=0.025, flat=0.04, inst="glock", double="vln_pizz", gain=0.3)
        p.note("cl_sus", in_range(key + 7, 60, 71), t_end - 2.5, 2.4, vel=0.3, gain=0.25, bus="winds", bend=-0.6)

    def ev_hymn(self, e, t_end, act, m, tr):
        c = self.c
        t0 = e["t"]
        spb = (t_end - t0 - 0.3) / 16.0
        c.fx("snare", t0 - 0.25, gain=0.35, bus="perc")
        self.hymn([0, 1, 2, 3], t0, spb, act, m, tr, gain=1.15, lead_vel=0.72)
        for b in range(4):
            c.timp(t0 + 4 * b * spb, (HYMN_CH[b][0][0] + tr) % 12, vel=0.8 if b in (0, 3) else 0.55)
        c.fx("clash", t0 + 12 * spb, gain=0.35, bus="perc")
        c.spores(t0 + 12 * spb, 4.0, density=35, gain=0.2)

    def ev_heresy(self, e, t_end, act, m, tr):
        p, c = self.p, self.c
        eid, t0 = e["id"], e["t"]
        ch = ((D + tr) % 12, (0, 4, 8))
        c.pad(t0, t_end + 0.5, ch, vel=0.35, gain=0.35, bass_only=True, **rot(m))
        c.buzz(t0, t_end - t0, gain=0.28)
        for j in range(2):
            c.fx("alien", t0 + 0.3 + 2.5 * j, gain=0.25, shift=3 - 4 * j, pan=-0.5 + j, bus="deep")
        if eid in ("urga", "altai"):
            for j in range(4):
                c.fx("nepal", t0 + 0.4 + 1.3 * j, gain=0.3, pan=0.4 - 0.25 * j, bus="harp")
        if eid == "urga":
            self.migo(t0 + 0.6)
        elif eid == "altai":  # the answer: mirrored, on the violas' harmonics
            self.migo(t0 + 0.6, inst="vla_harm", invert=True)
        elif eid == "exodus":  # the departure: slower, every note pulled upward
            p.note("org_quiet", 74 + tr, t0 - 2.2, 2.3, vel=0.5, gain=0.3, bus="organ", reverse=True)
            self.migo(t0 + 0.4, stretch=1.4, rise=1.5)
            c.fx("glock_up", e["hold"], gain=0.3, bus="harp")
            c.shepard(e["hold"], t_end, up=True, gain=0.2, period=5.0)
        if self.full:
            p.note("cbsn_sus", in_range(ch[0], 22, 33), t0, t_end - t0, vel=0.5, gain=0.35, bus="winds", attack=1.0,
                   bend=-0.7)
        if e["big"]:
            c.timp(t0, (8 + tr) % 12, vel=0.5)
        if e["has_doc"]:
            c.arpeggio(e["hold"] + 0.2, ch, n=9, step=0.06, vel=0.35, lo=62, gain=0.35)

    def ev_dry(self, e, t_end, act, m, tr):
        p, c = self.p, self.c
        eid, t0 = e["id"], e["t"]
        root = (D + tr) % 12
        c.pad(t0, t_end + 0.4, (root, FIFTH), vel=0.3, gain=0.42, bass_only=True, attack=1.5)
        if eid != "salt":
            t = t0
            while t < t_end - 0.3:
                p.note("cb_pizz", in_range(root, 28, 40), t, 0.4, vel=0.6, gain=0.7, pan=-0.2)
                t += 1.6
        else:  # salt: no pulse at all — a white, high, crystalline fifth over the bass, slowly cracking
            p.note("cb_sus", in_range(root, 28, 40), t0, t_end - t0, vel=0.5, gain=0.55, pan=-0.2, attack=1.0)
            for j, (inst, x) in enumerate([("vln_harm", root + 7), ("vla_harm", root), ("vln_harm", root + 14)]):
                p.note(inst, in_range(x, 79, 91) if inst == "vln_harm" else in_range(x, 72, 84), t0 + 0.6 * j,
                       t_end - t0 - 0.6 * j, vel=0.4, gain=0.22, pan=-0.4 + 0.4 * j, attack=1.2, release=1.5,
                       bend=-0.3 * j * m)
            for j in range(5):
                p.note("crotales" if j % 2 else "glock", in_range(root + [7, 14, 0, 9, 7][j], 86, 100),
                       t0 + 1.2 + 1.5 * j, 2.0, vel=0.35, gain=0.16, pan=0.5 - 0.25 * j, detune=-0.15 * j)
        c.fx("guiro", t0 + 0.2, gain=0.25, pan=0.3, bus="fx")
        c.fx("ambience", t0, gain=0.25, bus="deep", dur=t_end - t0, attack=1.5)
        lead = "choir" if act == "III" else "fl_sus"
        p.note(lead, in_range(root + 7, 64, 75), t0 + 0.8, 2.6, vel=0.3, gain=0.3, pan=0.3, attack=0.3)
        p.note(lead, in_range(root + 2, 60, 71), t0 + 3.6, 2.6, vel=0.25, gain=0.25, pan=0.3, attack=0.3)
        if eid == "salt":
            p.grains(fxcat.files("glass"), t0 + 0.3, t_end - 0.5, 9, gain=0.07, bus="spores", pitch=[12, 14, 17, 19, 24])
        if eid == "dry":
            c.fx("brick", e["hold"], gain=0.25, bus="fx")
        if eid == "drought":  # the hymn's head, so slow it is hardly a tune: the choir and the organ, parched
            spb = (t_end - t0 - 1.0) / 4.0
            self.play_tune(Tune([HYMN[0]]), t0 + 0.5, spb, 62 + tr, act, m, bed=False, gain=0.8, lead_vel=0.45)
        c.timp(t0, root, vel=0.35)

    # 1997: the round in four voices collapses into one note; the hymn in unison, rotten; then, in tune
    def ev_final(self, e, t_end, act, m, tr):
        p, c = self.p, self.c
        t_fly, t_tr, t_hold = e["fly"], e["t"], e["hold"]
        spb = 60 / 120
        glide = {k: (t_fly + 1.4 + 0.45 * k, 62) for k in range(4)}
        self.round(t_fly, t_tr, D, 4, "VI", spb, stretto=True, glide_to=glide)
        p.note("vln_solo", 74, t_fly + 0.3, t_tr - t_fly - 0.3, vel=0.5, gain=0.25, pan=0.4, attack=0.05,
               bend=-12)
        c.timp(t_fly + 0.3, 9, vel=0.7, roll=t_tr - t_fly - 0.2)
        c.fx("susp_scrape", t_fly, gain=0.25, bus="fx", dur=t_tr - t_fly)
        c.shepard(t_fly, t_tr + 0.5, up=True, gain=0.3, period=3.5)
        # the hymn's first bar, everyone in one voice (unison and octaves), the rot at its worst
        spb1 = (t_hold - t_tr) / 4.0
        everyone = [("choir", 0, .42), ("hn_sus", 0, .34), ("tpt_sus", 0, .22), ("vln_sus", 0, .3), ("ob_sus", 0, .2),
                    ("cl_sus", -12, .25), ("tbn_sus", -12, .32), ("vc_sus", -12, .3), ("org_loud", -12, .2)]
        self.hymn([0], t_tr, spb1, "VI", 1.0, 0, leads=everyone, lead_vel=0.75, gain=1.0)
        if self.full:
            self.choir_slide(t_tr, t_hold - t_tr + 0.3, D, up=False)
            self.piano_low(t_tr, root=26)
        # the last lamp: the second phrase in D major, harmonised, perfectly in tune — and the archive is mono
        dur = self.cues["outro"][0] + 0.3 - t_hold
        spb2 = dur / 16.0
        tune = Tune(HYMN_B_MAJ, HYMN_B_MAJ_CH)
        tm = TimeMap(t_hold, [spb2])
        mel = [(tm.sec(pos), d * spb2, 62 + off) for pos, off, d in tune.notes]
        self.lead(mel, "VI", 0.0, leads=[("tpt_sus", 12, .3), ("hn_sus", 0, .4), ("vln_sus", 12, .34),
                                          ("choir", 0, .4), ("fl_sus", 12, .2)], rot_on=False, vel=0.75)
        lanes = [(26, 38, 0, "tba_sus"), (40, 52, 2, "tbn_sus"), (47, 59, 1, "tbn_sus"), (55, 66, 0, "hn_sus")]
        for k, (pos, ch) in enumerate(tune.chords):
            a = tm.sec(pos)
            b = tm.sec(tune.chords[k + 1][0]) if k + 1 < len(tune.chords) else t_end + 1.0
            c.pad(a, b + 0.2, ch, vel=0.75, gain=0.5, attack=0.08)
            pc = pcs_of(ch)
            for lane, (lo, hi, deg, inst) in enumerate(lanes):
                p.note(inst, in_range(pc[min(deg, len(pc) - 1)], lo, hi), a, (b - a) * 0.97, vel=0.72, gain=0.36,
                       pan=-0.3 + 0.2 * lane, bus="brass", attack=0.04, release=0.6)
            p.note("org_loud", in_range(ch[0], 26, 37), a, b - a + 0.1, vel=0.7, gain=0.3, bus="organ", release=1.0)
            if k % 2 == 0:
                c.timp(a, ch[0], vel=0.8 if k in (0, 6) else 0.55)
        c.fx("gong_hit", t_hold, gain=0.45, bus="perc")
        c.fx("clash", t_hold, gain=0.4, bus="perc")
        for j, n_ in enumerate([79, 83, 86, 91, 95]):  # G major: the first chord of the phrase
            p.note("glock", n_, t_hold + 0.1 + j * 0.15, 1.0, vel=0.45, gain=0.22, pan=0.4 - 0.1 * j, bus="harp",
                   release=0.6)
        c.spores(t_hold + 0.1, 6.0, density=60, gain=0.16)

    def outro(self):
        p, c = self.p, self.c
        a, b = self.cues["outro"]
        # Lenin's lullaby, augmented, in D major, in the deepest voices: the sleeper is the whole world now
        maj = [(66, 1.0), (62, 0.8), (61, 0.8), (57, 2.2), (59, 0.9), (57, 2.0)]
        chords = [(D, MAJ), (D, MAJ), (9, MAJ), (D, MAJ), (7, MAJ), (D, MAJ)]
        tt = a + 0.3
        bass = ("cbsn_sus", -24) if self.full else ("bsn_sus", -24)
        for (n_, d_), ch in zip(maj, chords):
            d_ *= 1.25
            self.n(bass[0], n_ + bass[1], tt, d_ * 0.97, vel=0.5, gain=0.45, pan=-0.1, attack=0.2, release=0.8,
                   bus="winds")
            p.note("cb_sus", n_ - 24, tt, d_ * 0.97, vel=0.45, gain=0.4, pan=-0.3, attack=0.3, release=0.8)
            p.note("hn_mute", in_range(ch[0], 50, 61), tt, d_ * 0.97, vel=0.35, gain=0.22, pan=0.2, attack=0.3)
            c.pad(tt, tt + d_ + 0.05, ch, vel=0.4, gain=0.34, attack=0.6 if tt < a + 1 else 0.25, release=1.2)
            p.note("org_quiet", in_range(ch[0], 38, 49), tt, d_ + 0.05, vel=0.45, gain=0.3, bus="organ",
                   attack=0.5 if tt < a + 1 else 0.1, release=1.5 if tt + d_ < b else 3.0)
            tt += d_
        c.pad(tt, b + 1.0, (D, MAJ), vel=0.35, gain=0.3, attack=0.4, release=2.5)
        c.arpeggio(a + 0.3 + 1.25 * 2.6, (D, MAJ), n=8, step=0.12, vel=0.35, lo=50, gain=0.3, ring=2.0)
        c.heartbeat(a + 1.0, b - 1.0, gain=0.22)
        c.fx("alien", a + 4.0, gain=0.12, shift=-9, bus="deep", attack=2.0)


def build(ctx, variant="A"):
    return Score(ctx, variant).build()
