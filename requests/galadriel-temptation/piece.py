#!/usr/bin/env python3
"""Искушение Галадриэли — Лориен ночью, Фродо предлагает Кольцо (≈ 3:34). Редакция 2.

По источникам (research.md): ход сцены Зеркала у Шора (по расшифровке Complete Recordings) и приметы «Призрака
Оперы» (по MIDI). Мелодии обоих не цитируются: свои темы — Галадриэль D–A–B–E–D–A и Кольцо D–E♭–D–G♯.

  0:00  Лориен ночью: женский хор над бурдоном, звёздный свет
  0:28  Зеркало: тема Галадриэли у альтовой флейты, арфа — вода
  0:50  видение (Шор: «Шир горит» → Око): высокие скрипки, остинато фагота восьмыми → шестнадцатыми,
        засурдиненная труба и тромбон — мотив Кольца
  1:00  Фродо отшатнулся (Шор: 3/4, пиццикато на каждую долю, фраза валторны), тишина, «Я отдам его вам» — орган
  1:12  искушение, волна 1 (фа-диез минор, ♩=80): остинато виолончелей шестнадцатыми вокруг тоники, высокие
        скрипки, валторны fp< — каждый такт выше (Шор); голос Кольца в тромбонах; в конце волны орган —
        параллельные трезвучия хроматически вниз («Призрак»)
  1:42  волна 2 на полтона выше (соль минор): бас бьётся восьмыми на одном звуке, литавры («Призрак»), её ответ в хоре
  2:06  к кульминации: бас с акцентами, трубы, аккорды всё выше
  2:15  Тёмная Королева (ля минор, ff): вокализ взбирается по целым тонам («Призрак»); аккорды обваливаются вниз и
        литавровое тремоло (Шор) — обрыв
  2:42  «I pass the test»: одна валторна, тема на челесте
  3:05  уйти на Запад: фраза валторны над струнными; звёзды гаснут

    python3 -m kit run requests/galadriel-temptation/piece.py --sketch --parts
    python3 -m kit run requests/galadriel-temptation/piece.py --parts
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from kit import fx as fxcat  # noqa: E402
from kit.devices import Composer  # noqa: E402
from kit.events import Piece  # noqa: E402
from kit.harmony import MAJ, MIN, in_range  # noqa: E402

D = 2
GALADRIEL = [0, 7, 9, 14, 12, 7]            # D A B E D A (over D): Dorian sixth
RING = [0, 1, 0, -6]                        # D Eb D G#: minor second, tritone
STAR = [2, 4, 7, 9, 11]                     # D E G A B — Dorian-pentatonic starlight


class G:
    """the piece's state and helpers"""

    def __init__(self, ctx):
        self.cues = ctx.cues["cues"]
        self.total = ctx.cues["duration_s"]
        self.p = Piece("Искушение Галадриэли", bpm=80, meter=(4, 4), key="D minor", seed=31)
        self.p.meta["sends"] = {"choir": 0.6, "organ": 0.5, "harp": 0.55, "winds": 0.4, "strings": 0.42, "brass": 0.35}
        self.c = Composer(self.p, lib="sso", seed=17)
        self.rng = self.c.rng
        for cue in self.cues:
            if cue["kind"] in ("section", "hit", "silence"):
                self.p.mark(cue["t"], cue["label"][:24])

    def t(self, label):
        return next(c["t"] for c in self.cues if c["label"] == label)

    # colours measured too quiet in the sketch (balance table: celesta −16, crotales −26, harmonics −20 dB under
    # the choir); raised here, for every section
    LEVEL = {"celesta": 2.5, "crotales": 5.0, "vln_harm": 2.5}
    mult = 1.0  # a running level factor (the obsession grows phrase by phrase)

    def n(self, inst, m, t, d, **kw):
        kw["gain"] = kw.get("gain", 1.0) * self.mult
        if inst in self.LEVEL:
            kw["gain"] = kw["gain"] * self.LEVEL[inst]
        if inst == "org_quiet" and m < 36:  # no library recorded the quiet organ below C2: the loud pedal, softer
            inst = "org_loud"
            kw["gain"] = kw.get("gain", 1.0) * 0.55
        return self.p.note(inst, m, t, d, **kw)

    def chord(self, inst, ms, t, d, spread=0.012, **kw):
        return [self.n(inst, m, t + spread * i, d, **kw) for i, m in enumerate(ms)]

    def theme(self, inst, intervals, root, t, durs, **kw):
        tt = t
        for iv, d in zip(intervals, durs):
            if iv is not None:
                self.n(inst, root + iv, tt, d * 0.96, **kw)
            tt += d
        return tt


