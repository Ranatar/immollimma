#!/usr/bin/env python3
"""Hora Lucis Defunctae — час угасшего света (≈ 6:07).

Глава «De Hora Lucis Defunctae» кодекса Айдана (relatio_aidani_codex.html, листы xii–xiv). Айдан только смотрит:
его вечерни здесь нет. Хор поёт без слов — Айдан не понимал слов эльфов, до него доходила одна красота звука.

Сквозной процесс — свет. Вся пьеса стоит на одном белоклавишном звукоряде (мир Древ), и он «поворачивается»,
как Ковш за окном Айдана («paulo conversum»): опора ля (путь, закат) → ми (Варда) → фа (Яванна) → ре (Ниенна,
литания). Единственный звук вне звукоряда — фа-диез месяца, который Айдан в Амане видит впервые; потом им же
утешает Финрод.

  0:00  Veni mecum         валторна (Финрод) зовёт; шаги арфы и пиццикато, «как в храме»
  0:20  Theatrum           эльфы сходятся молча: струнные входят по одному звуку
  0:40  Occasus            закат: аккорд золотых валторн оседает к рыжим виолончелям и почти ничему
  1:20  Vox una            один голос без инструмента, к нему другой, третий
  1:36  I Varda            серебро: три высоких голоса, ми-фригийский; флажолеты и кротали — звёзды
  2:16  II Yavanna         золото: хорал ниже и теплее, фа-лидийский; Тельперион и Лаурэлин чередуются
  3:00  III Nienna         ре-дорийский: плач и его зеркальное обращение вокруг ре звучат вместе
                           и сходятся в один звук — нельзя отличить плачущих от ликующих (Ездра 3:13)
  3:48  silentium magnum
  3:52  Litania            речитатив Финрода, каденция «vos memoramur»; каждому имени — отголосок его музыки
  4:43  Ilúvatar           речитатив на кварту выше; 5:03 — общий поклон, плагальный аккорд
  5:12  Caelum stellarum   звёзды; 5:24 — месяц (фа-диез)
  5:42  Descensus          «Quae vere dolent, vere etiam consolantur… nondum totum est» — и полное молчание

    python3 -m kit run requests/hora-lucis-defunctae/piece.py --sketch --parts
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from kit.events import Piece  # noqa: E402
from kit.harmony import midi as M  # noqa: E402

BPM = 60          # доля = секунда: метки сценария ложатся на доли

# секции (секунды)
T_VENI, T_THEA, T_OCC, T_VOX, T_VARDA, T_YAV, T_NIEN = 0, 20, 40, 80, 96, 136, 180
T_SIL, T_LIT, T_ILU, T_STARS, T_MOON, T_DESC, T_END, LENGTH = 228, 232, 283, 312, 324, 342, 361, 367

D4 = 62           # ось зеркала Ниенны

# замер эскиза 0–136 (--parts): хор −31, басы −48, флажолеты −62, челеста −62, кротали не слышны
# окна (--from/--to --parts): Яванна — бас −5, Лаурэлин −11, Тельперион −13 от хора; Ниенна — педаль ре −18;
# звёзды и колокол заката не слышны (−55…−63); месяц на 18 дБ тише валторны Финрода
BALANCE = {"Basses": +8, "Violin harmonics": +14, "Viola harmonics": +8, "Celesta": +18, "Crotales": +24,
           "Telperion (harmonics)": +14, "Laurelin (cellos)": +5, "Luna (harmonic)": +16, "Horns": +3}


class Score:
    def __init__(self):
        self.p = Piece("Hora Lucis Defunctae", bpm=BPM, meter=(4, 4), key="A minor", seed=896)
        self.p.meta["subtitle"] = "час угасшего света — по кодексу брата Айдана, лл. xii–xiv"
        self.p.meta["sends"] = {"choir": 0.6, "strings": 0.5, "brass": 0.5, "winds": 0.5, "harp": 0.6}

    def n(self, inst, m, t, dur, part, vel=0.5, gain=0.5, attack=0.08, release=0.8, pan=0.0, art=None):
        if isinstance(m, str):
            m = M(m)
        return self.p.note(inst, m, t, dur, vel=vel, gain=gain, attack=attack, release=release, part=part,
                           pan=pan, art=art)

    def line(self, inst, notes, t, part, legato=0.96, **kw):
        """notes: [(pitch or None, seconds)]; returns the end time"""
        for m, d in notes:
            if m is not None:
                self.n(inst, m, t, d * legato, part, **kw)
            t += d
        return t

    # голос Финрода: речитатив по слогам
    def recite(self, t, sylls, part="Horn (Finrod)", syl=0.32, last=1.2, vel=0.5, gain=0.5):
        """sylls: list of pitches (one per syllable) or (pitch, seconds); returns the end time"""
        for i, s in enumerate(sylls):
            m, d = (s if isinstance(s, tuple) else (s, last if i == len(sylls) - 1 else syl))
            self.n("hn_sus", m, t, d * 0.97, part, vel=vel, gain=gain, attack=0.04, release=0.7)
            t += d
        return t


def tones(*names):
    return [M(x) for x in names]


def build(ctx):
    s = Score()
    p = s.p
    mk = p.mark

    # ───────────── Veni mecum ─────────────
    mk(T_VENI, "Veni mecum")
    # педаль ля под зовом
    s.n("cb_sus", "A1", 0.0, 9.0, "Basses", vel=0.35, gain=0.45, attack=1.5, release=1.5)
    s.n("vc_sus", "E2", 0.5, 8.5, "Cellos", vel=0.3, gain=0.35, attack=1.8, release=1.5)
    # «Ve-ni me-cum hac ves-pe-ra»: речитатив на ля, формула вниз к ми
    s.recite(1.0, [M("A3")] * 5 + [M("G3"), M("A3"), (M("E3"), 2.4)], syl=0.42, gain=0.55)
    # шаги: бас половинками, арфа октавой выше, тихие аккорды струнных — как в храме
    walk = [("A2", ("C4", "E4")), ("G2", ("B3", "E4")), ("F2", ("A3", "C4")), ("E2", ("G3", "C4")),
            ("F2", ("A3", "C4")), ("E2", ("G3", "B3"))]
    for i, (b, ch) in enumerate(walk):
        t = 8.0 + 2 * i
        s.n("cb_pizz", b, t, 1.2, "Basses", vel=0.45, gain=0.5, release=0.6)
        s.n("harp", M(b) + 12, t, 1.6, "Harp", vel=0.4, gain=0.4, release=1.2)
        for j, c in enumerate(ch):
            s.n("vla_sus" if j == 0 else "vln_sus", c, t, 2.0, "Violas" if j == 0 else "Violins",
                vel=0.25, gain=0.3, attack=0.5, release=0.6)
    # «Ve-ni nunc»
    s.recite(12.5, [M("A3"), M("B3"), (M("C4"), 3.0)], syl=0.45, gain=0.55)

    # ───────────── Theatrum ─────────────
    mk(T_THEA, "Theatrum")
    enter = [(20.0, "cb_sus", "A1", "Basses"), (21.5, "vc_sus", "E2", "Cellos"), (23.5, "vla_sus", "A3", "Violas"),
             (25.5, "vln_sus", "C5", "Violins"), (27.5, "vla_sus", "E4", "Violas"), (29.5, "vln_sus", "D5", "Violins"),
             (31.5, "vc_sus", "G3", "Cellos"), (33.5, "vln_harm", "E6", "Violin harmonics")]
    for t, inst, m, part in enter:
        end = T_OCC - 3.0 if m in ("E2", "G3") else T_OCC - 0.5     # низы уходят раньше: под фа не тянуть ми
        s.n(inst, m, t, end - t, part, vel=0.25, gain=0.32 if inst != "vln_harm" else 0.22,
            attack=3.0, release=2.0, pan=(-0.3 if "vla" in inst or "vc" in inst else 0.3))
    # среди старцев и детей — тот, что дал Айдану ягоду: «ai-pi-o»
    s.line("celesta", [(M("A5"), 0.5), (M("G5"), 0.5), (M("E5"), 2.0)], 35.5, "Celesta", vel=0.3, gain=0.22)

    # ───────────── Occasus: золото → рыжее → почти ничего ─────────────
    mk(T_OCC, "Occasus")
    sunset = [  # (время, аккорд, инструменты)
        (40, tones("F3", "A3", "C4", "E4"), "gold"),     # Лаурэлин аккордом
        (45, tones("E3", "G3", "B3", "D4"), "gold"),
        (50, tones("D3", "F3", "A3", "C4"), "gold+vc"),
        (55, tones("C3", "E3", "G3", "B3"), "vc+gold"),
        (60, tones("A2", "C3", "E3", "G3"), "vc"),
        (65, tones("G2", "B2", "E3"), "vc+cb"),
        (70, tones("F2", "C3", "G3"), "cb+vc"),
        (75, tones("E2", "B2"), "cb"),
    ]
    for k, (t, ch, col) in enumerate(sunset):
        dur = 4.9 if k < 7 else 4.0       # смена — хвостом реверберации, без наложения соседних аккордов
        fade = 1.0 - 0.09 * k
        for j, m in enumerate(ch):
            if col.startswith("gold") or col.endswith("gold"):
                s.n("hns_sus", m, t, dur, "Horns", vel=0.42 * fade, gain=0.42 * fade, attack=1.2, release=1.4)
            if "vc" in col:
                s.n("vc_sus", m, t, dur, "Cellos", vel=0.35, gain=0.4 * fade, attack=1.4, release=1.6, pan=-0.2)
            if "cb" in col and j == 0:
                s.n("cb_sus", m - 12 if m - 12 >= 28 else m, t, dur, "Basses", vel=0.3, gain=0.42 * fade,
                    attack=1.6, release=1.8)
            if col == "cb" and j == 1:
                s.n("cb_sus", m, t, dur, "Basses", vel=0.25, gain=0.25, attack=2.0, release=1.5)
        # колокол времени: низкая нота арфы на смене аккорда, пока свет ещё золотой
        if k < 5:
            s.n("harp", ch[0] - 12, t, 3.0, "Harp", vel=0.42, gain=0.7 * fade, release=2.0)
    # последний край солнца — флажолет ми, гаснет к 79 с (голос должен войти без инструмента)
    s.n("vln_harm", "E6", 70.0, 8.0, "Violin harmonics", vel=0.2, gain=0.14, attack=2.5, release=0.8)

    # ───────────── Vox una ─────────────
    mk(T_VOX, "Vox una")
    ch = dict(vel=0.5, attack=0.25, release=1.0)
    s.line("choir", [(M("E5"), 3), (M("F5"), 1), (M("E5"), 1), (M("D5"), 1), (M("E5"), 2),
                     (M("G5"), 2), (M("E5"), 2), (M("D5"), 2), (M("E5"), 2)], 80.0, "Choir I",
           gain=0.42, pan=0.0, legato=0.99, **ch)
    s.line("choir", [(M("B4"), 2), (M("A4"), 2), (M("B4"), 6)], 86.0, "Choir II", gain=0.36, pan=-0.25,
           legato=0.99, **ch)
    s.line("choir", [(M("A4"), 4), (M("E4"), 2)], 90.0, "Choir III", gain=0.33, pan=0.25, legato=0.99, **ch)

    # ───────────── I Varda, Tintallë: серебро ─────────────
    mk(T_VARDA, "I Varda, Tintallë")
    v1 = [("E5", 4), ("F5", 1), ("E5", 1), ("D5", 2), ("E5", 2),
          ("G5", 3), ("F5", 1), ("E5", 2), ("D5", 4),
          ("A5", 4), ("G5", 1), ("F5", 1), ("E5", 2), ("F5", 2),
          ("E5", 2), ("D5", 2), ("C5", 2), ("B4", 2), ("C5", 2)]
    v2 = [("B4", 10), ("C5", 6), ("B4", 4), ("D5", 6), ("C5", 4), ("B4", 4), ("A4", 6)]
    v3 = [("A4", 10), ("G4", 10), ("A4", 10), ("E4", 8), ("F4", 2)]
    s.line("choir", [(M(a), b) for a, b in v1], T_VARDA, "Choir I", gain=0.45, legato=0.99, **ch)
    s.line("choir", [(M(a), b) for a, b in v2], T_VARDA, "Choir II", gain=0.37, pan=-0.25, legato=0.99, **ch)
    s.line("choir", [(M(a), b) for a, b in v3], T_VARDA, "Choir III", gain=0.35, pan=0.25, legato=0.99, **ch)
    # Тинталлэ зажигает звёзды: по одной в начале каждой фразы — кротали и флажолет остаются
    for k, m in enumerate(tones("E6", "A6", "D7", "E7")):
        t = T_VARDA + 1 + 10 * k
        s.n("crotales", m, t, 3.0, "Crotales", vel=0.45, gain=0.22, release=3.0, pan=0.35 - 0.2 * k)
        s.n("vln_harm", m, t + 0.3, T_YAV - 2.5 - t, "Violin harmonics", vel=0.2, gain=0.12, attack=2.0, release=2.0,
            pan=0.35 - 0.2 * k)
    # верхний голос в серебре — флажолеты альтов на октаву ниже звёзд (очень тихо, «luminis frigidi»)
    s.line("vla_harm", [(M(a) + 12 if a[0] != "F" else None, b) for a, b in v1[:9]], T_VARDA, "Viola harmonics", vel=0.2, gain=0.1,
           legato=0.98, attack=0.4, release=0.8)

    # ───────────── II Yavanna: золото ─────────────
    mk(T_YAV, "II Yavanna")
    bars = [  # (бас, хор III, хор II, мелодия хора I)
        ("F2", "F3", "C4", [("A4", 4)]),
        ("F2", "G3", "D4", [("B4", 4)]),                 # лидийское свечение
        ("A2", "E3", "C4", [("A4", 2), ("G4", 2)]),
        ("D2", "A3", "D4", [("F4", 4)]),
        ("C2", "G3", "C4", [("E4", 2), ("D4", 2)]),
        ("E2", "G3", "B3", [("G4", 4)]),
        ("F2", "A3", "C4", [("A4", 2), ("C5", 2)]),
        ("G2", "G3", "D4", [("B4", 4)]),
        ("A2", "A3", "C4", [("A4", 4)]),
        ("G2", "E3", "B3", [("G4", 2), ("E4", 2)]),
        ("F2", "A3", "C4", [("A4", 4)]),
    ]
    for k, (b, lo, mid, mel) in enumerate(bars):
        t = T_YAV + 4 * k
        last = k == len(bars) - 1
        d = 5.0 if last else 4.0
        warm = 0.85 + 0.15 * (k / 10)
        s.n("cb_sus", b, t, d, "Basses", vel=0.4, gain=0.5 * warm, attack=0.5, release=1.2)
        s.n("vc_sus", M(b) + 12, t, d, "Cellos", vel=0.38, gain=0.36 * warm, attack=0.5, release=1.2, pan=-0.2)
        s.n("choir", lo, t, d * 0.99, "Choir III", gain=0.38, pan=0.25, **ch)
        s.n("choir", mid, t, d * 0.99, "Choir II", gain=0.38, pan=-0.25, **ch)
        s.line("choir", [(M(a), bb) for a, bb in mel],
               t, "Choir I", gain=0.46, legato=0.99, **ch)
        for m in (lo, mid):  # золото: валторны удваивают средние голоса
            s.n("hns_sus", m, t, d, "Horns", vel=0.38, gain=0.26 * warm, attack=0.6, release=1.0)
        # арфа берёт аккорд медленным арпеджио
        for i, m in enumerate((M(b) + 12, M(lo), M(mid))):
            s.n("harp", m, t + 0.09 * i, 3.0, "Harp", vel=0.38, gain=0.3, release=1.5, pan=0.2)
    # Лаурэлин (виолончель соло-строкой) и Тельперион (флажолеты) — как свет Древ, по очереди; в конце оба
    laur = [(M("F3"), 1), (M("A3"), 1), (M("C4"), 1), (M("E4"), 1.9)]   # ми гаснет до смены аккорда
    telp = [(M("E6"), 1), (M("D6"), 1), (M("B5"), 1), (M("A5"), 3)]
    for t in (T_YAV, T_YAV + 24):
        s.line("vc_sus", laur, t, "Laurelin (cellos)", vel=0.45, gain=0.42, attack=0.15, legato=1.0, pan=-0.3)
    for t in (T_YAV + 8, T_YAV + 32):
        s.line("vln_harm", telp, t + 0.5, "Telperion (harmonics)", vel=0.35, gain=0.22, attack=0.2, legato=1.0,
               pan=0.3)
    s.line("vc_sus", laur, T_YAV + 40, "Laurelin (cellos)", vel=0.45, gain=0.42, attack=0.15, legato=1.0, pan=-0.3)
    s.line("vln_harm", telp, T_YAV + 40.5, "Telperion (harmonics)", vel=0.35, gain=0.22, attack=0.2, legato=1.0,
           pan=0.3)

    # ───────────── III Nienna: плач и надежда — одно и то же ─────────────
    mk(T_NIEN, "III Nienna")
    lament = [
        # фраза 1: от ля
        ("A4", 2), ("G4", 1), ("F4", 2), ("E4", 1), ("D4", 4),
        # фраза 2: от до
        ("C5", 1.5), ("B4", 0.5), ("A4", 1.5), ("G4", 0.5), ("F4", 1.5), ("E4", 0.5), ("D4", 4),
        # фраза 3: от ми, слёзы чаще
        ("E5", 1), ("D5", 1), ("C5", 1), ("B4", 1), ("A4", 1), ("G4", 1), ("F4", 1), ("E4", 1), ("D4", 2),
        # фраза 4: вверх к кульминации (214) и обвал
        ("D5", 1), ("E5", 1), ("F5", 1), ("G5", 1), ("A5", 2),
        ("G5", 0.5), ("F5", 0.5), ("E5", 0.5), ("D5", 0.5), ("C5", 0.5), ("B4", 0.5), ("A4", 0.5), ("G4", 0.5),
        ("F4", 1), ("E4", 1),
        # сошлись: один звук
        ("D4", 5.5),
    ]
    t = T_NIEN
    for i, (a, d) in enumerate(lament):
        m = M(a)
        h = 2 * D4 - m                         # зеркальное обращение вокруг ре
        climax = T_NIEN + 30 <= t < T_NIEN + 42
        g = 0.44 + (0.12 if climax else 0.0) + 0.04 * min(1.0, (t - T_NIEN) / 30)
        last = i == len(lament) - 1
        dd = d * 0.99
        rel = 2.0 if last else 0.6
        s.n("choir", m, t, dd, "Choir I", gain=g, vel=0.55 if climax else 0.5, attack=0.12, release=rel, pan=0.25)
        s.n("choir", h, t, dd, "Choir II", gain=g * (0.95 if h != m else 0.6), vel=0.55 if climax else 0.5,
            attack=0.12, release=rel, pan=-0.25)
        if m >= 52:   # английский рожок — плач
            s.n("eh_sus", m, t, dd, "English horn", vel=0.45, gain=0.3, attack=0.06, release=rel, pan=0.35)
        if 50 <= h and h != m:   # кларнет — надежда
            s.n("cl_sus", h, t, dd, "Clarinet", vel=0.42, gain=0.26, attack=0.06, release=rel, pan=-0.35)
        if climax:
            s.n("vln_sus", m, t, dd, "Violins", vel=0.55, gain=0.6, attack=0.1, release=0.6, pan=0.3)
            s.n("vc_sus", h, t, dd, "Cellos", vel=0.5, gain=0.2, attack=0.1, release=0.6, pan=-0.3)
        t += d
    # третья часть хора: держит ре, куда сходятся голоса; бас — ре
    for t0, t1, g in ((T_NIEN, T_NIEN + 30, 0.28), (T_NIEN + 30, T_NIEN + 42, 0.38), (T_NIEN + 42, T_SIL - 0.8, 0.26)):
        s.n("choir", "D3", t0, t1 - t0, "Choir III", gain=g, vel=0.45, attack=1.0, release=1.5)
        s.n("cb_sus", "D2", t0, t1 - t0, "Basses", vel=0.45, gain=1.8 if g > 0.3 else 1.5, attack=1.0, release=1.5)
        s.n("vc_sus", "D3", t0, t1 - t0, "Cellos", vel=0.35, gain=0.08, attack=1.2, release=1.5, pan=-0.2)
    # кульминация: тяжесть слёз — валторны на ре и ля
    s.n("hns_sus", "D3", T_NIEN + 32, 8.0, "Horns", vel=0.55, gain=0.34, attack=2.0, release=1.5)
    s.n("hns_sus", "A3", T_NIEN + 32, 8.0, "Horns", vel=0.5, gain=0.28, attack=2.0, release=1.5)
    s.n("vla_sus", "A3", T_NIEN, 30, "Violas", vel=0.3, gain=0.22, attack=2.0, release=1.5)

    # ───────────── silentium magnum ─────────────
    mk(T_SIL, "silentium magnum")

    # ───────────── Litania ─────────────
    mk(T_LIT, "Litania")
    A3, G3, E3, D3 = M("A3"), M("G3"), M("E3"), M("D3")

    def flex(n):  # речитатив на ля с флексией в конце
        return [A3] * (n - 2) + [G3, A3]

    def memoramur(t):
        # «vos me-mo-ra-mur»: ля–соль–ля–ми–ре, медленно; под ре — пустая квинта струнных
        e = s.recite(t, [(A3, 0.6), (G3, 0.6), (A3, 0.6), (E3, 0.6), (D3, 2.2)], gain=0.52)
        s.n("vc_sus", "D3", t + 2.2, 3.4, "Cellos", vel=0.3, gain=0.3, attack=0.8, release=1.5)
        s.n("vla_sus", "A3", t + 2.3, 3.3, "Violas", vel=0.28, gain=0.25, attack=0.8, release=1.5)
        s.n("cb_sus", "D2", t + 2.2, 3.4, "Basses", vel=0.3, gain=0.38, attack=0.8, release=1.5)
        return e

    t = T_LIT + 0.5
    t = s.recite(t, flex(6))                                           # Telperion frater
    s.line("vln_harm", telp, t + 0.1, "Telperion (harmonics)", vel=0.3, gain=0.2, attack=0.2, legato=1.0, pan=0.3)
    t += 2.6
    t = s.recite(t, flex(5))                                           # Laurelin soror
    s.line("vc_sus", laur, t + 0.1, "Laurelin (cellos)", vel=0.4, gain=0.3, attack=0.15, legato=1.0, pan=-0.3)
    t += 2.8
    t = memoramur(t) + 1.6                                             # vos memoramur
    t = s.recite(t, flex(16))                                          # Varda domina stellarum…
    for k, m in enumerate(tones("E6", "A6", "D7")):
        s.n("crotales", m, t + 0.2 + 0.7 * k, 3.0, "Crotales", vel=0.45, gain=0.22, release=3.0, pan=0.3 - 0.25 * k)
    t += 2.2
    t = s.recite(t, flex(19))                                          # Yavanna domina rerum crescentium…
    for i, m in enumerate(tones("F2", "C3", "A3", "E4")):
        s.n("harp", m, t + 0.2 + 0.12 * i, 3.5, "Harp", vel=0.35, gain=0.16, release=2.0)
    t += 2.4
    t = s.recite(t, flex(17))                                          # Nienna soror dolentium…
    s.line("eh_sus", [(M("F4"), 1.2), (M("E4"), 1.6)], t + 0.2, "English horn", vel=0.4, gain=0.26, pan=0.35)
    s.line("cl_sus", [(M("B3"), 1.2), (M("C4"), 1.6)], t + 0.2, "Clarinet", vel=0.38, gain=0.22, pan=-0.35)
    t += 3.2
    t_lit_end = memoramur(t)                                           # vos memoramur
    assert t_lit_end < T_ILU, t_lit_end

    # ───────────── Ilúvatar ─────────────
    mk(T_ILU, "Ilúvatar")
    D4_, C4, E4, F4 = M("D4"), M("C4"), M("E4"), M("F4")
    t = T_ILU + 0.5
    t = s.recite(t, [(D4_, 0.8), (D4_, 1.4), (C4, 0.7), (D4_, 2.2)], gain=0.58, vel=0.55)       # Il-ú-va-tar
    t += 0.8
    t = s.recite(t, [(D4_, 0.5), (D4_, 0.5), (E4, 1.6)], gain=0.56, vel=0.55)                   # qui dedit
    t += 0.5
    t = s.recite(t, [(D4_, 0.5), (D4_, 0.5), (D4_, 0.5), (C4, 1.6)], gain=0.56, vel=0.55)       # qui abstulit
    t += 0.5
    t = s.recite(t, [(D4_, 0.5), (E4, 0.5), (D4_, 1.8)], gain=0.56, vel=0.55)                   # qui servat
    t += 0.9
    # «in ma-ni-bus tu-is su-mus» — каденция Финрода на кварту выше: ре–до–ре–ля–соль
    t = s.recite(t, [(D4_, 0.45), (D4_, 0.45), (F4, 0.45), (E4, 0.45), (D4_, 0.6), (C4, 0.6), (M("A3"), 0.7),
                     (M("G3"), 3.2)], gain=0.55, vel=0.52)
    t_bow = t - 3.2
    mk(t_bow, "inclinatio")
    # все склоняют головы разом: плагальный поклон G/D → пустая квинта ре (терции нет — её даст месяц)
    bow1 = [("cb_sus", "D2", "Basses"), ("vc_sus", "D3", "Cellos"), ("vla_sus", "G3", "Violas"),
            ("vln_sus", "B4", "Violins"), ("vln_sus", "D5", "Violins"), ("hns_sus", "B3", "Horns"),
            ("hns_sus", "D4", "Horns")]
    bow2 = [("cb_sus", "D2", "Basses"), ("vc_sus", "A2", "Cellos"), ("vla_sus", "D4", "Violas"),
            ("vln_sus", "A4", "Violins"), ("vln_sus", "D5", "Violins"), ("hns_sus", "A3", "Horns"),
            ("hns_sus", "D4", "Horns")]
    for inst, m, part in bow1:
        s.n(inst, m, t_bow, 4.0, part, vel=0.4, gain=0.34, attack=0.6, release=1.0)
    for m, part, pan in (("D3", "Choir III", 0.25), ("G3", "Choir III", 0.25), ("B3", "Choir II", -0.25),
                         ("D4", "Choir II", -0.25), ("G4", "Choir I", 0.0)):
        s.n("choir", m, t_bow, 4.0, part, vel=0.45, gain=0.34, attack=0.5, release=1.0, pan=pan)
    t2 = t_bow + 4.0
    for inst, m, part in bow2:
        s.n(inst, m, t2, T_STARS + 2 - t2, part, vel=0.35, gain=0.3, attack=0.5, release=2.5)
    for m, part, pan in (("D3", "Choir III", 0.25), ("A3", "Choir III", 0.25), ("D4", "Choir II", -0.25),
                         ("A4", "Choir I", 0.0)):
        s.n("choir", m, t2, T_STARS - t2, part, vel=0.42, gain=0.3, attack=0.5, release=2.5, pan=pan)
    assert t2 < T_STARS - 3, t2

    # ───────────── Caelum stellarum, luna nova ─────────────
    mk(T_STARS, "Caelum stellarum")
    s.n("cb_sus", "D2", T_STARS, T_DESC + 12 - T_STARS, "Basses", vel=0.25, gain=0.32, attack=3.0, release=3.0)
    s.n("vla_sus", "A3", T_STARS + 2, T_DESC + 12 - T_STARS - 2, "Violas", vel=0.22, gain=0.2, attack=3.0,
        release=3.0)
    stars = tones("E6", "A6", "B6", "D7", "G6", "C7", "E7", "A5", "B5")
    t = T_STARS + 1.5
    after = tones("E6", "A6", "B6", "D7", "A5", "B5", "E7")      # после месяца — без соль и до (полутон и тритон к фа-диезу)
    while t < T_DESC - 2:
        m = p.rng.choice(stars if t < T_MOON - 2.5 else after)
        inst = "crotales" if p.rng.random() < 0.55 and m >= 84 else "celesta"
        s.n(inst, m, t, 2.5, "Crotales" if inst == "crotales" else "Celesta", vel=0.4,
            gain=0.2 if inst == "crotales" else 0.16, release=2.5, pan=p.rng.uniform(-0.6, 0.6))
        t += p.rng.uniform(1.4, 3.2)
    # месяц: первый и единственный звук вне звукоряда, с востока
    mk(T_MOON, "luna nova")
    s.n("vln_harm", "F#6", T_MOON, T_END - 1 - T_MOON, "Luna (harmonic)", vel=0.25, gain=0.17, attack=4.0,
        release=3.0, pan=-0.45)
    # семя серебра и золота шевельнулось: тень Тельпериона и один звук Лаурэлин
    s.line("afl_sus", [(M("E5"), 1.5), (M("D5"), 1.5), (M("B4"), 1.5), (M("A4"), 4.0)], T_MOON + 6,
           "Alto flute", vel=0.35, gain=0.24, attack=0.2, legato=1.0, pan=0.2)
    s.n("vc_sus", "A3", T_MOON + 9, 6.0, "Laurelin (cellos)", vel=0.3, gain=0.22, attack=1.5, release=2.0, pan=-0.3)

    # ───────────── Descensus ─────────────
    mk(T_DESC, "Descensus")
    A3, B3, Fs3 = M("A3"), M("B3"), M("F#3")
    t = T_DESC + 0.5
    t = s.recite(t, [A3, A3, A3, (G3, 0.4), (A3, 1.0)], syl=0.38, gain=0.5)                    # Quae vere dolent,
    t += 0.4
    t = s.recite(t, [A3, A3, A3, A3, A3, (B3, 0.5), (A3, 0.5), (Fs3, 0.6), (D3, 1.8)], syl=0.38, gain=0.5)  # …consolantur
    t += 0.6
    t = s.recite(t, [A3] * 5 + [G3, (A3, 0.9)], syl=0.36, gain=0.46)                           # quod hodie audisti,
    t += 0.3
    t = s.recite(t, [(A3, 0.45), (A3, 0.45), (G3, 0.45), (A3, 0.45), (A3, 2.6)], gain=0.44)    # nondum totum est
    assert t < T_END, t
    # полное молчание: последнее, что звучит, — пустая квинта и месяц, они гаснут до T_END
    mk(T_END, "silentium plenum")
    p.meta["length"] = LENGTH
    p.meta["beats"] = LENGTH

    # динамика хора по разделам: один голос — тихо, Варда — p, Яванна — mp, Ниенна — до f
    shape = [(T_VOX, T_VARDA, 0.4), (T_VARDA, T_YAV, 0.48), (T_YAV, T_NIEN, 0.75), (T_NIEN, T_SIL, 0.9),
             (T_ILU, T_STARS, 0.8)]
    for e in p.notes():
        if e["part"].startswith("Choir"):
            for a, b, f in shape:
                if a <= e["t"] < b:
                    e["gain"] *= f
    # баланс — по замерам `--parts` (см. plan.md)
    p.balance(BALANCE)
    return p
