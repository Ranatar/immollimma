"""Notation out of the events: MIDI (one track per part), MusicXML (quantised, score order, techniques
written as text: pizz., trem., con sord., col legno, harmonics) and a PDF score through LilyPond.

What notation cannot carry is listed in the report instead: detune, glissando inside a note, ring
modulation, reversed notes, raw samples and grain clouds."""
import collections
import os
import shutil
import subprocess

import mido

from .instruments import INSTR

SCORE_ORDER = ["Piccolo", "Flute", "Alto flute", "Oboe", "English horn", "Clarinet", "Bass clarinet", "Bassoon",
               "Contrabassoon", "Horn", "Horns", "Trumpet", "Trombone", "Bass trombone", "Tuba", "Timpani",
               "Glockenspiel", "Crotales", "Xylophone", "Vibraphone", "Marimba", "Tubular bells", "Celesta", "Harp",
               "Piano", "Harpsichord", "Organ", "Choir", "Violin solo", "Violins", "Violas", "Cellos", "Basses"]
GM = {"Piccolo": 72, "Flute": 73, "Alto flute": 73, "Oboe": 68, "English horn": 69, "Clarinet": 71,
      "Bass clarinet": 71, "Bassoon": 70, "Contrabassoon": 70, "Horn": 60, "Horns": 60, "Trumpet": 56, "Trombone": 57,
      "Bass trombone": 57, "Tuba": 58, "Timpani": 47, "Glockenspiel": 9, "Crotales": 9, "Xylophone": 13,
      "Vibraphone": 11, "Marimba": 12, "Tubular bells": 14, "Celesta": 8, "Harp": 46, "Piano": 0, "Harpsichord": 6,
      "Organ": 19, "Choir": 52, "Violin solo": 40, "Violins": 48, "Violas": 48, "Cellos": 48, "Basses": 48}
def _clefs():
    from music21 import clef
    return {"Violas": clef.AltoClef, "Cellos": clef.BassClef, "Basses": clef.Bass8vbClef, "Bassoon": clef.BassClef,
            "Contrabassoon": clef.Bass8vbClef, "Trombone": clef.BassClef, "Bass trombone": clef.BassClef,
            "Tuba": clef.BassClef, "Timpani": clef.BassClef, "Glockenspiel": clef.Treble8vaClef,
            "Piccolo": clef.Treble8vaClef, "Crotales": clef.Treble8vaClef}


class _Lazy(dict):
    def __missing__(self, k):
        self.update(_clefs())
        if k in self:
            return dict.__getitem__(self, k)
        raise KeyError(k)

    def __contains__(self, k):
        if not dict.__len__(self):
            self.update(_clefs())
        return dict.__contains__(self, k)


CLEFS = _Lazy()
TECH = {"pizz": "pizz.", "trem": "trem.", "mute": "con sord.", "colleg": "col legno", "harm": "harmonics",
        "harmon": "harmon mute", "spic": "spicc.", "roll": "roll"}


def _order(name):
    """score order; a keyboard split into 'X RH' / 'X LH' keeps the right hand on top"""
    base, hand = name, 0
    for suf, h in ((" RH", 0), (" LH", 1)):
        if name.endswith(suf):
            base, hand = name[:-len(suf)], h
    i = SCORE_ORDER.index(base) if base in SCORE_ORDER else len(SCORE_ORDER)
    return (i, hand)


def parts_of(piece):
    by = collections.defaultdict(list)
    for e in piece.notes():
        by[e["part"]].append(e)
    return dict(sorted(by.items(), key=lambda kv: _order(kv[0])))


def lost(piece):
    """what the notation leaves out"""
    c = collections.Counter()
    for e in piece.events:
        if e["kind"] == "note":
            if e["detune"]:
                c["notes with detune (out-of-tune doubles)"] += 1
            if e["bend"]:
                c["notes with a glissando inside"] += 1
            if e["ringmod"]:
                c["ring-modulated notes"] += 1
            if e["reverse"]:
                c["reversed notes"] += 1
            if not 0 <= round(e["midi"]) <= 127:
                c["notes outside MIDI range"] += 1
        elif e["kind"] in ("sample", "grains"):
            c[{"sample": "raw samples (noises, unpitched percussion)", "grains": "grain clouds"}[e["kind"]]] += 1
    return dict(c)


