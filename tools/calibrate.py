#!/usr/bin/env python3
"""Measure every instrument of kit/instruments.py in each SFZ library and write kit/data/calib.json:

  keys    the keys that sound, per SFZ file (the engine does not have to probe them again)
  offset  sounding pitch minus key (pYIN), rounded to whole octaves when it is near one
  gain    level that matches the reference instrument played by the plain sampler at mezzo-forte
          (the same instrument if the plain sampler has it, otherwise its nearest relative, REF)

  python3 tools/calibrate.py [--only inst,inst] [--libs vsco,sso]
"""
import argparse
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from kit.instruments import INSTR, KNOWN_OFFSET  # noqa: E402
from kit.paths import DATA  # noqa: E402
from kit.sampler import SR, Sampler  # noqa: E402
from kit.sfz_engine import SfzSampler  # noqa: E402

# the plain-sampler instrument a level is matched to when the plain sampler lacks the instrument itself
REF = {"vln_spic": "vln_pizz", "vln_leg": "vln_sus", "vln_harm": "vln_sus", "vln_colleg": "vln_pizz", "vln_solo": "vln_sus",
       "vla_spic": "vla_pizz", "vla_leg": "vla_sus", "vla_harm": "vla_sus", "vc_spic": "vc_pizz", "vc_leg": "vc_sus",
       "vc_harm": "vc_sus", "vc_colleg": "vc_pizz", "cb_leg": "cb_sus", "hn_stac": "hn_sus", "hn_leg": "hn_sus",
       "hns_sus": "hn_sus", "tpt_harmon": "tpt_mute", "tpt_stac": "tpt_sus", "tpt_leg": "tpt_sus", "tbn_stac": "tbn_sus",
       "tbn_leg": "tbn_sus", "btbn_sus": "tbn_sus", "tba_stac": "tba_sus", "picc_sus": "fl_sus", "fl_vib": "fl_sus",
       "fl_stac": "fl_sus", "fl_leg": "fl_sus", "afl_sus": "fl_sus", "ob_stac": "ob_sus", "ob_leg": "ob_sus",
       "eh_sus": "ob_sus", "cl_stac": "cl_sus", "cl_leg": "cl_sus", "bcl_sus": "cl_sus", "bsn_stac": "bsn_sus",
       "cbsn_sus": "bsn_sus", "xylo": "glock", "marimba": "harp", "tubular": "glock", "celesta": "glock", "vibes": "glock",
       "crotales": "glock", "piano": "harp", "hpsd": "harp", "org_reed": "org_quiet", "choir": "vla_sus"}
UNPITCHED_OK = {"timp", "timp_roll"}  # pYIN hears timpani an octave low: trust the SFZ


def f0(y):
    import librosa
    m = y.mean(1)[int(0.2 * SR):int(1.4 * SR)].astype(np.float32)
    f, v, _ = librosa.pyin(m, fmin=25, fmax=4200, sr=SR, frame_length=4096)
    f = f[v] if v.any() else np.array([])
    return None if len(f) < 5 else float(69 + 12 * np.log2(np.median(f) / 440))


def grab(s, inst, midi, dur=1.6):
    s.buses.clear()
    s.note(inst, midi, 0.0, dur, vel=0.6, bus="x", release=0.3)
    b = s.buses.get("x")
    return np.zeros((int(2 * SR), 2), np.float32) if b is None else b[:int(2.0 * SR)].copy()


def rms(y, win=None):
    """level of a note: over 2 s for sustained sounds, over the first 0.35 s when a short sound is involved
    (otherwise a staccato would be matched to a whole held note and come out far too loud)"""
    if win:
        e = np.abs(y).max(1)
        k = int(np.argmax(e > e.max() * 0.05)) if e.max() > 0 else 0
        y = y[k:k + int(win * SR)]
    return float(np.sqrt((y ** 2).mean()) + 1e-12)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only")
    ap.add_argument("--libs", default="vsco,sso")
    a = ap.parse_args()
    path = os.path.join(DATA, "calib.json")
    old = json.load(open(path)) if os.path.exists(path) else {}
    plain = Sampler(4)
    only = set(a.only.split(",")) if a.only else None
    t0 = time.time()
    for lib in a.libs.split(","):
        res = old.get(lib, {})
        keys = old.get("keys", {}).get(lib, {})
        eng = SfzSampler(4, lib, calib={})
        for inst, e in INSTR.items():
            if not e[lib] or (only and inst not in only):
                continue
            ranges = []
            for name in e[lib]:
                s = eng.synth(name)
                keys[name] = s.find_range()
                ranges += keys[name]
            if not ranges:
                print(f"{lib:4} {inst:11} silent — check the SFZ", flush=True)
                continue
            # offset: measure at two keys inside the range (sounding pitch minus key)
            lo, hi = min(ranges), max(ranges)
            off = KNOWN_OFFSET.get((lib, inst))
            if off is None and inst not in UNPITCHED_OK:
                eng.offset_of[inst] = 0
                meas = []
                for k in (lo + (hi - lo) // 3, lo + 2 * (hi - lo) // 3):
                    p = f0(grab(eng, inst, k))
                    if p is not None:
                        meas.append(p - k)
                if len(meas) == 2 and abs(meas[0] - meas[1]) < 0.6:
                    d = float(np.mean(meas))
                    k12 = round(d / 12) * 12
                    off = int(k12) if abs(d - k12) < 0.6 else int(round(d))
                else:
                    off = 0
            off = off or 0
            eng.offset_of[inst] = off
            # level against the reference played by the plain sampler, at two pitches both can reach
            ref = inst if e["plain"] else REF.get(inst)
            gain = 1.0
            if ref and INSTR[ref]["plain"]:
                rows = plain.idx[INSTR[ref]["plain"]]
                plo, phi = min(r["note"] for r in rows), max(r["note"] for r in rows)
                a_, b_ = max(plo, lo + off), min(phi, hi + off)
                mids = [(a_ + b_) // 2, a_ + (b_ - a_) // 4] if b_ > a_ else [(plo + phi) // 2]
                lp, li = [], []
                win = 0.35 if (e["short"] or INSTR[ref]["short"]) else None
                for m in mids:
                    lp.append(rms(grab(plain, INSTR[ref]["plain"], m), win))
                    li.append(rms(grab(eng, inst, m), win))
                gain = float(np.exp(np.mean(np.log(lp)) - np.mean(np.log(li))))
            res[inst] = dict(offset=off, gain=round(gain, 4), lo=lo + off, hi=hi + off, ref=ref)
            print(f"{lib:4} {inst:11} sounds {lo + off}-{hi + off}  offset {off:+d}  gain {gain:6.2f}  ref {ref}", flush=True)
        old[lib] = res
        old.setdefault("keys", {})[lib] = keys
    json.dump(old, open(path, "w"), indent=1)
    print("written", path, round(time.time() - t0), "s")


if __name__ == "__main__":
    main()
