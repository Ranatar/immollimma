#!/usr/bin/env python3
"""Namárië — литания в манере «The Passing of the Elves» (≈ 3:00).

От разобранной песни Plan 9 — только приём: два голоса хора в одном ритме (речитатив на одном тоне и напев),
бурдон на квинте, который «дышит» каждые два такта под тихий удар, мерцающая терция, мажорный свет в конце.
Своё: речитатив на квинте ля, а не на тонике; «падающие листья» альтовой флейты; бурдон меняется по смыслу строк.

Текст Толкина в ноты не вписан. Каждая из 17 строк — два такта; ритм голосов построен по числу слогов строки
и долгому ударному слогу (SYL, LONG), так что текст подкладывается под ноты слог в слог.

  строки 1–4    голоса одни
  строки 5–7    бурдон ре–ля и удар литавры раз в два такта; фа на подъёмах, фа-диез на остановках
  строка 8      вопрос: всё смолкает, один напев
  строки 9–12   тьма: бурдон си-бемоль–фа, речитатив на фа
  строки 13–14  туман: бурдон до–соль, речитатив на соль
  строка 15     утрата: ре–ля, речитатив на октаву выше — кульминация
  строки 16–17  прощание: только фа-диез, последний аккорд — ре мажор

    python3 -m kit run requests/namarie/piece.py --parts
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from kit.events import Piece  # noqa: E402

BPM = 52
SPB = 60 / BPM
LINE = 8  # долей на строку (два такта)

# число слогов каждой строки и номер долгого (ударного, распетого) слога
SYL = [11, 12, 11, 12, 10, 13, 10, 10, 13, 12, 12, 12, 12, 13, 12, 12, 10]
LONG = [2, 1, 1, 4, 1, 2, 0, 3, 3, 2, 2, 2, 2, 1, 2, 1, 2]

# напев (хор II): шаблоны контура, растягиваются на число слогов строки
RISE = [57, 62, 62, 64, 65, 65, 64, 62, 64, 65, 67, 69]          # подъём к ля (фа на подъёме)
FALL_L = [69, 69, 67, 65, 64, 62, 64, 65, 64, 62, 64, 66]        # спуск, остановка на фа-диезе — свет
FALL_D = [69, 69, 67, 65, 64, 62, 64, 65, 64, 62, 60, 62]        # спуск к ре
QUEST = [69, 69, 70, 69, 67, 65, 64, 65, 67, 65, 64, 64]         # вопрос: повисает на ми
DARK_R = [58, 58, 60, 62, 62, 60, 58, 57, 58, 60, 62, 65]        # над си-бемолем: к фа
DARK_F = [65, 65, 62, 62, 60, 58, 60, 62, 60, 58, 57, 58]        # над си-бемолем: к си-бемолю
MIST_R = [62, 64, 67, 67, 65, 64, 62, 64, 65, 67, 69, 67]        # над до: к соль
MIST_F = [67, 67, 65, 64, 62, 60, 62, 64, 62, 60, 62, 64]        # над до: к ми
LOSS = [69, 74, 74, 76, 77, 77, 76, 74, 72, 70, 69, 69]          # утрата: вершина, фа натуральное
FARE1 = [62, 66, 66, 67, 69, 69, 71, 69, 67, 66, 64, 66]         # прощание: фа-диез, си натуральное
FARE2 = [69, 69, 67, 66, 64, 62, 64, 66, 64, 62, 61, 62]         # к ре

# строка: (контур, речитатив, бурдон (корень, квинта) или None, флейта: (ряд, держать) или None)
LEAF_D = ([81, 79, 77, 76, 74], 74)
LEAF_L = ([81, 79, 78, 76, 74], 74)
LEAF_B = ([79, 77, 74, 72, 70], 70)
LEAF_C = ([79, 77, 76, 74, 72], 72)
LEAF_X = ([86, 84, 81, 79, 77], 77)
LINES = [
    (RISE, 69, None, None), (FALL_L, 69, None, None), (RISE, 69, None, LEAF_D), (FALL_L, 69, None, None),
    (RISE, 69, (38, 45), LEAF_D), (FALL_L, 69, (38, 45), None), (RISE, 69, (38, 45), LEAF_D),
    (QUEST, None, None, None),
    (DARK_R, 65, (34, 41), None), (DARK_F, 65, (34, 41), LEAF_B), (DARK_R, 65, (34, 41), None),
    (DARK_F, 65, (34, 41), LEAF_B),
    (MIST_R, 67, (36, 43), LEAF_C), (MIST_F, 67, (36, 43), None),
    (LOSS, 74, (38, 45), LEAF_X),
    (FARE1, 69, (38, 45), LEAF_L), (FARE2, 69, (38, 45), None),
]


def rhythm(n, long_i):
    """слоги строки: начало после восьмой паузы, слоги восьмыми, долгий слог длиннее, последний — самый долгий"""
    extra = min(1.0, max(0.0, 7.5 - 0.5 * (n - 1) - 1.5))
    last = 7.5 - 0.5 * (n - 1) - extra
    out, b = [], 0.5
    for i in range(n):
        d = last if i == n - 1 else 0.5 + (extra if i == long_i else 0.0)
        out.append((b, d))
        b += d
    return out


def stretch(tpl, n):
    """шаблон контура на n слогов: последняя нота шаблона — на последний слог"""
    if n == len(tpl):
        return list(tpl)
    return [tpl[min(len(tpl) - 2, round(i * (len(tpl) - 2) / max(1, n - 2)))] for i in range(n - 1)] + [tpl[-1]]


class Lit:
    def __init__(self):
        self.p = Piece("Namárië", bpm=BPM, meter=(4, 4), key="D minor", seed=1954)
        self.p.meta["subtitle"] = "литания в манере «The Passing of the Elves» (текст в ноты не вписан)"
        self.slow = []

    def perf(self, beat):
        s = 0.0
        for b0, b1, f in sorted(self.slow):
            if beat <= b0:
                break
            s += (min(beat, b1) - b0) * (f - 1)
        return (beat + s) * SPB

    def n(self, inst, m, beat, dur, part, vel=0.55, gain=0.5, attack=0.08, release=0.6, legato=0.97, pan=0.0):
        t0, t1 = self.perf(beat), self.perf(beat + dur)
        e = self.p.note(inst, m, t0, max(0.05, (t1 - t0) * legato), vel=vel, gain=gain, attack=attack,
                        release=release, part=part, pan=pan)
        e["wt"], e["wdur"] = beat * SPB, dur * SPB
        return e


def build(ctx):
    o = Lit()
    # исполнение: вопрос (строка 8) свободнее, конец шире
    o.slow += [(56, 64, 1.18), (128, 136, 1.08), (136, 144, 1.5)]
    plan = []
    labels = {0: "Строки 1–4: голоса без баса", 4: "Строки 5–7: бурдон входит", 7: "Строка 8: вопрос",
              8: "Строки 9–12: тьма", 12: "Строки 13–14: туман", 14: "Строка 15: утрата", 15: "Строки 16–17: прощание"}
    for li, (tpl, rec, drone, leaf) in enumerate(LINES):
        b0 = li * LINE
        if li in labels:
            plan.append((b0, labels[li]))
        rh = rhythm(SYL[li], LONG[li])
        tune = stretch(tpl, SYL[li])
        loud = 0.62 if li == 14 else 0.5
        for (b, d), m in zip(rh, tune):
            o.n("choir", m, b0 + b, d, "Choir II", vel=0.55, gain=loud * (0.8 if li == 7 else 1.0), pan=-0.15)
            if rec is not None:
                o.n("choir", rec, b0 + b, d, "Choir I", vel=0.5, gain=loud * 0.8, pan=0.2)
        if li == 14:  # утрата: речитатив ещё и октавой ниже
            for (b, d) in rh:
                o.n("choir", 62, b0 + b, d, "Choir I", vel=0.5, gain=0.4, pan=0.2)
        if drone is not None:  # бурдон дышит: удар, нарастание, угасание к концу двух тактов
            root, fifth = drone
            g = 0.55 if li != 14 else 0.65
            o.n("cb_sus", root, b0, 7, "Contrabassi", vel=0.55, gain=g, attack=1.8, release=1.2, legato=1.0)
            o.n("vc_sus", fifth, b0, 7, "Violoncelli", vel=0.5, gain=g * 0.75, attack=2.0, release=1.2, legato=1.0)
            o.n("timp", root + 12, b0, 1.5, "Timpani", vel=0.42 if li < 8 else 0.5, gain=0.45, release=1.5)
        if leaf is not None:  # падающие листья: восьмые вниз в середине строки, затем долгая нота
            run, hold = leaf
            for i, m in enumerate(run):
                o.n("afl_sus", m, b0 + 4.5 + i / 2, 0.5, "Alto Flute", vel=0.5, gain=0.42, attack=0.03, legato=0.95, pan=0.3)
            o.n("afl_sus", hold, b0 + 7, 1.0, "Alto Flute", vel=0.48, gain=0.38, attack=0.05, release=0.8, pan=0.3)
    # конец: ре мажор, бурдон выдыхает
    fin = len(LINES) * LINE
    plan.append((fin, "Конец"))
    for m, part in ((62, "Choir II"), (66, "Choir II"), (69, "Choir I"), (74, "Choir I")):
        o.n("choir", m, fin, 6, part, vel=0.5, gain=0.45, attack=0.4, release=1.6)
    o.n("afl_sus", 78, fin + 1, 5, "Alto Flute", vel=0.45, gain=0.32, attack=0.6, release=1.4, pan=0.3)
    o.n("cb_sus", 38, fin, 7.5, "Contrabassi", vel=0.5, gain=0.5, attack=1.2, release=2.0, legato=1.0)
    o.n("vc_sus", 45, fin, 7.5, "Violoncelli", vel=0.45, gain=0.38, attack=1.4, release=2.0, legato=1.0)
    o.n("timp", 50, fin, 2, "Timpani", vel=0.35, gain=0.4, release=2.0)
    for bt, label in plan:
        o.p.mark(o.perf(bt), label)["wt"] = bt * SPB
    o.p.meta["beats"] = fin + 8
    # замер `--parts` без баланса: хор II −28.5, флейта −28.9, хор I −32.0, контрабасы −34.3, виолончели −40.5,
    # литавры −49.6 LUFS — бурдон и удар тонули; флейта вровень с напевом
    o.p.balance({"Alto Flute": -2, "Contrabassi": +3, "Violoncelli": +5, "Timpani": +9})
    return o.p
