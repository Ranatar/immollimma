"""One name per instrument and articulation, whichever library plays it.

Each entry:
  plain   key in data/index_vsco.json (the plain sampler over raw VSCO files), or None
  vsco    VSCO SFZ instrument(s) (first whose range holds the note wins)
  sso     Sonatina SFZ instrument(s)
  range   real sounding range of the instrument (MIDI), for live-performance checks
  bus     default mixing bus;  short: a struck/plucked sound (no lengthening of short recordings)
  part    notation part the articulation belongs to (sus/trem/pizz of violins → one part "Violins")

Backends (render.py) pick a source per note in this order:
  plain: plain → vsco → sso      vsco: vsco → sso → plain      sso: sso → vsco → plain
so an instrument one library lacks is taken from the other one; the report lists every substitution.
"""

S = "Strings - Notation/"
B = "Brass - Notation/"
W = "Woodwinds - Notation/"
P = "Percussion/"


def _i(part, rng, bus, plain=None, vsco=(), sso=(), short=False):
    return dict(part=part, range=rng, bus=bus, plain=plain, vsco=list(vsco), sso=list(sso), short=short)


INSTR = {
    # strings (sections)
    "vln_sus": _i("Violins", (55, 103), "strings", "vln_sus", ["ViolinEnsSusVib"], [S + "1st Violins Sustain"]),
    "vln_trem": _i("Violins", (55, 103), "strings", "vln_trem", ["ViolinEnsTrem"], [S + "1st Violins Tremolo"]),
    "vln_pizz": _i("Violins", (55, 96), "strings", "vln_pizz", ["ViolinEnsPizz"], [S + "1st Violins Pizzicato"], short=True),
    "vln_spic": _i("Violins", (55, 96), "strings", None, ["ViolinEnsSpic"], [S + "1st Violins Staccato"], short=True),
    "vln_leg": _i("Violins", (55, 103), "strings", None, [], [S + "1st Violins Legato"]),
    "vln_harm": _i("Violins", (67, 108), "strings", None, [], [S + "1st Violins Harmonics"]),
    "vln_colleg": _i("Violins", (55, 96), "strings", None, [], [S + "1st Violins Col Legno"], short=True),
    "vla_sus": _i("Violas", (48, 91), "strings", "vla_sus", ["ViolaEnsSusVib"], [S + "Violas Sustain"]),
    "vla_trem": _i("Violas", (48, 91), "strings", "vla_trem", ["ViolaEnsTrem"], [S + "Violas Tremolo"]),
    "vla_pizz": _i("Violas", (48, 84), "strings", "vla_pizz", ["ViolaEnsPizz"], [S + "Violas Pizzicato"], short=True),
    "vla_spic": _i("Violas", (48, 84), "strings", None, ["ViolaEnsSpic"], [S + "Violas Staccato"], short=True),
    "vla_leg": _i("Violas", (48, 91), "strings", None, [], [S + "Violas Legato"]),
    "vla_harm": _i("Violas", (60, 96), "strings", None, [], [S + "Violas Harmonics"]),
    "vc_sus": _i("Cellos", (36, 84), "strings", "vc_sus", ["CelloEnsSusVib"], [S + "Celli Sustain"]),
    "vc_trem": _i("Cellos", (36, 84), "strings", "vc_trem", ["CelloEnsTrem"], [S + "Celli Tremolo"]),
    "vc_pizz": _i("Cellos", (36, 76), "strings", "vc_pizz", ["CelloEnsPizz"], [S + "Celli Pizzicato"], short=True),
    "vc_spic": _i("Cellos", (36, 76), "strings", None, ["CelloEnsSpic"], [S + "Celli Staccato"], short=True),
    "vc_leg": _i("Cellos", (36, 84), "strings", None, [], [S + "Celli Legato"]),
    "vc_harm": _i("Cellos", (48, 91), "strings", None, [], [S + "Celli Harmonics"]),
    "vc_colleg": _i("Cellos", (36, 76), "strings", None, [], [S + "Celli Col Legno"], short=True),
    "cb_sus": _i("Basses", (28, 67), "strings", "cb_sus", ["ContrabassSusVB"], [S + "Basses Sustain"]),
    "cb_trem": _i("Basses", (28, 67), "strings", "cb_trem", ["ContrabassTrem"], [S + "Basses Tremolo"]),
    "cb_pizz": _i("Basses", (28, 60), "strings", "cb_pizz", ["ContrabassPizz"], [S + "Basses Pizzicato"], short=True),
    "cb_leg": _i("Basses", (28, 67), "strings", None, [], [S + "Basses Legato"]),
    "vln_solo": _i("Violin solo", (55, 103), "strings", None, ["SViolinVib"], ["Strings - Notation/Violin Solo 1 Marcato (looped)"]),
    # brass
    "hn_sus": _i("Horn", (34, 77), "brass", "hn_sus", ["FHornSus"], [B + "Horn Solo Sustain (looped)"]),
    "hn_mute": _i("Horn", (34, 77), "brass", "hn_mute", ["FHornMute"], []),
    "hn_stac": _i("Horn", (34, 77), "brass", None, ["FHornStac"], [], short=True),
    "hn_leg": _i("Horn", (34, 77), "brass", None, [], [B + "Horn Solo Legato"]),
    "hns_sus": _i("Horns", (34, 77), "brass", None, [], [B + "Horns Sustain"]),
    "tpt_sus": _i("Trumpet", (54, 84), "brass", "tpt_sus", ["TrumpetSus"], [B + "Trumpet Solo Sustain (looped)"]),
    "tpt_mute": _i("Trumpet", (54, 84), "brass", "tpt_mute", ["TrumpetStraightMuteSus"], []),
    "tpt_harmon": _i("Trumpet", (54, 84), "brass", None, ["TrumpetHarmonMuteSus"], []),
    "tpt_stac": _i("Trumpet", (54, 84), "brass", None, ["TrumpetStac"], [], short=True),
    "tpt_leg": _i("Trumpet", (54, 84), "brass", None, [], [B + "Trumpet Solo Legato"]),
    "tbn_sus": _i("Trombone", (40, 72), "brass", "tbn_sus", ["TromboneSus"],
                  [B + "Tenor Trombone Solo Sustain (looped)", B + "Bass Trombone Solo Sustain (looped)"]),
    "tbn_stac": _i("Trombone", (40, 72), "brass", None, ["TromboneStac"], [], short=True),
    "tbn_leg": _i("Trombone", (40, 72), "brass", None, [], [B + "Tenor Trombone Solo Legato"]),
    "btbn_sus": _i("Bass trombone", (34, 67), "brass", None, [], [B + "Bass Trombone Solo Sustain (looped)"]),
    "tba_sus": _i("Tuba", (28, 58), "brass", "tba_sus", ["TubaSus"], [B + "Tuba Sustain (looped)"]),
    "tba_stac": _i("Tuba", (28, 58), "brass", None, ["TubaStac"], [], short=True),
    # woodwinds
    "picc_sus": _i("Piccolo", (74, 108), "winds", None, ["PiccoloSus"], [W + "Piccolo Solo Sustain (looped)"]),
    "fl_sus": _i("Flute", (60, 96), "winds", "fl_sus", ["FluteSusNV"], [W + "Flute Solo 2 Sustain Non-Vibrato"]),
    "fl_vib": _i("Flute", (60, 96), "winds", None, ["FluteSusVib"], [W + "Flute Solo 1 Sustain (looped)"]),
    "fl_stac": _i("Flute", (60, 96), "winds", None, ["FluteStac"], [W + "Flute Solo 1 Staccato"], short=True),
    "fl_leg": _i("Flute", (60, 96), "winds", None, [], [W + "Flute Solo 1 Legato"]),
    "afl_sus": _i("Alto flute", (55, 86), "winds", None, [], [W + "Alto Flute Solo Sustain (looped)"]),
    "ob_sus": _i("Oboe", (58, 91), "winds", "ob_sus", ["OboeSusNV"], [W + "Oboe Solo Sustain (looped)"]),
    "ob_stac": _i("Oboe", (58, 91), "winds", None, ["OboeStac"], [W + "Oboe Solo Staccato"], short=True),
    "ob_leg": _i("Oboe", (58, 91), "winds", None, [], [W + "Oboe Solo Legato"]),
    "eh_sus": _i("English horn", (52, 81), "winds", None, [], [W + "Cor Anglais Solo Sustain (looped)"]),
    "cl_sus": _i("Clarinet", (50, 94), "winds", "cl_sus", ["ClarinetSus"], [W + "Clarinet Solo Sustain (looped)"]),
    "cl_stac": _i("Clarinet", (50, 94), "winds", None, ["ClarinetStac"], [W + "Clarinet Solo Staccato"], short=True),
    "cl_leg": _i("Clarinet", (50, 94), "winds", None, [], [W + "Clarinet Solo Legato"]),
    "bcl_sus": _i("Bass clarinet", (34, 77), "winds", None, [], [W + "Bass Clarinet Solo Sustain (looped)"]),
    "bsn_sus": _i("Bassoon", (34, 75), "winds", "bsn_sus", ["BassoonSus"],
                  [W + "Bassoon Solo Sustain (looped)", W + "Contrabassoon Solo Sustain (looped)"]),
    "bsn_stac": _i("Bassoon", (34, 75), "winds", None, ["BassoonStac"], [W + "Bassoon Solo Staccato"], short=True),
    "cbsn_sus": _i("Contrabassoon", (22, 53), "winds", None, [], [W + "Contrabassoon Solo Sustain (looped)"]),
    # keyboards, harp, pitched percussion, choir
    "harp": _i("Harp", (24, 103), "harp", "harp", ["Harp"], ["Concert Harp"], short=True),
    "glock": _i("Glockenspiel", (79, 108), "harp", "glock", ["Glockenspiel"], [P + "Glockenspiel"], short=True),
    "xylo": _i("Xylophone", (65, 108), "harp", None, ["Xylophone"], [P + "Xylophone"], short=True),
    "marimba": _i("Marimba", (45, 96), "harp", None, ["Marimba"], [P + "Marimba Hits"], short=True),
    "tubular": _i("Tubular bells", (60, 77), "perc", None, ["TubularBells"], [P + "Chimes"], short=True),
    "celesta": _i("Celesta", (60, 108), "harp", None, [], [P + "Celeste"], short=True),
    "vibes": _i("Vibraphone", (53, 89), "harp", None, [], [P + "Vibraphone"], short=True),
    "crotales": _i("Crotales", (84, 108), "harp", None, [], [P + "Crotales"], short=True),
    "piano": _i("Piano", (21, 108), "keys", None, ["UprightPiano"], ["Grand Piano/Grand Piano"], short=True),
    "hpsd": _i("Harpsichord", (29, 89), "keys", None, [], ["Harpsichord/Harpsichord 8'"], short=True),
    "org_loud": _i("Organ", (24, 96), "organ", "org_loud", ["OrganLoud", "OrganLoudPedal"],
                   ["Organ/Great - Open Diapason 8ft", "Organ/Pedal - Violon 16ft"]),
    "org_quiet": _i("Organ", (24, 96), "organ", "org_quiet", ["OrganQuiet", "OrganQuietPedal"],
                    ["Organ/Swell - Gedact 8ft", "Organ/Pedal - Bourdon 16ft"]),
    "org_reed": _i("Organ", (36, 96), "organ", None, [], ["Organ/Swell - Oboe 8ft"]),
    "choir": _i("Choir", (40, 81), "choir", None, [], ["Chorus - Notation/Mixed Chorus"]),
    "timp": _i("Timpani", (38, 57), "perc", "timp", ["Timpani"], [P + "Timpani"], short=True),
    "timp_roll": _i("Timpani", (38, 57), "perc", "timp_roll", ["TimpaniRolls"], [P + "Timpani"]),
}

# sounding pitch minus key, measured with pYIN (tools/calibrate.py) and kept in data/calib.json;
# these are the ones known before measuring (SFZ files written at notated pitch)
KNOWN_OFFSET = {("vsco", "glock"): 12, ("sso", "glock"): 24, ("vsco", "org_loud"): -12, ("sso", "timp_roll"): -24}

ORDER = {"plain": ("plain", "vsco", "sso"), "vsco": ("vsco", "sso", "plain"), "sso": ("sso", "vsco", "plain")}

LICENSES = {
    "plain": "VSCO 2 Community Edition (Versilian Studios, Sam Gossner), CC0",
    "vsco": "VSCO 2 Community Edition (Versilian Studios, Sam Gossner), CC0",
    "sso": "Sonatina Symphonic Orchestra (Mattias Westlund; SFZ by P. Eastman), CC Sampling Plus 1.0 — not for advertising",
}


def sources(inst, backend="plain"):
    """the library order to try for an instrument"""
    e = INSTR[inst]
    out = []
    for lib in ORDER[backend]:
        if (lib == "plain" and e["plain"]) or (lib != "plain" and e[lib]):
            out.append(lib)
    return out
