#!/usr/bin/env python3
"""Ainulindalë — Музыка Айнур, третья редакция (≈ 5:04).

По тексту «Айнулиндалэ» (Румиль — Пенголод — Эльфвинэ):
  * Великая Музыка — Айнур «развивают» Тему и «украшают каждый своими думами и замыслами»: Тема целиком — только в
    медленных голосах (бас, валторны с хором); остальные голоса поют свои неповторяющиеся мелодии из ячеек Темы
    (опевание, нисходящий ход, восходящий ход, конечный оборот — в обращении, ракоходе, сцеплениях, с дыханием).
    Повторение одного мотива — только у Мелькора («бесконечно повторялась»).
  * «Долгое время был доволен»: Великая Музыка идёт долго и развивается — Тема уходит в ля (пентатоника A) и
    возвращается кульминацией, когда «чертоги переполнились»; лишь тогда вступает Мелькор.
  * Лад — пентатоника (D E F♯ A B; в ля — A B C♯ E F♯; во второй теме — D F G B♭ C): наложения без полутонов и
    тритонов. Строй Илуватара и Айнур — чистый, по натуральному ряду D; Мелькор — в равномерном строе.
  * Мелькор: своя гордая тема → соседи смешиваются и подхватывают → море нестройных звуков → господство →
    против третьей темы «внутреннее единство»: трубы в унисон на нескольких нотах; его ноты вплетаются в скорбную
    часть: E♭–B♭–C♯–D = неаполитанская — VI — V7 — I.
  * Вторая тема — обращение Темы, со своим развитием; третья — вольная дорийская мелодия Детей, три проведения.
  * Один аккорд — натуральный ряд D в чистом строе; видение — музыка становится земной; Эа — первый ровный пульс.

Вторая редакция — в истории git (cc949f4), первая — в v1/.

    python3 -m kit run requests/ainulindale/piece.py --sketch --parts
    python3 -m kit run requests/ainulindale/piece.py --parts
"""
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from kit.devices import Composer  # noqa: E402
from kit.events import Piece  # noqa: E402

LEN = 304.0
OFF, T_SHIFT = 8.0, 36.45   # всё после изложения Темы сдвинуто на OFF: изложение удлинено с 11,6 до 17 с
D_PC = 2
JI = {0: 0.0, 1: 11.7, 2: 3.9, 3: 15.6, 4: -13.7, 5: -2.0, 6: -9.8, 7: 2.0, 8: 13.7, 9: -15.6, 10: -3.9, 11: -11.7}


def ji(m):
    return JI[(round(m) - D_PC) % 12] / 100.0


# ---------------------------------------------------------------- материал
THEME = [(62, 2), (69, 2), (71, 1), (69, 1), (66, 1.5), (64, .5), (62, 1), (64, 1), (69, 2), (71, 1), (76, 1),
         (74, 3)]                                    # D A B A F♯ E D E A B E D — 17 единиц
THEME_A = [(m + 7, d) for m, d in THEME]             # в ля: A E F♯ E C♯ B A B E F♯ B A
INV = [(62 - (m - 62), d) for m, d in THEME]          # вторая тема: обращение (пентатоника D F G B♭ C)
F_D, F_A, F_INV = {2, 4, 6, 9, 11}, {9, 11, 1, 4, 6}, {2, 5, 7, 10, 0}
# ячейки Темы в ступенях пентатоники: опевание, нисходящий ход, восходящий ход, конечный оборот и их сплавы
CELLS = [(3, 1, -1), (-1, -1, -1), (1, 2, 1), (2, -1), (1, -1), (-1, 2, -1), (3, -1, -1, -1), (-2, 1, 1), (1, 1, -2)]
MTHEME = [(50, 1), (56, 1), (57, .5), (58, .5), (57, 1), (55, .5), (53, .5), (52, .5), (53, .5), (58, 1), (57, .5),
          (63, 1.5), (62, 2)]                         # D G♯ | A B♭ A | G F E F | B♭ A E♭ D
OSTINATO = [(0, 1, 63), (1, 1, 63), (2, .5, 58), (2.5, .5, 61), (3, 1, 63)]
T3 = [(69, 1), (74, 1.5), (72, .5), (69, 1), (67, 1),
      (69, 1.5), (65, .5), (64, 1), (62, 1),
      (65, 1), (67, .5), (69, .5), (71, 1.5), (69, .5), (67, 1), (64, 1), (62, 1)]
T3_CHORDS = [(0, 2, "m"), (3, 5, "M"), (4, 0, "M"), (5, 2, "m"), (7, 9, "m"), (8, 2, "m"),
             (9, 10, "M"), (10, 0, "M"), (11, 7, "M"), (13, 0, "M"), (14, 9, "M"), (15, 2, "m")]
QUAL = {"M": (0, 4, 7), "m": (0, 3, 7)}
HEAD = [(0, 1.3), (7, 1.3), (9, .9), (7, 2.0)]
CONSONANT = {0, 3, 4, 5, 7, 8, 9}

