"""Mixing: buses → stereo with one shared synthetic hall (convolution), optional stems, loudness and
encoding through ffmpeg, muxing onto a video."""
import os
import subprocess

import numpy as np
import soundfile as sf
from scipy.signal import butter, oaconvolve, sosfilt

from .sampler import SR

# reverb send and level (dB) per bus — tuned on the R.S.F.G.R. score; a piece may override them
SENDS = {"strings": 0.38, "brass": 0.32, "winds": 0.32, "perc": 0.25, "organ": 0.45, "harp": 0.5, "keys": 0.3,
         "choir": 0.45, "fx": 0.45, "deep": 0.7, "spores": 0.55, "buzz": 0.5, "parade": 0.22}
GAINS = {"strings": 0.0, "brass": 1.0, "winds": 7.0, "perc": 2.0, "organ": 0.0, "harp": 9.0, "keys": 3.0,
         "choir": 0.0, "fx": 1.0, "deep": 3.0, "spores": 8.0, "buzz": 12.0, "parade": 1.0}


def make_ir(seconds=3.2, seed=3):
    rng = np.random.default_rng(seed)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    ir = rng.standard_normal((n, 2)).astype(np.float32)
    ir *= np.exp(-6.9 * t / seconds)[:, None]
    ir = sosfilt(butter(2, 4200, "low", fs=SR, output="sos"), ir, axis=0)
    ir = np.concatenate([np.zeros((int(0.022 * SR), 2), np.float32), ir])
    return (ir / np.sqrt((ir ** 2).sum(0))).astype(np.float32)


def _stem(b, n, s, g, ir):
    y = np.zeros((n, 2), np.float32)
    for c in range(2):
        y[:, c] = b[:n, c] * (1 - 0.35 * s) * g
        y[:, c] += 0.9 * oaconvolve(b[:, c] * (s * g), ir[:, c])[:n].astype(np.float32)
    return y


def _interp_points(points, t):
    """points: [[t, value], ...] sorted; linear between them, held outside; t: array of seconds"""
    pt = np.array([p[0] for p in points], float)
    pv = np.array([p[1] for p in points], float)
    return np.interp(t, pt, pv)


def archive(y, points, t0=0.0, seed=5):
    """The sound of an archive that changes over time — a process on the whole mix.
    points: [{"t": s, "lp": Hz, "hp": Hz, "width": 0..1, "crackle": 0..1, "hiss": dB}, ...] (sorted by t).
    Between points everything glides; a point with "step": true switches at once. lp/hp: a band like a
    gramophone (lp ≥ 18000 and hp ≤ 25 mean no filter); width: stereo width (0 = mono); crackle: clicks
    per second / 30; hiss: noise floor in dBFS (None = none)."""
    n = len(y)
    t = t0 + np.arange(n) / SR
    out = np.zeros_like(y)
    # band: piecewise, every segment between two points filtered with both ends' settings and crossfaded
    for k in range(len(points)):
        a = points[k]
        b = points[k + 1] if k + 1 < len(points) else a
        ta = a["t"] if k > 0 else -1e9
        tb = b["t"] if k + 1 < len(points) else 1e18
        i0, i1 = np.searchsorted(t, ta), np.searchsorted(t, tb)
        if i1 <= i0:
            continue
        pad = int(0.25 * SR)
        j0, j1 = max(0, i0 - pad), min(n, i1 + pad)
        seg = y[j0:j1]

        def band(p):
            z = seg
            if p.get("lp", 20000) < 18000:
                z = sosfilt(butter(4, p["lp"], "low", fs=SR, output="sos"), z, axis=0)
            if p.get("hp", 20) > 25:
                z = sosfilt(butter(2, p["hp"], "high", fs=SR, output="sos"), z, axis=0)
            return z
        za = band(a)
        zb = za if (b is a or b.get("step")) else band(b)
        if b is a or b.get("step") or tb - ta <= 0:
            w = np.zeros(j1 - j0, np.float32)
        else:
            w = np.clip((t[j0:j1] - ta) / (tb - ta), 0, 1).astype(np.float32)
        z = za * (1 - w)[:, None] + zb * w[:, None]
        out[i0:i1] = z[i0 - j0:i1 - j0]
    # width: mid/side
    def series(key, default):
        pts = []
        for k, p in enumerate(points):
            v = p.get(key, default)
            if p.get("step") and k > 0:
                pts.append([p["t"] - 1e-3, points[k - 1].get(key, default)])
            pts.append([p["t"], v])
        return _interp_points(pts, t)
    wdt = series("width", 1.0).astype(np.float32)
    mid = (out[:, 0] + out[:, 1]) * 0.5
    side = (out[:, 0] - out[:, 1]) * 0.5 * wdt
    out[:, 0], out[:, 1] = mid + side, mid - side
    # crackle and hiss, scaled to the music's own level so normalisation does not change them
    rng = np.random.default_rng(seed)
    ref = float(np.sqrt((out ** 2).mean()) + 1e-9)
    cr = series("crackle", 0.0)
    if cr.max() > 0:
        rate = cr * 30.0 / SR
        clicks = (rng.random(n) < rate).astype(np.float32) * rng.uniform(-1, 1, n).astype(np.float32)
        # a click is a short burst (≈ 1 ms), not a one-sample spike: a record's crackle, not a digital fault
        clicks = np.convolve(clicks, np.hanning(int(0.0012 * SR)).astype(np.float32), mode="same")
        clicks = sosfilt(butter(2, [700, 4500], "band", fs=SR, output="sos"), clicks) * ref * 1.2
        out += np.stack([clicks, clicks * 0.8], 1).astype(np.float32)
    hiss_db = [p.get("hiss") for p in points]
    if any(h is not None for h in hiss_db):
        hl = series("hiss", -120.0)
        noise = rng.standard_normal((n, 2)).astype(np.float32)
        noise = sosfilt(butter(2, [300, 5000], "band", fs=SR, output="sos"), noise, axis=0)
        noise /= np.sqrt((noise ** 2).mean()) + 1e-9
        out += noise * (10 ** (hl / 20) * ref / 10 ** (-30 / 20))[:, None].astype(np.float32)
    return out.astype(np.float32)


