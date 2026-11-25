#!/usr/bin/env python3
"""Ainulindalë — Музыка Айнур, вторая редакция (≈ 3:50).

По тексту «Айнулиндалэ» (Румиль — Пенголод — Эльфвинэ):
  * Музыка Айнур — не фуга, а многоголосие сразу на всех масштабах: одна Тема одновременно в шести скоростях
    (пропорциональный канон), от «глубочайших глубин» до «высочайших высот», без метра и каденций, с эхом,
    изливающимся в Пустоту. Лад — пентатоника D E F♯ A B: любые наложения без полутонов и тритонов.
  * Строй Илуватара и Айнур — чистый, по натуральному ряду D («в музыке не было изъянов»): аккорды без биений.
    Мелькор — в равномерном строе: его звуки физически бьются о чистое поле.
  * Мелькор проходит путь: своя гордая тема (тритон, бемоли, первый настойчивый ритм) → соседи смешиваются и
    подхватывают её → море нестройных звуков → господство → и лишь против третьей темы — «внутреннее единство»:
    трубы в унисон на нескольких нотах, бесконечно. Его победные ноты вплетаются в скорбную часть:
    E♭–B♭–C♯–D = неаполитанская — VI — V7 — I.
  * Вторая тема — обращение Темы: другая пентатоника (D F G B♭ C), «похожая и непохожая».
  * Третья тема не похожа на первые две: вольная дорийская мелодия Детей Илуватара.
  * Последний аккорд — сам натуральный ряд D1…D7 в чистом строе. Видение — музыка становится земной: вода, ветер,
    земля, дождь, море; обрыв. Эа — облако с живым пламенным сердцем: впервые ровный пульс — начинается Время.

    python3 -m kit run requests/ainulindale/piece.py --sketch --parts
    python3 -m kit run requests/ainulindale/piece.py --parts
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from kit.devices import Composer  # noqa: E402
from kit.events import Piece  # noqa: E402

LEN = 230.0
D_PC = 2
# чистый строй от D: отклонение от равномерного (центы) по интервалу от D
JI = {0: 0.0, 1: 11.7, 2: 3.9, 3: 15.6, 4: -13.7, 5: -2.0, 6: -9.8, 7: 2.0, 8: 13.7, 9: -15.6, 10: -3.9, 11: -11.7}
JI_SEVENTH = -31.2   # натуральная септима 7/4 — только в аккорде натурального ряда


def ji(m, natural7=False):
    iv = (round(m) - D_PC) % 12
    c = JI_SEVENTH if (natural7 and iv == 10) else JI[iv]
    return c / 100.0


# Тема Илуватара: пентатоника D E F♯ A B. (высота D4..E5, длительность в «единицах»)
THEME = [(62, 2), (69, 2), (71, 1), (69, 1), (66, 1.5), (64, .5), (62, 1), (64, 1), (69, 2), (71, 1), (76, 1),
         (74, 3)]
THEME_U = sum(d for _, d in THEME)           # 17 единиц
# вторая тема — обращение вокруг D4: D C B♭ G F (другая пентатоника)
INV = [(62 - (m - 62), d) for m, d in THEME]
# гордая мысль Мелькора: Тема, искажённая его замыслом — тритон вместо квинты, бемоли, свой ритм
MTHEME = [(50, 1), (56, 1), (57, .5), (58, .5), (57, 1), (55, .5), (53, .5), (52, .5), (53, .5), (58, 1), (57, .5),
          (63, 1.5), (62, 2)]                 # D3 G♯3 | A3 B♭3 A3 | G3 F3 E3 F3 | B♭3 A3 E♭4 D4
OSTINATO = [(0, 1, 63), (1, 1, 63), (2, .5, 58), (2.5, .5, 61), (3, 1, 63)]   # единство пустоты: E♭ E♭ B♭ D♭ E♭
# третья тема — Дети Илуватара: дорийская, вольная, фразы 5 + 4 + 7 долей
T3 = [(69, 1), (74, 1.5), (72, .5), (69, 1), (67, 1),
      (69, 1.5), (65, .5), (64, 1), (62, 1),
      (65, 1), (67, .5), (69, .5), (71, 1.5), (69, .5), (67, 1), (64, 1), (62, 1)]
# гармония третьей темы по долям: Dm Dm F C | Dm Am Dm | B♭ C G C A Dm  (корень, качество, бас)
T3_CHORDS = [(0, 2, "m"), (3, 5, "M"), (4, 0, "M"), (5, 2, "m"), (7, 9, "m"), (8, 2, "m"),
             (9, 10, "M"), (10, 0, "M"), (11, 7, "M"), (13, 0, "M"), (14, 9, "M"), (15, 2, "m")]
QUAL = {"M": (0, 4, 7), "m": (0, 3, 7)}


def chord_at(chords, b):
    cur = chords[0]
    for c in chords:
        if c[0] <= b + 1e-9:
            cur = c
    return cur


def voicing(root, qual, mel_lo, mel_notes, n=3, floor=45):
    """аккорд под мелодией: звуки аккорда ниже нижнего звука мелодии минус малая терция, без 2/7/тритона
    с любым звуком мелодии этого отрезка; бас — основной тон"""
    pcs = [(root + x) % 12 for x in QUAL[qual]]
    out = []
    m = mel_lo - 3
    while m >= floor and len(out) < n:
        if m % 12 in pcs and all(abs(m - x) % 12 not in (1, 2, 6, 10, 11) for x in mel_notes):
            if not out or out[-1] - m >= 3:
                out.append(m)
        m -= 1
    return out


def build(ctx):
    p = Piece("Ainulindalë", bpm=60, meter=(4, 4), key="D major", seed=23)
    p.meta["length"] = LEN
    p.meta["reverb_seconds"] = 5.5           # чертоги Илуватара
    p.meta["sends"] = {"choir": 0.6, "strings": 0.5, "harp": 0.6, "winds": 0.45, "organ": 0.55, "brass": 0.34}
    c = Composer(p, lib="vsco", seed=23)
    rng = p.rng

    def note(inst, m, t, d, vel, gain, pure=True, natural7=False, **kw):
        kw.setdefault("attack", 0.12)
        kw.setdefault("release", 0.8)
        det = (ji(m, natural7) if pure else 0.0) + kw.pop("detune", 0.0)
        p.note(inst, m, t, d, vel=vel, gain=gain, detune=det, **kw)

    def line(notes, t0, unit, shift, insts, vel, gain, t_end=None, legato=0.98, pan=0.0, echo=None, wobble=None,
             skip=None, fade=None):
        """провести мелодию: notes [(m, единицы)], unit — секунды на единицу; insts [(инструмент, усиление, сдвиг)];
        echo (задержка, усиление) — эхо в Пустоту; wobble(t) → сила смятения (расстройка, сдвиг во времени)"""
        t = t0
        for m, d in notes:
            dur = d * unit
            if t_end is not None and t >= t_end - 1e-6:
                break
            dd = dur if t_end is None else min(dur, t_end - t)
            if skip is None or not skip(t):
                w = wobble(t) if wobble else 0.0
                fg = fade(t) if fade else 1.0
                for inst, g0, sh in insts:
                    g = g0 * fg
                    det = rng.uniform(-0.45, 0.45) * w
                    tt = t + rng.uniform(0, 0.12) * w
                    note(inst, m + shift + sh, tt, dd * legato, vel, gain * g, detune=det, pan=pan,
                         attack=min(0.25, 0.08 + dd * 0.15), release=min(1.6, 0.3 + dd * 0.4))
                    if echo:
                        note(inst, m + shift + sh, tt + echo[0], dd * legato, vel * 0.8, gain * g * echo[1], detune=det,
                             pan=-pan, attack=0.2, release=1.4)
            t += dur
        return t

    for t, label in ((0, "I Голоса порознь"), (22, "II Илуватар предлагает Тему"), (36.5, "III Великая Музыка"),
                     (80, "IV Мысль Мелькора и разлад"), (110, "V Вторая тема"), (124, "Vb Господство Мелькора"),
                     (132, "VI Третья тема — Дети Илуватара"), (148, "VIb Две музыки"), (160, "VIc Вбирание"),
                     (176, "VII Один аккорд"), (185, "VIII Видение"), (214, "IX Эа")):
        p.mark(t, label)

    # ============================================================ I. Голоса порознь (0–22)
    # «каждый понимал лишь ту часть разума Илуватара, из которой вышел»: голова Темы в далёких тональностях,
    # затем всё ближе к D и всё чаще вместе — «согласие и гармония их возрастали»
    HEAD = [(0, 1.3), (7, 1.3), (9, .9), (7, 2.0)]
    SOLOS = [("fl_sus", 1.0, 79, 0.6), ("vla_sus", 4.2, 54, -0.4), ("harp", 7.0, 76, 0.2), ("cl_sus", 9.5, 61, -0.6),
             ("hn_sus", 12.0, 57, 0.5), ("vln_solo", 13.4, 69, -0.2), ("choir", 15.2, 62, 0.0),
             ("fl_sus", 16.0, 74, 0.5), ("vla_sus", 16.8, 57, -0.4)]
    for inst, t0, base, pan in SOLOS:
        t = t0
        for iv, d in HEAD:
            note(inst, base + iv, t, d * 0.97, 0.5, 0.42, pure=(base % 12) in (2, 9), pan=pan,
                 attack=0.2, release=1.4)
            t += d
    # тишина-ожидание 20.6–22: Илуватар созывает всех

    # ============================================================ II. Илуватар предлагает Тему (22–36.5)
    # «слава, в коей началась та музыка, и великолепие, в коей она окончилась» — расцвет в начале и в конце
    for m in (38, 45, 50, 54, 57):
        note("org_quiet", m, 22.0, 2.6, 0.55, 0.3, attack=1.2, release=1.5)
    for m in (50, 57):
        note("choir", m, 22.0, 2.6, 0.5, 0.35, attack=1.0, release=1.2)
    U2 = 0.68
    org_below = lambda m: m - 7 if (m - 7) % 12 in (2, 4, 6, 9, 11) else m - 5  # noqa: E731 органум ниже
    t = 23.6
    for m, d in THEME:
        dur = d * U2
        for inst, mm, g in (("choir", m - 12, 0.5), ("choir", org_below(m - 12), 0.4), ("hn_sus", m - 12, 0.32),
                            ("org_quiet", m - 12, 0.25), ("org_quiet", org_below(m - 12) - 12, 0.22),
                            ("vc_sus", org_below(m - 12) - (12 if org_below(m - 12) - 12 >= 36 else 0), 0.25)):
            note(inst, mm, t, dur * 0.98, 0.55, g, attack=0.15, release=0.9)
        t += dur
    for m in (62, 66, 69, 74, 78, 81, 86):            # великолепие конца: высокий расцвет
        inst = "vln_sus" if m >= 74 else "choir"
        note(inst, m, 34.3, 1.6, 0.6, 0.28, attack=0.4, release=1.6)
    note("harp", 74, 34.3, 2.0, 0.55, 0.35, release=2.0)
    # 35.9–36.5: «Айнур преклонились перед Илуватаром и умолкли»

    # ============================================================ III. Великая Музыка (36.5–80): канон в шести скоростях
    def drowned(t):                       # «мелодии, что слышались изначально, утонули в море нестройных звуков»
        return 1.0 - 0.75 * max(0.0, min(1.0, (t - 90.0) / 12.0))

    def troubled(t):                      # смятение соседей Мелькора (82–95)
        return max(0.0, min(1.0, (t - 81.0) / 8.0)) if t < 96 else 1.0

    LAYERS = [  # (вступление, единица, сдвиг, [(инстр., усил., сдвиг)], vel, gain, pan, эхо, конец)
        (36.8, 0.60, 0, [("vla_sus", 1.0, 0), ("choir", 0.8, 0), ("cl_sus", 0.45, 0)], 0.5, 0.42, -0.2, (0.45, 0.3), 92),
        (39.0, 1.20, -12, [("hn_sus", 1.0, 0), ("choir", 0.85, 0)], 0.5, 0.4, 0.25, (0.6, 0.25), 86.6),
        (42.5, 0.30, 12, [("vln_sus", 1.0, 0), ("fl_sus", 0.5, 0)], 0.48, 0.38, 0.35, (0.3, 0.3), 104),
        (45.5, 2.40, -24, [("vc_sus", 1.0, 0), ("cb_sus", 0.9, 0), ("org_quiet", 0.5, 0)], 0.5, 0.42, -0.1, None, 90),
        (51.0, 0.15, 24, [("harp", 1.0, 0), ("vln_harm", 0.4, 0)], 0.42, 0.32, 0.5, (0.22, 0.35), 100),
        (57.0, 4.80, -36, [("cbsn_sus", 1.0, 0), ("org_loud", 0.35, 0)], 0.5, 0.35, 0.0, None, 82),
    ]
    for t0, unit, sh, insts, vel, gain, pan, echo, t_end in LAYERS:
        t = t0
        k = 0
        while t < t_end - 0.05:
            v = vel + 0.18 * min(1.0, (t - 36.5) / 34.0)           # нарастание: чертоги переполняются
            t = line(THEME, t, unit, sh, insts, v, gain, t_end=t_end, pan=pan if k % 2 == 0 else -pan, echo=echo,
                     wobble=troubled if unit >= 0.6 else None, fade=drowned)
            k += 1

    # ============================================================ IV. Мысль Мелькора и разлад (80–110)
    MU = 0.6

    def melkor_line(t0, shift, insts, vel, gain, unit=MU, pan=-0.35):
        t = t0
        for m, d in MTHEME:
            for inst, g, sh in insts:
                note(inst, m + shift + sh, t, d * unit * 0.9, vel, gain * g, pure=False, pan=pan, attack=0.02,
                     release=0.35)
            t += d * unit
        return t

    BRASS_LO = [("tbn_sus", 1.0, 0), ("tba_sus", 0.8, -12), ("bcl_sus", 0.5, 0)]
    t = melkor_line(80.0, 0, BRASS_LO, 0.8, 0.45)                                   # своя мысль, гордая
    t = melkor_line(t, 1, BRASS_LO + [("hn_sus", 0.9, 12)], 0.88, 0.45)           # соседи подхватывают (86.6)
    t = melkor_line(t, 6, [("tbn_sus", 1.0, 0), ("hn_sus", 0.9, 0), ("vla_sus", 0.8, 12)], 0.92, 0.45, unit=0.5)
    # 93–108: море нестройных звуков — тёмные волны, воюющие друг с другом
    for period, base, inst, ph in ((3.0, 38, "cb_trem", 0.0), (4.3, 45, "vc_trem", 1.1), (3.7, 52, "vla_trem", 2.0),
                                   (5.1, 58, "vln_trem", 0.6)):
        t = 93.0 + ph
        while t < 110.0:
            d = min(period, 110.5 - t)
            note(inst, base + rng.choice((0, 1, 3, 6)), t, d, 0.95, 0.55, pure=False, attack=d * 0.55, release=0.4,
                 bend=rng.choice((-2.5, 2.0, 3.5, -1.5)))
            t += period * 0.8
    for k, t0 in enumerate((95.0, 97.4, 99.2, 101.6, 103.0, 104.8, 106.0)):    # обрывки его мысли — стреттой
        head = MTHEME[:5]
        tt = t0
        for m, d in head:
            for inst, g, sh in (("tbn_sus", 1.0, 0), ("hn_sus", 0.8, 12), ("tpt_sus", 0.6, 12)):
                note(inst, m + (k * 5) % 12 - 2 + sh, tt, d * 0.5 * 0.9, 1.0, 0.5 * g, pure=False, attack=0.02,
                     release=0.3, pan=rng.uniform(-0.7, 0.7))
            tt += d * 0.5
    for m in (50, 52, 53, 56, 57, 58):                                              # хоры, захваченные разладом
        note("choir", m, 98.0, 11.5, 0.8, 0.3, pure=False, attack=4.0, release=0.5, bend=rng.choice((-1.5, 1.5)))
    c.timp(97.0, 2, vel=0.7, roll=12.5)
    c.fx("tamtam", 104.0, gain=0.25, bus="perc")
    c.fx("sso_cymbal", 101.0, gain=0.15, bus="perc", attack=3.0, dur=8.0, fade=0.5)

    # ============================================================ V. Вторая тема (110–132)
    # «восстал Илуватар… улыбается… левая рука» — посреди бури, похожая и непохожая, обрела силу и красу
    SEC = [(110.0, 0.55, 24, [("vln_sus", 1.0, 0), ("fl_sus", 0.6, 0)], 0.5, 0.42, 0.35, 124.0),
           (111.5, 1.10, 12, [("choir", 1.0, 0), ("vla_sus", 0.7, 0)], 0.52, 0.42, -0.25, 125.5),
           (113.5, 0.275, 36, [("harp", 1.0, 0), ("vln_harm", 0.35, 0)], 0.45, 0.3, 0.5, 127.0),
           (115.0, 2.20, 0, [("hn_sus", 1.0, 0), ("vc_sus", 0.8, -12)], 0.52, 0.4, 0.0, 126.0)]
    for t0, unit, sh, insts, vel, gain, pan, t_end in SEC:
        t = t0
        while t < t_end - 0.05:
            v = vel + 0.15 * min(1.0, (t - 110.0) / 10.0)
            t = line(INV, t, unit, sh, insts, v, gain, t_end=t_end, pan=pan, echo=(0.4, 0.25))
    # 120: разлад громче, битва яростнее; «многие Айнур пришли в ужас и перестали играть» — голоса обрываются
    t = melkor_line(119.0, 0, [("tbn_sus", 1.0, 0), ("tba_sus", 0.8, -12), ("tpt_sus", 0.7, 12)], 0.95, 0.48)
    for period, base, inst, ph in ((2.8, 38, "cb_trem", 0.0), (3.9, 45, "vc_trem", 0.7)):
        t = 119.0 + ph
        while t < 132.0:
            d = min(period, 132.0 - t)
            note(inst, base + rng.choice((0, 1, 6)), t, d, 0.9, 0.3, pure=False, attack=d * 0.5, release=0.3,
                 bend=rng.choice((-2.0, 3.0)))
            t += period * 0.75
    # 125.6–132: господство — его мысль в увеличении всей медью
    melkor_line(125.6, 0, [("tpt_sus", 1.0, 12), ("tbn_sus", 1.0, 0), ("tba_sus", 0.9, -12), ("hn_sus", 0.8, 12)],
                1.0, 0.45, unit=0.58)
    c.timp(126.0, 2, vel=0.6, roll=5.5)

    # ============================================================ VI. Третья тема (132–176)
    def t3(t0, beat, mel_insts, mel_shift, vel, gain, harm=None, ripple=False, pan=0.3):
        """провести третью тему; harm — [(инстр., усил.)] для аккордов под ней; ripple — рябь арфы по аккордам"""
        b = 0.0
        notes_b = []
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
                lo = min(seg)
                vc_ = voicing(root, q, lo, seg, n=3, floor=50)
                bass = 38 + (root - 2) % 12 if (root - 2) % 12 <= 8 else 26 + (root - 2) % 12
                if harm:
                    for inst, g in harm:
                        ms = [bass] if inst in ("vc_sus", "cb_sus", "bsn_sus") else vc_
                        for mm in ms:
                            note(inst, mm, t0 + cb * beat, (ce - cb) * beat * 0.98, vel * 0.9, gain * g, attack=0.3,
                                 release=0.9, pan=-pan * 0.5)
                if ripple:
                    pcs = [(root + x) % 12 for x in QUAL[q]]
                    arp = sorted({m for m in range(57, 86) if m % 12 in pcs})[:6]
                    tt = t0 + cb * beat
                    k = 0
                    while tt < t0 + ce * beat - 0.05:
                        mm = arp[k % len(arp)] if (k // len(arp)) % 2 == 0 else arp[-1 - k % len(arp)]
                        end = t0 + ce * beat
                        if all(abs(mm - x) % 12 not in (1, 11, 6) for x in seg):
                            note("harp", mm, tt, min(0.6, end - tt), vel * 0.8, gain * 0.5,
                                 release=0.7 if tt + 0.6 < end else 0.12, pan=-0.4)
                        tt += beat / 4
                        k += 1

    # 132–144: тихая рябь посреди смятения — скрипка соло, флейта, арфа
    for period, base, inst, ph in ((3.5, 38, "cb_trem", 0.0),):                    # смятение ещё длится внизу
        t = 132.0
        while t < 141.0:
            note(inst, base + rng.choice((0, 1)), t, 3.0, 0.6, 0.18, pure=False, attack=1.2, release=0.6)
            t += period
    melkor_line(132.0, 0, [("tbn_sus", 1.0, 0)], 0.6, 0.32, unit=0.7)              # его мысль слабеет, но шумит
    t3(132.0, 0.75, [("vln_solo", 1.0), ("fl_sus", 0.4)], 12, 0.45, 0.42, ripple=True)
    # 144–160: «её невозможно было заглушить, и она росла, обретая мощь и глубину»
    t3(144.0, 1.0, [("vln_sus", 1.0), ("choir", 0.8)], 0, 0.6, 0.42,
       harm=[("vla_sus", 0.8), ("hn_sus", 0.6), ("cl_sus", 0.4), ("vc_sus", 0.9), ("cb_sus", 0.7)], pan=0.25)
    t3(144.0, 1.0, [("vln_sus", 0.6)], 12, 0.55, 0.42)
    # 148–172: музыка Мелькора «достигла внутреннего единства»: громкая, пустая, бесконечно повторяемая —
    # трубы в унисон на нескольких нотах
    for bar in range(148, 172, 4):
        insts = ([("tpt_sus", 1.0, 0), ("tpt_sus", 0.8, 12), ("tbn_sus", 0.9, -12), ("tba_sus", 0.8, -24)]
                 if bar < 160 else [("tpt_sus", 1.0, 0), ("tpt_sus", 0.6, 12)] if bar < 168 else [("tpt_sus", 0.8, 0)])
        for tt, d, m in OSTINATO:
            for inst, g, sh in insts:
                note(inst, m + sh, bar + tt, d * 0.85, 0.92 if bar < 168 else 0.7, 0.42 * g, pure=False, attack=0.01,
                     release=0.2, pan=-0.4)
    # 160–176: «вплетает в свою скорбную часть победные ноты соперницы»: бас E♭–B♭–C♯–D = N — VI — V7 — I
    ABS = [(160.0, 51, (67, 63, 58)), (164.0, 46, (65, 62, 58)), (168.0, 49, (64, 61, 57)),
           (170.0, 49, (64, 61, 55)), (172.0, 50, (66, 62, 57))]
    for i, (t0, bass, upper) in enumerate(ABS):
        d = (ABS[i + 1][0] if i + 1 < len(ABS) else 176.0) - t0
        for inst, mm, g in (("vc_sus", bass, 0.9), ("cb_sus", bass - 12, 0.8), ("tbn_sus", bass, 0.7),
                            ("tba_sus", bass - 12, 0.7), ("cbsn_sus", bass - 24, 0.5)):
            note(inst, mm, t0, d * 0.99, 0.75, 0.42 * g, attack=0.4, release=0.4)
        for j, mm in enumerate(upper):
            for inst, g in (("choir", 0.9), ("vln_sus" if j == 0 else "vla_sus", 0.8), ("hn_sus", 0.5)):
                note(inst, mm + (12 if inst == "vln_sus" else 0), t0, d * 0.99, 0.72, 0.4 * g, attack=0.4,
                     release=0.4)

    # ============================================================ VII. Один аккорд (176–180.5): натуральный ряд D
    # натуральный ряд без 7-го и 14-го обертонов (их септима с 5-м — тритон): мажор с ноной в чистом строе
    PARTIALS = [(1, 26), (2, 38), (3, 45), (4, 50), (5, 54), (6, 57), (8, 62), (9, 64), (10, 66), (12, 69),
                (16, 74), (18, 76), (20, 78), (24, 81), (32, 86), (40, 90), (48, 93), (64, 98)]
    ORCH = {26: ["org_loud", "cbsn_sus"], 38: ["org_loud", "cbsn_sus", "cb_sus", "tba_sus"], 45: ["cb_sus", "vc_sus", "tba_sus"],
            50: ["vc_sus", "tbn_sus", "choir", "org_loud"], 54: ["tbn_sus", "choir"], 57: ["tbn_sus", "vc_sus", "choir"],
            60: ["hn_sus", "choir"], 62: ["hn_sus", "vla_sus", "choir", "org_loud"], 64: ["vla_sus", "cl_sus"],
            66: ["hn_sus", "choir", "cl_sus"], 69: ["tpt_sus", "choir", "vla_sus"], 72: ["choir", "ob_sus"],
            74: ["tpt_sus", "vln_sus", "choir", "harp"], 76: ["vln_sus", "ob_sus"], 78: ["tpt_sus", "vln_sus", "choir"],
            81: ["vln_sus", "fl_sus", "choir"], 86: ["vln_sus", "fl_sus", "harp"], 90: ["fl_sus", "vln_harm"],
            93: ["vln_harm", "picc_sus"], 98: ["vln_harm", "picc_sus"]}
    for n_, m in PARTIALS:
        for inst in ORCH[m]:
            g = 0.3 / (1 + 0.04 * n_) * (0.08 if inst == "picc_sus" else 0.6 if inst == "choir" else
                                          0.7 if n_ in (7, 14) else 1.0)
            note(inst, m, 176.0, 4.5, 0.95, g, natural7=True, attack=0.04, release=0.4)
    note("harp", 50, 176.0, 4.0, 0.9, 0.35, release=0.4)
    c.timp(176.0, 2, vel=0.7)
    # 180.5–185: тишина — говорит Илуватар

    # ============================================================ VIII. Видение (185–210.5): музыка становится землёй
    cut = 210.5
    PENT = (62, 64, 66, 69, 71)
    CHILD = (62, 67, 69, 72)               # когда звучат Дети (дорийская мелодия), вода подстраивается под неё
    T_CHILD = 204.5
    t, k = 185.0, 0
    while t < cut - 1e-9:                                   # вода Ульмо: рябь
        ps = PENT if t < T_CHILD - 0.5 else CHILD
        up = [ps[(k + j) % len(ps)] + 12 * ((k + j) // len(ps) % 2) for j in range(5)]
        for j, m in enumerate(up + up[-2:0:-1]):
            tt = t + j * 0.125
            stop = cut if ps is CHILD else T_CHILD - 0.5      # смена лада — без звенящих хвостов
            if tt < stop:
                note("harp", m, tt, min(0.9, stop - tt), 0.34, 0.3, release=0.6 if tt + 0.9 < stop else 0.08,
                     pan=-0.4 + 0.8 * ((k % 4) / 3))
        t += 1.0
        k += 1
    for m in (86, 93):
        note("vln_harm", m, 185.5, cut - 185.5, 0.3, 0.12, attack=3.0, release=0.05, pan=0.2)
    for t0, base in ((188.0, 50), (197.0, 57)):            # рог Ульмо
        tt = t0
        for iv, d in HEAD:
            note("hn_sus", base + iv, tt, d, 0.42, 0.3, attack=0.2, release=1.0, pan=-0.6)
            tt += d
    for t0, m, d in ((192, 83, 1), (193, 81, 1), (194, 78, 1.5), (195.5, 76, .5), (196, 74, 1.5)):  # ветер Манвэ
        note("fl_sus", m, t0, d, 0.36, 0.3, attack=0.1, release=0.6, pan=0.6)
    for t0 in range(199, 210):                             # земля Аулэ
        note("vc_pizz", 38 if t0 % 2 else 45, t0, 0.4, 0.5, 0.35, release=0.3, pan=-0.2)
    t = 193.0                                              # дождь: «моя музыка слышна в шорохе дождя»
    while t < cut - 0.2:
        note("vln_pizz", rng.choice(PENT if t < T_CHILD else CHILD) + 12 * rng.choice((1, 2)), t, 0.2,
             rng.uniform(0.25, 0.45), 0.2,
             release=0.3, pan=rng.uniform(-0.8, 0.8))
        t += rng.uniform(0.12, 0.45)
    note("cb_trem", 38, 201.0, 4.0, 0.6, 0.25, attack=2.0, release=1.0)              # рёв моря — «великий непокой»
    note("vc_trem", 45, 201.5, 3.5, 0.55, 0.2, attack=2.0, release=1.0)
    tt = T_CHILD                                           # и Дети — их мелодия, одна, тихо
    for m, d in T3[:9]:
        dd = d * 0.7
        if tt >= cut:
            break
        note("vln_solo", m, tt, min(dd, cut - tt) * 0.97, 0.42, 0.4, attack=0.15, release=0.6 if tt + dd < cut else 0.05,
             pan=0.3)
        tt += dd
    # 210.5: видение сокрылось — Тьма (тишина до 214)

    # ============================================================ IX. Эа (214–230): облако с живым пламенным сердцем
    for inst, m, g, t0 in (("choir", 74, 0.3, 214.0), ("choir", 78, 0.25, 214.5), ("choir", 81, 0.22, 215.0),
                           ("vln_harm", 86, 0.12, 214.5), ("vln_harm", 93, 0.1, 215.5), ("org_quiet", 62, 0.2, 214.0),
                           ("org_quiet", 69, 0.18, 214.5), ("fl_sus", 86, 0.12, 216.0)):
        note(inst, m, t0, 227.0 - t0, 0.36, g, attack=3.0, release=3.0, pan=rng.uniform(-0.3, 0.3))
    t = 216.5
    k = 0
    while t < 227.0:                                       # сердце: впервые ровный пульс — начинается Время
        c.timp(t, 2, vel=0.32 + 0.1 * min(1.0, k / 4))
        note("harp", 38, t + 0.28, 1.0, 0.4, 0.3, release=1.0)
        note("cb_pizz", 38, t + 0.28, 0.6, 0.4, 0.25, release=0.6)
        t += 1.1
        k += 1
    note("choir", 62, 219.0, 8.0, 0.4, 0.3, attack=2.5, release=3.0)
    note("choir", 69, 219.5, 7.5, 0.4, 0.28, attack=2.5, release=3.0)
    # баланс партий по замеру --parts (эскиз 0–120 с): Тема и бас — вровень, мысль Мелькора — наравне с Темой
    p.balance({"Contrabassoon": -12, "Choir": +4, "Violins": +8, "Horn": +2, "Flute": -3, "Trombone": +9.5,
               "Bass clarinet": -2, "Basses": +5, "Organ": +7, "Violin solo": +14, "Harp": +8, "Timpani": +9})
    return p
