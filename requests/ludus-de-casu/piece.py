#!/usr/bin/env python3
"""Ludus de Casu — музыка к маске арлекинов о Падении (ludus.html, цикл 108 с).

Времена — из журнала прогона страницы (events.json → cues.json; инструменты — tools/). Такт страницы 2,4 с = три доли
по 0,8 с (сарабанда); вальсы II и IV — вдвое быстрее (такт 1,2 с). Все события лежат на сетке 0,4 с.

Сквозной процесс — бас-чакона нисходящим тетрахордом, меняющий природу:
  I    G–F♯–E–D, I–V6–vi–V — согласие;
  II   хроматическое ламенто G–F♯–F–E–E♭–D (вальс), и при каждом «не вернувшемся» па всё сползает на полутон вверх;
  III  спираль: верхний и нижний потоки сходятся в один звук, ускоряясь по кривой вихря страницы;
  IV   у Смерти свой бас — пляска смерти (скрипка соло с тритоном A–E♭ пустых струн, ксилофон-кости, Dies irae);
  V    g-moll G–F–E♭–D, i–v6–iv6–V (ламенто) — траур; тритон скрипки впервые разрешается;
  VI   маска: тот же напев в мажоре и миноре разом.
Тема труппы (сарабанда): D–G–F♯ | A–F♯–E | G–B–A | F♯–E–D. Маска: пустая квинта (I) → пересыщенный мажор (II) →
минорный вздох (IV) → оба наклонения (VI). Знаки страницы — линии: зеркальный канон (I), одинокая линия со спиралью (II),
фразы с выпавшими звуками (IV), три арки (V).

    python3 -m kit run requests/ludus-de-casu/piece.py --sketch --parts
    python3 -m kit run requests/ludus-de-casu/piece.py --parts
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from kit.devices import Composer  # noqa: E402
from kit.events import Piece  # noqa: E402

LEN = 108.0
Q, BR, WB, WQ = 0.8, 2.4, 1.2, 0.4          # доля и такт сарабанды; такт и доля вальса
G_HMIN = {7, 9, 10, 0, 2, 3, 6}
G_MIN = {7, 9, 10, 0, 2, 3, 5}


def B(n):
    return round(n * BR, 4)


def snap(m, pcs, up=False):
    for d in range(0, 12):
        for s in ((d, -d) if up else (-d, d)):
            if (m + s) % 12 in pcs:
                return m + s
    return m


# тема труппы (в долях; пунктирный подъём «Танца рыцарей»), g-moll, по тактам
T_BAR1 = [(55, .75), (58, .25), (62, .75), (67, .25), (70, 1)]                 # Gm: G B♭ D G B♭
T_BAR2 = [(69, .75), (67, .25), (66, 1), (62, 1)]                              # D/F♯
T_BAR2V = [(69, .75), (67, .25), (65, 1), (62, 1)]                             # Dm/F (V)
T_BAR3 = [(63, .75), (67, .25), (70, 1), (75, 1)]                              # E♭
T_BAR3N = [(60, .75), (63, .25), (68, 1), (72, 1)]                             # A♭/C — неаполитанский сдвиг
T_BAR4 = [(72, .75), (70, .25), (69, 1), (66, 1)]                              # D7
TROUPE = T_BAR1 + T_BAR2 + T_BAR3 + T_BAR4
TROUPE_MIN = TROUPE
# бас-чакона I: (бас, верхние звуки); второй круг — с неаполитанским аккордом в третьем такте
GROUND_I1 = [(43, (58, 62, 67)), (42, (57, 62, 66)), (39, (58, 63, 67)), (38, (57, 60, 66))]    # Gm D/F♯ E♭ D7
GROUND_I2 = [(43, (58, 62, 67)), (42, (57, 62, 66)), (36, (56, 60, 63)), (38, (57, 60, 66))]    # Gm D/F♯ A♭/C D7
GROUND_MIN = [(43, (58, 62, 67)), (41, (57, 62, 65)), (39, (55, 60, 63)), (38, (57, 62, 66))]   # Gm Dm/F Cm/E♭ D
# хроматическое ламенто вальса (по тактам вальса), от G
GROUND_LUX = [(43, (58, 62, 67)), (42, (57, 60, 62)), (41, (56, 59, 62)), (40, (55, 58, 61)),
              (39, (55, 60, 63)), (38, (57, 62, 66)), (36, (55, 60, 63)), (38, (57, 60, 62, 66))]   # Gm D7 F°7 E°7 Cm D Cm D7
MEL_LUX = [[(86, 2), (82, 1)], [(84, 2), (81, 1)], [(83, 2), (80, 1)], [(82, 2), (79, 1)],
           [(79, 1.5), (75, .5), (79, 1)], [(78, 1.5), (81, .5), (78, 1)], [(84, 1), (79, 1), (75, 1)], [(78, 2), (81, 1)]]
# вальс смерти (g-moll) по тактам вальса с 60.0
GROUND_MACABRE = [(43, (58, 62, 67)), (43, (58, 62, 67)), (43, (60, 63, 67)), (42, (57, 60, 62)), (43, (58, 62, 67)),
                  (39, (58, 63, 67)), (38, (57, 60, 66)), (43, (58, 62, 67)), (36, (60, 63, 67)), (38, (57, 60, 62, 66))]
DIES_IRAE = [58, 57, 58, 55, 57, 53, 55, 55]          # средневековый напев (общедоступен), в g-moll


def build(ctx):
    cues = ctx.cues
    p = Piece("Ludus de Casu", bpm=75, meter=(3, 4), key="G minor", seed=31)
    p.meta["length"] = LEN
    c = Composer(p, lib="vsco", seed=31)
    rng = p.rng
    for e in cues["cues"]:
        if e["kind"] == "section":
            p.mark(e["t"], e["label"])
    G = {g["name"]: g for g in cues["glyphs"]}

    def chord_I(t):
        i = int((t - B(2)) / BR + 1e-6)
        return (GROUND_I1 if i < 4 else GROUND_I2)[i % 4]

    def chord_V(t):
        return GROUND_MIN[int((t - 72.0) / BR + 1e-6) % 4]

    def pcs_of(ch):
        return {x % 12 for x in ch[1]} | {ch[0] % 12}

    def n(inst, m, t, d, vel=.5, gain=.4, **kw):
        p.note(inst, m, t, max(.05, d), vel=vel, gain=gain, **kw)

    def chord(inst, ms, t, d, vel=.5, gain=.3, **kw):
        for m in ms:
            n(inst, m, t, d, vel, gain, **kw)

    def line(inst, seq, t0, unit, vel=.55, gain=.4, gap=.04, tr=0, skip=(), release=.4, pan=0., **kw):
        t = t0
        for k, (m, d) in enumerate(seq):
            if m is not None and k not in skip:
                n(inst, m + tr, t, d * unit - gap, vel, gain, release=release, pan=pan, **kw)
            t += d * unit
        return t

    def laugh(t, ms, inst="fl_stac", vel=.6, gain=.3, step=Q / 3):
        for k, m in enumerate(ms):
            n(inst, m, t + k * step, step * .8, vel - .05 * k, gain, release=.15)

    def sarabande_bar(t, bass, upper, inst_r="hpsd", vel=.5, gain=.3, organ=.0, bass_insts=(("vc_sus", .38), ("cb_sus", .34))):
        # континуо: аккорд на первой доле (арпеджио клавесина) и опора на второй — акцент сарабанды
        for k, m in enumerate(upper):
            n(inst_r, m, t + k * .03, Q * .95, vel, gain, release=.5)
        for m in upper:
            n(inst_r, m, t + Q, Q * 1.9, vel * .9, gain * .9, release=.6)
        for inst, g in bass_insts:
            n(inst, bass, t, BR - .05, .5, g, release=.5)
        if organ:
            n("org_quiet", bass, t, BR - .02, .45, organ, release=.3)
            for m in upper:
                n("org_quiet", m - 12, t, BR - .02, .4, organ * .55, release=.3)

    def knight_bar(t, bass, upper, heavy=1.0, bass_insts=(("vc_sus", .4), ("cb_sus", .38), ("tba_sus", .26))):
        # тяжёлая поступь: бас и литавра на первой доле, короткие аккорды валторн и альтов на второй и третьей
        for inst, g_ in bass_insts:
            n(inst, bass, t, Q * .85, .7, g_ * heavy, release=.3)
        c.timp(t, bass % 12, vel=.55 + .2 * heavy)
        if heavy > .9:
            c.fx("bd_soft", t, gain=.16 * heavy, bus="perc")
        for b in (1, 2):
            for m in upper:
                n("hn_stac", m - 12, t + b * Q, .3, .6, .16 * heavy, release=.2)
            for m in upper[:2]:
                n("vla_spic", m, t + b * Q, .2, .6, .14 * heavy, release=.15)

    # ================================================================== ПРОЛОГ (0–4.8)
    n("harp", 67, .6, 3.0, .45, .35, release=3.0)
    n("vln_harm", 91, .6, 3.8, .35, .24, attack=.5, release=1.0)
    n("org_quiet", 43, 1.0, 3.9, .45, .42, attack=1.6, release=.6)
    n("org_quiet", 50, 1.6, 3.3, .4, .26, attack=1.6, release=.6)
    # занавес раскрывается от середины в обе стороны — два зеркальных арпеджио арфы
    for k, (up, dn) in enumerate(zip([67, 70, 74, 79, 82, 86], [67, 62, 58, 55, 50, 43])):
        n("harp", up, B(2) + k * .2, 1.1 - k * .15, .5, .32, release=.8, pan=.35)
        if k:
            n("harp", dn, B(2) + k * .2, 1.1 - k * .15, .5, .3, release=.8, pan=-.35)

    # занавес раскрылся — резкий аккорд-удар: Gm с малой ноной (A♭) и тритоном в басу, затем шёпот
    for m, inst, g_ in ((31, "cb_sus", .45), (37, "tba_sus", .4), (43, "tbn_sus", .42), (49, "tbn_sus", .36), (56, "hn_sus", .4),
                        (58, "hn_sus", .36), (62, "tpt_sus", .32), (68, "tpt_sus", .3), (70, "vln_sus", .36), (74, "vln_sus", .34)):
        n(inst, m, B(2), .45, 1.0, g_, release=.35)
    c.timp(B(2), 7, vel=1.0)
    c.fx("bd", B(2), gain=.3, bus="perc")
    c.fx("clash", B(2), gain=.18, bus="perc", dur=.8, fade=.5)

    # ================================================================== I AUREA AETAS (4.8–24): тяжёлый танец рыцарей
    THEME_I = [T_BAR1, T_BAR2, T_BAR3, T_BAR4, T_BAR1, T_BAR2, T_BAR3N, T_BAR4]
    for i in range(8):
        t = B(2 + i)
        bass, up = chord_I(t)
        swap = i == 6                                        # волна на изнанку: тема уходит в бас, бас — наверх
        knight_bar(t, bass, up, heavy=.75 if i < 4 else 1.0,
                   bass_insts=(("tba_sus", .26),) if swap else (("vc_sus", .4), ("cb_sus", .38), ("tba_sus", .26)))
        if swap:
            n("vln_sus", bass + 36, t, BR - .05, .55, .26)
            line("vc_sus", [(m - 12, d) for m, d in THEME_I[i]], t, Q, vel=.7, gain=.5, release=.3)
            line("cb_sus", [(m - 24, d) for m, d in THEME_I[i]], t, Q, vel=.6, gain=.3, release=.3)
            continue
        line("vln_sus", THEME_I[i], t, Q, vel=.62 if i < 4 else .72, gain=.44, release=.3)
        line("vc_sus", [(m - 12, d) for m, d in THEME_I[i]], t, Q, vel=.6, gain=.34, release=.3)
        if i >= 4:
            line("hn_sus", THEME_I[i], t, Q, vel=.65, gain=.26, release=.3)
    # знак согласия (12.0–16.8): двое пишут зеркально — к теме добавляется её зеркальное обращение у гобоя,
    # прижатое к звукам аккорда на сильных долях
    g0 = G["ordo"]["t0"]
    src = []
    t = B(2)
    for bar in THEME_I:
        for m, d in bar:
            src.append((t, m, d)); t += d * Q
    for (t, m, d) in src:
        if not (g0 - 1e-6 <= t < G["ordo"]["t1"] - 1e-6):
            continue
        pcs = pcs_of(chord_I(t))
        mm = 2 * 71 - m
        mm = snap(mm, pcs)
        n("ob_sus", mm, t, d * Q - .05, .6, .4, release=.3, pan=-.3)
        n("fl_sus", mm, t, d * Q - .05, .5, .2, release=.3, pan=-.3)
    # па: скольжения — короткие сбеги арфы, повороты — подъём по аккорду, смех — три звука
    for tg in (B(3), B(6)):
        for k, m in enumerate([79, 74, 70, 67] if chord_I(tg)[0] == 43 else [78, 74, 69, 66]):
            n("harp", m, tg + k * .1, .6, .4, .2, release=.6)
    for ts in (B(4), B(7)):
        bass, up = chord_I(ts)
        for k, m in enumerate([bass + 12] + list(up) + [up[0] + 12]):
            n("harp", m, ts + k * .08, 1.0, .42, .22, release=1.0)
    laugh(B(5), [86, 81, 78], inst="picc_sus", gain=.2)
    # тень маски — пустая квинта флажолетами (контур без лица)
    for th in (B(4), B(7), B(9)):
        r = [7, 2, 3, 2][int((th - B(2)) / BR + 1e-6) % 4]   # пустая квинта на основном тоне аккорда (G, D, E♭, D)
        n("vln_harm", 84 + r if r < 7 else 72 + r, th, 1.0, .35, .15, attack=.25, release=.6)
        n("vln_harm", (84 + r if r < 7 else 72 + r) + 7, th, 1.0, .35, .12, attack=.25, release=.6)
        n("harp", 60 + r, th, 1.2, .35, .18, release=1.2)
        n("harp", 67 + r, th + .05, 1.2, .35, .16, release=1.2)

    # ================================================================== II LUXURIA (24–43.2): вальс Одиночки
    def tr_at(t):
        return 0 if t < 28.8 - 1e-6 else 1 if t < 37.2 - 1e-6 else 2
    g = G["lux"]
    for k in range(16):
        t = 24.0 + WB * k
        tr = tr_at(t)
        bass, up = GROUND_LUX[k % 8]
        if k >= 14:                                         # её маска: зловещий a-moll с большой септимой на педали
            bass, up = 43, (58, 62, 66)                       # (+2 = A: A, C E G♯)
        alone = g["t0"] - 1e-6 <= t < g["t1"] - 1e-6        # Одиночка пишет свой знак одна: только бас и арфа
        n("cb_pizz", bass + tr, t, .35, .65, .45, release=.3)
        n("harp", bass + 12 + tr, t, .8, .5, .25, release=.6)
        if not alone:
            for b in (1, 2):
                for m in up:
                    n("vla_pizz" if m < 64 else "vln_pizz", m + tr, t + b * WQ, .3, .5, .2, release=.25)
        if k >= 12:                                         # всё в её цветах: струнные и валторны держат
            for m in up:
                n("hn_sus", m - 12 + tr, t, WB - .05, .55, .14, release=.3)
        if not alone:
            mel = MEL_LUX[k % 8]
            tt = t
            for j, (m, d) in enumerate(mel):
                mm = m + tr
                dd = d * WQ
                orn = k >= 8 and d >= 2                       # избыток растёт: трели на долгих звуках
                if orn:
                    up_n = mm + 1                                 # трели — полутоном, как дрожь
                    for r in range(int(dd / .1)):
                        n("fl_sus", up_n if r % 2 else mm, tt + r * .1, .09, .55, .3, release=.08)
                else:
                    n("fl_sus", mm, tt, dd - .03, .55, .34, release=.3)
                low = max(x + tr for x in up + (up[0] - 12,) if (x + tr) <= mm - 3)
                n("cl_sus", low, tt, dd - .03, .5, .3, release=.3)
                if k >= 12:
                    n("vln_sus", mm - 12, tt, dd - .03, .55, .3, release=.3)
                tt += dd
    # входит Одиночка: вкрадчивый хроматический подъём кларнета
    for k, m in enumerate([55, 56, 57, 58, 59]):
        n("cl_leg", m, 24.0 + k * .24, .26, .45, .3, release=.1)
    # поворот с перебором: подъём арфы проскакивает лишний полутон
    for k, m in enumerate([62, 65, 68, 71, 74, 77, 80, 81]):     # F°7 — и лишний полутон сверху
        n("harp", m, 26.4 + k * .07, .9, .5, .22, release=.9)
    # па не возвращаются: струнные съезжают на полутон и остаются
    for tb in (28.8, 37.2):
        for m in (67, 74):
            n("vln_sus", m + tr_at(tb - .1), tb - .3, .7, .5, .2, bend=1.0, release=.2)
    # её знак (31.2–36.0): тема труппы одна, в ритме вальса, с увеличенными секундами — и хвост-спираль
    tr = 1
    for k, (m, d) in enumerate(TROUPE):                    # венгерский минор: C → C♯ даёт увеличенные секунды
        tt = g["t0"] + k * WQ * .75
        if tt >= 34.8:
            break
        mm = m + 12 + tr + (1 if m % 12 == 0 else 0)
        n("fl_sus", mm, tt, WQ * .7, .6, .38, release=.25)
    spiral = [88, 87, 86, 84, 85, 83, 82, 80, 81, 79, 78, 76]
    for k, m in enumerate(spiral):
        n("fl_sus", m + tr - 2, 34.8 + k * .1, .1, .6, .34, release=.1)
        n("cl_sus", m + tr - 14, 34.8 + k * .1, .1, .5, .22, release=.1)
    laugh(33.6, [92, 91, 90, 89, 88], inst="picc_sus", vel=.55, gain=.18, step=Q / 3)
    # всё в её цветах (38.4): тарелка нарастает к удару
    c.fx("sso_cymbal", 36.6, gain=.18, bus="perc", attack=1.6, dur=1.9, fade=.05)
    c.timp(38.4, 9, vel=.75)
    # её маска — смеющаяся половина: a-moll с большой септимой и ноной — сладость с ядом
    for m, inst in ((57, "vc_sus"), (69, "vla_sus"), (72, "vln_sus"), (76, "vln_sus"), (80, "vln_sus"), (83, "vln_harm"), (88, "vln_harm")):
        n(inst, m, 40.8, 43.2 - 40.8 + .4, .55, .2, attack=.4, release=.3)
    for k, m in enumerate([69, 72, 76, 80, 83, 88, 92]):
        n("harp", m, 40.8 + k * .09, 1.6, .5, .24, release=1.4)

    # ================================================================== III CASUS (43.2–55.2): две спирали сходятся
    def vv(t):
        return ((t - 43.2) / 12.0) ** 1.6
    t = 43.2
    k = 0
    while t < 55.15:
        v = vv(t)
        ioi = .30 + (.045 - .30) * v ** .8
        osc = [0, 3, 1, 4][k % 4] * (1 - v)
        hi = round(96 + (74 - 96) * v + osc)
        lo = round(28 + (50 - 28) * v - osc)
        vel = .45 + .5 * v
        g_ = .3 + .2 * v
        n("vln_spic", min(hi, 100), t, min(.12, ioi * .8), vel, g_, release=.1, pan=.3)
        if v > .3:
            n("fl_stac", min(hi, 96), t, min(.1, ioi * .7), vel, g_ * .7, release=.08, pan=.35)
        n("vc_spic", max(lo, 36), t, min(.12, ioi * .8), vel, g_, release=.1, pan=-.3)
        if v > .45:
            n("bsn_stac", max(lo, 34), t, min(.1, ioi * .7), vel, g_ * .7, release=.08, pan=-.35)
        t += ioi
        k += 1
    # бас-спираль: хроматически вниз, всё чаще, к D
    t, bass, step = 43.2, 46, 1.8
    while t < 54.8 and bass >= 38:
        for inst, g_ in (("tba_sus", .32), ("cb_sus", .36)):
            n(inst, bass, t, step * .95, .6, g_, release=.2)
        t += step
        step = max(.4, step * .72)
        bass -= 1
    c.shepard(43.2, 54.8, up=False, gain=.2)
    c.timp(51.0, 2, vel=.7, roll=4.1)
    c.fx("sso_cymbal", 52.8, gain=.22, bus="perc", attack=2.2, dur=2.45, fade=.05)
    # вспышка (55.2): всё сходится в один звук D во всех октавах — и тьма
    for m, inst, g_ in ((26, "cbsn_sus", .45), (38, "tba_sus", .45), (38, "cb_sus", .45), (50, "tbn_sus", .45), (62, "hn_sus", .45),
                        (62, "vla_sus", .4), (74, "vln_sus", .42), (74, "tpt_sus", .4), (86, "vln_sus", .35), (86, "picc_sus", .25)):
        n(inst, m, 55.2, .35, 1.0, g_, release=.45)
    for m in (26, 38, 50, 62, 74):
        n("org_loud", m, 55.2, .35, .95, .22, release=.5)
    c.timp(55.2, 2, vel=1.0)
    c.fx("tamtam", 55.2, gain=.36, bus="perc", dur=1.4, fade=.9)
    c.fx("clash", 55.2, gain=.26, bus="perc", dur=1.0, fade=.7)

    # ================================================================== IV RUINA (57.6–72): пляска смерти
    for k in range(4):                                     # полночные удары арфы
        n("harp", 50, 57.6 + k * .4, 1.0, .6, .38, release=1.0)
        n("harp", 38, 57.6 + k * .4, 1.0, .6, .32, release=1.0)
    n("cb_pizz", 38, 57.6, .4, .6, .35, release=.4)
    # Шут настраивает скрипку: тритон A–E♭ пустых струн
    for t0, d in ((59.2, .7), (60.0, .35), (60.4, .35)):
        n("vln_solo", 69, t0, d, .75, .45, release=.25)
        n("vln_solo", 75, t0, d, .75, .42, release=.25)
    gr = G["ruin"]
    for k, (bass, up) in enumerate(GROUND_MACABRE):
        t = 60.0 + WB * k
        fade = 1.0 if k < 7 else .7 if k < 9 else .45
        n("cb_pizz", bass, t, .35, .6, .45 * fade, release=.3)
        n("vc_pizz", bass + 12, t, .35, .55, .3 * fade, release=.3)
        for b in (1, 2):
            for m in up[:3]:
                n("vla_pizz" if m < 62 else "vln_pizz", m, t + b * WQ, .3, .5, .18 * fade, release=.2)
        if k in (0, 1, 7, 8, 9):                          # кости
            for b in (1, 2):
                n("xylo", 79 if b == 1 else 74, t + b * WQ, .15, .7, .26 * fade, release=.15)
    # мотив Смерти: двойная нота тритона на сильной доле и хроматический спуск
    for k in range(2):
        t = 60.0 + WB * k
        n("vln_solo", 69 - k, t, .35, .75, .45, release=.2)
        n("vln_solo", 75 - k, t, .35, .75, .42, release=.2)
        for j, m in enumerate([79, 78, 77, 76]):
            n("vln_solo", m - k, t + WQ + j * .2, .18, .7, .42, release=.12)
            n("xylo", m - k + 12, t + WQ + j * .2, .12, .65, .2, release=.12)
    # обломки знака (62.4–67.2): тема труппы в миноре, по доле вальса, каждый третий звук выпал
    for k, (m, d) in enumerate(TROUPE_MIN):
        if k % 3 == 2:
            continue
        n("vln_solo", m, gr["t0"] + k * WQ, WQ * .8, .7, .44, release=.2)
    # Dies irae у фаготов, под обломками
    for k, m in enumerate(DIES_IRAE):
        n("bsn_sus", m - 12, 64.8 + k * .6, .55, .5, .3, release=.25)
        n("cbsn_sus", m - 24, 64.8 + k * .6, .55, .5, .28, release=.25)
    # Шут уходит — проступает плачущая половина: вздохи E♭–D, всё тише
    for k, t in enumerate((67.2, 68.4, 69.6, 70.8)):
        v = .65 - .1 * k
        n("vln_solo", 75, t, .75, v, .4 - .06 * k, release=.15)
        n("vln_solo", 74, t + .8, .35, v - .05, .36 - .06 * k, release=.3)
        n("vla_harm", 70, t, 1.1, .4, .1, attack=.2, release=.5)
    # тритон разрешается — смеётся Бог
    n("vln_solo", 69, 71.6, .38, .8, .45, release=.05)
    n("vln_solo", 75, 71.6, .38, .8, .42, release=.05)
    n("vln_solo", 70, 72.0, 1.5, .8, .45, release=.6)
    n("vln_solo", 74, 72.0, 1.5, .8, .42, release=.6)

    # ================================================================== V RISUS (72–91.2): траурная чакона
    for m in (31, 43, 50, 55, 58, 62, 67, 70, 74):
        n("org_loud", m, 72.0, 1.6, .85, .2, release=1.0)
    c.timp(72.0, 7, vel=.85)
    c.fx("tamtam", 72.0, gain=.22, bus="perc")
    laugh(72.0, [74, 70, 67], inst="hn_stac", vel=.8, gain=.4)
    for k, m in enumerate([55, 58, 62, 67, 70, 74, 79, 82]):    # сборка из середины — вверх
        n("harp", m, 72.0 + k * .12, 1.2, .55, .3, release=.8)
    for j in range(2):                                     # тремоло нарастает, следуя чаконе
        bass, up = GROUND_MIN[j]
        for m, inst in ((up[2] + 12, "vln_trem"), (up[1] + 12, "vln_trem"), (up[0], "vla_trem"), (bass + 12, "vc_trem")):
            t0 = 72.2 if j == 0 else 72.0 + BR * j
            n(inst, m, t0, 72.0 + BR * (j + 1) - .12 - t0, .6, .14 + .08 * j, attack=2.0 if j == 0 else .2, release=.2)
    rg = G["risus"]
    for cyc in range(2):
        for k, (bass, up) in enumerate(GROUND_MIN):
            t = 72.0 + BR * (4 * cyc + k)
            sarabande_bar(t, bass, up, organ=.22, vel=.5, gain=.24)
            n("hn_sus", up[-1] - 12, t, BR - .05, .45, .12, release=.4)
    THEME_V = T_BAR1 + T_BAR2V + [(63, .75), (67, .25), (72, 1), (75, 1)] + T_BAR4
    line("hn_sus", THEME_V, 72.0, Q, vel=.7, gain=.44, release=.3)
    line("tbn_sus", [(m - 12, d) for m, d in THEME_V], 72.0, Q, vel=.6, gain=.26, release=.3)
    # второй круг: два такта — знак смеха (три арки, трое), затем вторая половина темы у скрипок
    ARCH = [0, 1, 2, 3, 4, 5, 4, 3, 2, 1, 0, -1]
    scale = sorted({m for m in range(48, 96) if m % 12 in G_MIN})
    for v, (base, inst, g_) in enumerate(((67, "cl_sus", .34), (70, "ob_sus", .3), (74, "fl_sus", .3))):
        i0 = scale.index(base)
        for k, st in enumerate(ARCH):
            t = rg["t0"] + k * WQ
            bar = int((t - 72.0) / BR + 1e-6) % 4
            m = scale[i0 + st]
            if k % 2 == 0:
                pcs = {x % 12 for x in GROUND_MIN[bar][1]} | {GROUND_MIN[bar][0] % 12}
                m = snap(m, pcs)
            n(inst, m, t, WQ * .9, .55, g_, release=.25, pan=(v - 1) * .4)
    line("vln_sus", [(m + 12, d) for m, d in THEME_V[9:]], 86.4, Q, vel=.62, gain=.42, release=.3)
    line("vc_sus", THEME_V[9:], 86.4, Q, vel=.6, gain=.34, release=.3)
    laugh(79.2, [81, 78, 74])
    laugh(84.0, [86, 81, 77])
    for k, t in enumerate([79.2 + 1.6 * j for j in range(8)]):     # нити Паутины — блики арфы по звукам аккорда
        up = sorted(m + 24 for m in chord_V(t)[1])
        n("harp", up[k % 3], t, .7, .4, .16, release=.6, pan=.5 - .14 * k)
    for k, m in enumerate([74, 69, 66, 62]):
        n("harp", m, 88.8 + k * .1, .6, .4, .2, release=.6)

    # ================================================================== VI LARVA (91.2–100.8): маска
    n("org_quiet", 43, 91.2, 4.8, .45, .22, release=.4)
    n("org_quiet", 50, 91.2, 4.8, .4, .16, release=.4)
    # двое обводят контур — одна линия сверху вниз в октаву (зеркальные половины движутся одинаково по высоте)
    CONT = [86, 84, 82, 81, 79, 77, 74, 72, 70, 69, 67, 62]
    for k, m in enumerate(CONT):
        t = 91.2 + k * WQ
        n("vln_sus", m, t, WQ * .95, .5, .32, release=.3)
        n("vln_sus", m - 12, t, WQ * .95, .5, .26, release=.3)
    # третий — черты: два глаза (опевания) и рот (дуга)
    for k, m in enumerate([79, 81, 79, 78, 79]):
        n("cl_sus", m - 12, 92.4 + k * .16, .15, .5, .28, release=.1)
    for k, m in enumerate([79, 81, 79, 78, 79]):
        n("cl_sus", m - 12, 93.6 + k * .16, .15, .5, .28, release=.1)
    for k, m in enumerate([74, 72, 70, 72, 74]):
        n("cl_sus", m - 12, 94.8 + k * .24, .22, .5, .28, release=.15)
    # половины сходятся (96): один минорный напев двумя лицами — смех (стаккато, ксилофон, пикколо) и плач (легато)
    FACE = [(74, 1), (79, 1), (82, 1.5), (81, .5), (79, 2)]
    for k, (m, d) in enumerate(FACE):
        t = 96.0 + sum(x[1] for x in FACE[:k]) * Q
        for j in range(int(d * 2)):
            n("xylo", m + 12, t + j * WQ, .12, .7, .2, release=.1)
            n("picc_sus", m + 12, t + j * WQ, .12, .55, .12, release=.08)
    line("cl_sus", [(x - 12, dd) for x, dd in FACE], 96.0, Q, vel=.55, gain=.36, release=.6)
    line("vln_sus", [(x - 12, dd) for x, dd in FACE], 96.0, Q, vel=.5, gain=.26, release=.6)
    chord("org_quiet", (43, 55, 58, 62), 96.0, 4.75, .45, .18, release=.6)
    chord("vla_sus", (67, 70, 74), 96.0, 4.75, .45, .16, attack=.3, release=.6)
    for k, m in enumerate([67, 70, 74, 79]):
        n("harp", m, 96.0 + k * .1, 2.0, .5, .26, release=1.8)
    laugh(98.4, [86, 82, 79], vel=.5, gain=.22)
    laugh(98.8, [74, 70, 67], inst="cl_stac", vel=.5, gain=.22)

    # ================================================================== EXODIUM (100.8–108)
    for k, m in enumerate([67, 65, 63, 62, 60, 58, 57, 55]):
        n("vc_sus", m - 12, 100.8 + k * .3, .32, .45, .32, release=.3)
    n("cb_sus", 31, 102.6, .6, .4, .3, release=1.0)
    n("harp", 67, 103.2, 3.2, .45, .34, release=3.0)
    n("vln_harm", 91, 103.2, 2.6, .3, .14, attack=.4, release=1.0)
    n("org_quiet", 43, 103.2, 2.4, .35, .16, attack=.5, release=1.2)

    # баланс партий по замеру --parts
    p.balance({"Contrabassoon": -12, "Bassoon": -14, "Flute": -6, "Piccolo": -8, "Trumpet": -4, "Timpani": +5, "Horn": +2,
               "Violins": +6, "Harp": +4, "Basses": +6, "Violas": +3, "Tuba": +10, "Organ": +8, "Harpsichord": +11,
               "Trombone": +12, "Violin solo": +4, "Xylophone": +9})
    return p
