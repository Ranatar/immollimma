"""Events → buses → WAV. A note is played by the first library available for its instrument in the order
of the chosen backend (instruments.ORDER): plain sampler over raw VSCO, or sfizz over VSCO's or Sonatina's
SFZ. The result records which library played what, so substitutions and licences are visible."""
import collections
import json
import os
import random

import numpy as np

from . import mix as mixer
from .events import CURVES
from .instruments import INSTR, LICENSES, sources
from .paths import expand, status
from .sampler import SR, Sampler


class Renderer:
    def __init__(self, seconds, backend="plain", seed=7):
        self.backend = backend
        self.plain = Sampler(seconds, seed)
        self.n = self.plain.n
        self.buses = self.plain.buses
        self.seed = seed
        self.sfz = {}
        st = status()
        self.have = {"plain": st["VSCO-2-CE samples"],
                     "vsco": st["VSCO SFZ files"] and st["VSCO-2-CE samples"] and st["libsfizz"],
                     "sso": st["Sonatina (SSO)"] and st["libsfizz"]}
        self.used = collections.Counter()  # (inst, lib)
        self.missing = collections.Counter()

    def engine(self, lib):
        if lib == "plain":
            return self.plain
        if lib not in self.sfz:
            from .sfz_engine import SfzSampler
            e = SfzSampler(self.n / SR - 12, lib, self.seed)
            e.buses = self.buses  # one set of buses for every engine
            e.n = self.n
            self.sfz[lib] = e
        return self.sfz[lib]

    def note(self, e, t):
        for lib in sources(e["inst"], self.backend):
            if self.have[lib]:
                self.used[(e["inst"], lib)] += 1
                self.engine(lib).note(e["inst"], e["midi"], t, e["dur"], vel=e["vel"], gain=e["gain"], pan=e["pan"],
                                      bus=e["bus"], attack=e["attack"], release=e["release"], detune=e["detune"],
                                      bend=e["bend"], ringmod=e["ringmod"], reverse=e["reverse"])
                return
        self.missing[e["inst"]] += 1

    def play(self, events, t0=0.0):
        for e in sorted(events, key=lambda x: x["t"]):
            t = e["t"] - t0
            k = e["kind"]
            if k == "note":
                self.note(e, t)
            elif k == "sample":
                p = expand(e["path"])
                if os.path.exists(p):
                    self.plain.sample(p, t, gain=e["gain"], pan=e["pan"], bus=e["bus"], shift=e["shift"], bend=e["bend"],
                                      dur=e["dur"], reverse=e["reverse"], ringmod=e["ringmod"], attack=e["attack"],
                                      fade=e["fade"])
                    self.used[("sample", "plain" if "{VSCO}" in e["path"] else "sso")] += 1
                else:
                    self.missing["sample:" + os.path.basename(p)] += 1
            elif k == "grains":
                src = [expand(s) for s in e["sources"]]
                src = [s for s in src if os.path.exists(s)]
                if not src:
                    self.missing["grains"] += 1
                    continue
                self.plain.rng = random.Random(e["seed"])
                self.plain.grains(src, t, e["t1"] - t0, e["density"], gain=e["gain"], bus=e["bus"], pitch=e["pitch"],
                                  grain=tuple(e["grain"]), spread=e["spread"], curve=CURVES[e.get("curve", "flat")])
                self.used[("grains", "plain")] += 1

    def report(self):
        libs = sorted({lib for (_, lib) in self.used})
        subst = {}
        for (inst, lib), n in self.used.items():
            if inst in INSTR:
                first = sources(inst, self.backend)
                if first and first[0] != lib:
                    subst[inst] = f"{first[0]} unavailable → {lib}"
        return dict(backend=self.backend, libraries=libs, licenses=sorted({LICENSES[x] for x in libs if x in LICENSES}),
                    by_instrument={f"{i}@{lib}": n for (i, lib), n in sorted(self.used.items())},
                    substitutions=subst, missing=dict(self.missing),
                    sfizz_notes=sum(e.notes_rendered for e in self.sfz.values()),
                    lengthened=sum(e.extended for e in self.sfz.values()))


def render(piece, out_wav, backend="plain", t0=0.0, t1=None, sends=None, gains=None, ref_buses=None,
           stems_dir=None, seed=7, master_db=-1.0):
    """render the piece (or the window t0..t1) to a WAV; returns a report dict.
    ref_buses: a .buses.json of another rendering — every bus is scaled to it (same mix, other library)."""
    full = t1 is None and t0 == 0.0
    t1 = piece.end() if t1 is None else t1
    seconds = t1 - t0
    events = piece.events if full else piece.window(t0, t1)
    r = Renderer(seconds + 4, backend, seed)
    r.play(events, t0)
    stats = {k: float(np.sqrt((b ** 2).mean())) for k, b in r.buses.items()}
    if ref_buses:
        ref = json.load(open(ref_buses))
        for k, b in r.buses.items():
            if ref.get(k) and stats[k] > 0:
                b *= ref[k] / stats[k]
    json.dump(stats, open(os.path.splitext(out_wav)[0] + ".buses.json", "w"), indent=1)
    s = dict(piece.meta.get("sends", {}), **(sends or {}))
    g = dict(piece.meta.get("gains", {}), **(gains or {}))
    mixer.mix(r.buses, seconds + (2.0 if full else 0.0), out_wav, sends=s, gains=g, master_db=master_db,
              fade_in=0.0 if full else 0.3, fade_out=3.0 if full else 0.5, stems_dir=stems_dir)
    rep = r.report()
    rep.update(window=[t0, t1], seconds=seconds)
    return rep
