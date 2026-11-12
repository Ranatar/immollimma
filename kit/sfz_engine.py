"""Notes played through sfizz (the SFZ engine) from a library's own SFZ mapping (filters, loops, envelopes,
velocity zones), then transformed like the plain sampler does it: detune, glissando, reverse, ring
modulation, envelope, placement on a bus.
"""
import collections
import ctypes
import json
import os

import numpy as np

from .instruments import INSTR, KNOWN_OFFSET
from .paths import DATA, SFIZZ_LIB, SSO, VSCO_SFZ
from .sampler import SR, Sampler


def sfz_path(lib, name):
    return os.path.join(VSCO_SFZ if lib == "vsco" else SSO, name + ".sfz")


def load_calib():
    p = os.path.join(DATA, "calib.json")
    return json.load(open(p)) if os.path.exists(p) else {}


class Sfizz:
    """one libsfizz synth with one instrument loaded"""
    _lib = None

    def __init__(self, path):
        if Sfizz._lib is None:
            L = ctypes.CDLL(SFIZZ_LIB)
            L.sfizz_create_synth.restype = ctypes.c_void_p
            for f, args in [("sfizz_free", [ctypes.c_void_p]),
                            ("sfizz_set_sample_rate", [ctypes.c_void_p, ctypes.c_float]),
                            ("sfizz_set_samples_per_block", [ctypes.c_void_p, ctypes.c_int]),
                            ("sfizz_enable_freewheeling", [ctypes.c_void_p]),
                            ("sfizz_all_sound_off", [ctypes.c_void_p]),
                            ("sfizz_send_note_on", [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int]),
                            ("sfizz_send_note_off", [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int]),
                            ("sfizz_render_block", [ctypes.c_void_p, ctypes.POINTER(ctypes.POINTER(ctypes.c_float)),
                                                    ctypes.c_int, ctypes.c_int])]:
                getattr(L, f).argtypes = args
                getattr(L, f).restype = None
            L.sfizz_load_file.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
            L.sfizz_load_file.restype = ctypes.c_bool
            L.sfizz_get_num_regions.argtypes = [ctypes.c_void_p]
            L.sfizz_get_num_regions.restype = ctypes.c_int
            Sfizz._lib = L
        L = self.L = Sfizz._lib
        self.block = 512
        self.s = L.sfizz_create_synth()
        L.sfizz_set_sample_rate(self.s, float(SR))
        L.sfizz_set_samples_per_block(self.s, self.block)
        L.sfizz_enable_freewheeling(self.s)
        if not L.sfizz_load_file(self.s, path.encode()):
            raise RuntimeError("sfizz could not load " + path)
        self.regions = L.sfizz_get_num_regions(self.s)
        self.buf = np.zeros((2, self.block), np.float32)
        fp = ctypes.POINTER(ctypes.c_float)
        self.ptrs = (fp * 2)(self.buf[0].ctypes.data_as(fp), self.buf[1].ctypes.data_as(fp))
        self.range = None

    def render(self, key, vel, hold, total):
        """frames: note on at 0, off after `hold`, `total` frames in all → (total, 2) float32"""
        L = self.L
        L.sfizz_all_sound_off(self.s)
        for _ in range(2):  # flush whatever the reset left
            L.sfizz_render_block(self.s, self.ptrs, 2, self.block)
        out = np.zeros((total, 2), np.float32)
        pos = 0
        on_sent = off_sent = False
        while pos < total:
            if not on_sent:
                L.sfizz_send_note_on(self.s, 0, key, vel)
                on_sent = True
            if not off_sent and hold < pos + self.block:
                L.sfizz_send_note_off(self.s, max(0, hold - pos), key, 0)
                off_sent = True
            L.sfizz_render_block(self.s, self.ptrs, 2, self.block)
            n = min(self.block, total - pos)
            out[pos:pos + n] = self.buf[:, :n].T
            pos += self.block
        return out

    def find_range(self):
        """keys that sound (probe each key once, short)"""
        if self.range is None:
            ok = []
            for k in range(12, 109):
                y = self.render(k, 100, int(0.12 * SR), int(0.25 * SR))
                if np.abs(y).max() > 1e-4:
                    ok.append(k)
            self.range = ok
        return self.range


