#!/usr/bin/env python3
"""Fuga: Die Grenzen meiner Sprache (Tractatus 5.6), ре минор, 4 голоса (≈ 2:50).

Нотный текст — в fugue.py (тема, ответ, противосложение, интермедии, средние проведения, обращение, стретты,
органные пункты, увеличение; свободные голоса найдены поиском по гармоническому плану и проверены на параллели и
диссонансы на долях). Здесь — только оркестровка: кто играет какой голос в каком разделе.

    python3 requests/fugue-grenzen/fugue.py          # пересчитать голоса → fugue.json
    python3 -m kit run requests/fugue-grenzen/piece.py --parts
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from kit.events import Piece  # noqa: E402

BPM = 58
SPB = 60.0 / BPM
PICKUP = 3.5  # первая нота (затакт «Die») — на доле 3.5; время 0 — она


def sec(beat):
    return (beat - PICKUP) * SPB


# разделы (в долях) → оркестровка. Голос: [(инструмент, усиление, сдвиг в полутонах)]
STR = {"S": [("vln_sus", 1.0, 0)], "A": [("vln_sus", 0.9, 0)], "T": [("vla_sus", 1.0, 0)], "B": [("vc_sus", 1.0, 0)]}
SECTIONS = [
    (0, 32, "экспозиция", STR),
    (32, 47.5, "экспозиция/интермедия 1", dict(STR, B=STR["B"] + [("cb_sus", 0.8, -12)])),
    (47.5, 56, "проведение в F", dict(STR, S=[("ob_sus", 1.0, 0)], B=STR["B"] + [("cb_sus", 0.7, -12)])),
    (56, 63.5, "интермедия 2", dict(STR, B=STR["B"] + [("cb_sus", 0.7, -12)])),
    (63.5, 72, "обращение", dict(STR, T=[("bsn_sus", 1.0, 0)])),
    (72, 79.5, "интермедия 3", dict(STR, S=[("fl_sus", 1.0, 0)], B=STR["B"] + [("cb_sus", 0.7, -12)])),
    (79.5, 88, "проведение в a", dict(STR, B=STR["B"] + [("bsn_sus", 0.8, 0), ("cb_sus", 0.9, -12)])),
    (88, 95.5, "интермедия 4", dict(STR, B=STR["B"] + [("cb_sus", 0.8, -12)])),
    (95.5, 123, "стретта", {"S": STR["S"] + [("ob_sus", 0.7, 0)], "A": STR["A"] + [("org_quiet", 0.5, 0)],
                            "T": STR["T"] + [("org_quiet", 0.5, 0)],
                            "B": STR["B"] + [("bsn_sus", 0.7, 0), ("cb_sus", 0.9, -12)]}),
    (123, 130, "органный пункт", {"S": STR["S"] + [("ob_sus", 0.7, 0)], "A": STR["A"] + [("org_quiet", 0.5, 0)],
                                  "T": STR["T"] + [("org_quiet", 0.5, 0)],
                                  "B": [("org_loud", 0.7, 0), ("org_loud", 0.6, -12), ("cb_sus", 0.9, -12),
                                        ("vc_sus", 1.0, 0)]}),
    (130, 148.5, "увеличение", {"S": STR["S"] + [("ob_sus", 0.7, 0)], "A": STR["A"] + [("org_quiet", 0.5, 0)],
                                "T": STR["T"] + [("org_quiet", 0.5, 0)],
                                "B": [("vc_sus", 1.0, 0), ("bsn_sus", 0.8, 0), ("cb_sus", 0.9, -12),
                                      ("org_loud", 0.7, 0), ("org_loud", 0.6, -12)]}),
    (148.5, 170, "кода", {"S": [("ob_sus", 1.0, 0), ("vln_sus", 0.8, 0)], "A": STR["A"] + [("org_quiet", 0.5, 0)],
                          "T": STR["T"] + [("org_quiet", 0.5, 0)],
                          "B": [("org_loud", 0.7, 0), ("org_loud", 0.6, -12), ("cb_sus", 0.9, 0),
                                ("vc_sus", 1.0, 12)]}),
]
VOICE = {"S": "Soprano", "A": "Alto", "T": "Tenor", "B": "Bass"}
PRIMARY = {"vln_sus", "vla_sus", "vc_sus"}  # первое исполнение голоса — его нотоносец «Soprano/Alto/…»

# громкость по разделам: (доля, скорость нажатия) — линейно между точками
DYN = [(0, 0.5), (40, 0.46), (47.5, 0.55), (56, 0.47), (63.5, 0.55), (72, 0.5), (79.5, 0.6), (88, 0.55),
       (95.5, 0.66), (123, 0.66), (130, 0.76), (148.5, 0.7), (157, 0.78), (170, 0.78)]
THEMATIC = ("тема", "ответ", "обращение", "стретта", "увеличение")


def dyn(beat):
    for (b0, v0), (b1, v1) in zip(DYN, DYN[1:]):
        if b0 <= beat <= b1:
            return v0 + (v1 - v0) * (beat - b0) / (b1 - b0)
    return DYN[-1][1]


def section(beat):
    for s in SECTIONS:
        if s[0] <= beat < s[1]:
            return s
    return SECTIONS[-1]


def articulate(d):
    """барочная подача: короткие ноты отделены, длинные почти legato"""
    return d * (0.82 if d <= 0.25 else 0.86 if d <= 0.5 else 0.9 if d <= 1 else 0.96)


def load():
    path = os.path.join(HERE, "fugue.json")
    if not os.path.exists(path):
        subprocess.run([sys.executable, os.path.join(HERE, "fugue.py")], check=True, cwd=HERE)
    with open(path) as fh:
        return json.load(fh)


def build(ctx):
    data = load()
    p = Piece("Fuga: Die Grenzen meiner Sprache", bpm=BPM, meter=(4, 4), key="D minor", seed=56)
    p.meta["subtitle"] = "Tractatus 5.6 — a 4"
    p.meta["notation_offset"] = PICKUP
    p.meta["sends"] = {"strings": 0.3, "winds": 0.3, "organ": 0.38, "keys": 0.25}
    thematic = [(r[0], r[1], r[2]) for r in data["roles"] if r[3].startswith(THEMATIC)]

    def is_theme(v, t):
        return any(v == rv and t0 - 1e-6 <= t < t1 + 1e-6 for t0, t1, rv in thematic)

    for b, label in data["marks"]:  # по долям, а не по округлённым секундам сценария — иначе ноты сдвинутся с сетки
        p.mark(sec(b), label[:24])
    pan = {"S": -0.35, "A": -0.12, "T": 0.15, "B": 0.3}
    for v, notes in data["voices"].items():
        for t, d, m in notes:
            sec_ = section(t)
            vel = dyn(t) + (0.07 if is_theme(v, t) else 0.0) + (0.03 if d <= 0.25 else 0.0)
            for inst, g, sh in sec_[3][v]:
                part = VOICE[v] if inst in PRIMARY else None
                long_ = d >= 4
                p.note(inst, m + sh, sec(t), articulate(d) * SPB, vel=min(0.95, vel), gain=0.5 * g, pan=pan[v],
                       attack=0.02 if not inst.startswith("org") else 0.04,
                       release=0.25 if not long_ else 1.8, part=part)
    # генерал-бас: клавесин удваивает самый низкий звучащий голос (basso seguente) до тонического пункта
    allv = [(t, d, m, v) for v, ns in data["voices"].items() for t, d, m in ns]

    def lowest_at(t):
        cur = [(m, v) for tt, d, m, v in allv if tt - 1e-9 <= t < tt + d - 1e-9]
        return min(cur)[1] if cur else None

    for t, d, m, v in allv:
        if t >= 148.5 or lowest_at(t) != v:
            continue
        p.note("hpsd", m, sec(t), articulate(d) * SPB, vel=min(0.9, dyn(t) + 0.1), gain=0.45, pan=0.1)
        if m >= 48 and t >= 32:
            p.note("hpsd", m - 12, sec(t), articulate(d) * SPB, vel=min(0.9, dyn(t)), gain=0.3, pan=0.1)
    # аккорд-итог клавесина: ре мажор, арпеджированный
    for j, m in enumerate([50, 57, 62, 66, 69]):
        p.note("hpsd", m, sec(157) + 0.06 * j, 5 * SPB, vel=0.7, gain=0.4, pan=0.1)
    # голоса фуги равноправны: замер `--parts` на эскизе — альт −40.5, сопрано −35.4, тенор −27.5, бас −22.5,
    # клавесин −42 LUFS; выравниваем к ≈ −26 (бас чуть выше — опора), клавесин — слышимым континуо
    # второй замер (вся пьеса): фагот −18 (громче всех), флейта −23 — убрать; гобой −28 — добавить
    p.balance({"Alto": +14, "Soprano": +9, "Tenor": +1.5, "Bass": -1.5, "Basses": +3, "Harpsichord": +11,
               "Oboe": +1, "Bassoon": -6, "Flute": -2.5})
    return p
