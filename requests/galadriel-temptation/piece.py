#!/usr/bin/env python3
"""Искушение Галадриэли — Лориен ночью, Фродо предлагает Кольцо (≈ 3:34).

Style, not quotation: the obsession number of a stage musical (pipe organ, a pulsing quaver ostinato, a
chromatically descending bass under a minor chord, tempter ↔ tempted, every round a semitone higher, a
soprano vocalise climbing to the peak) joined with a Lothlórien/Ring film-score idiom (women's choir over a
drone, Dorian/Phrygian turns, low brass and contrabassoon with tritones and minor seconds, starlight bells).
Both themes are written here (brief.json): Galadriel D–A–B–E–D–A, the Ring D–E♭–D–G♯.

Through-processes (plan.md): the Ring's tritone shadow in the bass, growing to the peak and staying as a
shadow at the end; rounds a semitone up (D minor → E♭ minor → E minor); the 'rot' of the tuning from 1:12 to
the cut at 2:40, pure tuning after it.

    python3 -m kit run requests/galadriel-temptation/piece.py --sketch --parts
    python3 -m kit run requests/galadriel-temptation/piece.py --parts
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from kit import fx as fxcat  # noqa: E402
from kit.devices import Composer  # noqa: E402
from kit.events import Piece  # noqa: E402
from kit.harmony import MAJ, MIN, in_range  # noqa: E402

D = 2
GALADRIEL = [0, 7, 9, 14, 12, 7]            # D A B E D A (over D): Dorian sixth
RING = [0, 1, 0, -6]                        # D Eb D G#: minor second, tritone
STAR = [2, 4, 7, 9, 11]                     # D E G A B — Dorian-pentatonic starlight


class G:
    """the piece's state and helpers"""

    def __init__(self, ctx):
        self.cues = ctx.cues["cues"]
        self.total = ctx.cues["duration_s"]
        self.p = Piece("Искушение Галадриэли", bpm=104, meter=(4, 4), key="D minor", seed=31)
        self.p.meta["sends"] = {"choir": 0.6, "organ": 0.5, "harp": 0.55, "winds": 0.4, "strings": 0.42, "brass": 0.35}
        self.c = Composer(self.p, lib="sso", seed=17)
        self.rng = self.c.rng
        for cue in self.cues:
            if cue["kind"] in ("section", "hit", "silence"):
                self.p.mark(cue["t"], cue["label"][:24])

    def t(self, label):
        return next(c["t"] for c in self.cues if c["label"] == label)

    # colours measured too quiet in the sketch (balance table: celesta −16, crotales −26, harmonics −20 dB under
    # the choir); raised here, for every section
    LEVEL = {"celesta": 2.5, "crotales": 5.0, "vln_harm": 2.5}
    mult = 1.0  # a running level factor (the obsession grows phrase by phrase)

    def n(self, inst, m, t, d, **kw):
        kw["gain"] = kw.get("gain", 1.0) * self.mult
        if inst in self.LEVEL:
            kw["gain"] = kw["gain"] * self.LEVEL[inst]
        if inst == "org_quiet" and m < 36:  # no library recorded the quiet organ below C2: the loud pedal, softer
            inst = "org_loud"
            kw["gain"] = kw.get("gain", 1.0) * 0.55
        return self.p.note(inst, m, t, d, **kw)

    def chord(self, inst, ms, t, d, spread=0.012, **kw):
        return [self.n(inst, m, t + spread * i, d, **kw) for i, m in enumerate(ms)]

    def theme(self, inst, intervals, root, t, durs, **kw):
        tt = t
        for iv, d in zip(intervals, durs):
            if iv is not None:
                self.n(inst, root + iv, tt, d * 0.96, **kw)
            tt += d
        return tt


