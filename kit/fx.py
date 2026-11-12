"""Catalogue of raw recordings (noises, unpitched percussion) by kind. Paths keep the {VSCO}/{SSO}
placeholders so a piece's events.json is portable. VSCO's 'Miscellania Raw' and 'VSCO 1 Percussion' have no
counterpart in Sonatina; Sonatina adds a tam-tam, ratchet, castanets and more (see SSO_FX)."""
import glob
import os

from .paths import SSO, VSCO

M1, M2, P1 = "Miscellania Raw/Misc 1", "Miscellania Raw/Misc 2", "VSCO 1 Percussion"
VSCO_FX = {
    "alien": f"{M1}/alien*.wav", "bubbles": f"{M1}/bubbles*.wav", "siren": f"{M1}/siren*.wav",
    "chain": f"{M1}/chain*.wav", "brick": f"{M1}/brick*.wav", "glass": f"{M1}/glass_break*.wav",
    "metal": f"{M1}/metal_hit*.wav", "cymbgong": f"{M1}/cymb*gong*.wav", "ambience": f"{M1}/ambience*.wav",
    "timpsnare": f"{M1}/timp*snare*.wav", "zap": f"{M1}/zap*.wav",
    "nepal": f"{M2}/NepaleseBells/*.wav", "glock_down": f"{M2}/glock_glisses/*down*.wav",
    "glock_up": f"{M2}/glock_glisses/*up*.wav", "sleigh": f"{M2}/sleighbell*.wav", "tamb": f"{M2}/tamb*.wav",
    "gong_roll": f"{P1}/varMetal/Gong/gong_roll*.wav", "gong_scrape": f"{P1}/varMetal/Gong/gong_scrape*.wav",
    "gong_hit": f"{P1}/varMetal/Gong/gong_hit_f*.wav", "susp_scrape": f"{P1}/varMetal/Cymbals/susp/susp_FX_scrape*.wav",
    "susp": f"{P1}/varMetal/Cymbals/susp/*.wav", "clash": f"{P1}/varMetal/Cymbals/clash/*.wav",
    "triangle": f"{P1}/varMetal/triangle/*/*.wav",
    "snare": f"{P1}/drums/snare/drum3_marching/snare3_[fmp]*.wav",
    "snare_soft": f"{P1}/drums/snare/drum3_marching/snare3_pp*.wav",
    "bd": f"{P1}/drums/bass/bdrum_*.wav", "bd_soft": f"{P1}/drums/bass/bdrum*_pp*.wav",
    "guiro": f"{P1}/varWood/guiro*.wav", "claves": f"{P1}/varWood/claves*.wav",
    "logdrum": f"{P1}/varWood/log_drum/*.wav", "maraca": f"{P1}/varWood/maraca*", "slapstick": f"{P1}/varWood/slapstick*.wav",
    "wood_click": f"{P1}/varWood/wood*", "vsco_ratchet": f"{P1}/varWood/ratchet*",
}
SSO_FX = {
    "tamtam": "Samples/Percussion/tamtam*", "ratchet": "Samples/Percussion/ratchet*",
    "castanets": "Samples/Percussion/castanets*", "sso_snare": "Samples/Percussion/snare*",
    "sso_bd": "Samples/Percussion/bass_drum*", "sso_cymbal": "Samples/Percussion/cymbal*",
    "vibraslap": "Samples/Percussion/vibraslap*", "woodblocks": "Samples/Percussion/wood_block*", "sso_tamb": "Samples/Percussion/tambourine*",
    "bell_tree": "Samples/Percussion/bell_tree*", "cabasa": "Samples/Percussion/cabasa*",
}
# grain sources for spore-like clouds
GRAIN_SOURCES = {
    "vsco": ["Strings/Harp/*.wav", "Percussion/Glock/*.wav", "Strings/Violin Section/Pizz/*.wav"],
    "sso": ["Samples/Harp/*.wav", "Samples/Percussion/glockenspiel*", "Samples/1st Violins/1st-violins-piz*"],
}

_cache = {}


def _glob(root, tag, pattern):
    files = sorted(glob.glob(os.path.join(root, pattern)))
    return [f"{{{tag}}}/" + os.path.relpath(f, root) for f in files]


def files(kind):
    """placeholder paths for a kind (VSCO_FX or SSO_FX); empty if the library is not installed"""
    if kind not in _cache:
        if kind in VSCO_FX:
            _cache[kind] = _glob(VSCO, "VSCO", VSCO_FX[kind])
        elif kind in SSO_FX:
            _cache[kind] = _glob(SSO, "SSO", SSO_FX[kind])
        else:
            raise KeyError(f"unknown fx kind {kind!r}")
    return _cache[kind]


def grain_sources(lib="vsco", limit_pizz=12, extra=("bubbles",)):
    root, tag = (VSCO, "VSCO") if lib == "vsco" else (SSO, "SSO")
    out = []
    for i, pat in enumerate(GRAIN_SOURCES[lib]):
        f = _glob(root, tag, pat)
        out += f[:limit_pizz] if i == 2 else f
    for k in extra:
        out += files(k)
    return out


def kinds():
    return {k: len(files(k)) for k in list(VSCO_FX) + list(SSO_FX)}