# ------------------------------------------------------------------------------------------------------------
def lorien(g, t0, t1):
    """0:00 — night in Lórien: women's choir over a D–A drone, starlight, harmonics; very far — the dark"""
    dur = t1 - t0
    g.n("cb_sus", 38, t0, dur + 1, vel=0.3, gain=0.45, attack=4.0, release=3.0)
    g.n("vc_sus", 45, t0 + 1.0, dur, vel=0.28, gain=0.4, attack=4.0, release=3.0)
    g.n("org_quiet", 26, t0 + 2.0, dur, vel=0.35, gain=0.3, attack=5.0, release=3.0)
    voicings = [[62, 65, 69, 76], [60, 64, 67, 74], [62, 65, 70, 76], [62, 64, 69, 74]]  # Dm9, C/D, B♭(♯11)/D, Dsus
    for i, v in enumerate(voicings):
        g.chord("choir", v, t0 + 2.5 + 6.2 * i, 7.0, vel=0.3 + 0.03 * i, gain=1.0, attack=2.4, release=2.5, spread=0.15)
    g.n("vln_harm", 93, t0 + 4.0, 12.0, vel=0.25, gain=0.5, attack=3.0, release=3.0, pan=0.4)
    g.n("vln_harm", 100, t0 + 14.0, 12.0, vel=0.22, gain=0.42, attack=3.0, release=3.0, pan=-0.4)
    t = t0 + 3.0
    while t < t1 - 2:  # starlight: sparse bells from the Dorian pentatonic
        inst = g.rng.choice(["celesta", "celesta", "crotales", "glock"])
        lo = {"celesta": 79, "crotales": 86, "glock": 84}[inst]
        m = in_range(g.rng.choice(STAR), lo, lo + 14)
        gain = {"celesta": 2.4, "crotales": 2.4, "glock": 1.1}[inst]  # starlight must be heard (balance, sketch 1)
        g.n(inst, m, t, 2.5, vel=0.25 + 0.1 * g.rng.random(), gain=gain, pan=g.rng.uniform(-0.7, 0.7), release=2.5)
        t += g.rng.uniform(0.9, 2.2)
    g.c.arpeggio(t0 + 0.6, (D, (0, 7, 14, 17, 21)), n=9, step=0.11, lo=38, gain=0.4, vel=0.3, ring=4.0)
    g.c.arpeggio(t0 + 14.5, (D, (0, 7, 14, 16, 21)), n=9, step=0.11, lo=38, gain=0.38, vel=0.28, ring=4.0)
    # very far away: the Ring's tritone, felt rather than heard
    g.n("cbsn_sus", 32, t0 + 18.0, 7.0, vel=0.2, gain=0.15, attack=3.0, release=2.5, bend=-0.3)