# ------------------------------------------------------------------------------------------------------------
def lorien(g, t0, t1):
    """0:00 — night in Lórien: women's choir over a D–A drone, starlight, harmonics; very far — the dark"""
    dur = t1 - t0
    g.n("cb_sus", 38, t0, dur + 1, vel=0.3, gain=0.45, attack=4.0, release=3.0)
    g.n("vc_sus", 45, t0 + 1.0, dur, vel=0.28, gain=0.4, attack=4.0, release=3.0)
    g.n("org_quiet", 26, t0 + 2.0, dur, vel=0.35, gain=0.3, attack=5.0, release=3.0)
    voicings = [[62, 65, 69, 76], [60, 64, 67, 74], [62, 65, 70, 76], [62, 64, 69, 74]]  # Dm9, C/D, B♭(♯11)/D, Dsus
    for i, v in enumerate(voicings):
        g.chord("choir", v, t0 + 2.5 + 6.2 * i, 7.0, vel=0.3 + 0.03 * i, gain=1.0, attack=2.4, release=2.5, spread=0.15)
    g.n("vln_harm", 93, t0 + 4.0, 12.0, vel=0.25, gain=0.5, attack=3.0, release=3.0, pan=0.4)
    g.n("vln_harm", 100, t0 + 14.0, 12.0, vel=0.22, gain=0.42, attack=3.0, release=3.0, pan=-0.4)
    t = t0 + 3.0
    while t < t1 - 2:  # starlight: sparse bells from the Dorian pentatonic
        inst = g.rng.choice(["celesta", "celesta", "crotales", "glock"])
        lo = {"celesta": 79, "crotales": 86, "glock": 84}[inst]
        m = in_range(g.rng.choice(STAR), lo, lo + 14)
        gain = {"celesta": 2.4, "crotales": 2.4, "glock": 1.1}[inst]  # starlight must be heard (balance, sketch 1)
        g.n(inst, m, t, 2.5, vel=0.25 + 0.1 * g.rng.random(), gain=gain, pan=g.rng.uniform(-0.7, 0.7), release=2.5)
        t += g.rng.uniform(0.9, 2.2)
    g.c.arpeggio(t0 + 0.6, (D, (0, 7, 14, 17, 21)), n=9, step=0.11, lo=38, gain=0.4, vel=0.3, ring=4.0)
    g.c.arpeggio(t0 + 14.5, (D, (0, 7, 14, 16, 21)), n=9, step=0.11, lo=38, gain=0.38, vel=0.28, ring=4.0)
    # very far away: the Ring's tritone, felt rather than heard
    g.n("cbsn_sus", 32, t0 + 18.0, 7.0, vel=0.2, gain=0.15, attack=3.0, release=2.5, bend=-0.3)


