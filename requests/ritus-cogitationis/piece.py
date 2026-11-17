#!/usr/bin/env python3
"""Ritus Cogitationis — музыка к анимации ritus.html (обряд Культа Машины, цикл 102 с).

Все времена — из журнала прогона анимации (events.json → cues.json; инструмент — tools/):
  * стадии, вспышки, подписи — метки cues.json;
  * удары механизма — cues["bell_beats"]; в установившемся ходе ровно на кратных 1,6 с: при 150 уд/мин такт 4/4
    = один удар, шестнадцатая = 0,1 с, и все метки ложатся на сетку;
  * механическое время — cues["mt_curve"]: двоичный кант стоит на сетке механического времени (шестнадцатая =
    0,1 единицы), поэтому он трогается, глохнет, разгоняется и замедляется до остановки вместе с шестернями.

Материал:
  Дух Машины   — напев в D-фригийском (D F G A | A B♭ A G A — A A B♭ C B♭ G F‑E♭ D) с органумом;
  двоичный кант — биты ASCII литаний (1 — удар, 0 — пауза), высоты по циклу из 5 звуков против 8-битных групп;
  скверна       — переворот битов, четвертитоны, тонущие расстроенные дубли, кольцевая модуляция, облака.
Сквозные процессы — сборка аккорда кольцами (II), аддитивная служба (V), остывание металла (VII→IX), машинный ход.

    python3 -m kit run requests/ritus-cogitationis/piece.py --sketch --parts
    python3 -m kit run requests/ritus-cogitationis/piece.py --parts
"""
import bisect
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from kit.devices import Composer  # noqa: E402
from kit.events import Piece  # noqa: E402

BAR, Q, S16 = 1.6, 0.4, 0.1
LEN = 102.0


def bits(text):
    return [int(b) for ch in text for b in format(ord(ch) & 255, "08b")]


class Mech:
    """механическое время анимации: mt(t) и обратное — когда механизм проходит отметку u"""

    def __init__(self, curve):
        self.h = curve["step"]
        self.v = curve["values"]

    def mt(self, t):
        f = max(0.0, min(t, LEN)) / self.h
        i = min(int(f), len(self.v) - 2)
        return self.v[i] + (self.v[i + 1] - self.v[i]) * (f - i)

    def t_of(self, u):
        i = bisect.bisect_left(self.v, u - 1e-9)
        if i >= len(self.v):
            return None
        if i == 0:
            return 0.0
        a, b = self.v[i - 1], self.v[i]
        return (i - 1 + (u - a) / ((b - a) or 1.0)) * self.h


def chant(p, t0, syl, inst="choir", voices=(0,), vel=0.5, gain=0.5, gap=0.03, attack=0.06, release=0.7, pan=0.0,
          detune=0.0, bend=0.0, skip=()):
    """напев по слогам: [(midi | None, секунды)], голоса — сдвиги (органум); skip — номера слогов-«лакун»"""
    t = t0
    for k, (m, d) in enumerate(syl):
        if m is not None and k not in skip:
            for j, off in enumerate(voices):
                if inst == "choir" and not 40 <= m + off <= 81:
                    continue
                p.note(inst, m + off, t, max(0.08, d - gap), vel=vel, gain=gain * (1.0 if j == 0 else 0.75),
                       pan=pan + (0.18 * j if j % 2 else -0.18 * j), attack=attack, release=release,
                       detune=detune, bend=bend if d > 0.8 else 0.0)
        t += d
    return t


