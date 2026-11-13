"""Rebuild kit/data/index_vsco.json — the plain sampler's index of raw VSCO-2 CE recordings: note (MIDI),
velocity layer, round robin, path relative to the VSCO folder. Needs librosa; ≈ 10 min.
The timpani rows ('timp', 'timp_roll') are added at the end with the drums' pitches from VSCO's own SFZ
(pYIN hears timpani an octave low, so they are not measured).
Note names are checked against measured pitch (pYIN); each articulation gets its octave offset."""
import glob, json, os, re, sys, collections
import numpy as np, soundfile as sf, librosa
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
V = os.environ.get("VSCO_DIR", os.path.join(ROOT, "libs", "VSCO-2-CE"))
ART = {  # name: (dir, glob)
 "vln_sus": "Strings/Violin Section/susVib", "vln_trem": "Strings/Violin Section/Trem", "vln_pizz": "Strings/Violin Section/Pizz",
 "vla_sus": "Strings/Viola Section/susvib", "vla_trem": "Strings/Viola Section/trem", "vla_pizz": "Strings/Viola Section/pizz",
 "vc_sus": "Strings/Cello Section/susvib", "vc_trem": "Strings/Cello Section/trem", "vc_pizz": "Strings/Cello Section/pizzT",
 "cb_sus": "Strings/Solo Contrabass/SusVib", "cb_trem": "Strings/Solo Contrabass/Trem", "cb_pizz": "Strings/Solo Contrabass/Pizz",
 "hn_sus": "Brass/F Horn/sus", "hn_mute": "Brass/F Horn/mute", "tbn_sus": "Brass/Tenor Trombone/sus", "tba_sus": "Brass/Tuba/sus",
 "tpt_sus": "Brass/Trumpet/sus", "tpt_mute": "Brass/Trumpet/straightM-sus",
 "fl_sus": "Woodwinds/Flute/susNV", "ob_sus": "Woodwinds/Oboe/Sus", "cl_sus": "Woodwinds/Clarinet/susLong", "bsn_sus": "Woodwinds/Bassoon/sus",
 "harp": "Strings/Harp", "glock": "Percussion/Glock", "org_loud": "Keys/Organ/Loud", "org_quiet": "Keys/Organ/Quiet",
}
NOTE = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
def parse(fn):
    m = re.search(r"_([A-G])(#|b)?(-?\d)(?=[_.])", fn)
    note = None
    if m:
        note = 12 * (int(m.group(3)) + 1) + NOTE[m.group(1)] + (1 if m.group(2) == "#" else -1 if m.group(2) == "b" else 0)
    v = re.search(r"_v(\d)", fn); rr = re.search(r"_(?:rr|RR)?(\d)(?:_\w+)?\.wav$", fn)
    return note, int(v.group(1)) if v else 1, rr.group(1) if rr else "1"
def measure(path):
    d, sr = sf.read(path, always_2d=True); d = d.mean(1)
    a = int(0.15 * sr); seg = d[a:a + int(1.2 * sr)]
    if len(seg) < sr * 0.3: seg = d[:int(1.2 * sr)]
    f, vf, _ = librosa.pyin(seg.astype(np.float32), fmin=25, fmax=4200, sr=sr, frame_length=4096)
    f = f[vf] if vf.any() else f[~np.isnan(f)]
    if len(f) == 0: return None
    return float(69 + 12 * np.log2(np.median(f) / 440))
# VSCO organs are numbered by key, every 3rd (Rode_Man3Open_01..61 = 61-key manual C2–C7). pYIN cannot read them:
# the loud plenum's upper half carries a 16' (an octave below the key), the quiet stopped flute's twelfth (3rd
# partial) beats its fundamental, so measured notes were off by octaves and fifths. Checked by the lowest partial.
# family: (key offset, keep?) — the pedals overlap the manuals and the sampler would alternate the two timbres as
# round robins, so a pedal is kept only below the manual; Man3Open_04 lacks its 8' (sounds an octave up)
ORGAN = {"Rode_Man3Open": (35, lambda n: n != 4), "Rode_Pedal": (23, lambda n: n <= 10),
         "NT5_Man3Quiet": (-86, lambda n: True), "NT5_PedalQuiet": (-28, lambda n: False)}
def organ(rows):
    kept = []
    for r in rows:
        k = re.match(r"(.*?)_(\d+)(?:_rr\d)?\.wav$", os.path.basename(r["path"]))
        off, keep = ORGAN[k.group(1)]
        if keep(int(k.group(2))):
            r["note"] = int(k.group(2)) + off
            kept.append(r)
    return kept
out = {}
for name, d in ART.items():
    files = sorted(glob.glob(os.path.join(V, d, "*.wav")))
    rows = []
    for p in files:
        n, v, rr = parse(os.path.basename(p))
        rows.append(dict(path=p, named=n, vel=v, rr=rr))
    # measure a sample of files to find the octave offset (or all, if unnamed)
    unnamed = all(r["named"] is None for r in rows)
    probe = rows if unnamed else rows[::max(1, len(rows) // 10)]
    diffs = []
    for r in probe:
        m = measure(r["path"]); r["measured"] = m
        if m is not None and r["named"] is not None: diffs.append(round((m - r["named"]) / 12) * 12)
    off = collections.Counter(diffs).most_common(1)[0][0] if diffs else 0
    for r in rows:
        r["note"] = (r["named"] + off) if r["named"] is not None else (round(r["measured"]) if r.get("measured") is not None else None)
    if name in ("org_loud", "org_quiet"):  # органы: файлы без имён нот, номер = клавиша (см. ORGAN)
        rows = organ(rows)
    out[name] = [r for r in rows if r["note"] is not None]
    print(f"{name:10} files {len(files):3}  offset {off:+d}  range {min(r['note'] for r in out[name])}-{max(r['note'] for r in out[name])}  vels {sorted({r['vel'] for r in rows})}", flush=True)
pitch = {1: 42, 2: 46, 3: 49, 4: 52, 5: 54}  # VSCO's Timpani.sfz keycenters
for key, pat in (("timp", "Percussion/Timpani/Timpani%d_Hit_*.wav"), ("timp_roll", "Percussion/Timpani/Rolls/Timpani%d_Roll_*.wav")):
    out[key] = []
    for i, m in pitch.items():
        for f in sorted(glob.glob(os.path.join(V, pat % i))):
            out[key].append(dict(path=f, named=None, vel=int(re.search(r"_v(\d)", f).group(1)),
                                 rr=re.search(r"_rr(\d)", f).group(1), note=m))
for rows in out.values():
    for r in rows:
        r["path"] = os.path.relpath(r["path"], V)
json.dump(out, open(os.path.join(ROOT, "kit", "data", "index_vsco.json"), "w"), indent=0)