class SfzSampler(Sampler):
    """lib: 'vsco' or 'sso'. calib.json gives per instrument: gain (level matched to the plain sampler at
    mezzo-forte), offset (sounding pitch minus key) and the keys that sound."""

    def __init__(self, seconds, lib, seed=7, calib=None):
        super().__init__(seconds, seed)
        self.lib = lib
        self.synths = {}
        self.ncache = collections.OrderedDict()
        c = (calib if calib is not None else load_calib()).get(lib, {})
        self.gain_of = {k: v.get("gain", 1.0) for k, v in c.items()}
        self.offset_of = {k: v.get("offset", 0) for k, v in c.items()}
        for (lb, inst), off in KNOWN_OFFSET.items():
            if lb == lib:
                self.offset_of.setdefault(inst, off)
        self.keys = (calib if calib is not None else load_calib()).get("keys", {}).get(lib, {})
        self.notes_rendered = 0
        self.extended = 0

    def synth(self, name):
        if name not in self.synths:
            self.synths[name] = Sfizz(sfz_path(self.lib, name))
            if self.keys.get(name):
                self.synths[name].range = self.keys[name]  # measured by tools/calibrate.py
        return self.synths[name]

    def choose(self, inst, midi):
        """the instrument file and key for a wanted (sounding) pitch; outside the range: the nearest key,
        resampled"""
        midi = midi - self.offset_of.get(inst, 0)
        best = None
        for name in INSTR[inst][self.lib]:
            s = self.synth(name)
            rng = s.find_range()
            if not rng:
                continue
            k = min(rng, key=lambda x: abs(x - midi))
            if best is None or abs(k - midi) < abs(best[1] - midi):
                best = (s, k)
            if abs(k - midi) < 0.5:
                break
        return best

    def dry(self, inst, key_synth, key, vel, hold, total):
        ck = (inst, id(key_synth), key, vel, hold // 2205, total // 2205)
        if ck in self.ncache:
            self.ncache.move_to_end(ck)
            y = self.ncache[ck]
            if len(y) >= total:
                return y[:total]
        y = key_synth.render(key, vel, hold, total)
        self.notes_rendered += 1
        self.ncache[ck] = y
        while len(self.ncache) > 400:
            self.ncache.popitem(last=False)
        return y

    def extend(self, d, hold, need):
        """a sustained note that dies before its note-off (a recording without a loop shorter than the note):
        lengthened the way the plain sampler does it, with crossfaded repeats of the body of the recording"""
        env = np.abs(d[:hold]).max(1)
        peak = env.max() + 1e-12
        alive = np.nonzero(env > peak * 0.06)[0]
        end = int(alive[-1]) if len(alive) else 0
        if end > hold - int(0.3 * SR) or end < int(1.0 * SR):
            return d
        self.extended += 1
        body = d[:end - int(0.25 * SR)]
        b0, xf = int(0.35 * len(body)), int(0.6 * SR)
        out = body
        while len(out) < need:
            seg = body[b0:]
            w = np.linspace(0, 1, xf, dtype=np.float32)[:, None]
            out = np.concatenate([out[:-xf], out[-xf:] * (1 - w) + seg[:xf] * w, seg[xf:]])
        return out[:need]

    def note(self, art, midi, t, dur, vel=0.6, gain=1.0, pan=0.0, bus="main", attack=0.0, release=0.6,
             detune=0.0, bend=0.0, ringmod=0.0, reverse=False):
        s, key = self.choose(art, int(round(midi)))
        r0 = 2 ** ((midi - self.offset_of.get(art, 0) - key + detune) / 12.0)
        n_out = int((dur + release) * SR)
        k = int(dur * SR)
        if bend:
            tt = np.minimum(np.arange(n_out) / max(1, k), 1.0)
            ratio = r0 * 2 ** (bend * tt / 12.0)
        else:
            ratio = np.full(n_out, r0)
        pos = np.concatenate([[0.0], np.cumsum(ratio[:-1])])
        need = int(pos[-1]) + 8
        hold = int(pos[min(k, n_out - 1)]) if k < n_out else need
        mvel = max(1, min(127, int(round(1 + 126 * vel))))
        d = self.dry(art, s, key, mvel, hold, need)
        if not INSTR[art]["short"] and hold > int(1.5 * SR):
            d = self.extend(d, hold, need)
        if reverse:
            d = d[::-1].copy()
            # a reversed swell ends where the recording began: drop the silence the reversal brought to the front
            e = np.abs(d).max(1)
            j = int(np.argmax(e > e.max() * 0.01))
            d = np.concatenate([d[j:], np.zeros((j, 2), np.float32)])
        y = np.stack([np.interp(pos, np.arange(len(d)), d[:, c]) for c in range(2)], 1).astype(np.float32)
        if ringmod:
            y *= (0.35 + 0.65 * np.sin(2 * np.pi * ringmod * np.arange(n_out) / SR)).astype(np.float32)[:, None]
        env = np.ones(n_out, np.float32)
        a = min(n_out, int(attack * SR))
        if a > 1:
            env[:a] = np.linspace(0, 1, a) ** 1.5
        if k < n_out:
            env[k:] = np.exp(-np.linspace(0, 6, n_out - k)).astype(np.float32)
        y *= env[:, None]
        self.place(y, t, bus, gain * (0.35 + 0.65 * vel) * self.gain_of.get(art, 1.0), pan)