def to_midi(piece, path, tpb=480):
    mf = mido.MidiFile(ticks_per_beat=tpb, charset="utf-8")  # Cyrillic titles and marks
    tick = lambda t: int(round(t * piece.bpm / 60.0 * tpb))  # noqa: E731
    head = mido.MidiTrack()
    head.append(mido.MetaMessage("track_name", name=piece.title, time=0))
    head.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(piece.bpm), time=0))
    head.append(mido.MetaMessage("time_signature", numerator=piece.meter[0], denominator=piece.meter[1], time=0))
    marks = sorted((tick(e["t"]), e["label"]) for e in piece.events if e["kind"] == "mark")
    last = 0
    for t, lab in marks:
        head.append(mido.MetaMessage("marker", text=str(lab)[:60], time=t - last))
        last = t
    mf.tracks.append(head)
    ch = 0
    for name, notes in parts_of(piece).items():
        if ch == 9:
            ch += 1
        tr = mido.MidiTrack()
        tr.append(mido.MetaMessage("track_name", name=name, time=0))
        tr.append(mido.Message("program_change", program=GM.get(name, 48), channel=ch % 16, time=0))
        ev = []
        for e in notes:
            m = int(round(e["midi"]))
            if not 0 <= m <= 127:
                continue
            v = max(1, min(127, int(round(1 + 126 * e["vel"]))))
            ev.append((tick(e["t"]), 1, m, v))
            ev.append((max(tick(e["t"]) + 1, tick(e["t"] + e["dur"])), 0, m, 0))
        ev.sort(key=lambda x: (x[0], x[1]))
        last = 0
        for t, on, m, v in ev:
            tr.append(mido.Message("note_on" if on else "note_off", note=m, velocity=v, channel=ch % 16, time=t - last))
            last = t
        mf.tracks.append(tr)
        ch += 1
    mf.save(path)
    return path


def _tech(inst):
    suf = inst.split("_", 1)[1] if "_" in inst else ""
    return TECH.get(suf)