def mirror(g, t0, t1, t_acc):
    """0:28 — the Mirror: Galadriel's theme on the alto flute, the harp as water; Frodo's clarinet answers"""
    dur = t1 - t0
    g.n("cb_sus", 38, t0, dur + 0.5, vel=0.3, gain=0.45, attack=2.0, release=2.0)
    for m, pan in ((50, -0.2), (57, 0.0), (64, 0.2)):  # D–A–E open strings as the ground of the water
        g.n("vla_sus" if m > 52 else "vc_sus", m, t0, dur, vel=0.25, gain=0.32, attack=2.5, release=2.0, pan=pan)
    g.chord("choir", [57, 62, 69], t0 + 1, dur - 1, vel=0.22, gain=0.35, attack=3.0, release=2.0)
    # water: rippling harp sextuplets over D Dorian, slowly changing figure
    figs = [[50, 57, 62, 64, 69, 71], [50, 57, 62, 67, 69, 74], [48, 55, 62, 64, 67, 72], [50, 57, 60, 64, 69, 76]]
    t, k = t0 + 0.2, 0
    while t < t1 - 0.4:
        f = figs[(k // 12) % len(figs)]
        g.n("harp", f[k % 6] + (12 if (k // 6) % 2 else 0), t, 1.6, vel=0.32, gain=0.21, pan=-0.3 + 0.1 * (k % 6), release=1.5)
        t += 0.135
        k += 1
    # the theme (alto flute): D A B E D A
    g.theme("afl_sus", GALADRIEL, 62, t0 + 2.0, [1.6, 1.0, 1.4, 2.6, 1.1, 3.2], vel=0.45, gain=0.55, attack=0.25,
            release=1.2, pan=0.1)
    # Frodo: a plain, trusting phrase
    g.theme("cl_sus", [0, 2, 3, 2, 0], 57, t0 + 12.0, [0.8, 0.8, 1.6, 0.8, 2.4], vel=0.38, gain=0.45, attack=0.12, pan=-0.25)
    # the water trembles
    g.c.fx("glock_down", t_acc - 0.1, gain=0.25, pan=0.3, bus="harp")
    g.c.spores(t_acc, 3.0, density=24, gain=0.16, lib="sso")
    g.n("vln_harm", 99, t_acc, 4.0, vel=0.3, gain=0.3, attack=0.4, pan=-0.3, detune=0.15)
    # the theme again, first notes only, a step lower — shadowed
    g.theme("afl_sus", [0, 7, 8], 62, t_acc + 0.8, [1.4, 1.2, 3.4], vel=0.4, gain=0.5, attack=0.3, release=1.5)


def vision(g, t0, t1):
    """0:50 — видение (как у Шора: «Шир горит» → Око): скрипки держат высокий звук, внизу остинато фагота
    восьмыми, потом шестнадцатыми; засурдиненная труба и тромбон — мотив Кольца; к концу — Око"""
    q = 0.75
    dur = t1 - t0
    g.n("vln_sus", 88, t0, dur, vel=0.4, gain=0.35, attack=1.5, release=0.6, pan=0.3)       # высокий E — пожар вдали
    g.n("vln_sus", 89, t0 + dur * 0.55, dur * 0.45, vel=0.45, gain=0.3, attack=2.0, release=0.4, pan=-0.3)  # и полутон
    g.n("cb_sus", 37, t0, dur, vel=0.4, gain=0.45, attack=1.0, release=0.5)                 # C♯ в глубине
    # фагот: C♯–D♯–E… восьмыми, с середины — шестнадцатыми, с акцентом на доле
    cell = [37, 39, 40, 39]
    t, k = t0 + 0.4, 0
    while t < t1 - 0.2:
        fast = t > t0 + dur * 0.45
        step = q / 4 if fast else q / 2
        m = cell[k % 4] + (12 if fast and (k // 8) % 2 else 0)
        g.n("bsn_sus", m + 12, t, step * 0.85, vel=0.5 + (0.12 if k % 4 == 0 else 0), gain=0.5, release=0.1, pan=-0.2)
        g.n("cbsn_sus", m, t, step * 0.85, vel=0.45, gain=0.3, release=0.1) if k % 2 == 0 else None
        t += step
        k += 1
    # Око: мотив Кольца у засурдиненной трубы, отвечает тромбон; всё ближе
    for j, (inst, root, tt) in enumerate((("tpt_mute", 62, t0 + 4.5), ("tbn_sus", 50, t0 + 9.0),
                                           ("tpt_mute", 63, t0 + 12.5), ("tbn_sus", 51, t0 + 15.0))):
        g.theme(inst, RING, root, tt, [0.5, 0.5, 0.5, 1.6], vel=0.55 + 0.08 * j, gain=0.45 if inst == "tpt_mute" else 0.4,
                attack=0.03, release=0.3, pan=0.25 if inst == "tpt_mute" else -0.25)
    g.c.fx("tamtam", t0 + 12.4, gain=0.18, bus="perc")
    g.c.timp(t1 - 2.2, 1, vel=0.55, roll=2.1)


def recoil(g, t0, t1):
    """1:00 — Фродо отшатывается: 3/4, пиццикато баса на каждую долю, аккорды струнных, длинная фраза валторны
    (тема Галадриэли в миноре), p → mf"""
    beat = 0.75
    prog = [[50, 57, 62, 65], [49, 57, 61, 64], [47, 55, 62, 67], [46, 58, 62, 65]]  # Dm | A/C♯ | Gm/B | B♭
    t, i = t0, 0
    while t < t1 - 0.2:
        ch = prog[(i // 3) % 4]
        x = (t - t0) / (t1 - t0)
        g.n("cb_pizz", ch[0] - 12, t, 0.5, vel=0.55 + 0.2 * x, gain=0.5)
        if i % 3 == 0:
            for m in ch[1:]:
                g.n("vla_sus" if m < 60 else "vln_sus", m, t, 3 * beat, vel=0.35 + 0.25 * x, gain=0.28, attack=0.3, release=0.3)
        t += beat
        i += 1
    g.theme("hn_sus", [0, 7, 8, 12, 10, 7], 50, t0 + 0.75, [1.5, 0.75, 1.5, 2.25, 0.75, 2.0], vel=0.5, gain=0.5,
            attack=0.08, release=0.5, pan=-0.15)


def offer(g, t):
    """1:10 — "I will give it to you": the organ at full strength"""
    org = [26, 38, 50, 57, 62, 65, 69, 74]
    for m in org:
        g.n("org_loud", m, t, 2.4, vel=0.85, gain=0.42, attack=0.02, release=1.8)
    for m, inst in ((26, "tba_sus"), (38, "tbn_sus"), (45, "tbn_sus"), (53, "hns_sus"), (57, "hns_sus")):
        g.n(inst, m, t, 1.8, vel=0.8, gain=0.45, attack=0.02, release=1.0)
    g.c.timp(t, D, vel=0.95)
    g.c.fx("tamtam", t, gain=0.45, bus="perc")
    g.c.fx("bd", t, gain=0.4, bus="perc")


Q = 0.75  # четверть при ♩=80 — темп искушения в фильме


def wave(g, t0, nbars, key, level, *, pulse=False, organ_riff=True, choir=False):
    """волна искушения: остинато виолончелей шестнадцатыми вокруг тоники (как у Шора — F♯), высокие скрипки,
    валторны — аккорды fp < , каждый такт выше; «Призрак»: бас бьётся восьмыми на одном звуке, орган в конце
    волны — параллельные минорные трезвучия хроматически вниз; голос Кольца — тромбоны"""
    root = in_range(key, 42, 53)  # F♯2…
    bar = 4 * Q
    t_end = t0 + nbars * bar
    g.n("vln_sus", in_range(key + 7, 85, 96), t0, t_end - t0, vel=0.35 + 0.1 * level, gain=0.32, attack=1.2, release=0.4,
        pan=0.3)
    g.n("vln_sus", in_range(key, 81, 92), t0 + bar, t_end - t0 - bar, vel=0.32 + 0.1 * level, gain=0.28, attack=2.0,
        release=0.4, pan=-0.3)
    fig = [0, 3, 7, 8, 7, 3, 7, 12, 0, 3, 8, 7, 3, 7, 10, 15]   # i, ♭3, 5, ♭6 — кружение; в конце такта — взлёт
    for b in range(nbars):
        tb = t0 + b * bar
        x = b / max(1, nbars - 1)
        g.mult = 10 ** ((-3 + 4 * x + 3 * level) / 20)
        for j in range(16):
            m = root + fig[j] + (2 if (b % 2 and j >= 12) else 0)
            g.n("vc_sus", m, tb + j * Q / 4, Q / 4 * 0.95, vel=0.5 + (0.1 if j % 4 == 0 else 0), gain=0.42, attack=0.01,
                release=0.08, pan=-0.2)
            if level >= 1:
                g.n("vla_sus", m + 12, tb + j * Q / 4, Q / 4 * 0.95, vel=0.42, gain=0.25, attack=0.01, release=0.08, pan=0.2)
        # валторны: fp — и нарастание; аккорд каждый такт на ступень выше
        sc = [0, 2, 3, 5, 7, 8, 10]
        deg = b % 7
        tri = [in_range(key + sc[deg], 55, 66), in_range(key + sc[(deg + 2) % 7], 58, 70), in_range(key + sc[(deg + 4) % 7], 62, 73)]
        for m in tri:
            g.n("hn_sus", m, tb, 0.25, vel=0.75, gain=0.4, attack=0.01, release=0.1)            # f
            g.n("hn_sus", m, tb + 0.2, bar - 0.25, vel=0.4 + 0.35 * x, gain=0.45, attack=bar * 0.85, release=0.2)  # p <
        if level >= 1:
            for m in tri:
                g.n("cl_sus", m + 12, tb + 0.2, bar - 0.25, vel=0.35 + 0.3 * x, gain=0.3, attack=bar * 0.85, release=0.2)
        if pulse:  # «Призрак»: бас бьётся восьмыми на одном звуке, акцент на сильных
            for k in range(8):
                g.n("cb_sus", root - 12, tb + k * Q / 2, Q / 2 * 0.7, vel=0.55 + (0.15 if k % 2 == 0 else 0), gain=0.55,
                    attack=0.01, release=0.08)
                g.n("vc_spic", root, tb + k * Q / 2, Q / 2 * 0.7, vel=0.5, gain=0.3, release=0.06)
            g.c.timp(tb, key, vel=0.6 + 0.3 * x)
            g.c.fx("bd", tb, gain=0.3, bus="perc")
        else:
            g.n("cb_sus", root - 12, tb, bar * 0.98, vel=0.5, gain=0.5, attack=0.2, release=0.3)
        # голос Кольца в тромбонах — на втором и шестом такте волны
        if b % 4 == 1:
            g.theme("tbn_sus", RING + [None, 5, 4], in_range(key, 43, 54), tb, [Q, Q, Q, 2 * Q, Q, Q, 2 * Q], vel=0.6 + 0.15 * level,
                    gain=0.45, attack=0.03, release=0.3, pan=-0.3)
        # её ответ: тема Галадриэли (в миноре) у хора / скрипок — она отвечает Кольцу
        if choir and b % 4 == 3:
            ans = [0, 7, 8, 12, 10, 7]
            g.theme("choir", ans, in_range(key, 62, 73), tb, [Q, Q / 2, Q, 1.5 * Q, Q / 2, 1.5 * Q], vel=0.6 + 0.1 * level,
                    gain=0.5, attack=0.15, release=0.6)
    # орган в последнем такте волны: трезвучия хроматически вниз по долям — и на шестую ступень
    if organ_riff:
        tb = t_end - bar
        for k, sh in enumerate((0, -1, -2, -3)):
            r = key + sh
            for m in (in_range(r, 26, 37), in_range(r, 57, 68), in_range(r + 3, 60, 71), in_range(r + 7, 64, 75)):
                g.n("org_loud", m, tb + k * Q, Q * 0.95, vel=0.75 + 0.05 * level, gain=0.3, attack=0.02, release=0.3)
    g.mult = 1.0


def swell(g, t0, t1, key):
    """к кульминации (как у Шора с т. 3152): бас восьмыми с акцентами, литавры, трубы; аккорды ff всё выше"""
    root = in_range(key, 42, 53)
    t, k = t0, 0
    while t < t1 - 0.05:
        x = (t - t0) / (t1 - t0)
        g.n("cb_sus", root - 12, t, Q / 2 * 0.7, vel=0.7 + 0.2 * x, gain=0.6, attack=0.01, release=0.06)
        g.n("vc_spic", root + (7 if k % 2 else 0), t, Q / 2 * 0.7, vel=0.65 + 0.2 * x, gain=0.4, release=0.06)
        if k % 2 == 0:
            g.c.timp(t, key if k % 4 == 0 else key + 7, vel=0.55 + 0.4 * x)
        t += Q / 2
        k += 1
    bar = 4 * Q
    for j in range(int((t1 - t0) / bar) + 1):
        tb = t0 + j * bar
        if tb >= t1 - 0.3:
            break
        tri = [in_range(key + 7 + 2 * j, 60, 72), in_range(key + 10 + 2 * j, 63, 75), in_range(key + 14 + 2 * j, 67, 79)]
        for inst, o, gn in (("hn_sus", -12, 0.45), ("tpt_sus", 0, 0.35), ("tbn_sus", -24, 0.35), ("choir", 0, 0.4)):
            for m in tri:
                g.n(inst, m + o, tb, bar * 0.98, vel=0.65 + 0.12 * j, gain=gn, attack=bar * 0.7, release=0.1)
    g.c.shepard(t0, t1, up=True, gain=0.22, period=3.0)
    g.c.fx("susp_scrape", t1 - 4.0, gain=0.3, bus="fx", dur=4.0)


def dark_queen(g, t_hit, t_cut, key):
    """2:15 — Тёмная Королева: ff; бас бьётся восьмыми; вокализ взбирается по целым тонам (как финал «Призрака»);
    за два такта до конца — аккорды обваливаются вниз (как у Шора), литавровое тремоло — и обрыв"""
    root = in_range(key, 40, 51)
    bar = 4 * Q
    t_fall = t_cut - 2 * bar
    # удар
    for m in (in_range(key, 26, 37), in_range(key, 38, 49), in_range(key + 7, 50, 61), in_range(key, 60, 71),
              in_range(key + 3, 62, 73), in_range(key + 7, 66, 77)):
        g.n("org_loud", m, t_hit, t_fall - t_hit, vel=0.85, gain=0.3, attack=0.02, release=0.2)
    g.c.fx("tamtam", t_hit, gain=0.45, bus="perc")
    g.c.fx("clash", t_hit, gain=0.4, bus="perc")
    g.c.timp(t_hit, key, vel=0.95)
    # бас и мотор
    t, k = t_hit, 0
    while t < t_fall - 0.05:
        g.n("cb_sus", root - 12, t, Q / 2 * 0.7, vel=0.8, gain=0.6, attack=0.01, release=0.06)
        g.n("vc_spic", root, t, Q / 2 * 0.7, vel=0.75, gain=0.4, release=0.06)
        if k % 4 == 0:
            g.c.fx("bd", t, gain=0.35, bus="perc")
        t += Q / 2
        k += 1
    # гармония под вокализом: i – ♭VI – ♭VII – i, каждые два такта сдвиг на целый тон вверх
    shifts = [0, 2, 4]
    seg = (t_fall - t_hit) / 3
    for j, sh in enumerate(shifts):
        tt = t_hit + j * seg
        for sub, (r, q3) in enumerate(((0, 3), (8, 4), (10, 4), (0, 3))):
            ts = tt + sub * seg / 4
            rr = key + sh + r
            for inst, lo, gn in (("hn_sus", 53, 0.4), ("tbn_sus", 43, 0.35), ("choir", 57, 0.42)):
                for m in (in_range(rr, lo, lo + 11), in_range(rr + q3, lo + 3, lo + 14), in_range(rr + 7, lo + 5, lo + 16)):
                    g.n(inst, m, ts, seg / 4 * 0.97, vel=0.8, gain=gn, attack=0.05, release=0.1)
            g.n("tba_sus", in_range(rr, 28, 39), ts, seg / 4 * 0.97, vel=0.75, gain=0.4, attack=0.03, release=0.1)
        # вокализ: фраза, каждая следующая — на целый тон выше
        top = in_range(key + sh, 74, 85)
        run = [top, top + 2, top + 3, top + 5, top + 7, top + 5, top + 3, top + 2]
        durs = [Q / 2, Q / 2, Q / 2, Q / 2, 2 * Q, Q / 2, Q / 2, seg - 5 * Q]
        for inst, o, gn in (("vln_sus", 0, 0.55), ("choir", -12, 0.32), ("fl_sus", 12 if top + 19 <= 96 else 0, 0.12)):
            g.theme(inst, [x - top for x in run], top + o, tt, durs, vel=0.85, gain=gn, attack=0.04, release=0.2,
                    pan=0.3 if inst == "vln_sus" else 0.0)
    # обвал: аккорды ff вниз по ступеням, затем литавровое тремоло
    falls = [(key + 7, 4), (key + 5, 3), (key + 3, 4), (key + 1, 4)]
    for j, (r, q3) in enumerate(falls):
        tt = t_fall + j * Q
        for inst, lo, gn in (("hn_sus", 55, 0.45), ("tpt_sus", 64, 0.35), ("tbn_sus", 43, 0.4), ("vln_sus", 72, 0.4),
                             ("choir", 60, 0.35)):
            for m in (in_range(r, lo, lo + 11), in_range(r + q3, lo + 3, lo + 14), in_range(r + 7, lo + 5, lo + 16)):
                g.n(inst, m, tt, Q * 0.9 if j < 3 else 1.5 * Q, vel=0.9 - 0.08 * j, gain=gn, attack=0.02, release=0.2)
        g.c.timp(tt, r, vel=0.85 - 0.1 * j)
    g.c.timp(t_fall + 5 * Q, key + 1, vel=0.5, roll=t_cut - t_fall - 5 * Q - 0.1)


def passed(g, t0, t1):
    """2:42 — the test is passed: Galadriel's theme in D major on the celesta, the harp, choir pp; Frodo's relief"""
    dur = t1 - t0
    g.n("cb_sus", 38, t0, dur + 0.5, vel=0.3, gain=0.5, attack=0.8, release=2.0)  # the light returns at once
    g.n("vc_sus", 50, t0 + 0.5, dur, vel=0.28, gain=0.38, attack=2.0, release=2.0)
    g.n("org_quiet", 38, t0, dur, vel=0.4, gain=0.3, attack=1.5, release=2.0)
    for i, v in enumerate([[62, 66, 69, 76], [61, 66, 69, 76], [59, 66, 71, 74], [62, 66, 69, 74]]):  # D(add9) D/C# Bm D
        g.chord("choir", v, t0 + 1.0 + 5.5 * i, 6.5, vel=0.3, gain=0.45, attack=2.2, release=2.0, spread=0.12)
    # «I pass the test»: сперва одна валторна, тихо; потом тема — на челесте, как звёздный свет
    g.theme("hn_sus", [0, 7, 9], 50, t0 + 0.5, [1.5, 1.0, 3.0], vel=0.35, gain=0.45, attack=0.2, release=1.0)
    g.theme("celesta", GALADRIEL, 74, t0 + 6.0, [1.0, 0.8, 1.0, 2.0, 0.8, 2.6], vel=0.5, gain=0.5, pan=0.2)
    g.theme("afl_sus", GALADRIEL, 62, t0 + 10.0, [1.5, 1.0, 1.3, 2.6, 1.1, 3.6], vel=0.45, gain=0.5, attack=0.25, release=1.2)
    g.c.arpeggio(t0 + 0.1, (D, (0, 7, 14, 16, 19)), n=10, step=0.1, lo=38, gain=0.6, vel=0.4, ring=4.0)
    g.c.arpeggio(t0 + 9.8, (D, (0, 7, 14, 16, 21)), n=10, step=0.1, lo=50, gain=0.35, vel=0.3, ring=4.0)
    g.n("vln_harm", 90, t0 + 3.0, dur - 4, vel=0.25, gain=0.28, attack=3.0, release=2.0)
    # Frodo's relief: the plain phrase, now ending upward
    g.theme("cl_sus", [0, 2, 4, 5], 57, t0 + 17.0, [0.8, 0.8, 0.8, 3.2], vel=0.4, gain=0.45, attack=0.12, pan=-0.25)


def west(g, t0, t_stars, t_end):
    """3:05 — to the West: English-horn elegy, D major with the minor subdominant, the Ring's tritone a shadow in
    the bass; 3:28 the stars go out"""
    g.mult = 10 ** (3 / 20)  # full render 3: too faint after the climax
    dur = t_end - t0
    prog = [((D, MAJ), 5.0), ((11, MIN), 5.0), ((7, MAJ), 5.0), ((7, MIN), 5.5), ((D, MAJ), dur - 20.5)]
    tt = t0
    for ch, d in prog:
        g.c.pad(tt, tt + d, ch, vel=0.3, gain=0.4, attack=1.8, release=2.5)
        pcs = [(ch[0] + i) % 12 for i in ch[1]]
        g.chord("choir", [in_range(pcs[0], 55, 66), in_range(pcs[1], 60, 71), in_range(pcs[2], 64, 76)], tt, d,
                vel=0.25, gain=0.4, attack=2.0, release=2.5)
        tt += d
    g.n("cb_sus", 38, t0, dur, vel=0.28, gain=0.5, attack=2.0, release=3.0)
    # the elegy: a falling line, then the theme's opening, unfinished
    g.theme("hn_sus", [7, 5, 4, 2, 0, None, 4, 2, -3], 50, t0 + 1.0, [1.2, 0.8, 0.8, 1.2, 3.0, 0.6, 1.0, 1.0, 3.6],
            vel=0.45, gain=0.55, attack=0.15, release=1.2, pan=0.1)
    g.theme("afl_sus", [0, 7, 9], 62, t0 + 15.0, [1.6, 1.2, 4.5], vel=0.4, gain=0.45, attack=0.3, release=2.0, pan=-0.1)
    # the shadow: the Ring's tritone, very low, under the major chord
    g.n("cbsn_sus", 32, t0 + 11.0, 11.0, vel=0.25, gain=0.4, attack=3.0, release=3.0, bend=-0.2)
    g.n("org_quiet", 26, t0 + 12.0, dur - 12.0, vel=0.35, gain=0.3, attack=4.0, release=3.0)
    # the stars go out: bells falling and thinning, harmonics fading
    for j, (m, gap) in enumerate([(86, 0.0), (81, 1.1), (76, 1.3), (74, 1.6), (69, 2.0), (62, 2.6)]):
        t_ = t_stars - 0.5 + sum(x[1] for x in [(86, 0.0), (81, 1.1), (76, 1.3), (74, 1.6), (69, 2.0), (62, 2.6)][:j + 1])
        g.n("celesta", m, t_, 3.0, vel=0.32 - 0.03 * j, gain=0.4, pan=0.4 - 0.15 * j, release=3.0)
    g.n("crotales", 98, t_stars + 0.3, 3.0, vel=0.25, gain=0.25, pan=-0.3)
    g.n("vln_harm", 86, t_stars - 3.0, t_end - t_stars + 2.0, vel=0.22, gain=0.25, attack=2.0, release=3.0)


def build(ctx):
    g = G(ctx)
    T = g.t
    t_mirror, t_acc, t_vision = T("Зеркало"), T("Вода в чаше дрогнула"), T("Видение")
    t_recoil, t_sil1, t_offer = T("Фродо отшатнулся"), T("Фродо протягивает Кольцо"), T("«Я отдам его вам»")
    t_obs, t_r2, t_swell = T("Искушение"), T("Второй круг"), T("К кульминации")
    t_hit, t_sil2, t_passed = T("Тёмная Королева"), T("Она опускает руку"), T("Испытание пройдено")
    t_west, t_stars = T("Уйти на Запад"), T("Звёзды гаснут")
    F_SHARP, G_, A_ = 6, 7, 9
    lorien(g, 0.0, t_mirror)
    mirror(g, t_mirror, t_vision, t_acc)
    vision(g, t_vision, t_recoil)
    recoil(g, t_recoil, t_sil1 - 0.1)
    offer(g, t_offer)
    wave(g, t_obs, round((t_r2 - t_obs) / (4 * Q)), F_SHARP, 0)
    wave(g, t_r2, round((t_swell - t_r2) / (4 * Q)), G_, 1, pulse=True, choir=True)
    swell(g, t_swell, t_hit, G_)
    dark_queen(g, t_hit, t_sil2 - 0.1, A_)
    passed(g, t_passed, t_west)
    west(g, t_west, t_stars, g.total - 1.0)
    # замер `--parts`: труба (−18.6) и хор (−17) выпирали; остинато виолончелей (−30), бьющийся бас (−37),
    # голос Кольца в тромбонах (−39.5) — главное в искушении — тонули
    g.p.balance({"Trumpet": -7, "Choir": -4, "Bassoon": -4, "Cellos": +6, "Basses": +9, "Trombone": +12,
                 "Violins": +5, "Violas": +8, "Timpani": +6, "Tuba": +4, "Organ": +4, "Contrabassoon": +3})
    return g.p
