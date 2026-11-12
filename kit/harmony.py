"""Pitch helpers: pitch classes, chords, scales, Roman numerals, voicing by nearest motion."""

NOTE = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
MIN, MAJ, FIFTH, DIM, AUG = (0, 3, 7), (0, 4, 7), (0, 7), (0, 3, 6), (0, 4, 8)
DOM7, MIN7, MAJ7, HDIM7, DIM7 = (0, 4, 7, 10), (0, 3, 7, 10), (0, 4, 7, 11), (0, 3, 6, 10), (0, 3, 6, 9)
ADD9, MAJ9, MIN9, SUS2, SUS4, QUARTAL = (0, 4, 7, 14), (0, 4, 7, 11, 14), (0, 3, 7, 10, 14), (0, 2, 7), (0, 5, 7), (0, 5, 10)

SCALES = {
    "major": (0, 2, 4, 5, 7, 9, 11), "minor": (0, 2, 3, 5, 7, 8, 10), "harmonic_minor": (0, 2, 3, 5, 7, 8, 11),
    "dorian": (0, 2, 3, 5, 7, 9, 10), "phrygian": (0, 1, 3, 5, 7, 8, 10), "lydian": (0, 2, 4, 6, 7, 9, 11),
    "mixolydian": (0, 2, 4, 5, 7, 9, 10), "locrian": (0, 1, 3, 5, 6, 8, 10), "whole_tone": (0, 2, 4, 6, 8, 10),
    "octatonic": (0, 1, 3, 4, 6, 7, 9, 10), "octatonic_wh": (0, 2, 3, 5, 6, 8, 9, 11),
    "pentatonic": (0, 2, 4, 7, 9), "minor_pentatonic": (0, 3, 5, 7, 10), "chromatic": tuple(range(12)),
}
QUARTER = [x / 2 for x in range(-10, 11)]  # quarter-tone offsets, ±5 semitones


def pc(name):
    """'D' → 2, 'Bb' → 10, 'F#' → 6"""
    n = NOTE[name[0].upper()]
    for ch in name[1:]:
        n += 1 if ch == "#" else -1 if ch == "b" else 0
    return n % 12


def midi(name):
    """'D4' → 62, 'Bb2' → 46 (C4 = 60)"""
    i = len(name) - 1
    while i > 0 and (name[i].isdigit() or name[i] == "-"):
        i -= 1
    return 12 * (int(name[i + 1:]) + 1) + pc(name[:i + 1])


def in_range(pitch_class, lo, hi, near=None):
    """the pitch with that pitch class inside lo..hi (nearest to `near` if given)"""
    c = [m for m in range(lo, hi + 1) if m % 12 == pitch_class % 12]
    if not c:
        return lo
    return c[0] if near is None else min(c, key=lambda m: abs(m - near))


def chord_pcs(chord):
    root, iv = chord
    return [(root + i) % 12 for i in iv]


def scale_degree(key_pc, scale, degree, octave_base=60):
    """degree from 0 (may be negative or beyond the octave) → MIDI"""
    s = SCALES[scale] if isinstance(scale, str) else scale
    o, d = divmod(degree, len(s))
    return octave_base + key_pc + s[d] + 12 * o


ROMAN = {"i": 0, "ii": 1, "iii": 2, "iv": 3, "v": 4, "vi": 5, "vii": 6}


def roman(key_pc, numeral, scale="major"):
    """'V7', 'ii', 'bVI', 'iv', 'vii°' in a key → (root pc, intervals)"""
    s = SCALES[scale]
    shift = 0
    while numeral[0] in "b#":
        shift += -1 if numeral[0] == "b" else 1
        numeral = numeral[1:]
    core = "".join(ch for ch in numeral if ch.lower() in "iv")
    rest = numeral[len(core):]
    deg = ROMAN[core.lower()]
    root = (key_pc + s[deg] + shift) % 12
    major = core.isupper()
    if "°" in rest or "o" in rest:
        iv = DIM7 if "7" in rest else DIM
    elif "ø" in rest:
        iv = HDIM7
    elif "+" in rest:
        iv = AUG
    elif "7" in rest:
        iv = (MAJ7 if "maj" in rest else DOM7) if major else MIN7
    else:
        iv = MAJ if major else MIN
    return root, iv


def voice(chord, lanes, prev=None):
    """voice a chord over lanes [(lo, hi), ...] (bass first): bass gets the root, upper lanes the other tones,
    each pitch chosen nearest to the previous voicing (smooth voice leading)"""
    pcs = chord_pcs(chord)
    order = [pcs[0]] + (pcs[1:] if len(pcs) > 1 else pcs)
    out = []
    for i, (lo, hi) in enumerate(lanes):
        p = order[0] if i == 0 else order[1 + (i - 1) % max(1, len(order) - 1)] if len(order) > 1 else order[0]
        near = prev[i] if prev and i < len(prev) else (lo + hi) // 2
        out.append(in_range(p, lo, hi, near))
    return out
