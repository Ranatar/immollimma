"""The plain sampler: raw VSCO-2 CE recordings, indexed by measured pitch (data/index_vsco.json, made by
tools/index_samples.py), played by resampling from the nearest recorded note.

Notes are placed on stereo buses (float32, 44.1 kHz); each bus has its own reverb send.
Pitch is reached from the nearest recorded note by resampling (at most a few semitones away).
"""
import collections
import json
import os
import random

import numpy as np
import soundfile as sf

SR = 44100
from .paths import DATA, VSCO


class Sampler:
    def __init__(self, seconds, seed=7):
        self.idx = json.load(open(os.path.join(DATA, "index_vsco.json")))
        for rows in self.idx.values():
            for r in rows:
                r["path"] = os.path.join(VSCO, r["path"])
        self.n = int(seconds * SR) + SR * 12
        self.buses = {}
        self.cache = collections.OrderedDict()  # LRU: the whole library would not fit in memory
        self.rng = random.Random(seed)

    def bus(self, name):
        if name not in self.buses:
            self.buses[name] = np.zeros((self.n, 2), np.float32)
        return self.buses[name]

    def _load(self, path):
        if path in self.cache:
            self.cache.move_to_end(path)
        else:
            while len(self.cache) > 90:
                self.cache.popitem(last=False)
            d, sr = sf.read(path, always_2d=True, dtype="float32")
            if d.shape[1] == 1:
                d = np.repeat(d, 2, 1)
            if sr != SR:
                t = np.arange(0, len(d), sr / SR)
                d = np.stack([np.interp(t, np.arange(len(d)), d[:, c]) for c in range(2)], 1).astype(np.float32)
            # trim leading silence (keeps the attack on the beat)
            env = np.abs(d).max(1)
            k = int(np.argmax(env > env.max() * 0.02))
            self.cache[path] = d[max(0, k - 64):]
        return self.cache[path]

    def pick(self, art, midi, vel):
        rows = self.idx[art]
        best = min(abs(r["note"] - midi) for r in rows)
        near = [r for r in rows if abs(r["note"] - midi) == best]
        vels = sorted({r["vel"] for r in near})
        want = vels[min(len(vels) - 1, int(round(vel * (len(vels) - 1))))]
        cand = [r for r in near if r["vel"] == want]
        return self.rng.choice(cand)

    def note(self, art, midi, t, dur, vel=0.6, gain=1.0, pan=0.0, bus="main", attack=0.0, release=0.6,
             detune=0.0, bend=0.0, ringmod=0.0, reverse=False):
        """detune: semitones (fractions = cents); bend: pitch drift in semitones over the note (glissando);
        ringmod: Hz of a ring modulator (insect buzz); reverse: play the sample backwards (a swell)."""
        r = self.pick(art, midi, vel)
        d = self._load(r["path"])
        if reverse:
            d = d[::-1].copy()
        r0 = 2 ** ((midi - r["note"] + detune) / 12.0)
        n_out = int((dur + release) * SR)
        if bend:
            tt = np.minimum(np.arange(n_out) / max(1, int(dur * SR)), 1.0)
            ratio = r0 * 2 ** (bend * tt / 12.0)
        else:
            ratio = np.full(n_out, r0)
        pos = np.concatenate([[0.0], np.cumsum(ratio[:-1])])
        need = int(pos[-1]) + 8
        if need > len(d) and len(d) < 2.5 * SR:  # a short (plucked, struck) sample just rings out
            d = np.concatenate([d, np.zeros((need - len(d), 2), np.float32)])
        elif need > len(d):  # long note: crossfaded repeats of the body of the sample
            body0, xf = int(0.35 * len(d)), int(0.6 * SR)
            parts = [d]
            total = len(d)
            while total < need:
                seg = d[body0:].copy()
                parts.append(seg)
                total += len(seg) - xf
            out = parts[0]
            for seg in parts[1:]:
                w = np.linspace(0, 1, xf, dtype=np.float32)[:, None]
                out = np.concatenate([out[:-xf], out[-xf:] * (1 - w) + seg[:xf] * w, seg[xf:]])
            d = out
        src = d[:need]
        y = np.stack([np.interp(pos, np.arange(len(src)), src[:, c]) for c in range(2)], 1).astype(np.float32)
        if ringmod:
            y *= (0.35 + 0.65 * np.sin(2 * np.pi * ringmod * np.arange(n_out) / SR)).astype(np.float32)[:, None]
        env = np.ones(n_out, np.float32)
        a = min(n_out, int(attack * SR))
        if a > 1:
            env[:a] = np.linspace(0, 1, a) ** 1.5
        k = int(dur * SR)
        if k < n_out:
            env[k:] = np.exp(-np.linspace(0, 6, n_out - k)).astype(np.float32)
        y *= env[:, None]
        self.place(y, t, bus, gain * (0.35 + 0.65 * vel), pan)

    def place(self, y, t, bus, gain=1.0, pan=0.0):
        lp, rp = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
        y = y * np.array([lp, rp], np.float32) * (1.414 * gain)
        s = int(t * SR)
        b = self.bus(bus)
        if s < 0:
            y, s = y[-s:], 0
        e = min(len(b), s + len(y))
        if e > s:
            b[s:e] += y[:e - s]

    def sample(self, path, t, gain=1.0, pan=0.0, bus="fx", shift=0.0, bend=0.0, dur=None, reverse=False,
               ringmod=0.0, attack=0.0, fade=0.8):
        """a raw sample (effects, percussion): shift/bend in semitones, optional cut with a fade."""
        d = self._load(path)
        if reverse:
            d = d[::-1].copy()
        n_src = len(d)
        r0 = 2 ** (shift / 12)
        n_out = int(n_src / r0) if dur is None else int((dur + fade) * SR)
        if bend:
            tt = np.minimum(np.arange(n_out) / max(1, n_out), 1.0)
            ratio = r0 * 2 ** (bend * tt / 12)
        else:
            ratio = np.full(n_out, r0)
        pos = np.concatenate([[0.0], np.cumsum(ratio[:-1])])
        pos = pos[pos < n_src - 1]
        y = np.stack([np.interp(pos, np.arange(n_src), d[:, c]) for c in range(2)], 1).astype(np.float32)
        if dur is not None:
            k = int(dur * SR)
            if k < len(y):
                f = min(len(y) - k, int(fade * SR))
                y = y[:k + f]
                y[k:] *= np.linspace(1, 0, f, dtype=np.float32)[:, None]
        if attack:
            a = min(len(y), int(attack * SR))
            y[:a] *= np.linspace(0, 1, a, dtype=np.float32)[:, None] ** 1.5
        if ringmod:
            y *= (0.35 + 0.65 * np.sin(2 * np.pi * ringmod * np.arange(len(y)) / SR)).astype(np.float32)[:, None]
        self.place(y, t, bus, gain, pan)

    def grains(self, sources, t0, t1, density, gain=0.3, bus="spores", pitch=(0.0,), grain=(0.04, 0.18),
               spread=1.0, curve=None):
        """a cloud of short grains cut from the sources (paths); density in grains per second, optionally
        shaped by curve(x) for x in 0..1 over the cloud; pitch: semitone offsets to choose from."""
        rng = self.rng
        t = t0
        while t < t1:
            x = (t - t0) / max(1e-6, t1 - t0)
            dens = density * (curve(x) if curve else 1.0)
            if dens > 0.05:
                d = self._load(rng.choice(sources))
                gl = rng.uniform(*grain)
                n = int(gl * SR)
                if len(d) > n + 10:
                    s = rng.randrange(0, len(d) - n)
                    seg = d[s:s + n].copy()
                    r = 2 ** (rng.choice(pitch) / 12)
                    pos = np.arange(0, n - 1, r)
                    seg = np.stack([np.interp(pos, np.arange(n), seg[:, c]) for c in range(2)], 1).astype(np.float32)
                    w = np.hanning(len(seg)).astype(np.float32)[:, None]
                    self.place(seg * w, t, bus, gain * rng.uniform(0.5, 1.0), rng.uniform(-spread, spread))
            t += rng.expovariate(max(dens, 0.05))

    def chord(self, art, notes, t, dur, **kw):
        for i, m in enumerate(notes):
            self.note(art, m, t + 0.012 * i, dur, **kw)