# ---------------------------------------------------------------- время (с)
T_THEME = 23.6
T_GREAT, T_DEV_A, T_RETURN, T_MELKOR = 36.5, 73.0, 93.4, 105.0
T_SEA, T_SEC, T_SEC_BATTLE, T_MASTERY = 118.0, 140.0, 158.0, 172.0
T_THIRD, T_T3_2, T_T3_3, T_UNISON, T_ABSORB, T_CHORD = 180.0, 192.0, 208.0, 204.0, 224.0, 240.0
T_VISION, T_VCUT, T_EA = 249.0, 274.5, 278.0


def voicing(root, qual, mel_lo, mel_notes, n=3, floor=45):
    pcs = [(root + x) % 12 for x in QUAL[qual]]
    out, m = [], mel_lo - 3
    while m >= floor and len(out) < n:
        if m % 12 in pcs and all(abs(m - x) % 12 not in (1, 2, 6, 10, 11) for x in mel_notes):
            if not out or out[-1] - m >= 3:
                out.append(m)
        m -= 1
    return out


def scale_of(pcs, lo, hi):
    return [m for m in range(lo, hi + 1) if m % 12 in pcs]


def develop(t0, t1, field, lo, hi, value, seed, cantus=None, start=None):
    """мелодия Айну: фразы из ячеек Темы (обращение, ракоход, сцепление), длительности вокруг value, дыхание
    между фразами; на долгих звуках — консонанс к звучащему cantus. Без повторения фраз. → [(t, d, m)]"""
    rng = random.Random(seed)
    sc = scale_of(field, lo, hi)
    idx = len(sc) // 2 if start is None else min(range(len(sc)), key=lambda i: abs(sc[i] - start))
    out, t, last = [], t0, None
    while t < t1 - value:
        n = rng.randint(4, 10)
        steps = []
        while len(steps) < n:
            cell = rng.choice([c for c in CELLS if c != last])
            last = cell
            if rng.random() < 0.35:
                cell = tuple(-x for x in cell)
            if rng.random() < 0.2:
                cell = tuple(reversed(cell))
            steps.extend(cell)
        if idx > len(sc) * 0.75:          # от края — к середине диапазона
            steps = [-abs(s) if i % 3 != 2 else s for i, s in enumerate(steps)]
        elif idx < len(sc) * 0.25:
            steps = [abs(s) if i % 3 != 2 else s for i, s in enumerate(steps)]
        for i, st in enumerate(steps[:n]):
            idx += st
            if idx < 0:
                idx = -idx
            if idx >= len(sc):
                idx = 2 * (len(sc) - 1) - idx
            idx = max(0, min(len(sc) - 1, idx))
            d = value * (rng.choice((2, 3)) if i == n - 1 else rng.choice((1, 1, 1, 2, .5, .5, 1.5)))
            if t + d > t1:
                d = t1 - t
                if d < value * 0.4:
                    break
            m = sc[idx]
            if cantus and d >= 1.5 * value:
                cm = cantus(t)
                if cm is not None and (m - cm) % 12 not in CONSONANT:
                    for j in (1, -1, 2, -2):
                        k2 = idx + j
                        if 0 <= k2 < len(sc) and (sc[k2] - cm) % 12 in CONSONANT:
                            idx, m = k2, sc[k2]
                            break
            out.append((t, d, m))
            t += d
        t += value * rng.uniform(0.6, 2.6)
    return out


def sounding(notes, t):
    for a, d, m in notes:
        if a <= t + 1e-9 < a + d:
            return m
    return None


