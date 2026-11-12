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


def mix(buses, seconds, out_path, sends=None, gains=None, master_db=-1.0, fade_in=0.0, fade_out=3.0,
        stems_dir=None, reverb_seconds=3.2):
    """buses: {name: (frames, 2) float32}; writes a 24-bit WAV peak-normalised to master_db.
    Stems (one WAV per bus, same scaling, so they sum to the mix) when stems_dir is given."""
    sends = {**SENDS, **(sends or {})}
    gains = {**GAINS, **(gains or {})}
    ir = make_ir(reverb_seconds)
    n = int(seconds * SR)
    y = np.zeros((n, 2), np.float32)
    for name, b in buses.items():
        y += _stem(b, n, sends.get(name, 0.3), 10 ** (gains.get(name, 0.0) / 20), ir)
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