def build(ctx):
    cues = ctx.cues
    mech = Mech(cues["mt_curve"])
    bells = cues["bell_beats"]
    p = Piece("Ritus Cogitationis", bpm=150, meter=(4, 4), key="D minor", seed=7)
    p.meta["length"] = LEN
    c = Composer(p, lib="vsco", seed=7)
    rng = p.rng
    for e in cues["cues"]:
        if e["kind"] == "section":
            p.mark(e["t"], e["label"])

    def corrupt(t):  # сила скверны: растёт 58→67 линейно, как в анимации
        return max(0.0, min(1.0, (t - 58.0) / 9.0)) if 58.0 <= t < 66.75 else 0.0

    lacunae = []  # окна общего молчания в IX

    def in_lacuna(t):
        return any(a <= t < b for a, b in lacunae)

    # ---------------------------------------------------------------- двоичный кант (по механическому времени)
    def cant(t_lo, t_hi, text, cycle, inst, step=S16, vel=0.5, gain=0.4, pan=0.0, every=1, accent=0.15,
             dur_frac=0.85, max_dur=0.5, bus=None, double=None, ramp_db=0.0):
        b = bits(text)
        n = len(b)
        u_lo, u_hi = mech.mt(t_lo), mech.mt(t_hi)
        k0, k1 = math.ceil(u_lo / step - 1e-9), math.floor(u_hi / step + 1e-9)
        for k in range(k0, k1 + 1):
            if k % every:
                continue
            t = mech.t_of(k * step)
            if t is None or t < t_lo or t >= t_hi:
                continue
            cr = corrupt(t)
            bit = b[k % n]
            if cr and rng.random() < 0.45 * cr:
                bit = 1 - bit
            if not bit or in_lacuna(t) or (cr and rng.random() < 0.3 * cr):
                continue
            t_next = mech.t_of((k + 1) * step)
            d = max(0.06, min(max_dur, ((t_next or t + step) - t) * dur_frac))
            m = cycle[k % len(cycle)]
            det = rng.uniform(-1.0, 1.0) * cr if cr else 0.0
            tt = t + (rng.uniform(-0.04, 0.04) * cr if cr else 0.0)
            v = vel + (accent if k % 16 == 0 else 0.0)
            g = gain * 10 ** (ramp_db * (t - t_lo) / max(1e-6, t_hi - t_lo) / 20)
            p.note(inst, m, tt, d, vel=min(1.0, v), gain=g, pan=pan, release=0.25, detune=det, bus=bus)
            if double:
                inst2, off, g2 = double
                p.note(inst2, m + off, tt, d, vel=min(1.0, v), gain=g2 * g / gain, pan=-pan, release=0.25, detune=det * 1.3, bus=bus)

    # ================================================================ I TENEBRAE (0–4)
    c.fx("zap", 0.0, gain=0.12, shift=-7, bus="fx")
    p.note("vln_harm", 98, 0.3, 3.4, vel=0.25, gain=0.12, pan=0.4, attack=0.6, release=0.6)  # писк кинескопа
    c.breath(0.4, 4.6, gain=0.32)
    c.fx("ambience", 0.8, gain=0.22, shift=-5, bus="deep", attack=1.5, dur=3.6)

    # ================================================================ II INVOCATIO (4–22): напев и сборка аккорда
    P1 = [(50, .4), (53, .4), (55, .4), (57, .6), (57, .4), (58, .4), (57, .4), (55, .4), (57, .9)]
    P2 = [(57, .4), (57, .4), (58, .4), (60, .6), (58, .4), (55, .4), (53, .3), (51, .3), (50, 1.2)]
    P3 = [(57, .3), (60, .3), (62, .3), (62, .45), (63, .3), (62, .3), (60, .45), (62, .3), (60, .3), (58, .3),
          (57, .3), (57, .8)]
    P4 = [(62, .4), (69, .8), (67, .4), (69, .4), (70, .4), (69, .3), (62, 1.8)]
    chant(p, 4.0, P1, voices=(0, -7), vel=0.38, gain=0.42)
    chant(p, 8.5, P2, voices=(0, -7, 12), vel=0.45, gain=0.46)
    chant(p, 13.2, P3, voices=(0, -5, -12, 12), vel=0.55, gain=0.48)
    chant(p, 13.2, P3, inst="org_quiet", voices=(0,), vel=0.45, gain=0.25)
    chant(p, 17.8, P4, voices=(0, -12, -7, 12), vel=0.72, gain=0.55)
    chant(p, 17.8, P4, inst="tbn_sus", voices=(-12,), vel=0.6, gain=0.3)

    # сборка: каждое кольцо добавляет звук в держащийся аккорд (до начала помазания)
    ASSEMBLY = [(4.5, 38, "org_quiet", 0.45), (4.5, 38, "cb_sus", 0.3), (5.5, 45, "vc_sus", 0.32),
                (6.5, 50, "vla_sus", 0.3), (9.0, 57, "hn_mute", 0.3), (9.8, 58, "bcl_sus", 0.3),
                (14.0, 63, "eh_sus", 0.26), (15.0, 69, "vln_sus", 0.24), (16.0, 74, "vln_harm", 0.2)]
    for t0, m, inst, g in ASSEMBLY:
        p.note(inst, m, t0, 22.4 - t0, vel=0.42, gain=g, attack=0.5, release=1.6, pan=rng.uniform(-0.4, 0.4))
        if t0 > 5:
            p.note("harp", m + 12 if m < 60 else m, t0, 2.0, vel=0.55, gain=0.4, pan=0.3, release=1.5)
    p.note("tubular", 62, 4.5, 3.0, vel=0.55, gain=0.45, release=3.0)            # сердце загорелось
    c.timp(4.5, 2, vel=0.45)
    gear = [74, 75, 77, 79, 81, 82, 84, 86, 87, 89, 91, 93]                        # 12 шестерён: зубья входят в зацепление
    for i, m in enumerate(gear):
        t = 10.8 + 0.3 * i
        p.note("vln_colleg", min(m, 96), t, 0.2, vel=0.5, gain=0.3, pan=-0.5 + i / 11, release=0.2)
        c.fx("wood_click", t, gain=0.08, pan=0.5 - i / 11, bus="perc")
        if i % 3 == 2:
            p.note("crotales", m + 12 if m + 12 <= 108 else m, t, 1.2, vel=0.3, gain=0.12, release=1.2)
    # обод: полный аккорд, тамтам
    for m in (38, 45, 50, 57, 58, 63, 69, 74):
        p.note("org_loud", m, 18.2, 4.2, vel=0.6, gain=0.24, attack=0.05, release=1.8)
    p.note("cbsn_sus", 26, 18.2, 4.0, vel=0.6, gain=0.4, release=1.5)
    c.timp(18.2, 2, vel=0.75)
    c.fx("tamtam", 18.2, gain=0.3, bus="perc")
    p.note("tubular", 62, 18.2, 3.0, vel=0.7, gain=0.5, release=3.0)
    # 6 спутников: тяжёлые удары, бас спускается к D
    for i, m in enumerate((50, 48, 46, 45, 43, 38)):
        t = 19.0 + 0.4 * i
        p.note("tbn_stac", m if m >= 40 else m + 12, t, 0.3, vel=0.7, gain=0.45, release=0.4)
        p.note("tba_stac", m - 12 if m - 12 >= 28 else m, t, 0.3, vel=0.7, gain=0.4, release=0.4)
        c.fx("metal", t, gain=0.1, pan=0.4 if i % 2 else -0.4, shift=-6, bus="perc")

    # ================================================================ III UNCTIO (22–27): золотые волны
    for m in (38, 45, 54, 57, 62, 64):
        p.note("org_quiet", m, 22.2, 5.0, vel=0.4, gain=0.3, attack=0.9, release=1.2)
    for m in (78, 81):
        p.note("vln_harm", m, 22.4, 4.6, vel=0.35, gain=0.16, attack=1.2, release=1.0, pan=0.3)
    gold = {2, 4, 6, 9, 11}    # D мажор с секстой и ноной — «золото»
    for i in range(9):          # волна на каждое кольцо, изнутри наружу — всё выше
        t = 22.3 + 0.18 * i + 0.3
        notes, m = [], 50 + 3 * i
        while len(notes) < 7:
            if m % 12 in gold:
                notes.append(m)
            m += 1
        for j, nt in enumerate(notes):
            p.note("harp", nt, t + 0.07 * j, 2.0, vel=0.45, gain=0.32, pan=-0.5 + i / 8, release=1.6)
    p.note("crotales", 98, 26.6, 2.0, vel=0.4, gain=0.18, release=2.0)                # unctio perfecta

    # ================================================================ IV EXCITATIO (27–38): пуск, заминка, разгон
    for inst, m, g in (("cb_trem", 38, 0.45), ("vc_trem", 45, 0.38), ("tba_sus", 38, 0.4)):
        p.note(inst, m, 27.0, 1.6, vel=0.55, gain=g, attack=0.6, release=0.1, bend=3.0)        # раскрутка
        p.note(inst, m + 3, 28.6, 1.3, vel=0.5, gain=g, attack=0.02, release=0.1, bend=-8.0)  # глохнет
    p.note("hn_mute", 62, 29.0, 0.7, vel=0.6, gain=0.35, release=0.3)                        # «renititur»
    p.note("hn_mute", 63, 29.0, 0.7, vel=0.6, gain=0.35, release=0.3)
    p.note("hn_mute", 68, 29.0, 0.7, vel=0.6, gain=0.3, release=0.3)
    c.fx("ratchet", 29.1, gain=0.18, bus="perc", dur=0.7)
    # 30.0–30.6 — тишина
    # 30.6 «Iterum: surge!»
    chant(p, 30.6, [(62, .45), (69, 1.4)], voices=(0, -12, 12, -7), vel=0.85, gain=0.6)
    for m in (26, 38, 45, 50, 57, 62, 69):
        p.note("org_loud", m if m >= 24 else 26, 30.6, 2.2, vel=0.75, gain=0.26, release=1.5)
    for inst, ms in (("tbn_sus", (50, 57)), ("hn_sus", (62, 69)), ("tpt_sus", (74,))):
        for m in ms:
            p.note(inst, m, 30.6, 1.8, vel=0.8, gain=0.4, release=0.8)
    c.timp(30.6, 2, vel=0.9)
    c.fx("tamtam", 30.6, gain=0.35, bus="perc")
    # 33.2 «Vis motiva adest»: напев, разгон литавр к первому удару хода
    chant(p, 33.2, [(57, .4), (57, .4), (60, .4), (62, .6), (62, .4), (57, 1.4)], voices=(0, -7, 12), vel=0.6,
          gain=0.5)
    c.timp(33.4, 2, vel=0.5, roll=5.0)
    p.note("cbsn_sus", 26, 33.4, 5.0, vel=0.55, gain=0.35, attack=4.0, release=0.3)
    p.note("tba_sus", 38, 34.4, 4.0, vel=0.55, gain=0.3, attack=3.0, release=0.3)

    # ================================================================ двоичный кант: с пуска до остановки
    T_ORDO = "Ordo ex numero "
    T_LUX = "Lux ex ordine "
    PH = [62, 65, 69, 70, 75]            # D F A B♭ E♭
    cant(27.0, 30.0, T_ORDO, PH, "hpsd", vel=0.55, gain=0.42, pan=0.25)
    cant(33.0, 66.75, T_ORDO, PH, "hpsd", vel=0.55, gain=0.36, pan=0.25, ramp_db=6.0)
    cant(38.4, 66.75, T_LUX, [38, 45, 39], "cb_pizz", step=0.2, vel=0.6, gain=0.5, pan=-0.25,
         double=("bsn_stac", 12, 0.25), ramp_db=5.0)
    cant(48.0, 66.75, T_ORDO, [74, 77, 81, 82, 87], "xylo", every=2, vel=0.45, gain=0.2, pan=0.4, ramp_db=4.0)
    # VIII — гуще
    PH2 = [69, 70, 74, 77, 75]
    cant(71.6, 80.0, T_ORDO, PH2, "hpsd", vel=0.62, gain=0.45, pan=0.25)
    cant(71.6, 80.0, T_ORDO, [m + 12 for m in PH2], "xylo", vel=0.5, gain=0.2, pan=0.4)
    cant(72.0, 80.0, T_ORDO, [m - 12 for m in PH2], "vln_spic", vel=0.5, gain=0.25, pan=-0.3)
    cant(72.0, 80.0, T_LUX, [38, 45, 39], "cb_pizz", step=0.2, vel=0.65, gain=0.5, pan=-0.25,
         double=("tba_stac", 0, 0.3))
    # IX — мажор, светло (через лакуны — молчит)
    lacunae.extend([(82.4 + 0.5 * k, 82.4 + 0.5 * k + 0.5) for k in (2, 5, 7)])
    cant(81.0, 88.0, T_ORDO, [62, 66, 69, 71, 74], "hpsd", vel=0.45, gain=0.32, pan=0.25)
    cant(81.6, 88.0, T_LUX, [38, 45, 50], "cb_pizz", step=0.4, vel=0.5, gain=0.4, pan=-0.25)
    # X — замедление до остановки
    cant(88.0, 96.0, T_ORDO, [74, 70, 69, 65, 62], "hpsd", vel=0.42, gain=0.32, pan=0.25, max_dur=0.9)
    cant(88.0, 93.0, T_LUX, [38, 45, 39], "cb_pizz", step=0.4, vel=0.45, gain=0.35, pan=-0.25, max_dur=1.0)

    # удары механизма — литавры (в ереси — сбивчивое сердцебиение вместо них)
    for i, tb in enumerate(bells):
        if 58.0 <= tb < 71.5 or in_lacuna(tb) or abs(tb - 80.0) < 0.05:
            continue
        v = 0.42 if tb < 38 else 0.5 if tb < 58 else 0.6 if tb < 80 else 0.45 if tb < 88 else 0.35
        c.timp(tb, 2, vel=v)
        if tb >= 88.0:
            p.note("tubular", 62, tb, 2.5, vel=0.35, gain=0.22, release=2.5)

    # ================================================================ V COGITATIO (38–58): служба, слой за слоем
    c.timp(38.4, 2, vel=0.75)
    p.note("tba_sus", 26 + 12, 38.4, 0.8, vel=0.7, gain=0.4, release=0.4)
    for m in (38, 45):
        p.note("org_quiet", m, 41.6, 25.1, vel=0.4, gain=0.28, attack=1.5, release=0.3)
    # cantus firmus: напев в увеличении, по такту на слог (последний звук застаёт ересь и гниёт)
    for i, (m, _) in enumerate(P1):
        t = 44.8 + BAR * i
        last = i == len(P1) - 1
        d = (66.75 - t) if last else BAR - 0.05
        for off, g in ((0, 0.45), (-7, 0.3)):
            p.note("choir", m + off, t, d, vel=0.5, gain=g, attack=0.15, release=0.2 if last else 0.6,
                   bend=-1.6 if last else 0.0)
            if last:
                p.note("choir", m + off, t + 0.05, d, vel=0.45, gain=g * 0.6, attack=2.0, release=0.2,
                       detune=0.35, bend=-2.6)
    for b in range(4):                               # валторны, держащие квинту
        t = 51.2 + BAR * b
        for m in (62, 69):
            p.note("hn_sus", m, t, BAR - 0.05, vel=0.45, gain=0.22, attack=0.4, release=0.4)
    for k in range(int((57.6 - 51.2) / Q)):         # часы: col legno на четвертях
        p.note("vc_colleg", 50 if k % 2 else 57, 51.2 + Q * k, 0.1, vel=0.45, gain=0.2, release=0.1)
    for b in range(3):                               # колокол каждый такт
        p.note("tubular", 62 if b % 2 == 0 else 69, 54.4 + BAR * b, 3.0, vel=0.5, gain=0.3, release=2.5)

    # ================================================================ VI HAERESIS (58–67)
    c.fx("alien", 58.0, gain=0.35, shift=-3, bus="deep")
    p.note("hn_mute", 51, 58.0, 0.6, vel=0.75, gain=0.4, release=0.3)
    p.note("hn_mute", 52, 58.0, 0.6, vel=0.75, gain=0.4, release=0.3)
    p.note("tbn_sus", 44, 58.0, 0.6, vel=0.75, gain=0.4, release=0.3)
    c.heartbeat(58.6, 66.6, gain=0.32, pattern=(1.3, 0.9, 1.6, 0.7, 1.1))
    c.buzz(59.0, 7.7, notes=(75, 81, 86), gain=0.3)
    c.buzz(62.5, 4.2, notes=(63, 70), gain=0.3, rates=(47.0, 89.0))
    c.spores(60.0, 6.7, density=40, gain=0.3, curve="rise")
    for m, inst in ((39, "tba_sus"), (44, "tbn_sus"), (50, "tbn_sus"), (51, "hn_sus"), (56, "hn_sus")):  # скверна поглощает
        p.note(inst, m, 62.0, 4.7, vel=0.8, gain=0.32, attack=4.4, release=0.1, detune=0.3, bend=-0.7)
    p.note("vln_trem", 87, 63.5, 3.2, vel=0.7, gain=0.22, attack=3.0, release=0.1, bend=-3.0)
    for m in (38, 45):                                # орган гниёт: расстроенные дубли тонут
        p.note("org_quiet", m, 60.0, 6.75, vel=0.45, gain=0.22, detune=0.4, bend=-1.5, attack=2.0, release=0.2)
    c.breath(62.0, 4.75, gain=0.4)
    c.shepard(61.0, 66.75, up=True, gain=0.18)
    t = 58.8
    while t < 66.5:                                    # скрап-код: искры, чаще к концу
        c.fx("zap", t, gain=0.08 + 0.12 * corrupt(t), pan=rng.uniform(-0.8, 0.8), shift=rng.uniform(-4, 6), bus="fx")
        t += 0.9 - 0.65 * corrupt(t) + rng.uniform(0, 0.2)
    c.fx("alien", 61.5, gain=0.25, shift=2, bus="deep")
    c.fx("alien", 64.2, gain=0.3, shift=-6, bus="deep", reverse=True)
    c.fx("siren", 65.0, gain=0.18, shift=-12, bus="fx", dur=1.75, attack=1.0, fade=0.1)
    # 66.75–67.0 — вдох перед изгнанием (тишина)

    # ================================================================ VII EXORCISMUS (67–71.5)
    for m in (26, 38, 45, 50, 57, 62, 65, 69, 74):
        p.note("org_loud", max(m, 24), 67.0, 3.15, vel=0.85, gain=0.24, release=0.4)
    c.timp(67.0, 2, vel=1.0)
    c.fx("tamtam", 67.0, gain=0.45, bus="perc")
    c.fx("clash", 67.0, gain=0.25, bus="perc")
    # декламация: «Ex-or-ci-za-mus te, co-dex im-mun-de!» — хорал хора и меди
    EXO = [  # (длительность, бас, аккорд-сопрано и средние)
        (.24, 38, (62, 65, 69)), (.24, 38, (62, 65, 69)), (.24, 43, (62, 67, 70)), (.24, 39, (63, 67, 70)),
        (.36, 39, (63, 67, 67)), (.38, 38, (62, 69, 69)),
        (.22, 36, (64, 67, 67)), (.32, 34, (62, 65, 65)), (.22, 43, (62, 67, 67)), (.22, 39, (63, 67, 67)),
        (.32, 38, (62, 69, 69)),
    ]
    t = 67.2
    for d, bass, (a, b_, s) in EXO:
        for m, inst, g in ((s, "choir", 0.55), (b_, "choir", 0.45), (s - 12, "choir", 0.45),
                           (s, "tpt_sus", 0.38), (b_, "hn_sus", 0.4), (a, "hn_sus", 0.35),
                           (bass + 12, "tbn_sus", 0.45), (bass, "tba_sus", 0.45)):
            p.note(inst, m, t, d * 0.92, vel=0.92, gain=g, attack=0.02, release=0.25)
        t += d
    # «Redi in ordinem» — к белому накалу (71.5)
    REDI = [(.26, 43, (62, 67, 70)), (.26, 45, (61, 64, 69)), (.26, 46, (62, 65, 70)), (.26, 48, (64, 67, 72)),
            (.26, 45, (62, 64, 69))]
    t = 70.2
    for d, bass, (a, b_, s) in REDI:
        for m, inst, g in ((s, "choir", 0.55), (b_, "choir", 0.42), (a, "choir", 0.42), (s, "tpt_sus", 0.35),
                           (b_, "hn_sus", 0.38), (bass + 12, "tbn_sus", 0.42), (bass, "tba_sus", 0.42)):
            p.note(inst, m, t, d * 0.92, vel=0.9, gain=g, attack=0.02, release=0.2)
        t += d
    # накал: тремоло струнных нарастает 67 → 71.5
    for m, inst in ((74, "vln_trem"), (81, "vln_trem"), (69, "vla_trem"), (62, "vc_trem")):
        p.note(inst, m, 67.1, 4.4, vel=0.75, gain=0.3 if inst != "vla_trem" else 0.1, attack=4.2, release=0.25, bend=1.0 if m > 70 else 0.0)
    # 71.5 — очищено, белый накал
    for m in (26, 38, 50, 57, 62, 69, 74):
        p.note("org_loud", max(m, 24), 71.5, 2.4, vel=0.8, gain=0.22, release=1.2)
    chant(p, 71.5, [(62, 1.6)], voices=(0, -12, 12, -5), vel=0.8, gain=0.5)
    p.note("tubular", 62, 71.5, 4.0, vel=0.85, gain=0.55, release=4.0)
    p.note("tubular", 74 - 5, 71.52, 4.0, vel=0.7, gain=0.35, release=4.0)
    p.note("crotales", 98, 71.5, 3.0, vel=0.6, gain=0.22, release=3.0)
    c.timp(71.5, 2, vel=0.9)
    # остывание: высокий флажолет сползает и гаснет 14 с
    p.note("vln_harm", 98, 71.5, 13.5, vel=0.45, gain=0.18, attack=0.05, release=1.0, bend=-2.0, pan=0.35)
    p.note("vln_harm", 93, 72.5, 12.0, vel=0.4, gain=0.12, attack=1.5, release=1.0, bend=-1.0, pan=-0.35)

    # ================================================================ VIII COGITATIO RESUMPTA (71.5–80)
    for i, (m, _) in enumerate(P2):                   # cantus у тромбонов, по полтакта, финальная D — к 80
        t = 72.8 + 0.8 * i
        d = (80.0 - t) if i == len(P2) - 1 else 0.76
        p.note("tbn_sus", m, t, d, vel=0.62 + 0.03 * i, gain=0.42, attack=0.05, release=0.3)
        p.note("hn_sus", m + 12, t, d, vel=0.55 + 0.03 * i, gain=0.3, attack=0.05, release=0.3)
    for m in (38, 45):
        p.note("org_quiet", m, 72.0, 8.0, vel=0.5, gain=0.26, attack=1.0, release=0.2)
    c.timp(78.4, 2, vel=0.55, roll=1.55)
    c.fx("sso_cymbal", 77.6, gain=0.18, bus="perc", attack=2.0, dur=2.4, fade=0.05)
    c.swell(80.0, inst="org_loud", midi_=50, dur=2.6, gain=0.25)

    # ================================================================ IX RESPONSUM (80–88): D мажор, три лакуны
    DMAJ = (26, 38, 45, 50, 54, 57, 62, 66, 69, 74, 78)
    for m in DMAJ:
        p.note("org_loud", max(m, 24), 80.0, 2.3, vel=0.95, gain=0.22, release=1.6)
    for m, inst in ((50, "tbn_sus"), (57, "tbn_sus"), (62, "hn_sus"), (66, "hn_sus"), (69, "hn_sus"),
                    (74, "tpt_sus"), (78, "tpt_sus"), (38, "tba_sus")):
        p.note(inst, m, 80.0, 1.9, vel=0.95, gain=0.4, attack=0.01, release=0.9)
    chant(p, 80.0, [(62, 2.0)], voices=(0, -12, 12, -8, 4), vel=0.9, gain=0.5)
    c.timp(80.0, 2, vel=1.0)
    c.fx("clash", 80.0, gain=0.3, bus="perc")
    c.fx("tamtam", 80.0, gain=0.3, bus="perc")
    for m in (62, 69, 74 - 5):
        p.note("tubular", m, 80.0, 4.0, vel=0.85, gain=0.42, release=4.0)
    p.note("crotales", 102, 80.0, 3.0, vel=0.6, gain=0.2, release=3.0)
    # гимн в мажоре с тремя лакунами (молчит весь состав): 82.4 + 0.5·k, k = 2, 5, 7
    P1M = [(50, .5), (54, .5), (55, .5), (57, .5), (57, .5), (59, .5), (57, .5), (55, .5), (50, 1.6)]
    SK = (2, 5, 7)
    chant(p, 82.4, P1M, voices=(0, 12, 7), vel=0.62, gain=0.5, skip=SK)
    chant(p, 82.4, P1M, inst="org_quiet", voices=(0, -12), vel=0.5, gain=0.3, skip=SK)
    CH = {0: (38, 54, 57), 1: (38, 54, 57), 3: (45, 52, 57), 4: (45, 52, 61), 6: (43, 50, 59), 8: (38, 54, 57)}
    for k, chord in CH.items():
        t = 82.4 + 0.5 * k
        d = 1.6 if k == 8 else 0.5
        for m in chord:
            p.note("org_quiet", m, t, d - 0.02, vel=0.5, gain=0.28, release=0.2 if k != 8 else 1.5)
        p.note("vc_sus", chord[0] + 12, t, d - 0.02, vel=0.5, gain=0.3, release=0.2 if k != 8 else 1.2)
        p.note("cb_sus", chord[0], t, d - 0.02, vel=0.5, gain=0.32, release=0.2 if k != 8 else 1.2)

    # ================================================================ X QUIES (88–102)
    GLO = [(57, .45), (57, .45), (58, .45), (57, .45), (55, .45), (57, .45), (53, .45), (55, .45), (51, .45), (50, 1.9)]
    chant(p, 89.0, GLO, voices=(0, -7, 12), vel=0.42, gain=0.42)
    for m in (38, 45):
        p.note("org_quiet", m, 88.0, 9.0, vel=0.35, gain=0.25, attack=1.0, release=2.0)
    c.breath(93.8, 4.4, gain=0.28)
    p.note("tubular", 62, 95.6, 2.4, vel=0.35, gain=0.3, release=2.0)
    p.note("vln_harm", 98, 97.3, 1.3, vel=0.3, gain=0.12, attack=0.05, release=0.6, pan=0.4)
    c.fx("zap", 97.3, gain=0.07, shift=-9, bus="fx")

    # баланс партий по замеру --parts (эскиз 0–60 с): кант и удары механизма — вровень с хором, бас — опорой
    p.balance({"Bassoon": -22, "Trumpet": -5.5, "Contrabassoon": -6.5, "Harp": -1, "Horn": +2, "Organ": +6,
               "Violins": +2, "Cellos": +5.5, "Bass clarinet": +4, "English horn": +4.5, "Tuba": +10,
               "Trombone": +11.5, "Basses": +11, "Harpsichord": +16, "Timpani": +17, "Tubular bells": +14,
               "Violas": +14, "Xylophone": +17, "Crotales": +21})
    return p
