"""Reusable devices — the composer's vocabulary as code. Each writes events into a Piece.

  c = Composer(piece)                    # 'lib' picks grain sources and the FX family ('vsco' / 'sso')
  c.pad(t0, t1, (2, MIN))                # sustained string chord, smooth voice leading
  c.pad(..., detune=0.2, drift=-0.3)     # 'rot': an out-of-tune double sinking under the chord
  c.motif(t, (2, MIN), steps=(0, 7, 8, 7)) …

The out-of-tune double (detune/drift), the spores, heartbeat, breath, Shepard glissando, ring-modulated
buzz, the sour march come from the R.S.F.G.R. score (examples/rsfgr) and are general tools now.
"""
import random

from . import fx as fxcat
from .harmony import MAJ, MIN, QUARTER, chord_pcs, in_range


class Composer:
    def __init__(self, piece, lib="vsco", seed=11):
        self.p = piece
        self.lib = lib
        self.rng = random.Random(seed)
        self.voices = {"cb": 38, "vc": 50, "vla": 57, "vln": 65}

    # -- raw sounds ----------------------------------------------------------------------------------------
    def fx(self, kind, t, **kw):
        files = fxcat.files(kind)
        if not files:
            return None
        kw.setdefault("bus", "fx")
        return self.p.sample(self.rng.choice(files), t, **kw)

    # -- strings, chords -----------------------------------------------------------------------------------
    def pad(self, t0, t1, chord, vel=0.5, insts=("cb_sus", "vc_sus", "vla_sus", "vln_sus"), gain=0.5, attack=0.8,
            bass_only=False, detune=0.0, drift=0.0, double_gain=0.5, release=1.4):
        """a four-lane string chord (bass, cello, viola, violin) moving by the nearest step from the last one.
        detune/drift > 0: every lane doubled out of tune (semitones), the double sinking by `drift` over
        the chord — the 'rot'."""
        root, iv = chord
        pcs = chord_pcs(chord)
        lanes = [("cb", 28, 41, root % 12, insts[0], -0.35),
                 ("vc", 40, 55, pcs[-1] if len(pcs) > 2 else root, insts[1], -0.15),
                 ("vla", 52, 64, pcs[1] if len(pcs) > 2 else pcs[-1], insts[2], 0.15),
                 ("vln", 62, 76, pcs[0] if len(pcs) > 2 else pcs[-1], insts[3], 0.35)]
        if bass_only:
            lanes = lanes[:2]
        out = []
        for lane, lo, hi, pc, inst, pan in lanes:
            m = in_range(pc, lo, hi, self.voices[lane])
            self.voices[lane] = m
            self.p.note(inst, m, t0, t1 - t0, vel=vel, gain=gain, pan=pan, attack=attack, release=release,
                        bend=drift * 0.5)
            if detune > 0.04:
                self.p.note(inst, m, t0 + 0.05, t1 - t0, vel=vel * 0.9, gain=gain * double_gain, pan=-pan,
                            attack=attack * 1.3, release=release, detune=detune, bend=drift)
            out.append(m)
        return out

    def motif(self, t, chord, inst="hn_sus", vel=0.6, gain=0.55, octave=None, steps=(0, 7, 8, 7),
              durs=(0.55, 0.55, 0.55, 1.6), detune=0.0, drift=0.0, pan=-0.2, bus=None, double_gain=0.5):
        """a short figure over the chord's root (steps in semitones; a minor sixth becomes major in a major
        chord); returns the end time"""
        root, iv = chord
        base = in_range(root, 50, 61, 55) if octave is None else in_range(root, octave, octave + 11)
        st = [9 if (x == 8 and 4 in iv) else x for x in steps]
        tt = t
        for s_, d_ in zip(st, durs):
            self.p.note(inst, base + s_, tt, d_ * 0.95, vel=vel, gain=gain, pan=pan, bus=bus, release=0.5,
                        bend=drift * 0.6 if d_ > 1.0 else 0.0)
            if detune > 0.12:
                self.p.note(inst, base + s_, tt + 0.03, d_ * 0.95, vel=vel * 0.8, gain=gain * double_gain, pan=-pan, bus=bus,
                            release=0.5, detune=detune)
            tt += d_
        return tt

    def arpeggio(self, t, chord, n=7, step=0.085, vel=0.5, lo=50, gain=0.5, inst="harp", ring=2.5, pan=0.3):
        root, iv = chord
        notes, m = [], in_range(root, lo, lo + 11)
        while len(notes) < n:
            for i in iv:
                if len(notes) < n:
                    notes.append(m + i)
            m += 12
        for k, nt in enumerate(notes):
            self.p.note(inst, nt, t + k * step, ring, vel=vel, gain=gain, pan=pan, release=1.5)
        return t + n * step

    def chorale(self, t0, t1, prog, lanes=None, vel=0.72, gain=0.42, timp=True, strings=True):
        """a brass chorale over a progression, spread evenly over t0..t1 (strings doubling, timpani on the
        first and the last chord)"""
        lanes = lanes or [(29, 40, 0, "tba_sus"), (40, 52, 2, "tbn_sus"), (50, 62, 0, "tbn_sus"),
                          (55, 67, 1, "hn_sus"), (60, 70, 2, "hn_sus")]
        seg = (t1 - t0) / len(prog)
        for j, ch in enumerate(prog):
            tt = t0 + j * seg
            if strings:
                self.pad(tt, tt + seg + 0.4, ch, vel=vel, gain=0.55, attack=0.25)
            pcs = chord_pcs(ch)
            for k, (lo, hi, deg, inst) in enumerate(lanes):
                self.p.note(inst, in_range(pcs[min(deg, len(pcs) - 1)], lo, hi), tt, seg * 0.96, vel=vel, gain=gain,
                            pan=-0.3 + 0.15 * k, attack=0.05, release=0.6)
            if timp:
                self.timp(tt, ch[0], vel=0.8 if j in (0, len(prog) - 1) else 0.55)
        return seg

    def ostinato(self, t0, t1, root, pattern, beat, insts=("vc_pizz",), vel=(0.55, 0.35), gain=0.42, accent_every=None,
                 accent_fx=None):
        """a repeated figure (semitones over `root`) until t1; instruments alternate per bar of the pattern"""
        t, j = t0, 0
        n = len(pattern)
        while t < t1 - 0.05:
            inst = insts[(j // n) % len(insts)]
            self.p.note(inst, root + pattern[j % n], t, 0.25, vel=vel[0] if j % n == 0 else vel[1], gain=gain,
                        pan=-0.1 if j % 2 else 0.1, release=0.3)
            if accent_fx and accent_every and j % accent_every == 0:
                self.fx(accent_fx, t, gain=0.12, pan=0.5, bus="perc")
            t += beat
            j += 1

    def melody(self, t, notes, inst="fl_sus", vel=0.4, gain=0.4, pan=0.25, bend=0.0, detune_double=0.0,
               attack=0.12, bus=None):
        """[(midi, seconds), ...]; bend: every note sinks while held; detune_double adds an out-of-tune twin"""
        tt = t
        for n_, d_ in notes:
            if n_ is not None:
                self.p.note(inst, n_, tt, d_, vel=vel, gain=gain, pan=pan, attack=attack, bend=bend, bus=bus)
                if detune_double:
                    self.p.note(inst, n_, tt + 0.04, d_, vel=vel * 0.85, gain=gain * 0.5, pan=-pan, attack=attack,
                                detune=detune_double, bend=bend * 1.5, bus=bus)
            tt += d_
        return tt

    def music_box(self, t, tune, step=0.38, slow=0.025, flat=0.04, inst="glock", double="vln_pizz", gain=0.3):
        """a tune that runs down: every note later and flatter than the last"""
        tt = t
        for j, n_ in enumerate(tune):
            self.p.note(inst, n_, tt, 0.7, vel=0.4, gain=gain, pan=0.3, detune=-flat * j)
            if double:
                self.p.note(double, n_ - 24 if n_ - 24 >= 55 else n_ - 12, tt, 0.3, vel=0.35, gain=gain, pan=-0.2,
                            detune=-flat * 0.75 * j)
            tt += step + slow * j
        return tt

    # -- percussion ----------------------------------------------------------------------------------------
    def timp(self, t, root_pc, vel=0.7, roll=None, lo=38, hi=49):
        """timpani on the pitch class (D2–F3 by default); roll: seconds of a roll instead of a stroke"""
        m = in_range(root_pc, lo, hi, (lo + hi) // 2)
        g = 1.0 / (0.35 + 0.65 * vel)  # undo the velocity scaling of the samplers: the stroke itself is louder
        if roll:
            self.p.note("timp_roll", m, t, roll, vel=vel, gain=0.55 * vel * g, pan=-0.1, release=0.8)
        else:
            self.p.note("timp", m, t, 0.3, vel=vel, gain=0.7 * vel * g, pan=-0.1, release=3.0)

    def heartbeat(self, t0, t1, gain=0.35, pattern=(1.9, 2.3, 1.7, 2.6)):
        """a soft bass drum, long-short, irregular — a pulse that is not a tempo"""
        t, k = t0, 0
        while t < t1:
            self.fx("bd_soft", t, gain=gain, bus="perc")
            self.fx("bd_soft", t + 0.28, gain=gain * 0.6, bus="perc")
            t += pattern[k % len(pattern)]
            k += 1

    def march(self, t0, t1, key=10, bpm=116, gain=0.45, sour=0.0, detune=0.0, tune=None):
        """a cheerful parade march; sour: semitones it slides down per round of the tune; detune: the second
        trumpet out of tune"""
        beat = 60.0 / bpm
        tune = tune or [(7, 1), (12, 1), (16, 1), (19, 1), (21, 1.5), (19, .5), (16, 1), (12, 2), (14, 1), (16, 1),
                        (17, 1), (14, 1), (19, 3), (None, 1),
                        (7, 1), (12, 1), (16, 1), (19, 1), (24, 1.5), (23, .5), (21, 1), (19, 2), (17, 1), (16, 1),
                        (14, 1), (11, 1), (12, 3), (None, 1)]
        bass = [0, 7, 0, 7, 5, 0, 7, 7]
        t, slide = t0, 0.0
        while t < t1 - beat:
            for n_, d_ in tune:
                if t >= t1 - beat:
                    break
                if n_ is not None:
                    base = in_range(key, 55, 66) + n_ - 12 - slide
                    self.p.note("tpt_sus", base, t, d_ * beat * 0.9, vel=0.62, gain=gain * 0.75, pan=-0.15, bus="parade",
                                release=0.25)
                    if detune:
                        self.p.note("tpt_sus", base, t + 0.02, d_ * beat * 0.9, vel=0.55, gain=gain * 0.45, pan=0.2,
                                    bus="parade", release=0.25, detune=detune)
                    self.p.note("glock", in_range(n_ + key, 79, 96) - slide, t, 0.6, vel=0.5, gain=gain * 0.35, pan=0.4)
                t += d_ * beat
            slide += sour
        t, k = t0, 0
        while t < t1 - beat * 0.5:
            if k % 4 in (0, 2):
                self.fx("bd", t, gain=gain * 0.55, bus="perc")
                self.p.note("tba_sus", in_range(key + bass[(k // 2) % 8], 33, 45), t, beat * 0.8, vel=0.55,
                            gain=gain * 0.6, pan=-0.3, bus="parade", release=0.2)
            else:
                self.fx("snare", t, gain=gain * 0.45, pan=0.1, bus="perc")
                for d, pn in ((4, 0.25), (7, 0.3)):
                    self.p.note("hn_sus", in_range(key + d, 55, 66), t, beat * 0.5, vel=0.45, gain=gain * 0.33, pan=pn,
                                bus="parade", release=0.15)
            self.fx("sleigh", t + beat / 2, gain=gain * 0.18, pan=0.5, bus="perc", dur=0.3)
            t += beat
            k += 1

    # -- the uncanny ---------------------------------------------------------------------------------------
    def spores(self, t, dur, density=30, gain=0.22, lib=None, curve="decay2"):
        """a granular cloud of harp, glockenspiel, pizzicato and bubbles on a quarter-tone scale, thinning out"""
        self.p.grains(fxcat.grain_sources(lib or self.lib), t, t + dur, density, gain=gain, bus="spores",
                      pitch=QUARTER, curve=curve)

    def breath(self, t, dur, gain=0.5):
        """something enormous breathes: double bass and tuba far below their range, swelling and sinking"""
        self.p.note("cb_sus", 14, t, dur, vel=0.7, gain=gain, pan=-0.1, bus="deep", attack=dur * 0.45, release=2.5,
                    bend=-2.0)
        self.p.note("tba_sus", 17, t + 0.4, dur * 0.8, vel=0.6, gain=gain * 0.6, pan=0.15, bus="deep", attack=dur * 0.4,
                    release=2.0, bend=-1.5, detune=0.3)

    def shepard(self, t0, t1, up=False, gain=0.35, period=7.0, inst="org_quiet"):
        """an endless glissando (overlapping organ voices gliding three octaves each)"""
        t, k = t0 - period * 0.6, 0
        while t < t1:
            start, span = (48, 36) if up else (84, -36)
            st = max(t, t0)
            cut = st - t
            dur = period * 3 - cut
            if dur > 1:
                self.p.note(inst, start + span * (cut / (period * 3)), st, min(dur, t1 - st + 1.5), vel=0.5, gain=gain,
                            pan=-0.4 + 0.27 * (k % 4), bus="deep", attack=min(period * 1.2, dur * 0.4), release=2.0,
                            bend=span * (1 - cut / (period * 3)))
            t += period
            k += 1

    def buzz(self, t, dur, notes=(76, 80, 84), gain=0.25, rates=(53.0, 61.0, 71.0)):
        """a swarm, not a section: tremolo violins through a ring modulator"""
        for j, n_ in enumerate(notes):
            self.p.note("vln_trem", n_, t + 0.15 * j, dur, vel=0.5, gain=gain, pan=-0.5 + 0.5 * j, bus="buzz", attack=0.8,
                        release=1.0, ringmod=rates[j % len(rates)], detune=0.25 * (j - 1))

    def swell(self, t_end, inst="org_quiet", midi_=62, dur=2.2, gain=0.3):
        """a reversed note swelling into t_end"""
        self.p.note(inst, midi_, t_end - dur, dur, vel=0.5, gain=gain, reverse=True)


__all__ = ["Composer", "MIN", "MAJ"]