def to_musicxml(piece, path, divisors=(4, 3), max_staves=4):
    import math

    from music21 import articulations, chord, clef, expressions, instrument, metadata, meter, note, stream, tempo

    shift = float(piece.meta.get("notation_offset", 0.0))  # quarters before t=0 in the first bar (anacrusis)
    q = lambda t: t * piece.bpm / 60.0 + shift  # noqa: E731  seconds → quarter lengths
    sc = stream.Score()
    md = metadata.Metadata()
    md.title = piece.title
    md.composer = piece.meta.get("composer", " ")
    md.movementName = piece.meta.get("subtitle", " ")  # otherwise the title is printed twice
    sc.metadata = md
    marks = [(q(e.get("wt", e["t"])), str(e["label"])) for e in piece.events if e["kind"] == "mark"]
    first = True
    ksig, spell = _key_spelling(piece.key)
    for name, notes in parts_of(piece).items():
        # simultaneous notes of one length → chords; what still overlaps goes to a second staff (divisi)
        grid = 12 if 3 in divisors else max(divisors)
        groups = collections.defaultdict(list)
        for e in notes:
            m = int(round(e["midi"]))
            if not 21 <= m <= 108:
                continue
            # written time/length (wt, wdur) win over the performed ones: rubato and pedal stay out of the notation
            on = round(q(e.get("wt", e["t"])) * grid) / grid
            # a note played shorter than written (legato 0.9…0.97, staccato) keeps its written length
            ln = max(0.25, math.ceil((q(e.get("wdur", e["dur"])) - shift) * 4 - 0.15) / 4)
            art = e.get("art") or ("staccato" if e["inst"].endswith(("_stac", "_spic")) else None)
            groups[(on, ln, _tech(e["inst"]), art)].append(m)
        staves = []  # [(end, [items])]
        order = lambda k: (k[0], k[1], k[2] or "", k[3] or "")  # noqa: E731  None and text marks side by side
        for key in sorted(groups, key=order):
            on, ln = key[0], key[1]
            for st in staves:
                if st[0] <= on + 1e-6:
                    st[0] = on + ln
                    st[1].append((key, groups[key]))
                    break
            else:
                if len(staves) < max_staves:
                    staves.append([on + ln, [(key, groups[key])]])
                else:  # too many layers: cut the longest-running staff short
                    st = min(staves, key=lambda s_: s_[0])
                    st[0] = on + ln
                    st[1].append((key, groups[key]))
        for si, (_, items) in enumerate(staves):
            part = stream.Part()
            ins = instrument.Instrument()
            ins.partName = name if len(staves) == 1 else f"{name} {si + 1}"
            ins.partAbbreviation = ins.partName[:5]
            part.insert(0, ins)
            part.insert(0, meter.TimeSignature(f"{piece.meter[0]}/{piece.meter[1]}"))
            if name in CLEFS:
                part.insert(0, CLEFS[name]())
            else:  # a low staff (left hand, low voice) gets the bass clef
                ms_ = sorted(m for _, ms in items for m in ms)
                if ms_ and ms_[len(ms_) // 2] < 57:
                    part.insert(0, clef.BassClef())
            if ksig is not None:
                part.insert(0, ksig.__class__(ksig.sharps))
            last_tech = None
            prev_end = 0.0
            for (on, ln, tech, art), ms in items:
                ln = max(0.25, min(ln, ln))
                obj = note.Note(spell(ms[0])) if len(set(ms)) == 1 else chord.Chord([spell(x) for x in sorted(set(ms))])
                obj.quarterLength = ln
                if on < prev_end:  # a cut-short note (more layers than staves)
                    continue
                if tech != last_tech:
                    txt = tech or ("arco" if last_tech in ("pizz.", "col legno", "spicc.") else
                                   "senza sord." if last_tech in ("con sord.", "harmon mute") else
                                   "ord." if last_tech else None)
                    if txt:
                        part.insert(on, expressions.TextExpression(txt))
                    last_tech = tech
                if tech in ("trem.", "roll"):
                    obj.expressions.append(expressions.Tremolo(numberOfMarks=3))
                if art == "staccato":
                    obj.articulations.append(articulations.Staccato())
                elif art == "accent":
                    obj.articulations.append(articulations.Accent())
                part.insert(on, obj)
                prev_end = on + ln
            if first:
                part.insert(0, tempo.MetronomeMark(number=round(piece.bpm)))
                for on, lab in marks:
                    part.insert(on, expressions.RehearsalMark(lab[:24]))
                first = False
            sc.insert(0, part)
    sc = sc.quantize(quarterLengthDivisors=divisors, processOffsets=True, processDurations=True, inPlace=False)
    sc.write("musicxml", fp=path)
    return path


def _key_spelling(key_text):
    """'D-flat major', 'B minor', 'Db', 'F#m' → (KeySignature | None, midi → Pitch spelled in that key)"""
    from music21 import key as m21key, pitch
    ks, scale_names, flats, sharps = None, {}, False, False
    try:
        txt = (key_text or "").strip()
        tonic, _, mode = txt.partition(" ")
        tonic = tonic.replace("-flat", "-").replace("-sharp", "#").replace("b", "-") if len(tonic) > 1 else tonic
        mode = "minor" if ("minor" in mode or tonic.endswith("m")) else "major"
        tonic = tonic.rstrip("m") or tonic
        k = m21key.Key(tonic.upper()[0] + tonic[1:] if mode == "major" else tonic.lower()[0] + tonic[1:])
        ks = m21key.KeySignature(k.sharps)
        for p_ in k.getScale(mode).getPitches("C1", "B1"):
            scale_names[p_.pitchClass] = p_.name
        if mode == "minor":  # raised 6th and 7th (leading tone) belong to minor too
            for iv in ("-m2", "-m3"):
                p_ = k.tonic.transpose(iv)
                scale_names.setdefault(p_.pitchClass, p_.name)
        flats = k.sharps < 0
        sharps = k.sharps > 0
    except Exception:  # noqa: BLE001 — no key: default spelling
        ks = None

    def spell(m):
        p_ = pitch.Pitch(midi=m)
        name = scale_names.get(m % 12)
        if name is None and ks is not None:  # chromatic note: flats in flat keys, sharps in sharp keys
            name = p_.name
            if (flats and "#" in name) or (sharps and "-" in name):
                name = p_.getEnharmonic().name
        if name:
            q_ = pitch.Pitch(name + "4")
            q_.octave += (m - q_.midi) // 12
            return q_
        return p_
    return ks, spell


def to_pdf(musicxml, pdf):
    """MusicXML → LilyPond → PDF; returns the PDF path, or None when LilyPond is not installed"""
    if not (shutil.which("musicxml2ly") and shutil.which("lilypond")):
        return None
    base = os.path.splitext(pdf)[0]
    ly = base + ".ly"
    subprocess.run(["musicxml2ly", "--no-beaming", "-o", ly, musicxml], check=True, capture_output=True)
    # a readable score on A4 portrait, small staves
    src = open(ly, encoding="utf-8").read()
    src = src.replace('\\version', '#(set-global-staff-size 14)\n\\version', 1)
    # a "French" score: staves without notes in a system are not printed (big scores stay readable)
    # (a top-level \layout only counts when it stands before \score)
    src = src.replace("\\score {", "\\layout { \\context { \\Staff \\RemoveAllEmptyStaves } }\n\\score {", 1)
    open(ly, "w", encoding="utf-8").write(src)
    r = subprocess.run(["lilypond", "-dno-point-and-click", "-o", base, ly], capture_output=True, text=True)
    return pdf if os.path.exists(pdf) else (r.stderr[-800:] and None)


def fits_grid(piece, div=4, tol=0.04):
    """do all onsets and lengths sit on the semiquaver grid (then no triplets are needed)"""
    q = piece.bpm / 60.0
    for e in piece.notes():
        x = e["t"] * q
        if abs(x * div - round(x * div)) > tol * div:
            return False
    return True


def export_all(piece, out_dir, pdf=True, max_pdf_seconds=420):
    os.makedirs(out_dir, exist_ok=True)
    slug = "score"
    res = {"midi": to_midi(piece, os.path.join(out_dir, slug + ".mid")), "lost": lost(piece)}
    xml = os.path.join(out_dir, slug + ".musicxml")
    tries = [(4,)] if fits_grid(piece) else [(4, 3), (4,)]
    for div in tries:  # musicxml2ly chokes on some of music21's tuplets: fall back to a plain grid
        try:
            res["musicxml"] = to_musicxml(piece, xml, divisors=div)
            res.pop("notation_error", None)
            if pdf and piece.end() <= max_pdf_seconds:
                res["pdf"] = to_pdf(xml, os.path.join(out_dir, slug + ".pdf"))
            res["grid"] = list(div)
            break
        except Exception as ex:  # notation is a by-product: never let it stop the audio
            res["notation_error"] = repr(ex)[:300]
    return res