def mix(buses, seconds, out_path, sends=None, gains=None, master_db=-1.0, fade_in=0.0, fade_out=3.0,
        stems_dir=None, reverb_seconds=3.2, post=None, t0=0.0, bus_post=None):
    """buses: {name: (frames, 2) float32}; writes a 24-bit WAV peak-normalised to master_db.
    Stems (one WAV per bus, same scaling, so they sum to the mix) when stems_dir is given.
    post: processes on the whole mix, e.g. [{"kind": "archive", "points": [...]}] (see archive());
    t0: the time of the first frame in the piece (for windows).
    bus_post: processes on one bus before the hall, e.g. {"radio": [{"kind": "archive", "points": [...]}]} —
    a sound «from a loudspeaker» inside an otherwise clean mix (the hall is added after, as in the room)."""
    sends = {**SENDS, **(sends or {})}
    gains = {**GAINS, **(gains or {})}
    ir = make_ir(reverb_seconds)
    n = int(seconds * SR)
    y = np.zeros((n, 2), np.float32)
    buses = dict(buses)
    for name, procs in (bus_post or {}).items():
        if name in buses:
            for pr in procs:
                if pr.get("kind") == "archive":
                    buses[name] = archive(buses[name], pr["points"], t0=t0)
    for name, b in buses.items():
        y += _stem(b, n, sends.get(name, 0.3), 10 ** (gains.get(name, 0.0) / 20), ir)
    for pr in post or []:
        if pr.get("kind") == "archive":
            y = archive(y, pr["points"], t0=t0)
    k = 10 ** (master_db / 20) / (np.abs(y).max() + 1e-9)
    y *= k
    if fade_in:
        f = int(fade_in * SR)
        y[:f] *= np.linspace(0, 1, f, dtype=np.float32)[:, None]
    if fade_out:
        f = min(n, int(fade_out * SR))
        y[-f:] *= np.linspace(1, 0, f, dtype=np.float32)[:, None]
    sf.write(out_path, y, SR, subtype="PCM_24")
    if stems_dir:
        os.makedirs(stems_dir, exist_ok=True)
        for name, b in buses.items():
            st = _stem(b, n, sends.get(name, 0.3), 10 ** (gains.get(name, 0.0) / 20), ir) * k
            sf.write(os.path.join(stems_dir, f"{name}.wav"), st, SR, subtype="PCM_24")
    return y


def encode(wav, out, lufs=-16.0, lra=16.0, bitrate="320k"):
    """loudness-normalised MP3 (or any format ffmpeg infers from the extension)"""
    args = ["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-af", f"loudnorm=I={lufs}:TP=-1.5:LRA={lra}",
            "-ar", str(SR)]
    if out.endswith(".mp3"):
        args += ["-c:a", "libmp3lame", "-b:a", bitrate]
    subprocess.run(args + [out], check=True)
    return out


def mux(audio, video, out):
    """the music as the video's sound track (video copied as it is)"""
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", video, "-i", audio, "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "224k", "-shortest", "-movflags", "+faststart", out],
                   check=True)
    return out
