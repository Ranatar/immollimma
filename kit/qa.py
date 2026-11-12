"""Instrument check of a rendering (what can be measured without ears) → report.md + report.png.

  level     0.1 s RMS over time; gaps (≥ 1 s below −50 dBFS inside the piece, except declared silences)
  damage    clipped samples, isolated clicks
  colour    spectral centroid, share above 2 kHz
  monotony  timbre/harmony diversity in 20 s windows (MFCC + chroma); 'flat' stretches are where the
            music stops changing — a proxy for boredom, not a verdict
  sections  novelty peaks (where the music changes most), to compare with the intended form
  score     (with the events) parts active over time, density, notes outside an instrument's real
            range, notes stretched far beyond the recorded range
"""
import collections
import json
import os

import numpy as np
import soundfile as sf

from .instruments import INSTR
from .paths import DATA


def _rms_db(m, sr, hop=0.1):
    h = int(sr * hop)
    n = len(m) // h
    r = np.sqrt((m[:n * h].reshape(n, h) ** 2).mean(1))
    return 20 * np.log10(r + 1e-7)


def _runs(mask, hop, min_len):
    out, start = [], None
    for i, v in enumerate(list(mask) + [False]):
        if v and start is None:
            start = i
        elif not v and start is not None:
            if (i - start) * hop >= min_len:
                out.append((round(start * hop, 1), round(i * hop, 1)))
            start = None
    return out


def features(m, sr):
    import librosa
    y = librosa.resample(m.astype(np.float32), orig_sr=sr, target_sr=22050)
    hop = 5512  # 0.25 s
    mf = librosa.feature.mfcc(y=y, sr=22050, n_mfcc=13, hop_length=hop)
    ch = librosa.feature.chroma_stft(y=y, sr=22050, hop_length=hop)
    f = np.vstack([mf[1:], ch * 4])  # drop the loudness coefficient: monotony is about colour and harmony
    f = (f - f.mean(1, keepdims=True)) / (f.std(1, keepdims=True) + 1e-9)
    return f.T, 0.25


def monotony(f, step, win=20.0):
    n = int(win / step)
    out = []
    for a in range(0, max(1, len(f) - n), max(1, int(5.0 / step))):
        w = f[a:a + n]
        c = w.mean(0)
        out.append((a * step, float(np.sqrt(((w - c) ** 2).sum(1)).mean())))
    return out


def novelty(f, step, k=16):
    s = f @ f.T / f.shape[1]
    g = np.outer(np.hanning(2 * k), np.hanning(2 * k))
    sign = np.block([[np.ones((k, k)), -np.ones((k, k))], [-np.ones((k, k)), np.ones((k, k))]])
    ker = g * sign
    nov = np.zeros(len(f))
    for i in range(k, len(f) - k):
        nov[i] = (s[i - k:i + k, i - k:i + k] * ker).sum()
    nov = np.maximum(nov, 0)
    peaks = [i for i in range(1, len(nov) - 1) if nov[i] > nov[i - 1] and nov[i] >= nov[i + 1] and nov[i] > np.percentile(nov, 90)]
    peaks = sorted(peaks, key=lambda i: -nov[i])[:12]
    return nov, sorted(round(i * step, 1) for i in peaks)


def score_checks(piece):
    calib = json.load(open(os.path.join(DATA, "calib.json"))) if os.path.exists(os.path.join(DATA, "calib.json")) else {}
    out_real, stretched = collections.Counter(), collections.Counter()
    for e in piece.notes():
        inst = INSTR[e["inst"]]
        lo, hi = inst["range"]
        if e["bus"] not in ("deep", "fx") and not lo - 0.5 <= e["midi"] <= hi + 0.5:
            out_real[e["inst"]] += 1
        recorded = [calib.get(lib, {}).get(e["inst"]) for lib in ("vsco", "sso")]
        recorded = [r for r in recorded if r]
        if recorded:
            rlo, rhi = min(r["lo"] for r in recorded), max(r["hi"] for r in recorded)
            if e["midi"] < rlo - 5 or e["midi"] > rhi + 5:
                stretched[e["inst"]] += 1
    return out_real, stretched


