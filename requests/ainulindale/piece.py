#!/usr/bin/env python3
"""Ainulindalë — Музыка Айнур (≈ 3:44, темп 60: доля = секунда).

Нотный текст Великой Музыки — music.py (тема, ответ, проведения, обращение, минор, вбирание; свободные голоса найдены
поиском по гармоническому плану и проверены на параллели и диссонансы на долях) → music.json. Здесь — оркестровка:
кто играет какой голос в каком разделе, унисон Мелькора и захват голосов, буря, рябь, видение, Эа.

    python3 requests/ainulindale/music.py      # пересчитать голоса → music.json
    python3 -m kit run requests/ainulindale/piece.py --sketch --parts
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from kit.devices import Composer  # noqa: E402
from kit.events import Piece  # noqa: E402

LEN = 224.0

# оркестровка голосов по разделам: голос → [(инструмент, усиление, сдвиг в полутонах)]
ORCH = [
    (20, 36, {"A": [("choir", 1.0, 0)]}),
    (36, 52, {"S": [("vln_sus", 1.0, 0)], "A": [("vla_sus", 1.0, 0), ("cl_sus", 0.6, 0)]}),
    (52, 68, {"S": [("vln_sus", 1.0, 0), ("fl_sus", 0.6, 0)], "A": [("vla_sus", 1.0, 0), ("cl_sus", 0.6, 0)],
              "B": [("vc_sus", 1.0, 0), ("bsn_sus", 0.7, 0)]}),
    (68, 84, {"S": [("vln_sus", 1.0, 0), ("fl_sus", 0.7, 0), ("ob_sus", 0.6, 0), ("picc_sus", 0.45, 12)],
              "A": [("vla_sus", 1.0, 0), ("cl_sus", 0.7, 0)],
              "T": [("hn_sus", 1.0, 0), ("choir", 0.9, 0), ("vc_sus", 0.6, 0)],
              "B": [("vc_sus", 0.8, 0), ("cb_sus", 0.9, 0), ("bsn_sus", 0.7, 0), ("cbsn_sus", 0.6, -12)]}),
    (84, 112, {"S": [("vln_sus", 1.0, 0), ("fl_sus", 0.7, 0), ("ob_sus", 0.7, 0)],
               "A": [("vla_sus", 1.0, 0), ("cl_sus", 0.6, 0)], "T": [("hn_sus", 1.0, 0)],
               "B": [("vc_sus", 1.0, 0), ("bsn_sus", 0.7, 0), ("cb_sus", 0.8, 0)]}),
    (112, 128, {"S": [("vln_sus", 1.0, 0), ("fl_sus", 0.7, 0), ("ob_sus", 0.6, 0)],
                "A": [("cl_sus", 0.8, 0), ("vla_sus", 0.9, 0)], "T": [("hn_sus", 1.0, 0)],
                "B": [("vc_sus", 1.0, 0), ("cb_sus", 0.8, 0), ("bsn_sus", 0.6, 0)]}),
    (128, 136, {"S": [("vln_sus", 1.0, 0)], "A": [("vla_sus", 1.0, 0)], "T": [("hn_sus", 1.0, 0)],
                "B": [("vc_sus", 1.0, 0)]}),
    (144, 160, {"S": [("vln_sus", 1.0, 0), ("vln_sus", 0.6, 12)], "A": [("vla_sus", 1.0, 0)],
                "T": [("vc_sus", 1.0, 0), ("hn_sus", 0.8, 0), ("choir", 0.9, 0)],
                "B": [("cb_sus", 1.0, 0), ("bsn_sus", 0.6, 0)]}),
    (160, 176, {"S": [("vln_sus", 1.0, 0), ("fl_sus", 0.6, 0), ("vln_sus", 0.5, 12)],
                "A": [("vla_sus", 1.0, 0), ("choir", 0.8, 0)], "T": [("hn_sus", 1.0, 0), ("choir", 0.7, 0)],
                "B": [("vc_sus", 1.0, 0), ("cb_sus", 0.9, -12), ("tbn_sus", 0.8, 0), ("tba_sus", 0.8, -12),
                      ("cbsn_sus", 0.6, -12)]}),
]
# громкость (скорость нажатия) по времени — линейно между точками
DYN = [(0, .35), (20, .45), (36, .5), (52, .58), (68, .7), (84, .78), (100, .85), (112, .6), (124, .72),
       (136, .4), (144, .6), (160, .72), (176, .9)]


def dyn(t):
    for (a, va), (b, vb) in zip(DYN, DYN[1:]):
        if a <= t < b:
            return va + (vb - va) * (t - a) / (b - a)
    return DYN[-1][1]


def orch_at(t):
    for a, b, m in ORCH:
        if a <= t < b:
            return m
    return {}


# унисон Мелькора: кто его играет (инструмент, сдвиг, усиление, скорость) — захват голосов и их уход
def melkor_orch(t):
    core = [("tpt_sus", 0, 1.0), ("tbn_sus", -12, 1.0), ("tba_sus", -24, 0.9)]
    if 84 <= t < 112:
        out = list(core)
        if t >= 88:
            out.append(("hn_sus", 0, 0.9))           # тенор втянут
        if t >= 92:
            out += [("vla_sus", 0, 0.9), ("cl_sus", 0, 0.7)]   # альт втянут
        if t >= 96:
            out += [("vc_sus", -12, 0.9), ("bsn_sus", -12, 0.7), ("cb_sus", -24, 0.8)]   # бас втянут
        if t >= 100:
            out += [("choir", 0, 0.45)]               # айнур, подладившие свою музыку к его
        return out, (.9 if t < 100 else 1.0)
    if 112 <= t < 124:
        return [("tbn_sus", -12, 0.8)], .45
    if 124 <= t < 136:
        return core, .95
    if 136 <= t < 144:
        return core, .42
    if 144 <= t < 160:
        return core, .95
    if 160 <= t < 168:
        return [("tpt_sus", 0, 1.0)], .8                # тромбоны и туба ушли — играют его ноты в каденции
    if 168 <= t < 172:
        return [("tpt_sus", 0, 0.8)], .62
    return [], 0


def load():
    path = os.path.join(HERE, "music.json")
    if not os.path.exists(path):
        subprocess.run([sys.executable, os.path.join(HERE, "music.py")], check=True, cwd=HERE)
    return json.load(open(path))


def build(ctx):
    mus = load()
    p = Piece("Ainulindalë", bpm=60, meter=(4, 4), key="D major", seed=11)
    p.meta["length"] = LEN
    c = Composer(p, lib="vsco", seed=11)
    rng = p.rng
    for t, label in mus["marks"]:
        p.mark(t, label)

    # ---------------------------------------------------------------- I. одинокие голоса
    for n in mus["solos"]:
        p.note(n["inst"], n["m"], n["t"], n["d"], vel=0.55,
               gain=0.5 * {"cl_sus": 0.45, "fl_sus": 1.3, "vla_sus": 2.2, "harp": 1.4, "hn_sus": 1.0}[n["inst"]],
               attack=0.12, release=1.2,
               pan={"fl_sus": 0.6, "cl_sus": -0.55, "vla_sus": 0.3, "harp": -0.2, "hn_sus": -0.7}[n["inst"]])

    # ---------------------------------------------------------------- II–VI. Великая Музыка: голоса SATB
    for k, voice in mus["voices"].items():
        for t, d, m in voice:
            for inst, g, sh in orch_at(t).get(k, []):
                long_ = d >= 1.5
                p.note(inst, m + sh, t, d * (0.97 if long_ else 0.9), vel=dyn(t), gain=0.42 * g,
                       attack=0.06 if not long_ else 0.12, release=0.5 if long_ else 0.25,
                       pan={"S": 0.3, "A": -0.25, "T": 0.15, "B": -0.1}[k])
    # педаль под первой Темой: Илуватар предлагает её в тишине
    for m in (38, 45):
        p.note("cb_sus" if m == 38 else "vc_sus", m, 20.0, 16.0, vel=0.35, gain=0.25, attack=2.0, release=1.5)
    # литавры tutti и бури — тоника и доминанта на сильных долях
    for t, m in ((68, 2), (72, 2), (80, 9)):           # литавры — по гармонии: I, vi (D — её терция), V
        c.timp(t, m, vel=0.55)
    c.timp(84.0, 2, vel=0.7)

    # ---------------------------------------------------------------- унисон Мелькора (84–172)
    for t, d, m in mus["melkor"]:
        insts, vel = melkor_orch(t)
        for inst, sh, g in insts:
            p.note(inst, m + sh, t, d * 0.85, vel=vel, gain=0.55 * g, attack=0.01, release=0.2, pan=-0.35)
    # буря: «как бурное море» — волны тремоло, литавры, тарелки (100–112, 128–136)
    for t0, t1 in ((100, 112), (128, 136)):
        t = t0
        while t < t1:
            for inst, m in (("vc_trem", 50), ("cb_trem", 38), ("vla_trem", 57)):
                p.note(inst, m + rng.choice((0, 1, 3)), t, 2.0, vel=0.85, gain=0.3, attack=0.9, release=0.4,
                       bend=rng.choice((-2.0, 2.0, 3.0)))
            t += 2.0
        c.timp(t0, 2, vel=0.55, roll=t1 - t0 - 0.5)
        c.fx("sso_cymbal", t0 + 0.5, gain=0.18, bus="perc", attack=1.5, dur=t1 - t0 - 1, fade=0.4)
        c.fx("tamtam", t0, gain=0.25, bus="perc")
    # 100–112: в сопрано — голова Темы в отчаянии, секвенцией вверх против унисона
    for i, base in enumerate((74, 76, 78, 79, 81, 83)):
        t = 100 + 2 * i
        for dt, dd, iv in ((0, .5, 0), (.5, .5, 7 if base + 7 <= 93 else -5), (1, .5, 9 if base + 9 <= 93 else -3),
                           (1.5, .5, 7 if base + 7 <= 93 else -5)):
            for inst, g in (("vln_sus", 1.0), ("fl_sus", 0.7)):
                p.note(inst, base + iv - 12 * (inst == "vln_sus" and base > 80), t + dt, dd * 0.9, vel=0.85,
                       gain=0.42 * g, attack=0.03, release=0.2, pan=0.3)

    # ---------------------------------------------------------------- VI. третья тема: рябь (136–144)
    rip = [(62, 65, 69, 74, 69, 65), (58, 62, 65, 70, 65, 62), (55, 58, 62, 67, 62, 58), (57, 61, 64, 69, 64, 61)]
    for b in range(8):
        chord = rip[(b // 2) % 4]
        for j, m in enumerate(chord):
            tt = 136 + b + j / 6
            p.note("harp", m + 12, tt, min(0.9, 144.0 - tt), vel=0.4, gain=0.35,
                   release=1.0 if tt + 0.9 < 144 else 0.15, pan=-0.3)
    SOLO = [(137, 1.5, 86), (138.5, .5, 93), (139, 1, 94), (140, 1, 93), (141, 1.5, 91), (142.5, .5, 89),
            (143, 1, 88), (144, 2, 86)]  # голова Темы в миноре, высоко и тихо
    for t, d, m in SOLO:
        p.note("vln_solo", m - 12, t, d * 0.95, vel=0.4, gain=0.42, attack=0.15, release=0.8, pan=0.35)
        p.note("fl_sus", m - 12, t, d * 0.95, vel=0.35, gain=0.22, attack=0.15, release=0.8, pan=0.5)

    # ---------------------------------------------------------------- VII. последний аккорд (176–180.5) и тишина
    FINAL = {"cbsn_sus": (26, 38), "cb_sus": (38, 45), "tba_sus": (38, 45), "vc_sus": (50, 57, 62),
             "tbn_sus": (50, 57, 62), "bsn_sus": (50, 57), "hn_sus": (62, 66, 69), "vla_sus": (62, 66, 69),
             "tpt_sus": (69, 74), "cl_sus": (66, 74), "ob_sus": (78, 81), "vln_sus": (74, 78, 81, 86),
             "fl_sus": (86, 90), "picc_sus": (93, 98), "choir": (50, 57, 62, 66, 69, 74), "vln_harm": (98,)}
    for inst, ms in FINAL.items():
        for m in ms:
            g = 0.36 * {"picc_sus": 0.12, "choir": 0.6, "fl_sus": 0.6}.get(inst, 1.0)
            p.note(inst, m, 176.0, 4.5, vel=0.95, gain=g, attack=0.03, release=0.35)
    p.note("org_loud", 26, 176.0, 4.5, vel=0.9, gain=0.22, release=0.35)   # педаль 16′ — глубже бездны
    p.note("org_loud", 38, 176.0, 4.5, vel=0.9, gain=0.18, release=0.35)
    c.timp(176.0, 2, vel=0.75, roll=4.2)

    # ---------------------------------------------------------------- VIII. видение: отзвук Музыки в водах (184–206.5)
    LYD = (62, 64, 66, 69, 71)                         # пентатоника D E F♯ A B — вода Ульмо (без полутонов и тритонов)
    cut = 206.5
    t = 184.0
    k = 0
    while t < cut - 1e-9:
        up = [LYD[(k + j) % 5] + 12 * ((k + j) // 5 % 2) for j in range(5)]
        for j, m in enumerate(up + up[-2:0:-1]):
            tt = t + j * 0.125
            if tt < cut:
                p.note("harp", m, tt, min(0.9, cut - tt), vel=0.32, gain=0.3, release=0.6 if tt + 0.9 < cut else 0.05,
                       pan=-0.4 + 0.8 * ((k % 4) / 3))
        t += 1.0
        k += 1
    for m in (86, 93):
        p.note("vln_harm", m, 184.5, cut - 184.5, vel=0.3, gain=0.13, attack=2.5, release=0.05, pan=0.2)
    for t0, base in ((187.0, 50), (196.0, 57)):        # рог Ульмо: голова Темы, издалека
        for dt, dd, iv in ((0, 1.2, 0), (1.2, 1.2, 7), (2.4, .8, 9), (3.2, 1.8, 7)):
            p.note("hn_sus", base + iv, t0 + dt, dd, vel=0.4, gain=0.3, attack=0.2, release=1.0, pan=-0.6)
    for t, d, m in ((191, 1, 83), (192, 1, 81), (193, 1.5, 78), (194.5, .5, 76), (195, 1.5, 74)):  # воздух Манвэ
        p.note("fl_sus", m, t, d, vel=0.35, gain=0.3, attack=0.1, release=0.6, pan=0.6)
    for t in range(199, 207):                            # земля Аулэ
        if t + 0.4 < cut:
            p.note("vc_pizz", 38 if t % 2 else 45, t, 0.4, vel=0.5, gain=0.35, release=0.3, pan=-0.2)
    p.note("hn_sus", 64, 204.0, cut - 204.0, vel=0.42, gain=0.3, attack=0.2, release=0.05, pan=-0.6)  # оборвано

    # ---------------------------------------------------------------- IX. Эа (210–224): Неугасимое пламя
    p.note("harp", 62, 210.0, 5.0, vel=0.5, gain=0.4, release=3.0)
    p.note("harp", 50, 210.0, 5.0, vel=0.45, gain=0.35, release=3.0)
    for inst, m, g, t0 in (("choir", 50, 0.45, 210.0), ("choir", 57, 0.45, 210.0), ("vc_sus", 38, 0.3, 210.0),
                           ("cb_sus", 38, 0.3, 210.0), ("vla_sus", 57, 0.3, 211.0), ("vln_harm", 86, 0.13, 211.5),
                           ("choir", 62, 0.4, 214.0), ("vln_sus", 66, 0.25, 216.0), ("choir", 66, 0.3, 216.5),
                           ("fl_sus", 81, 0.18, 217.0)):
        p.note(inst, m, t0, 221.0 - t0, vel=0.38, gain=g, attack=2.0, release=3.0, pan=rng.uniform(-0.3, 0.3))

    # баланс партий по замеру --parts (эскиз 0–90 с): тема и бас — вровень, краски на 4–8 дБ ниже
    p.balance({"Violins": +10, "Bassoon": -13.5, "Contrabassoon": -13, "Piccolo": -12, "Cellos": -3, "Choir": +3.5,
               "Horn": +4.5, "Trombone": +15, "Tuba": +5, "Timpani": +8, "Harp": +3, "Basses": +6, "Violin solo": +22,
               "Clarinet": -3, "Flute": -1.5, "Oboe": -2})
    return p
