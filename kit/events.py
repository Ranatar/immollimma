"""A piece is a list of events, not audio. The score code writes events; render.py turns them into sound,
export.py into MIDI / MusicXML / PDF, qa.py checks them. Times are in seconds.

  note    an instrument (instruments.INSTR) at a MIDI pitch (fractions allowed) with the transformations of
          the samplers: detune (semitones), bend (glissando over the note, semitones), ringmod (Hz),
          reverse
  sample  a raw recording (noises, percussion), path with {VSCO}/{SSO} placeholders
  grains  a granular cloud cut from a list of recordings (paths with placeholders), deterministic by seed
  mark    a label in the timeline (sections, cues) — for reports and notation rehearsal marks
"""
import json
import random

from .instruments import INSTR

CURVES = {  # density shapes for grains, x in 0..1
    "flat": lambda x: 1.0,
    "decay2": lambda x: (1 - x) ** 2 + 0.05,
    "rise": lambda x: x * x + 0.05,
    "bell": lambda x: 4 * x * (1 - x) + 0.05,
}


class Piece:
    def __init__(self, title="untitled", bpm=60.0, meter=(4, 4), key=None, seed=1):
        self.title = title
        self.bpm = float(bpm)
        self.meter = tuple(meter)
        self.key = key
        self.events = []
        self.rng = random.Random(seed)
        self.meta = {}

    # -- time ----------------------------------------------------------------------------------------------
    def b(self, beats):
        """beats → seconds at the piece's tempo"""
        return beats * 60.0 / self.bpm

    def bar(self, n, beat=0.0):
        """start of bar n (from 0) plus beats → seconds"""
        return self.b(n * self.meter[0] * 4.0 / self.meter[1] + beat)

    # -- events --------------------------------------------------------------------------------------------
    def note(self, inst, midi, t, dur, vel=0.6, gain=1.0, pan=None, bus=None, attack=0.0, release=0.6,
             detune=0.0, bend=0.0, ringmod=0.0, reverse=False, part=None, art=None):
        if inst not in INSTR:
            raise KeyError(f"unknown instrument {inst!r}; see kit/instruments.py")
        e = dict(kind="note", inst=inst, midi=float(midi), t=float(t), dur=float(dur), vel=float(vel),
                 gain=float(gain), pan=0.0 if pan is None else float(pan), bus=bus or INSTR[inst]["bus"],
                 attack=float(attack), release=float(release), detune=float(detune), bend=float(bend),
                 ringmod=float(ringmod), reverse=bool(reverse), part=part or INSTR[inst]["part"])
        if art:
            e["art"] = art  # a notation mark: 'staccato', 'accent', 'tremolo', 'pizz', 'harmonic', ...
        self.events.append(e)
        return e

    def chord(self, inst, notes, t, dur, spread=0.012, **kw):
        return [self.note(inst, m, t + spread * i, dur, **kw) for i, m in enumerate(notes)]

    def line(self, inst, notes, t, legato=0.95, **kw):
        """notes: [(midi or None for a rest, beats), ...] at the piece's tempo; returns the end time"""
        for m, beats in notes:
            d = self.b(beats)
            if m is not None:
                self.note(inst, m, t, d * legato, **kw)
            t += d
        return t

    def sample(self, path, t, gain=1.0, pan=0.0, bus="fx", shift=0.0, bend=0.0, dur=None, reverse=False,
               ringmod=0.0, attack=0.0, fade=0.8):
        e = dict(kind="sample", path=path, t=float(t), gain=float(gain), pan=float(pan), bus=bus,
                 shift=float(shift), bend=float(bend), dur=None if dur is None else float(dur),
                 reverse=bool(reverse), ringmod=float(ringmod), attack=float(attack), fade=float(fade))
        self.events.append(e)
        return e

    def grains(self, sources, t0, t1, density, gain=0.3, bus="spores", pitch=(0.0,), grain=(0.04, 0.18),
               spread=1.0, curve="flat", seed=None):
        e = dict(kind="grains", sources=list(sources), t=float(t0), t1=float(t1), density=float(density),
                 gain=float(gain), bus=bus, pitch=list(pitch), grain=list(grain), spread=float(spread),
                 curve=curve, seed=self.rng.randrange(1 << 30) if seed is None else int(seed))
        self.events.append(e)
        return e

    def mark(self, t, label, **info):
        e = dict(kind="mark", t=float(t), label=label, **info)
        self.events.append(e)
        return e

    def balance(self, db_by_part):
        """after composing: raise or lower whole parts (dB), e.g. {"Celesta": +10, "Clarinet": -6}; measure first
        with `python3 -m kit run piece.py --parts` (perceived loudness of each part alone)"""
        for e in self.events:
            if e["kind"] == "note" and e["part"] in db_by_part:
                e["gain"] *= 10 ** (db_by_part[e["part"]] / 20)
        self.meta.setdefault("balance", {}).update(db_by_part)
        return self

    # -- views ---------------------------------------------------------------------------------------------
    def end(self):
        out = 0.0
        for e in self.events:
            if e["kind"] == "note":
                out = max(out, e["t"] + e["dur"] + e["release"])
            elif e["kind"] == "grains":
                out = max(out, e["t1"])
            elif e["kind"] == "sample":
                out = max(out, e["t"] + (e["dur"] or 2.0))
        return out

    def notes(self):
        return [e for e in self.events if e["kind"] == "note"]

    def window(self, t0, t1, pad=8.0):
        """events that sound inside [t0, t1] (a note that began up to pad seconds earlier still rings)"""
        out = []
        for e in self.events:
            a = e["t"]
            if e["kind"] == "note":
                b = a + e["dur"] + e["release"]
            elif e["kind"] == "grains":
                b = e["t1"]
            elif e["kind"] == "sample":
                b = a + (e["dur"] if e["dur"] is not None else pad)
            else:
                b = a
            if b >= t0 and a <= t1:
                out.append(e)
        return out

    # -- storage -------------------------------------------------------------------------------------------
    def to_json(self, path):
        json.dump(dict(title=self.title, bpm=self.bpm, meter=list(self.meter), key=self.key, meta=self.meta,
                       events=self.events), open(path, "w"), ensure_ascii=False)

    @classmethod
    def from_json(cls, path):
        d = json.load(open(path))
        p = cls(d.get("title", "untitled"), d.get("bpm", 60), d.get("meter", (4, 4)), d.get("key"))
        p.events = d["events"]
        p.meta = d.get("meta", {})
        return p