def report(wav, out_dir, piece=None, silences=(), title=None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import scipy.signal as ss

    os.makedirs(out_dir, exist_ok=True)
    y, sr = sf.read(wav, always_2d=True)
    m = y.mean(1)
    dur = len(m) / sr
    db = _rms_db(m, sr)
    sounding = np.nonzero(db > -60)[0]
    first, last = (sounding[0], sounding[-1]) if len(sounding) else (0, len(db) - 1)
    gaps = [g for g in _runs((db < -50) & (np.arange(len(db)) > first) & (np.arange(len(db)) < last - 40), 0.1, 1.0)
            if not any(a <= g[0] and g[1] <= b + 0.5 for a, b in silences)]
    clipped = int((np.abs(y) >= 0.999).sum())
    d = np.abs(np.diff(m))
    loc = np.convolve(d, np.ones(441) / 441, "same") + 1e-6
    spikes = np.nonzero((d > 25 * loc) & (d > 0.05))[0]
    clicks = sorted({round(i / sr, 1) for i in spikes})[:20]
    f, t, S = ss.spectrogram(m[::2], sr / 2, nperseg=4096, noverlap=2048)
    cen = (S * f[:, None]).sum(0) / (S.sum(0) + 1e-12)
    hf = 10 * np.log10(S[f > 2000].sum(0) / (S.sum(0) + 1e-12) + 1e-9)
    feats, step = features(m, sr)
    mono = monotony(feats, step)
    nov, bounds = novelty(feats, step)
    med = np.median([v for _, v in mono]) if mono else 0
    flat = [(a, round(a + 20, 1)) for a, v in mono if v < 0.6 * med]

    rows = 5 if piece else 4
    fig, ax = plt.subplots(rows, 1, figsize=(18, 2.6 * rows), sharex=True)
    ax[0].plot(np.arange(len(db)) * 0.1, db, lw=0.6)
    ax[0].set_ylim(-60, 0)
    ax[0].set_ylabel("dBFS")
    for a, b in gaps:
        ax[0].axvspan(a, b, color="red", alpha=0.25)
    ax[1].pcolormesh(t, f, 10 * np.log10(S + 1e-12), vmin=-110, vmax=-30, shading="auto")
    ax[1].set_ylim(0, 8000)
    ax[1].set_ylabel("Hz")
    ax[2].plot(t, ss.medfilt(cen, 9), lw=0.6, label="centroid")
    ax[2].set_ylabel("centroid Hz")
    ax[3].plot([a + 10 for a, _ in mono], [v for _, v in mono], lw=1)
    for a, b in flat:
        ax[3].axvspan(a, b, color="orange", alpha=0.25)
    ax[3].plot(np.arange(len(nov)) * step, nov / (nov.max() + 1e-9) * (max(v for _, v in mono) if mono else 1), lw=0.5,
               alpha=0.6)
    for b_ in bounds:
        ax[3].axvline(b_, color="k", lw=0.5, ls=":")
    ax[3].set_ylabel("diversity / novelty")
    lines = []
    if piece:
        parts = sorted({e["part"] for e in piece.notes()}, key=lambda n: -[e["part"] for e in piece.notes()].count(n))
        for i, pn in enumerate(parts):
            for e in piece.notes():
                if e["part"] == pn:
                    ax[4].plot([e["t"], e["t"] + e["dur"]], [i, i], lw=3, solid_capstyle="butt", alpha=0.5)
        for e in piece.events:
            if e["kind"] == "mark":
                for a_ in ax:
                    a_.axvline(e["t"], color="green", lw=0.6, alpha=0.6)
        ax[4].set_yticks(range(len(parts)))
        ax[4].set_yticklabels(parts, fontsize=7)
        out_real, stretched = score_checks(piece)
        dens = collections.Counter(int(e["t"] // 10) for e in piece.notes())
        lines += ["", "## Score", f"- notes: {len(piece.notes())}, parts: {len(parts)}, "
                  f"densest 10 s: {max(dens.values()) if dens else 0} notes at {10 * max(dens, key=dens.get) if dens else 0}–… s",
                  f"- outside the real range of the instrument (matters for live players): {dict(out_real) or 'none'}",
                  f"- more than 5 semitones beyond the recorded range (resampled, may sound artificial): "
                  f"{dict(stretched) or 'none'}"]
    ax[-1].set_xlim(0, dur)
    ax[-1].set_xticks(np.arange(0, dur, 10 if dur < 400 else 20))
    for a_ in ax:
        a_.grid(alpha=0.3)
    plt.tight_layout()
    png = os.path.join(out_dir, "report.png")
    plt.savefig(png, dpi=60)
    plt.close(fig)
    seg = db[first:last + 1]
    md = [f"# Report: {title or os.path.basename(wav)}", "",
          f"- length {dur:.1f} s; level p10/p50/p90 {np.percentile(seg, 10):.1f}/{np.percentile(seg, 50):.1f}/"
          f"{np.percentile(seg, 90):.1f} dBFS; peak {20 * np.log10(np.abs(y).max() + 1e-9):.1f} dBFS",
          f"- gaps ≥ 1 s below −50 dBFS: {gaps or 'none'}",
          f"- clipped samples: {clipped}; isolated clicks at: {clicks or 'none'}",
          f"- centroid median {np.median(cen):.0f} Hz; share above 2 kHz median {np.median(hf):.1f} dB",
          f"- flat stretches (diversity < 60 % of the median, 20 s windows): {flat or 'none'}",
          f"- strongest changes (novelty peaks), s: {bounds}"] + lines + ["", "![report](report.png)", ""]
    open(os.path.join(out_dir, "report.md"), "w").write("\n".join(md))
    return dict(gaps=gaps, clipped=clipped, clicks=clicks, flat=flat, bounds=bounds, png=png)