def mirror(g, t0, t1, t_acc):
    """0:28 — the Mirror: Galadriel's theme on the alto flute, the harp as water; Frodo's clarinet answers"""
    dur = t1 - t0
    g.n("cb_sus", 38, t0, dur + 0.5, vel=0.3, gain=0.45, attack=2.0, release=2.0)
    for m, pan in ((50, -0.2), (57, 0.0), (64, 0.2)):  # D–A–E open strings as the ground of the water
        g.n("vla_sus" if m > 52 else "vc_sus", m, t0, dur, vel=0.25, gain=0.32, attack=2.5, release=2.0, pan=pan)
    g.chord("choir", [57, 62, 69], t0 + 1, dur - 1, vel=0.22, gain=0.35, attack=3.0, release=2.0)
    # water: rippling harp sextuplets over D Dorian, slowly changing figure
    figs = [[50, 57, 62, 64, 69, 71], [50, 57, 62, 67, 69, 74], [48, 55, 62, 64, 67, 72], [50, 57, 60, 64, 69, 76]]
    t, k = t0 + 0.2, 0
    while t < t1 - 0.4:
        f = figs[(k // 12) % len(figs)]
        g.n("harp", f[k % 6] + (12 if (k // 6) % 2 else 0), t, 1.6, vel=0.32, gain=0.21, pan=-0.3 + 0.1 * (k % 6), release=1.5)
        t += 0.135
        k += 1
    # the theme (alto flute): D A B E D A
    g.theme("afl_sus", GALADRIEL, 62, t0 + 2.0, [1.6, 1.0, 1.4, 2.6, 1.1, 3.2], vel=0.45, gain=0.55, attack=0.25,
            release=1.2, pan=0.1)
    # Frodo: a plain, trusting phrase
    g.theme("cl_sus", [0, 2, 3, 2, 0], 57, t0 + 12.0, [0.8, 0.8, 1.6, 0.8, 2.4], vel=0.38, gain=0.45, attack=0.12, pan=-0.25)
    # the water trembles
    g.c.fx("glock_down", t_acc - 0.1, gain=0.25, pan=0.3, bus="harp")
    g.c.spores(t_acc, 3.0, density=24, gain=0.16, lib="sso")
    g.n("vln_harm", 99, t_acc, 4.0, vel=0.3, gain=0.3, attack=0.4, pan=-0.3, detune=0.15)
    # the theme again, first notes only, a step lower — shadowed
    g.theme("afl_sus", [0, 7, 8], 62, t_acc + 0.8, [1.4, 1.2, 3.4], vel=0.4, gain=0.5, attack=0.3, release=1.5)


def vision(g, t0, t_cut):
    """0:50 — the vision: the Ring whispers (contrabassoon, bass clarinet), a semitone cluster, breathing,
    a falling endless glissando; crescendo to the cut before the silence"""
    dur = t_cut - t0
    # no hole at the seam with the Mirror: the ground is there at once
    g.n("org_quiet", 26, t0 - 0.5, dur + 0.5, vel=0.5, gain=0.4, attack=0.8, release=0.3)
    g.n("cb_trem", 38, t0, dur, vel=0.45, gain=0.5, attack=1.2, release=0.3, pan=-0.3)
    g.n("cb_sus", 38, t0 - 0.3, 4.0, vel=0.35, gain=0.5, attack=0.5, release=2.0)
    g.n("vc_trem", 50, t0 + 5, dur - 5, vel=0.4, gain=0.35, attack=5.0, release=0.3, pan=-0.1)
    g.n("vla_trem", 51, t0 + 7, dur - 7, vel=0.35, gain=0.3, attack=5.0, release=0.3, pan=0.15, detune=0.2)
    # the Ring: D Eb D G# — low, slow; then an octave higher, then closer still
    # each statement nearer and louder: the vision grows to the cut
    g.theme("cbsn_sus", RING, 38, t0 + 2.0, [1.6, 1.6, 1.6, 3.5], vel=0.4, gain=0.42, attack=0.4, release=1.0)
    g.theme("bcl_sus", RING, 50, t0 + 8.5, [1.3, 1.3, 1.3, 2.8], vel=0.5, gain=0.75, attack=0.3, release=1.0, pan=0.2)
    g.theme("hns_sus", RING, 50, t0 + 13.0, [0.9, 0.9, 0.9, t_cut - t0 - 15.7], vel=0.65, gain=0.75, attack=0.2, release=0.3,
            pan=-0.25)
    # the swell: full organ creeping in under everything, to the cut
    for m in (26, 38, 39, 45, 50, 51):
        g.n("org_loud", m, t0 + 9.0, t_cut - t0 - 9.0, vel=0.7, gain=0.3, attack=t_cut - t0 - 9.5, release=0.2)
    g.c.breath(t0 + 4.0, 8.0, gain=0.4)
    g.c.shepard(t0 + 9.0, t_cut, gain=0.2, period=6.0)
    g.c.heartbeat(t0 + 5.0, t_cut - 0.6, gain=0.28)
    # the Eye: a tritone flickering high in harmonics, ring-modulated
    g.n("vln_harm", 99, t0 + 10.0, t_cut - t0 - 10.2, vel=0.3, gain=0.25, attack=2.0, release=0.2, ringmod=7.0, pan=0.4)
    g.n("vln_harm", 93, t0 + 11.0, t_cut - t0 - 11.2, vel=0.3, gain=0.22, attack=2.0, release=0.2, ringmod=5.0, pan=-0.4)
    g.c.timp(t_cut - 3.0, D, vel=0.55, roll=2.9)


def offer(g, t):
    """1:10 — "I will give it to you": the organ at full strength"""
    org = [26, 38, 50, 57, 62, 65, 69, 74]
    for m in org:
        g.n("org_loud", m, t, 2.4, vel=0.85, gain=0.42, attack=0.02, release=1.8)
    for m, inst in ((26, "tba_sus"), (38, "tbn_sus"), (45, "tbn_sus"), (53, "hns_sus"), (57, "hns_sus")):
        g.n(inst, m, t, 1.8, vel=0.8, gain=0.45, attack=0.02, release=1.0)
    g.c.timp(t, D, vel=0.95)
    g.c.fx("tamtam", t, gain=0.45, bus="perc")
    g.c.fx("bd", t, gain=0.4, bus="perc")


def obsession(g, t0, t1, key, round_no, swell=None):
    """the obsession: quaver ostinato, the chromatic bass descending under the minor chord, organ blows at the
    head of each phrase, the Ring (brass) ↔ Galadriel (choir, flute / violins); round 2 a semitone higher,
    denser, the tuning rotting"""
    p, c = g.p, g.c
    q = 60.0 / 104 / 2              # a quaver
    bar = 8 * q
    nbars = int((t1 - t0) / bar)
    rot = 0.08 if round_no == 1 else 0.18
    bass = [0, -1, -2, -3, -4, -5]  # D C# C B Bb A under D minor — two bars each
    for b in range(nbars):
        tb = t0 + b * bar
        x = b / max(1, nbars - 1)
        # growth (full render 3: both rounds sat at one level for a minute): round 1 from −2 dB to +1.5,
        # round 2 from +2 to +6 — the obsession grows phrase by phrase
        g.mult = 10 ** (((-2 + 3.5 * x) if round_no == 1 else (2 + 4 * x)) / 20)
        step = bass[(b // 2) % 6]
        groot = in_range(key, 38, 49)
        low = groot + step
        last_bar = b == nbars - 1
        # the pulse: quavers on the root, octave leap on 4 and 8
        for k in range(8):
            m = groot - 12 if k in (3, 7) else groot
            v = 0.62 if k in (0, 4) else 0.45
            if round_no == 2 or swell:
                v += 0.08
            g.n("vc_spic", m + 12, tb + k * q, q * 0.8, vel=v, gain=0.5, pan=-0.15, release=0.2)
            if round_no == 2:
                g.n("vla_spic", m + 24, tb + k * q, q * 0.8, vel=v * 0.9, gain=0.35, pan=0.2, release=0.2)
        # the chromatic bass (the floor): contrabasses, contrabassoon, organ pedal
        if b % 2 == 0:
            d2 = 2 * bar
            g.n("cb_sus", low, tb, d2 * 0.98, vel=0.6, gain=0.6, attack=0.05, release=0.6, pan=-0.3)
            g.n("cbsn_sus", low - 12 if low - 12 >= 22 else low, tb, d2 * 0.98, vel=0.55, gain=0.45, attack=0.05, release=0.5)
            g.n("org_quiet", low - 12, tb, d2, vel=0.5, gain=0.3, attack=0.05, release=0.5)
            # the minor chord above the moving bass (organ manual, sustained strings)
            ch = [in_range(key, 60, 71), in_range(key + 3, 60, 72), in_range(key + 7, 62, 74)]
            for m in ch:
                g.n("org_reed", m, tb, d2, vel=0.45, gain=0.3, attack=0.1, release=0.6)
            c.pad(tb, tb + d2, (key, MIN), vel=0.45 + 0.1 * round_no, gain=0.35, attack=0.4, detune=rot,
                  drift=-0.1 * round_no, double_gain=0.4, bass_only=False)
        if b % 4 == 0:  # the organ blow at the head of the phrase
            for m in [in_range(key, 26, 37), in_range(key, 38, 49), in_range(key + 7, 50, 61), in_range(key, 60, 71),
                      in_range(key + 3, 62, 73), in_range(key + 7, 66, 77)]:
                g.n("org_loud", m, tb, bar * 0.45, vel=0.75, gain=0.35, attack=0.02, release=1.2)
            c.timp(tb, key, vel=0.75)
            c.fx("bd", tb, gain=0.35, bus="perc")
        elif round_no == 2 or swell:
            c.fx("bd_soft", tb, gain=0.35 * g.mult, bus="perc")
        if round_no == 2 and b >= 4 and b % 2 == 0:  # horns hold the minor chord: the room fills up
            for m in (in_range(key, 50, 61), in_range(key + 3, 53, 64), in_range(key + 7, 55, 67)):
                g.n("hns_sus", m, tb, 2 * bar * 0.98, vel=0.55 + 0.2 * x, gain=0.35, attack=0.6, release=0.4, pan=0.15,
                    detune=rot * 0.6)
        if round_no == 2 and b >= nbars - 4:  # the last four bars: timpani on every beat
            for k in range(4):
                c.timp(tb + k * 2 * q, key if k % 2 == 0 else key + 7, vel=0.6 + 0.3 * x)
        # dialogue: the Ring speaks on bars 1–2 of four, Galadriel answers on 3–4
        ph = b % 4
        if ph == 0 and not last_bar:
            ring_inst = ("hns_sus",) if round_no == 1 else ("tbn_sus", "tba_sus")
            base = in_range(key, 50, 61) if round_no == 1 else in_range(key, 43, 54)
            for inst in ring_inst:
                o = -12 if inst == "tba_sus" else 0
                g.theme(inst, RING + [None, 5, 4, 3, 1], base + o, tb, [q * 2, q * 2, q * 2, q * 6, q * 2, q * 2, q * 2, q * 2, q * 6],
                        vel=0.65 + 0.1 * (round_no - 1), gain=0.5, attack=0.05, release=0.4, pan=-0.3)
            if round_no == 2:  # the Ring's echo in the horns a bar later: the voices intertwine
                g.theme("hns_sus", RING, in_range(key, 55, 66), tb + bar, [q * 2, q * 2, q * 2, q * 6], vel=0.55, gain=0.4,
                        attack=0.05, pan=0.3, detune=rot)
        if ph == 2 and not last_bar:
            # Galadriel answers: her theme in minor with a Phrygian second (… B♭ E♭ …)
            ans = [0, 7, 8, 13, 12, 7]
            durs = [q * 3, q * 2, q * 3, q * 4, q * 2, q * 2]
            if round_no == 1:
                g.theme("choir", ans, in_range(key, 62, 73), tb, durs, vel=0.55, gain=0.5, attack=0.25, release=0.8)
                g.theme("afl_sus", ans, in_range(key, 62, 73), tb, durs, vel=0.5, gain=0.4, attack=0.1, release=0.6, pan=0.2)
            else:
                g.theme("vln_leg", ans, in_range(key, 67, 78), tb, durs, vel=0.65, gain=0.5, attack=0.08, release=0.6, pan=0.3)
                g.theme("choir", ans, in_range(key, 62, 73), tb, durs, vel=0.62, gain=0.5, attack=0.2, release=0.8)
                g.theme("fl_sus", ans, in_range(key, 74, 85), tb, durs, vel=0.5, gain=0.35, attack=0.08, release=0.6,
                        pan=0.35, detune=rot * 0.5)
    g.mult = 1.0
    if swell:  # 2:05 → 2:15: everything climbs into the Dark Queen
        s0, s1 = swell
        c.shepard(s0, s1, up=True, gain=0.3, period=3.0)
        c.timp(s1 - 6.0, key, vel=0.85, roll=5.9)
        c.fx("susp_scrape", s1 - 5.0, gain=0.3, bus="fx", dur=5.0)
        for lane, (inst, m) in enumerate((("cb_trem", 40), ("vc_trem", 52), ("vla_trem", 59), ("vln_trem", 67))):
            g.n(inst, m, s0, s1 - s0, vel=0.7, gain=0.4, attack=s1 - s0, release=0.3, pan=-0.3 + 0.2 * lane,
                bend=4.0)
        g.chord("choir", [in_range(key, 55, 66), in_range(key + 3, 60, 70), in_range(key + 7, 62, 74)], s0, s1 - s0,
                vel=0.7, gain=0.5, attack=s1 - s0 - 0.5, release=0.3)


def dark_queen(g, t_hit, t0, t_cut):
    """2:15 — the Dark Queen (E minor): full organ, choir ff, a brass chorale i–♭VI–♭II–i, the vocalise
    climbing by semitones; the rot at its worst; cut dead before the silence"""
    E = 4
    prog = [(E, MIN), (0, MAJ), (5, MAJ), (E, MIN)]
    seg = (t_cut - t_hit) / len(prog)
    for j, ch in enumerate(prog):
        tt = t_hit + j * seg
        d = seg if j < len(prog) - 1 else t_cut - tt
        root = ch[0]
        pcs = [(root + i) % 12 for i in ch[1]]
        organ = [in_range(root, 26, 37), in_range(root, 38, 49), in_range(pcs[2], 50, 61), in_range(pcs[0], 60, 71),
                 in_range(pcs[1], 62, 73), in_range(pcs[2], 66, 77), in_range(pcs[0], 72, 83)]
        for m in organ:
            g.n("org_loud", m, tt, d, vel=0.9, gain=0.33, attack=0.03, release=0.15)
        g.chord("choir", [in_range(pcs[0], 52, 63), in_range(pcs[1], 57, 68), in_range(pcs[2], 62, 73), in_range(pcs[0], 69, 80)],
                tt, d, vel=0.85, gain=0.55, attack=0.15, release=0.15)
        for k, (lo, hi, deg, inst) in enumerate([(28, 40, 0, "tba_sus"), (40, 52, 2, "tbn_sus"), (47, 59, 0, "tbn_sus"),
                                                 (52, 64, 1, "hns_sus"), (57, 69, 2, "hns_sus")]):
            m = in_range(pcs[deg], lo, hi)
            g.n(inst, m, tt, d * 0.97, vel=0.85, gain=0.42, pan=-0.3 + 0.15 * k, attack=0.04, release=0.15)
            g.n(inst, m, tt + 0.03, d * 0.97, vel=0.7, gain=0.18 + 0.05 * j, pan=0.3 - 0.15 * k, attack=0.05, release=0.15,
                detune=0.18 + 0.08 * j, bend=-0.2 * j)
        g.c.pad(tt, tt + d, ch, vel=0.85, gain=0.5, attack=0.1, release=0.15, detune=0.15 + 0.08 * j, drift=-0.2 * j,
                double_gain=0.5)
        g.c.timp(tt, root, vel=0.9 if j in (0, 3) else 0.6)
        # the Ring under it all, in the depths: E F E A#
        g.theme("cbsn_sus", RING, 28, tt, [d / 6, d / 6, d / 6, d / 2], vel=0.75, gain=0.55, attack=0.03, release=0.15)
    g.c.fx("tamtam", t_hit, gain=0.5, bus="perc")
    g.c.fx("clash", t_hit, gain=0.4, bus="perc")
    g.c.fx("gong_hit", t_hit + 0.02, gain=0.35, bus="perc")
    # the vocalise: each phrase starts a semitone higher than the last; it climbs and climbs
    start = 76  # E5
    t = t0 + 0.6
    k = 0
    while t < t_cut - 4.0:
        top = start + k
        run = [top, top + 2, top + 3, top + 5, top + 7, top + 5, top + 3]
        durs = [0.32, 0.32, 0.32, 0.32, 1.4, 0.5, 0.9]
        # flute an octave up only while it stays in its range; quieter: a high flute cuts through everything
        for inst, o, gn in (("vln_sus", 0, 0.55), ("fl_sus", 12 if top + 19 <= 96 else 0, 0.15), ("choir", -12, 0.3)):
            g.theme(inst, [x - top for x in run], top + o, t, durs, vel=0.8, gain=gn, attack=0.04, release=0.3,
                    pan=0.3 if inst == "vln_sus" else 0.0)
        t += sum(durs) + 0.35
        k += 1
    # the last held note: as high as she can — and it sinks: despair; cut dead
    last = start + k + 7
    hold = t_cut - t
    # the piccolo very soft: in this register it would drown the whole orchestra (full render 1: −1.8 LUFS)
    for inst, o, gn in (("vln_sus", 0, 0.6), ("picc_sus", 12 if last + 12 <= 103 else 0, 0.06), ("vln_harm", 12, 0.12),
                        ("choir", -12 if last - 12 <= 84 else -24, 0.35)):
        g.n(inst, last + o, t, hold, vel=0.9, gain=gn, attack=0.08, release=0.12, bend=-0.6)
    # the ostinato keeps driving under the queen
    q = 60.0 / 104 / 2
    tt = t_hit
    while tt < t_cut - q:
        g.n("vc_spic", 52 if int((tt - t_hit) / q) % 4 != 3 else 40, tt, q * 0.8, vel=0.7, gain=0.45, pan=-0.15, release=0.1)
        tt += q


def passed(g, t0, t1):
    """2:42 — the test is passed: Galadriel's theme in D major on the celesta, the harp, choir pp; Frodo's relief"""
    dur = t1 - t0
    g.n("cb_sus", 38, t0, dur + 0.5, vel=0.3, gain=0.5, attack=0.8, release=2.0)  # the light returns at once
    g.n("vc_sus", 50, t0 + 0.5, dur, vel=0.28, gain=0.38, attack=2.0, release=2.0)
    g.n("org_quiet", 38, t0, dur, vel=0.4, gain=0.3, attack=1.5, release=2.0)
    for i, v in enumerate([[62, 66, 69, 76], [61, 66, 69, 76], [59, 66, 71, 74], [62, 66, 69, 74]]):  # D(add9) D/C# Bm D
        g.chord("choir", v, t0 + 1.0 + 5.5 * i, 6.5, vel=0.3, gain=0.45, attack=2.2, release=2.0, spread=0.12)
    g.theme("celesta", GALADRIEL, 74, t0 + 2.0, [1.0, 0.8, 1.0, 2.0, 0.8, 2.6], vel=0.5, gain=0.5, pan=0.2)
    g.theme("afl_sus", GALADRIEL, 62, t0 + 10.0, [1.5, 1.0, 1.3, 2.6, 1.1, 3.6], vel=0.45, gain=0.5, attack=0.25, release=1.2)
    g.c.arpeggio(t0 + 0.1, (D, (0, 7, 14, 16, 19)), n=10, step=0.1, lo=38, gain=0.6, vel=0.4, ring=4.0)
    g.c.arpeggio(t0 + 9.8, (D, (0, 7, 14, 16, 21)), n=10, step=0.1, lo=50, gain=0.35, vel=0.3, ring=4.0)
    g.n("vln_harm", 90, t0 + 3.0, dur - 4, vel=0.25, gain=0.28, attack=3.0, release=2.0)
    # Frodo's relief: the plain phrase, now ending upward
    g.theme("cl_sus", [0, 2, 4, 5], 57, t0 + 17.0, [0.8, 0.8, 0.8, 3.2], vel=0.4, gain=0.45, attack=0.12, pan=-0.25)


def west(g, t0, t_stars, t_end):
    """3:05 — to the West: English-horn elegy, D major with the minor subdominant, the Ring's tritone a shadow in
    the bass; 3:28 the stars go out"""
    g.mult = 10 ** (3 / 20)  # full render 3: too faint after the climax
    dur = t_end - t0
    prog = [((D, MAJ), 5.0), ((11, MIN), 5.0), ((7, MAJ), 5.0), ((7, MIN), 5.5), ((D, MAJ), dur - 20.5)]
    tt = t0
    for ch, d in prog:
        g.c.pad(tt, tt + d, ch, vel=0.3, gain=0.4, attack=1.8, release=2.5)
        pcs = [(ch[0] + i) % 12 for i in ch[1]]
        g.chord("choir", [in_range(pcs[0], 55, 66), in_range(pcs[1], 60, 71), in_range(pcs[2], 64, 76)], tt, d,
                vel=0.25, gain=0.4, attack=2.0, release=2.5)
        tt += d
    g.n("cb_sus", 38, t0, dur, vel=0.28, gain=0.5, attack=2.0, release=3.0)
    # the elegy: a falling line, then the theme's opening, unfinished
    g.theme("eh_sus", [7, 5, 4, 2, 0, None, 4, 2, -3], 62, t0 + 1.0, [1.2, 0.8, 0.8, 1.2, 3.0, 0.6, 1.0, 1.0, 3.6],
            vel=0.45, gain=0.55, attack=0.15, release=1.2, pan=0.1)
    g.theme("afl_sus", [0, 7, 9], 62, t0 + 15.0, [1.6, 1.2, 4.5], vel=0.4, gain=0.45, attack=0.3, release=2.0, pan=-0.1)
    # the shadow: the Ring's tritone, very low, under the major chord
    g.n("cbsn_sus", 32, t0 + 11.0, 11.0, vel=0.25, gain=0.4, attack=3.0, release=3.0, bend=-0.2)
    g.n("org_quiet", 26, t0 + 12.0, dur - 12.0, vel=0.35, gain=0.3, attack=4.0, release=3.0)
    # the stars go out: bells falling and thinning, harmonics fading
    for j, (m, gap) in enumerate([(86, 0.0), (81, 1.1), (76, 1.3), (74, 1.6), (69, 2.0), (62, 2.6)]):
        t_ = t_stars - 0.5 + sum(x[1] for x in [(86, 0.0), (81, 1.1), (76, 1.3), (74, 1.6), (69, 2.0), (62, 2.6)][:j + 1])
        g.n("celesta", m, t_, 3.0, vel=0.32 - 0.03 * j, gain=0.4, pan=0.4 - 0.15 * j, release=3.0)
    g.n("crotales", 98, t_stars + 0.3, 3.0, vel=0.25, gain=0.25, pan=-0.3)
    g.n("vln_harm", 86, t_stars - 3.0, t_end - t_stars + 2.0, vel=0.22, gain=0.25, attack=2.0, release=3.0)


def build(ctx):
    g = G(ctx)
    T = g.t
    t_mirror, t_acc, t_vision = T("Зеркало"), T("Вода в чаше дрогнула"), T("Видение")
    t_sil1, t_offer, t_obs = T("Фродо протягивает Кольцо"), T("«Я отдам его вам»"), T("Искушение")
    t_r2, t_swell, t_hit = T("Второй круг"), T("К кульминации"), T("Тёмная Королева")
    t_peak, t_sil2, t_passed = T("Вершина"), T("Она опускает руку"), T("Испытание пройдено")
    t_west, t_stars = T("Уйти на Запад"), T("Звёзды гаснут")
    lorien(g, 0.0, t_mirror)
    mirror(g, t_mirror, t_vision, t_acc)
    vision(g, t_vision, t_sil1 - 0.15)
    offer(g, t_offer)
    obsession(g, t_obs, t_r2, D, 1)
    obsession(g, t_r2, t_hit, 3, 2, swell=(t_swell, t_hit))
    dark_queen(g, t_hit, t_peak, t_sil2 - 0.1)
    passed(g, t_passed, t_west)
    west(g, t_west, t_stars, g.total - 1.0)
    return g.p