def build(ctx):
    p = Piece("Ainulindalë", bpm=60, meter=(4, 4), key="D major", seed=29)
    p.meta["length"] = LEN
    p.meta["reverb_seconds"] = 5.5
    p.meta["sends"] = {"choir": 0.6, "strings": 0.5, "harp": 0.6, "winds": 0.45, "organ": 0.55, "brass": 0.34}
    c = Composer(p, lib="vsco", seed=29)
    rng = p.rng

    def tshift(t):
        return t + OFF if t >= T_SHIFT else t

    def note(inst, m, t, d, vel, gain, pure=True, raw=False, **kw):
        kw.setdefault("attack", 0.12)
        kw.setdefault("release", 0.8)
        det = (ji(m) if pure else 0.0) + kw.pop("detune", 0.0)
        p.note(inst, m, t if raw else tshift(t), d, vel=min(1.0, vel), gain=gain, detune=det, **kw)

    def timp(t, *a, **k):
        c.timp(tshift(t), *a, **k)

    def fx(name, t, *a, **k):
        c.fx(name, tshift(t), *a, **k)

    def play(notes, insts, vel, gain, pan=0.0, echo=None, wobble=None, fade=None, legato=0.97, vel_fn=None):
        """сыграть [(t, d, m)] составом insts [(инстр., усил., сдвиг)]"""
        for t, d, m in notes:
            w = wobble(t) if wobble else 0.0
            fg = fade(t) if fade else 1.0
            v = vel_fn(t) if vel_fn else vel
            for inst, g, sh in insts:
                det = rng.uniform(-0.45, 0.45) * w
                tt = t + rng.uniform(0, 0.12) * w
                note(inst, m + sh, tt, d * legato, v, gain * g * fg, detune=det, pan=pan,
                     attack=min(0.3, 0.08 + d * 0.15), release=min(1.6, 0.3 + d * 0.4))
                if echo:
                    note(inst, m + sh, tt + echo[0], d * legato, v * 0.8, gain * g * fg * echo[1], detune=det,
                         pan=-pan, attack=0.2, release=1.4)

    def theme_notes(theme, t0, unit, shift=0):
        out, t = [], t0
        for m, d in theme:
            out.append((t, d * unit, m + shift))
            t += d * unit
        return out

    marks = [(0, "I Голоса порознь"), (22, "II Илуватар предлагает Тему"), (T_GREAT, "III Великая Музыка"),
             (T_DEV_A, "IIIb Тема развивается: в ля"), (T_RETURN, "IIIc Возвращение: чертоги переполнились"),
             (T_MELKOR, "IV Мысль Мелькора"), (T_SEA, "IVb Море нестройных звуков"), (T_SEC, "V Вторая тема"),
             (T_SEC_BATTLE, "Vb Битва звуков"), (T_MASTERY, "Vc Господство Мелькора"),
             (T_THIRD, "VI Третья тема — Дети Илуватара"), (T_UNISON, "VIb Две музыки"), (T_ABSORB, "VIc Вбирание"),
             (T_CHORD, "VII Один аккорд"), (T_VISION, "VIII Видение"), (T_EA, "IX Эа")]
    for t, label in marks:
        p.mark(tshift(t), label)

    # ============================================================ I. Голоса порознь (0–22)
    SOLOS = [("fl_sus", 1.0, 79, 0.6), ("vla_sus", 4.2, 54, -0.4), ("harp", 7.0, 76, 0.2), ("cl_sus", 9.5, 61, -0.6),
             ("hn_sus", 12.0, 57, 0.5), ("vln_solo", 13.4, 69, -0.2), ("choir", 15.2, 62, 0.0),
             ("fl_sus", 16.0, 74, 0.5), ("vla_sus", 16.8, 57, -0.4)]
    for inst, t0, base, pan in SOLOS:
        t = t0
        for iv, d in HEAD:
            note(inst, base + iv, t, d * 0.97, 0.5, 0.42, pure=(base % 12) in (2, 9), pan=pan, attack=0.2, release=1.4)
            t += d

    # ============================================================ II. Илуватар предлагает Тему (22–44.5, без сдвига)
    # «мощная тема… слава, в коей началась та музыка, и великолепие, в коей она окончилась… Айнур преклонились и умолкли»
    for m in (38, 45, 50, 54, 57):
        note("org_quiet", m, 22.0, 3.0, 0.55, 0.3, attack=1.2, release=1.5, raw=True)
    for m in (50, 57):
        note("choir", m, 22.0, 3.0, 0.5, 0.35, attack=1.0, release=1.2, raw=True)
    org_below = lambda m: m - 7 if (m - 7) % 12 in F_D else m - 5  # noqa: E731
    T_ST, U_ST = 24.6, 1.0
    t_end = T_ST + 17 * U_ST
    for t, d, m in theme_notes(THEME, T_ST, U_ST):
        v = 0.6 + 0.15 * (t - T_ST) / 17.0
        for inst, mm, g in (("choir", m, 0.55), ("choir", m - 12, 0.45), ("hn_sus", m - 12, 0.38),
                            ("tpt_sus", m, 0.12), ("choir", org_below(m - 12), 0.26),
                            ("org_quiet", m - 12, 0.22), ("org_quiet", org_below(m - 12) - 12, 0.2)):
            note(inst, mm, t, d * 0.98, v, g, attack=0.15, release=0.9, raw=True)
    for inst, m, g in (("vla_sus", 57, 0.22), ("vc_sus", 50, 0.25), ("vc_sus", 45, 0.22), ("cb_sus", 38, 0.28)):
        note(inst, m, T_ST, t_end - T_ST, 0.45, g, attack=2.0, release=1.2, raw=True)   # чистая квинта D–A
    for m in (62, 66, 69, 74, 78, 81, 86):                    # великолепие конца
        note("vln_sus" if m >= 74 else "choir", m, t_end, 2.0, 0.65, 0.28, attack=0.4, release=1.6, raw=True)
    note("harp", 74, t_end, 2.4, 0.55, 0.35, release=2.0, raw=True)
    # t_end + 2 … 44.5: Айнур умолкли

    # ============================================================ III. Великая Музыка (36.5–105)
    def drowned(t):                    # мелодии тонут в море нестройных звуков
        return 1.0 - 0.8 * max(0.0, min(1.0, (t - 112.0) / 12.0))

    def troubled(t):                   # смятение соседей Мелькора
        return max(0.0, min(1.0, (t - 106.0) / 8.0))

    def grow(t):                       # «чертоги переполнились звуками» — нарастание к возвращению
        return 0.46 + 0.32 * max(0.0, min(1.0, (t - T_GREAT) / (T_RETURN + 6 - T_GREAT)))

    # медленные голоса несут Тему целиком
    cantus_mid = theme_notes(THEME, 36.6, 1.0, -12)                    # Айнур подхватывают Тему — валторны и хор
    cantus_lo = theme_notes(THEME, 39.0, 2.0, -24)                     # и бас — по 2 с на единицу
    cantus_A = theme_notes(THEME_A, T_DEV_A + 0.2, 1.15, -12)          # 73.2–92.8: Тема развивается — в ля
    cantus_A_lo = [(T_DEV_A, 10.0, 33), (T_DEV_A + 10, 10.4, 40)]      # педаль A1 → E2
    ret_head = theme_notes(THEME[:4], T_RETURN + 0.2, 1.4, -12)        # возвращение: голова Темы в увеличении
    ret_tail = theme_notes(THEME[9:], T_RETURN + 0.2 + 6 * 1.4, 1.1, -12)   # и конечный оборот B–E–D
    cantus_ret_lo = [(T_RETURN, 11.6, 26)]                              # D1 — «глубочайшие глубины»

    def cantus_at(t):
        for seq in (cantus_mid, cantus_lo, cantus_A, ret_head + ret_tail):
            m = sounding(seq, t)
            if m is not None:
                return m
        return None

    play(cantus_lo, [("vc_sus", 1.0, 0), ("cb_sus", 0.9, 0), ("org_quiet", 0.5, 0)], 0.5, 0.42, pan=-0.1,
         vel_fn=grow)
    play(cantus_mid, [("hn_sus", 1.0, 0), ("choir", 0.85, 0)], 0.5, 0.42, pan=0.25, echo=(0.6, 0.25), vel_fn=grow)
    play(cantus_A, [("hn_sus", 1.0, 0), ("choir", 0.9, 0), ("tbn_sus", 0.35, -12)], 0.6, 0.44, pan=0.2,
         echo=(0.6, 0.25), vel_fn=grow)
    play(cantus_A_lo, [("cb_sus", 1.0, 0), ("org_quiet", 0.6, 12), ("cbsn_sus", 0.5, 0)], 0.55, 0.4)
    play(ret_head + ret_tail, [("tpt_sus", 0.8, 12), ("hn_sus", 1.0, 0), ("choir", 1.0, 0), ("choir", 0.7, 12),
                               ("org_loud", 0.3, -12)], 0.82, 0.44, echo=(0.7, 0.3))
    play(cantus_ret_lo, [("org_loud", 0.4, 0), ("cbsn_sus", 0.8, 0), ("cb_sus", 0.8, 12)], 0.75, 0.4)
    # развивающиеся голоса: каждый — свои мелодии из ячеек Темы, в своём регистре и темпе
    VOICES = [  # (вступление, регистр, длительность-ориентир, состав, gain, pan, эхо, конец)
        (42.5, (57, 76), 0.6, [("vla_sus", 1.0, 0), ("cl_sus", 0.45, 0)], 0.42, -0.25, (0.45, 0.3), 118.0),
        (46.5, (69, 88), 0.3, [("vln_sus", 1.0, 0), ("fl_sus", 0.45, 0)], 0.38, 0.35, (0.3, 0.3), 124.0),
        (50.0, (81, 100), 0.15, [("harp", 1.0, 0), ("vln_harm", 0.35, 0)], 0.3, 0.5, (0.22, 0.35), 116.0),
        (55.0, (26, 45), 2.4, [("cbsn_sus", 1.0, 0), ("org_loud", 0.3, 0)], 0.32, 0.0, None, 108.0),
        (57.5, (50, 69), 1.0, [("hn_sus", 0.8, 0), ("choir", 0.7, 0)], 0.36, 0.15, (0.6, 0.2), 112.0),
        (61.0, (64, 83), 0.45, [("ob_sus", 0.6, 0), ("vla_sus", 0.6, 0)], 0.34, -0.45, (0.4, 0.25), 110.0),
    ]
    # окна лада с зазором: хвосты и эхо прежнего лада не звенят поверх нового
    WINDOWS = [(T_GREAT, T_DEV_A - 0.4, F_D), (T_DEV_A + 0.4, T_RETURN - 0.4, F_A), (T_RETURN + 0.4, 130.0, F_D)]
    for vi, (t0, (lo, hi), val, insts, gain, pan, echo, t_end) in enumerate(VOICES):
        prev = None
        for wi, (a, b, field) in enumerate(WINDOWS):
            a, b = max(a, t0), min(b, t_end)
            if b - a < 1.0:
                continue
            notes = develop(a, b, field, lo, hi, val, seed=100 * vi + wi, cantus=cantus_at, start=prev)
            if notes:
                prev = notes[-1][2]
            play(notes, insts, 0.5, gain, pan=pan, echo=echo, wobble=troubled if val >= 0.6 else None,
                 fade=drowned, vel_fn=grow)

    # ============================================================ IV. Мысль Мелькора и разлад (105–140)
    def melkor_line(t0, shift, insts, vel, gain, unit=0.6, pan=-0.35):
        t = t0
        for m, d in MTHEME:
            for inst, g, sh in insts:
                note(inst, m + shift + sh, t, d * unit * 0.9, vel, gain * g, pure=False, pan=pan, attack=0.02,
                     release=0.35)
            t += d * unit
        return t

    BRASS_LO = [("tbn_sus", 1.0, 0), ("tba_sus", 0.8, -12), ("bcl_sus", 0.5, 0)]
    t = melkor_line(T_MELKOR, 0, BRASS_LO, 0.8, 0.45)                        # своя мысль
    t = melkor_line(t, 1, BRASS_LO + [("hn_sus", 0.9, 12)], 0.88, 0.45)    # соседи подхватывают
    t = melkor_line(t, 6, [("tbn_sus", 1.0, 0), ("hn_sus", 0.9, 0), ("vla_sus", 0.8, 12)], 0.92, 0.45, unit=0.5)

    def waves(t0, t1, spec, gain=0.55):
        for period, base, inst, ph in spec:
            t = t0 + ph
            while t < t1:
                d = min(period, t1 + 0.5 - t)
                note(inst, base + rng.choice((0, 1, 3, 6)), t, d, 0.95, gain, pure=False, attack=d * 0.55,
                     release=0.4, bend=rng.choice((-2.5, 2.0, 3.5, -1.5)))
                t += period * 0.8

    waves(T_SEA, T_SEC + 4.0, ((3.0, 38, "cb_trem", 0.0), (4.3, 45, "vc_trem", 1.1), (3.7, 52, "vla_trem", 2.0),
                               (5.1, 58, "vln_trem", 0.6)))
    for k, t0 in enumerate((120.0, 122.4, 124.2, 126.6, 128.0, 129.8, 131.0, 133.2, 134.4)):
        tt = t0
        for m, d in MTHEME[:5]:
            for inst, g, sh in (("tbn_sus", 1.0, 0), ("hn_sus", 0.8, 12), ("tpt_sus", 0.6, 12)):
                mm = m + (k * 5) % 12 - 2 + sh
                mm = mm - 12 if inst == "hn_sus" and mm > 77 else mm
                note(inst, mm, tt, d * 0.45, 1.0, 0.5 * g, pure=False, attack=0.02,
                     release=0.3, pan=rng.uniform(-0.7, 0.7))
            tt += d * 0.5
    for m in (50, 52, 53, 56, 57, 58):
        note("choir", m, 123.0, 13.0, 0.8, 0.3, pure=False, attack=4.0, release=0.5, bend=rng.choice((-1.5, 1.5)))
    timp(122.0, 2, vel=0.7, roll=15.0)
    fx("tamtam", 130.0, gain=0.25, bus="perc")
    fx("sso_cymbal", 125.0, gain=0.15, bus="perc", attack=3.0, dur=10.0, fade=0.5)

    # ============================================================ V. Вторая тема (140–180)
    sec_cantus = theme_notes(INV, T_SEC + 1.0, 0.8, 24)               # 141–154.6: скрипки, хор
    sec_lo = theme_notes(INV, T_SEC + 2.0, 1.6, 0)                    # 142–169: валторны, виолончели
    sec_peak = theme_notes(INV[:6], 155.0, 0.7, 12)                   # «обрела силу и новую красоту»

    def sec_cantus_at(t):
        for seq in (sec_cantus, sec_lo, sec_peak):
            m = sounding(seq, t)
            if m is not None:
                return m
        return None

    def sec_grow(t):
        return 0.5 + 0.3 * max(0.0, min(1.0, (t - T_SEC) / 16.0))

    play(sec_cantus, [("vln_sus", 1.0, 0), ("fl_sus", 0.6, 0), ("choir", 0.8, -12)], 0.55, 0.44, pan=0.3,
         echo=(0.4, 0.25), vel_fn=sec_grow)
    play([n for n in sec_lo if n[0] < 166.0], [("hn_sus", 1.0, 0), ("vc_sus", 0.8, -12)], 0.55, 0.42,
         vel_fn=sec_grow)
    play(sec_peak, [("vln_sus", 1.0, 0), ("choir", 0.9, 0), ("hn_sus", 0.7, 0)], 0.85, 0.44, echo=(0.4, 0.3))
    SEC_VOICES = [(140.5, (60, 79), 0.4, [("vla_sus", 1.0, 0), ("cl_sus", 0.4, 0)], 0.4, -0.3, 166.0),
                  (143.0, (82, 98), 0.2, [("harp", 1.0, 0), ("vln_harm", 0.35, 0)], 0.3, 0.5, 167.5),
                  (146.0, (70, 88), 0.3, [("fl_sus", 0.7, 0), ("ob_sus", 0.5, 0)], 0.34, 0.4, 164.5),
                  (148.0, (38, 55), 1.6, [("cb_sus", 1.0, 0), ("bsn_sus", 0.4, 0)], 0.38, -0.1, 168.5)]
    for vi, (t0, (lo, hi), val, insts, gain, pan, t_end) in enumerate(SEC_VOICES):
        notes = develop(t0, t_end, F_INV, lo, hi, val, seed=700 + vi, cantus=sec_cantus_at)
        play(notes, insts, 0.5, gain, pan=pan, echo=(0.4, 0.25), vel_fn=sec_grow)   # обрывы — «перестали играть»
    waves(T_SEC, T_SEC + 5.0, ((3.2, 38, "cb_trem", 0.0),), gain=0.3)            # буря ещё стихает
    melkor_line(T_SEC_BATTLE, 0, [("tbn_sus", 1.0, 0), ("tba_sus", 0.8, -12), ("tpt_sus", 0.7, 12)], 0.95, 0.48)
    melkor_line(T_SEC_BATTLE + 6.6, 3, [("tbn_sus", 1.0, 0), ("hn_sus", 0.7, 12), ("tpt_sus", 0.8, 12)], 1.0, 0.48,
                unit=0.5)
    waves(T_SEC_BATTLE, T_THIRD, ((2.8, 38, "cb_trem", 0.0), (3.9, 45, "vc_trem", 0.7), (3.3, 52, "vla_trem", 1.5)))
    melkor_line(T_MASTERY, 0, [("tpt_sus", 1.0, 12), ("tbn_sus", 1.0, 0), ("tba_sus", 0.9, -12), ("hn_sus", 0.8, 12)],
                1.0, 0.45, unit=0.72)                                     # господство: его тема в увеличении
    timp(T_MASTERY, 2, vel=0.6, roll=7.5)

    # ============================================================ VI. Третья тема (180–240)
    def t3(t0, beat, mel_insts, mel_shift, vel, gain, harm=None, ripple=False, pan=0.3):
        notes_b, b = [], 0.0
        for m, d in T3:
            notes_b.append((b, d, m))
            b += d
        for bb, d, m in notes_b:
            for inst, g in mel_insts:
                note(inst, m + mel_shift, t0 + bb * beat, d * beat * 0.97, vel, gain * g, pan=pan, attack=0.18,
                     release=1.0)
        if harm or ripple:
            starts = [x[0] for x in T3_CHORDS] + [16]
            for i, (cb, root, q) in enumerate(T3_CHORDS):
                ce = starts[i + 1]
                seg = [m + mel_shift for bb, d, m in notes_b if bb < ce - 1e-9 and bb + d > cb + 1e-9]
                vc_ = voicing(root, q, min(seg), seg, n=3, floor=50 if mel_shift >= 0 else 38)
                bass = 38 + (root - 2) % 12 if (root - 2) % 12 <= 8 else 26 + (root - 2) % 12
                if harm:
                    for inst, g in harm:
                        ms = [bass] if inst in ("vc_sus", "cb_sus", "bsn_sus", "cbsn_sus") else vc_
                        for mm in ms:
                            mm2 = mm - 12 if inst == "cbsn_sus" else mm
                            note(inst, mm2, t0 + cb * beat, (ce - cb) * beat * 0.98, vel * 0.9, gain * g, attack=0.3,
                                 release=0.9, pan=-pan * 0.5)
                if ripple:
                    pcs = [(root + x) % 12 for x in QUAL[q]]
                    arp = sorted({m for m in range(57, 86) if m % 12 in pcs})[:6]
                    tt, k, end = t0 + cb * beat, 0, t0 + ce * beat
                    while tt < end - 0.05:
                        mm = arp[k % len(arp)] if (k // len(arp)) % 2 == 0 else arp[-1 - k % len(arp)]
                        if all(abs(mm - x) % 12 not in (1, 11, 6) for x in seg):
                            note("harp", mm, tt, min(0.6, end - tt), vel * 0.8, gain * 0.5,
                                 release=0.7 if tt + 0.6 < end else 0.12, pan=-0.4)
                        tt += beat / 4
                        k += 1

    t = T_THIRD                                                    # смятение ещё длится внизу
    while t < T_THIRD + 9.0:
        note("cb_trem", 38 + rng.choice((0, 1)), t, 3.0, 0.6, 0.18, pure=False, attack=1.2, release=0.6)
        t += 3.5
    melkor_line(T_THIRD, 0, [("tbn_sus", 1.0, 0)], 0.6, 0.32, unit=0.7)
    # 1) «мягкой и сладкозвучной, лёгкая рябь негромких звуков в нежной мелодии»
    t3(T_THIRD, 0.75, [("vln_solo", 1.0), ("fl_sus", 0.4)], 12, 0.45, 0.42, ripple=True)
    # 2) «её невозможно было заглушить, и она росла, обретая мощь и глубину»
    t3(T_T3_2, 1.0, [("vln_sus", 1.0), ("choir", 0.8)], 0, 0.58, 0.42,
       harm=[("vla_sus", 0.8), ("hn_sus", 0.6), ("cl_sus", 0.4), ("vc_sus", 0.9), ("cb_sus", 0.7)], pan=0.25)
    t3(T_T3_2, 1.0, [("vln_sus", 0.6)], 12, 0.52, 0.42)
    # 3) «глубокой и широкой, и прекрасной, но медленной и исполненной неизмеримой печали»
    t3(T_T3_3, 1.0, [("vln_sus", 0.9), ("choir", 0.8)], 0, 0.68, 0.44,
       harm=[("vla_sus", 0.7), ("hn_sus", 0.6), ("org_quiet", 0.5), ("vc_sus", 0.9), ("cb_sus", 0.8),
             ("cbsn_sus", 0.5)], pan=0.1)
    t3(T_T3_3, 1.0, [("vln_sus", 0.7)], 12, 0.62, 0.42)
    # против неё — «внутреннее единство» Мелькора: трубы в унисон, бесконечно
    for bar in range(int(T_UNISON), int(T_ABSORB) + 4, 4):
        insts = ([("tpt_sus", 1.0, 0), ("tpt_sus", 0.8, 12), ("tbn_sus", 0.9, -12), ("tba_sus", 0.8, -24)]
                 if bar < T_ABSORB else [("tpt_sus", 1.0, 0), ("tpt_sus", 0.5, 12)])
        for tt, d, m in OSTINATO:
            for inst, g, sh in insts:
                note(inst, m + sh, bar + tt, d * 0.85, 0.92 if bar < T_ABSORB else 0.72, 0.42 * g, pure=False,
                     attack=0.01, release=0.2, pan=-0.4)
    # вбирание: бас E♭–B♭–C♯–D = N — VI — V7 — I
    ABS = [(0, 51, (67, 63, 58)), (4, 46, (65, 62, 58)), (8, 49, (64, 61, 57)), (10, 49, (64, 61, 55)),
           (12, 50, (66, 62, 57))]
    for i, (dt, bass, upper) in enumerate(ABS):
        t0 = T_ABSORB + dt
        d = (T_ABSORB + ABS[i + 1][0] if i + 1 < len(ABS) else T_CHORD) - t0
        for inst, mm, g in (("vc_sus", bass, 0.9), ("cb_sus", bass - 12, 0.8), ("tbn_sus", bass, 0.7),
                            ("tba_sus", bass - 12, 0.7), ("cbsn_sus", bass - 24, 0.5)):
            note(inst, mm, t0, d * 0.99, 0.75, 0.42 * g, attack=0.4, release=0.4)
        for j, mm in enumerate(upper):
            for inst, g in (("choir", 0.9), ("vln_sus" if j == 0 else "vla_sus", 0.8), ("hn_sus", 0.5)):
                note(inst, mm + (12 if inst == "vln_sus" else 0), t0, d * 0.99, 0.72, 0.4 * g, attack=0.4,
                     release=0.4)

    # ============================================================ VII. Один аккорд — натуральный ряд D
    PARTIALS = [(1, 26), (2, 38), (3, 45), (4, 50), (5, 54), (6, 57), (8, 62), (9, 64), (10, 66), (12, 69),
                (16, 74), (18, 76), (20, 78), (24, 81), (32, 86), (40, 90), (48, 93), (64, 98)]
    ORCH = {26: ["org_loud", "cbsn_sus"], 38: ["org_loud", "cbsn_sus", "cb_sus", "tba_sus"],
            45: ["cb_sus", "vc_sus", "tba_sus"], 50: ["vc_sus", "tbn_sus", "choir", "org_loud"], 54: ["tbn_sus", "choir"],
            57: ["tbn_sus", "vc_sus", "choir"], 62: ["hn_sus", "vla_sus", "choir", "org_loud"], 64: ["vla_sus", "cl_sus"],
            66: ["hn_sus", "choir", "cl_sus"], 69: ["tpt_sus", "choir", "vla_sus"], 74: ["tpt_sus", "vln_sus", "choir", "harp"],
            76: ["vln_sus", "ob_sus"], 78: ["tpt_sus", "vln_sus", "choir"], 81: ["vln_sus", "fl_sus", "choir"],
            86: ["vln_sus", "fl_sus", "harp"], 90: ["fl_sus", "vln_harm"], 93: ["vln_harm", "picc_sus"],
            98: ["vln_harm", "picc_sus"]}
    for n_, m in PARTIALS:
        for inst in ORCH[m]:
            g = 0.3 / (1 + 0.04 * n_) * (0.08 if inst == "picc_sus" else 0.6 if inst == "choir" else 1.0)
            note(inst, m, T_CHORD, 4.5, 0.95, g, attack=0.04, release=0.4)
    note("harp", 50, T_CHORD, 4.0, 0.9, 0.35, release=0.4)
    timp(T_CHORD, 2, vel=0.7)

    # ============================================================ VIII. Видение: музыка становится землёй
    cut = T_VCUT
    PENT = (62, 64, 66, 69, 71)
    CHILD = (62, 67, 69, 72)
    T_CHILD = cut - 6.0
    t, k = T_VISION, 0
    while t < cut - 1e-9:
        ps = PENT if t < T_CHILD - 0.5 else CHILD
        up = [ps[(k + j) % len(ps)] + 12 * ((k + j) // len(ps) % 2) for j in range(5)]
        for j, m in enumerate(up + up[-2:0:-1]):
            tt = t + j * 0.125
            stop = cut if ps is CHILD else T_CHILD - 0.5
            if tt < stop:
                note("harp", m, tt, min(0.9, stop - tt), 0.34, 0.3, release=0.6 if tt + 0.9 < stop else 0.08,
                     pan=-0.4 + 0.8 * ((k % 4) / 3))
        t += 1.0
        k += 1
    V = T_VISION
    for m in (86, 93):
        note("vln_harm", m, V + 0.5, cut - V - 0.5, 0.3, 0.12, attack=3.0, release=0.05, pan=0.2)
    for t0, base in ((V + 3.0, 50), (V + 12.0, 57)):                     # рог Ульмо
        tt = t0
        for iv, d in HEAD:
            note("hn_sus", base + iv, tt, d, 0.42, 0.3, attack=0.2, release=1.0, pan=-0.6)
            tt += d
    for dt, m, d in ((7, 83, 1), (8, 81, 1), (9, 78, 1.5), (10.5, 76, .5), (11, 74, 1.5)):   # ветер Манвэ
        note("fl_sus", m, V + dt, d, 0.36, 0.3, attack=0.1, release=0.6, pan=0.6)
    for dt in range(14, int(cut - V)):                                    # земля Аулэ
        note("vc_pizz", 38 if dt % 2 else 45, V + dt, 0.4, 0.5, 0.35, release=0.3, pan=-0.2)
    t = V + 8.0                                                           # дождь
    while t < cut - 0.2:
        if T_CHILD - 1.0 < t < T_CHILD - 0.5:      # капля не звенит через смену лада
            t += 0.3
            continue
        note("vln_pizz", rng.choice(PENT if t < T_CHILD - 0.5 else CHILD) + 12 * rng.choice((1, 2)), t, 0.2,
             rng.uniform(0.25, 0.45), 0.2, release=0.3, pan=rng.uniform(-0.8, 0.8))
        t += rng.uniform(0.12, 0.45)
    note("cb_trem", 38, V + 16.0, 4.0, 0.6, 0.25, attack=2.0, release=1.0)        # рёв моря
    note("vc_trem", 45, V + 16.5, 3.5, 0.55, 0.2, attack=2.0, release=1.0)
    tt = T_CHILD                                                          # Дети
    for m, d in T3[:9]:
        dd = d * 0.7
        if tt >= cut:
            break
        note("vln_solo", m, tt, min(dd, cut - tt) * 0.97, 0.42, 0.4, attack=0.15,
             release=0.6 if tt + dd < cut else 0.05, pan=0.3)
        tt += dd

    # ============================================================ IX. Эа: облако с живым пламенным сердцем
    E = T_EA
    for inst, m, g, dt in (("choir", 74, 0.3, 0.0), ("choir", 78, 0.25, 0.5), ("choir", 81, 0.22, 1.0),
                           ("vln_harm", 86, 0.12, 0.5), ("vln_harm", 93, 0.1, 1.5), ("org_quiet", 62, 0.2, 0.0),
                           ("org_quiet", 69, 0.18, 0.5), ("fl_sus", 86, 0.12, 2.0)):
        note(inst, m, E + dt, 13.0 - dt, 0.36, g, attack=3.0, release=3.0, pan=rng.uniform(-0.3, 0.3))
    t, k = E + 2.5, 0
    while t < E + 13.0:
        timp(t, 2, vel=0.32 + 0.1 * min(1.0, k / 4))
        note("harp", 38, t + 0.28, 1.0, 0.4, 0.3, release=1.0)
        note("cb_pizz", 38, t + 0.28, 0.6, 0.4, 0.25, release=0.6)
        t += 1.1
        k += 1
    note("choir", 62, E + 5.0, 8.0, 0.4, 0.3, attack=2.5, release=3.0)
    note("choir", 69, E + 5.5, 7.5, 0.4, 0.28, attack=2.5, release=3.0)

    p.balance({"Contrabassoon": -12, "Choir": +4, "Violins": +8, "Horn": +2, "Flute": -3, "Trombone": +9.5,
               "Bass clarinet": -2, "Bassoon": -5, "Basses": +5, "Organ": +7, "Violin solo": +14, "Harp": +8, "Timpani": +9})
    return p
