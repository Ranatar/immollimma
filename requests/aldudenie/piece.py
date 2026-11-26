#!/usr/bin/env python3
"""Aldudénië — плач о Двух Древах (музыка к aldudenie.html, цикл 104 с).

Материал:
  * Напев Aldu — речитация на до-диезе со свободным, «слоговым» ритмом и мелизматическим спуском на конце строки
    (принцип Namárië Суонна — Толкина, без цитаты). Ритм — из ударений квэнья: tel-PE-ri-on ar LAU-re-lin (a, кончается
    на си — открыто) / al-du-DÉ-ni-ë (b, подъём к фа-диезу и спуск к ля).
  * Три лада одного ля: серебро Тельпериона — лидийский (ре-диез), золото Лаурелин — миксолидийский (соль),
    смешение — ионийский. Лад арфы в первой ступени идёт по кривой света Древ из журнала страницы.
  * Аккорд Сильмарилей A–E–B (три камня — три звука, квинты без терции): общий всем ладам. Собирается по звуку в
    30/33/36 с и держится, не меняясь, до конца — единственный «смешанный свет» после гибели Древ.
  * Не-Свет — квинты си-бемоля (B♭–F–C), на полутон от аккорда камней; паутина — пиццикато-нити, ползущие
    по полутонам из трёх «начал» (52,6 / 53,1 / 53,6 — как нити на странице).
  * Плач — скрипка соло, напев в пентатонике фа-диез минора (F♯ A B C♯ E: без единого полутона к аккорду камней).
  * Исиль и Анар — фраза a флажолетами (серебро), фраза b валторной в миксолидийском (золото); не звучат вместе.

    python3 -m kit run requests/aldudenie/piece.py --sketch --parts
    python3 -m kit run requests/aldudenie/piece.py --parts
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from kit.events import Piece  # noqa: E402

LEN = 104.0
BPM = 72
B = 60.0 / BPM                       # доля = 0,8333 с; час Древ в первой ступени = 2 доли

# ---------------------------------------------------------------- напев (звучащие MIDI, доли)
A_ION = [(73, .5), (76, 1.5), (74, .5), (73, .5), (71, 1), (73, 1.5), (74, .5), (71, 2)]      # Telperion ar Laurelin
A_LYD = [(m + 1 if m == 74 else m, d) for m, d in A_ION]                                       # серебро: ре-диез
B_ION = [(69, .5), (71, .5), (78, 2), (76, .5), (74, .5), (73, .5), (71, .5), (69, 2.5), (None, .5)]  # Aldudénië
B_GOLD = [(57, .5), (59, .5), (66, 2), (64, .5), (62, .5), (59, .5), (55, .5), (57, 2.5)]       # золото: соль
LAM_A = [(69, .5), (73, 1.5), (71, .5), (69, .5), (66, 1), (69, 1.5), (71, .5), (64, 2)]       # плач: пентатоника F♯m
LAM_B = [(66, .5), (69, .5), (76, 2), (73, .5), (71, .5), (69, .5), (64, .5), (66, 2.5)]
SILM = [81, 88, 95]                  # A5 E6 B6 — аккорд камней (флажолеты)
SILM_CROT = [93, 100, 107]           # A6 E7 B7


def build(ctx):
    p = Piece("Aldudénië", bpm=BPM, meter=(4, 4), key="A major", seed=1126)
    rng = p.rng
    cues = json.load(open(os.path.join(HERE, "cues.json")))
    hours = cues["hours"]
    curve = cues["light_curve"]

    def light(t):
        c = min(curve, key=lambda c: abs(c["t"] - t))
        return c["iT"], c["iL"]

    def n(inst, m, t, dur, **kw):
        return p.note(inst, m, t, dur, **kw)

    def line(inst, seq, t, scale=1.0, legato=0.97, **kw):
        """напев: [(midi|None, доли)], scale — растяжение (рубато плача)"""
        for m, d in seq:
            s = d * B * scale
            if m is not None:
                n(inst, m, t, s * legato, **kw)
            t += s
        return t

    def harp_slot(t, notes, gain, step=None, ring=1.4, span=None):
        """span — длина слота: звенящий хвост не заходит в следующий аккорд (грабля «хвосты арфы»)"""
        step = step or B / 2
        for k, m in enumerate(notes):
            r = ring if span is None else max(0.25, min(ring, span - k * step))
            n("harp", m, t + k * step, r, vel=0.42, gain=gain * (1.0 if k == 0 else 0.8), pan=-0.3,
              release=0.5 if span is None else 0.2)

    for c in cues["cues"]:
        if c["kind"] == "section":
            p.mark(c["t"], c["label"])
    p.meta["length"] = LEN
    p.meta["reverb_seconds"] = 4.6
    p.meta["sends"] = {"choir": 0.6, "strings": 0.5, "harp": 0.55, "winds": 0.45, "brass": 0.4}

    # ============================================================ I  Telperion ar Laurelin (0–20)
    # «гитара» Суонна → арфа: бас, квинта, краска лада, квинта — по 4 восьмых на час Древ (2 доли)
    T_A = 2 * B * 2                  # напев вступает на 3,33 с (второй час)
    slots_I = [  # (время, звуки) — под полутакты напева; лад — по свету
        (0.0, [45, 52, 59, 63]), (2 * B, [45, 52, 59, 63]),                         # серебро (лидийский)
        (T_A, [45, 52, 59, 61]), (T_A + 2 * B, [45, 52, 59, 63]),                   # a: C♯ E | D♯ C♯ B
        (T_A + 4 * B, [45, 52, 59, 64]), (T_A + 6 * B, [45, 52, 59, 66]),           #    C♯ D♯ | B
        (T_A + 8 * B, [45, 52, 54, 61]), (T_A + 10 * B, [45, 50, 54, 57]),          # b: F♯m | D
        (T_A + 12 * B, [45, 52, 59, 64]), (T_A + 14 * B, [45, 52, 55, 59]),         #    Asus2 | A7sus (золото)
        (T_A + 16 * B, [45, 52, 55, 62]), (T_A + 18 * B, [45, 52, 59, 64]),         # золото, полночь
    ]
    for k, (t, notes) in enumerate(slots_I):
        harp_slot(t + 0.02, notes, gain=0.34 * min(1.0, 0.35 + t / 2.2), span=2 * B)
    n("vc_sus", 45, 1.2, 18.6, vel=0.4, gain=1.2, attack=2.5, release=1.2, pan=-0.15)
    n("cb_sus", 33, 2.0, 17.8, vel=0.38, gain=1.05, attack=2.5, release=1.2, pan=-0.3)
    p.mark(T_A, "напев (альтовая флейта)")
    line("afl_sus", A_LYD, T_A, vel=0.45, gain=0.5, pan=0.1, attack=0.08, release=0.5)
    line("afl_sus", B_ION, T_A + 8 * B, vel=0.48, gain=0.52, pan=0.1, attack=0.08, release=0.8)

    # часы Древ: серебряный — челеста высоко, золотой — арфа низко; полночь (четверная пуста) — кроталы
    for h in hours:
        t, hr = h["t"], h["h"]
        if t > 39.5:
            continue
        iT, iL = light(t + 0.01)
        if hr == 0:
            n("crotales", 93, t, 2.5, vel=0.35, gain=0.16, pan=0.2)
        elif iT >= iL:
            m = [95, 90][hr % 2] if t < 30 else [88, 95][hr % 2]   # си / фа-диез; после камней — ми / си
            n("celesta", m, t, 1.6, vel=0.4, gain=0.22 * (0.5 + iT), pan=0.35)
        else:
            n("harp", [57, 52][hr % 2], t, 2.0, vel=0.45, gain=0.3 * (0.5 + iL), pan=-0.1)

    # ============================================================ II  silima (20–40)
    # струнный фон крепнет; до 30 с — лидийский, потом — ионийский (камни: без ре-диеза)
    pads_II = [(20.0, 25.0, [45, 52, 59, 63, 66]), (25.0, 30.0, [45, 52, 61, 63, 68]),
               (30.0, 35.0, [45, 52, 59, 64, 69]), (35.0, 40.2, [45, 52, 57, 64, 71])]
    for k, (a, b, ch) in enumerate(pads_II):
        g = 0.48 + 0.12 * k
        for m, inst in zip(ch, ["cb_sus", "vc_sus", "vla_sus", "vla_sus", "vln_sus"]):
            mm = m - 12 if inst == "cb_sus" else m
            n(inst, mm, a, b - a + 0.4, vel=0.34 + 0.05 * k, gain=g, attack=1.0, release=1.0,
              pan={"cb_sus": -0.3, "vc_sus": -0.15, "vla_sus": 0.1, "vln_sus": 0.3}[inst])
    # потоки света: бегущие фигуры к трём звукам камней; гуще к каждому зажжению
    scale_lyd = [57, 59, 61, 63, 64, 66, 68]
    scale_ion = [57, 59, 61, 62, 64, 66, 68]

    def scale_notes(sc, lo, hi):
        out = []
        for o in range(0, 60, 12):
            out += [m + o for m in sc]
        return [m for m in out if lo <= m <= hi]

    targets = [(30.0, SILM[0]), (33.0, SILM[1]), (36.0, SILM[2])]
    t = 22.0
    while t < 37.6:
        nxt = [tt for tt, _ in targets if tt > t + 0.4]
        if not nxt:
            break
        tt = nxt[0]
        tgt = dict(targets)[tt]
        sc = scale_notes(scale_lyd if t < 29.5 else scale_ion, 60, 100)
        k = min(range(len(sc)), key=lambda i: abs(sc[i] - tgt))
        ln = rng.randint(5, 8)
        frm = max(0, k - ln) if rng.random() < 0.6 else min(len(sc) - 1, k + ln)
        seq = sc[frm:k + 1] if frm <= k else sc[k:frm + 1][::-1]
        step = 0.13 if t < 27 else 0.105
        inst = "celesta" if rng.random() < 0.55 else "harp"
        for i, m in enumerate(seq):
            n(inst, m, t + i * step, 0.5, vel=0.4, gain=0.30 + 0.16 * (t - 22) / 16, pan=rng.uniform(-0.5, 0.5),
              release=0.35)
        gap = max(0.35, 1.5 - (t - 22) * 0.08)
        t += len(seq) * step + gap
    # зажжения: кроталы + колокольчики + арфа, и звук камня встаёт флажолетом
    for i, (tt, m) in enumerate(targets):
        p.mark(tt, f"Сильмариль {i + 1}")
        n("crotales", SILM_CROT[i], tt, 4.0, vel=0.6, gain=0.24, pan=(-0.3, 0.3, 0.0)[i])
        n("glock", SILM_CROT[i] - 12, tt, 2.0, vel=0.45, gain=0.14, pan=(-0.3, 0.3, 0.0)[i])
        n("celesta", m, tt, 2.0, vel=0.5, gain=0.22, pan=(-0.3, 0.3, 0.0)[i])
        harp_slot(tt, [45, 52, 59, 64, 69, 71, 76][: 4 + i], gain=0.34, step=0.06, ring=2.5)
    # 37,5 «Silmarilli»: хор вступает — светлое «а» на аккорде камней
    for m, g in [(57, 0.26), (64, 0.24), (69, 0.26), (71, 0.22)]:
        n("choir", m, 37.5, 2.9, vel=0.35, gain=g, attack=1.4, release=0.6)

    # аккорд камней — флажолеты, держатся (каждые ~8 с обновляются внахлёст), до 89 с
    def silm_hold(t0, t1, gain, idx=(0, 1, 2), seg=8.0):
        t = t0
        while t < t1 - 0.5:
            d = min(seg, t1 - t)
            for i in idx:
                n("vln_harm", SILM[i], t, d + 1.2, vel=0.35, gain=gain, attack=1.2, release=1.4,
                  pan=(-0.25, 0.25, 0.05)[i], part="Violin harmonics")
            t += seg
    silm_hold(30.0, 33.0, 0.10, idx=(0,))
    silm_hold(33.0, 36.0, 0.10, idx=(0, 1))
    silm_hold(36.0, 52.0, 0.10)

    # ============================================================ III  Valinórë (40–52)
    T3 = 40.0
    p.mark(T3, "напев (хор)")
    line("choir", A_ION, T3, vel=0.62, gain=0.62, attack=0.12, release=0.4)
    t_b = T3 + 8 * B                                           # = 46,67: вместе со словом telpë
    endb = t_b
    for m, d in B_ION:                                          # последний звук обрывает Не-Свет в 52,0
        s = d * B
        if m is not None:
            dd = min(s * 0.97, 52.0 - endb)
            n("choir", m, endb, dd, vel=0.62, gain=0.62, attack=0.12, release=0.25)
        endb += s
    hb = [  # (начало в долях от T3, звуки хора под напевом, бас)
        (0, [45, 52, 61], 33), (2, [47, 52, 54], 33), (4, [45, 52, 59], 33), (6, [45, 52, 59], 33),
        (8, [42, 49, 57], 30), (10, [50, 54, 66], 38), (12, [52, 57, 59], 33), (14, [45, 52, 61], 33),
    ]
    for k, (bt, ch, bass) in enumerate(hb):
        a = T3 + bt * B
        d = min(2 * B, 52.0 - a)
        for m in ch:
            n("choir", m, a, d, vel=0.5, gain=0.40, attack=0.25, release=0.3)
        for m, inst in zip(ch, ["vc_sus", "vla_sus", "vln_sus"]):
            if inst == "vln_sus" and m < 55:
                m += 12
            n(inst, m, a, d, vel=0.55, gain=0.22, attack=0.3, release=0.3)
        n("cb_sus", bass, a, d, vel=0.55, gain=0.40, attack=0.2, release=0.3, pan=-0.3)
        n("hn_sus", ch[0] + 12 if ch[0] < 50 else ch[0], a, d, vel=0.5, gain=0.20, attack=0.3, release=0.3, pan=-0.2)
        harp_slot(a, [bass + 12, ch[0], ch[1], ch[2], ch[2] + 7][:5], gain=0.28, step=B / 3, ring=1.2, span=d)
    # malta (41): золотой зов валторны — восходящие квинта и кварта
    p.mark(41.0, "malta — зов валторны")
    line("hn_sus", [(57, 1), (64, 1), (69, 2.5)], 41.0, vel=0.62, gain=0.42, pan=-0.25, release=0.5)
    # telpë (46,6): серебряный ливень челесты по F♯m и D
    for i, m in enumerate([97, 93, 90, 85, 81]):
        n("celesta", m, 46.67 + i * 0.16, 1.4, vel=0.45, gain=0.22, pan=0.4)
    for i, m in enumerate([98, 93, 90, 86]):
        n("celesta", m, 48.33 + i * 0.16, 1.4 - 0.16 * i, vel=0.42, gain=0.2, pan=0.4)

    # ============================================================ IV  Ungoliantë (52–72)
    p.mark(52.0, "Не-Свет")
    # последний звук напева тонет: хор тянет ля вниз
    n("choir", 69, 52.0, 3.4, vel=0.5, gain=0.40, bend=-2.0, attack=0.0, release=1.2)
    n("choir", 57, 52.0, 3.0, vel=0.45, gain=0.30, bend=-1.0, attack=0.0, release=1.2)
    # свет Древ мерцает и гаснет к 62: тремоло высоких скрипок, ступенями
    t = 52.0
    while t < 61.6:
        f = max(0.0, 1 - (t - 52) / 10) * (0.7 + 0.3 * rng.random())
        for m in (81, 85, 88):
            n("vln_trem", m, t, 1.0, vel=0.3, gain=0.10 * f, attack=0.15, release=0.3, pan=0.3)
        t += 0.9
    # Не-Свет: квинты си-бемоля, низко, нарастают по входам
    for a, m, inst, g in [(52.2, 34, "cbsn_sus", 0.30), (53.4, 41, "cb_sus", 0.30), (55.0, 46, "bcl_sus", 0.24),
                          (56.6, 53, "bcl_sus", 0.0)]:
        if g > 0:
            n(inst, m, a, 61.8 - a, vel=0.45, gain=g, attack=2.0, release=0.4, pan=-0.2)
    for m in (46, 53, 60):                                   # Úcala Ungolianteva: мужские голоса хора
        n("choir", m, 54.0, 7.8, vel=0.35, gain=0.28, attack=2.2, release=0.4)
    # паутина: три нити пиццикато из трёх начал, ползут по полутонам, учащаясь
    for k, (t0, inst, m0) in enumerate([(52.6, "vc_pizz", 46), (53.1, "vla_pizz", 53), (53.6, "cb_pizz", 39)]):
        t, m = t0, m0
        lo, hi = {"vc_pizz": (40, 62), "vla_pizz": (48, 70), "cb_pizz": (31, 50)}[inst]
        while t < 61.7:
            n(inst, m, t, 0.3, vel=0.45 + 0.2 * (t - 52) / 10, gain=0.24 + 0.14 * (t - 52) / 10, pan=(-0.4, 0.4, 0.0)[k])
            m = min(hi, max(lo, m + rng.choice([-1, 1, 1, -2, 2, 1])))
            t += max(0.11, 0.55 - (t - t0) * 0.05) * rng.uniform(0.85, 1.15)
    # «Ungoliantë yúla i Aldu»: голова напева стянута вниз (бас-кларнет), каждый раз ниже и уже
    line("bcl_sus", [(61, .5), (63, 1.0), (62, 1.0)], 55.3, vel=0.4, gain=0.30, bend=-0.5)
    line("bcl_sus", [(57, .5), (59, 1.0), (58, 1.5)], 58.4, vel=0.42, gain=0.32, bend=-0.7)
    # 62: Древа мертвы — почти тишина; один низкий гул и ночь (lómë)
    p.mark(62.0, "Древа мертвы")
    n("cbsn_sus", 34, 62.0, 4.5, vel=0.3, gain=0.16, attack=0.3, release=2.0)
    n("harp", 34, 62.4, 3.0, vel=0.4, gain=0.25)
    n("cb_pizz", 34, 62.4, 0.5, vel=0.4, gain=0.22)
    # 65: Сильмарилли не даются — вспышка аккорда камней
    p.mark(65.0, "Сильмарилли не даются")
    for i in range(3):
        n("crotales", SILM_CROT[i], 65.0 + 0.03 * i, 4.5, vel=0.7, gain=0.26, pan=(-0.3, 0.3, 0.0)[i])
        n("glock", SILM_CROT[i] - 12, 65.0 + 0.03 * i, 2.5, vel=0.55, gain=0.14)
        n("celesta", SILM[i], 65.0 + 0.03 * i, 2.5, vel=0.55, gain=0.22)
    harp_slot(65.0, [45, 52, 57, 59, 64, 69, 71, 76], gain=0.36, step=0.05, ring=3.0)
    for i in range(3):
        n("vln_harm", SILM[i], 65.0, 4.2, vel=0.6, gain=0.18, attack=0.05, release=1.6, part="Violin harmonics")
    for m, g in [(57, 0.26), (64, 0.24), (69, 0.26), (71, 0.22)]:   # «Silmarilli uir túrimë mornienen»
        n("choir", m, 66.0, 5.2, vel=0.4, gain=g, attack=1.0, release=1.2)
    silm_hold(69.0, 89.5, 0.045)

    # ============================================================ V  nainië (72–90)
    p.mark(72.0, "плач (скрипка соло)")
    for a, d in [(70.5, 9.0), (79.0, 11.0)]:
        n("cb_sus", 30, a, d, vel=0.38, gain=1.2, attack=2.0, release=1.5, pan=-0.3)
        n("vc_sus", 42, a, d, vel=0.38, gain=1.05, attack=2.0, release=1.5, pan=-0.15)
        n("vc_sus", 49, a + 0.5, d - 0.5, vel=0.3, gain=0.45, attack=2.0, release=1.5, pan=0.1)
    SC = 1.3
    t = line("vln_solo", LAM_A, 72.6, scale=SC, vel=0.5, gain=0.42, pan=0.15, attack=0.15, release=0.6)
    line("vln_solo", LAM_B, t, scale=SC, vel=0.52, gain=0.44, pan=0.15, attack=0.15, release=1.0)
    # звуки уходят из букв: источник звенит, звук дугой поднимается к другой букве (anna — уходит в никуда)
    PENT = [66, 69, 71, 73, 76, 78, 81, 83, 85, 88]
    for t0, src, dst in [(74.0, 78, 85), (79.0, 81, 88), (84.0, 83, None)]:
        n("celesta", src, t0, 2.2, vel=0.4, gain=0.2, pan=-0.35)
        top = dst or 95
        path = [m for m in PENT + [90, 93, 95] if src < m <= top]
        k = len(path)
        for i, m in enumerate(path):
            ti = t0 + 1.6 + 3.2 * (i / max(1, k))
            g = 0.2 if dst else 0.2 * (1 - i / k)
            n("harp", m, ti, 1.2, vel=0.35, gain=g, pan=-0.35 + 0.7 * i / max(1, k))
        if dst:
            n("celesta", dst, t0 + 4.8, 2.0, vel=0.45, gain=0.22, pan=0.35)
            n("harp", dst - 12, t0 + 4.8, 2.0, vel=0.4, gain=0.18, pan=0.35)
        p.mark(t0, "звук уходит" if dst else "anna — без звука")
    for m in (54, 57, 61, 64):                                       # vanwa: хор едва слышно
        n("choir", m, 85.2, 4.3, vel=0.3, gain=0.22, attack=1.6, release=1.2)

    # ============================================================ VI  Isil ar Anar (90–104)
    # камни теперь мерцают: кроталы и челеста тихо, поочерёдно (смешанный свет — только здесь)
    for k, t in enumerate([89.4, 92.0, 94.6, 97.2, 99.8, 102.2]):
        i = k % 3
        n("celesta", SILM[i], t, 2.4, vel=0.38, gain=0.3, pan=(-0.3, 0.3, 0.0)[i])
        if k % 2 == 0:
            n("crotales", SILM_CROT[i], t + 0.05, 3.0, vel=0.35, gain=0.10, pan=(-0.3, 0.3, 0.0)[i])
    # Исиль: фраза a флажолетами, высоко, над серебряной арфой (без золота)
    p.mark(90.8, "Isil — флажолеты")
    line("vln_harm", [(m + 12, d) for m, d in A_ION], 90.8, vel=0.5, gain=0.30, attack=0.1, release=0.5,
         part="Violin harmonics", pan=0.25)
    for k in range(4):
        a = 90.8 + k * 2 * B
        harp_slot(a, [[57, 64, 71, 73], [57, 64, 69, 76], [57, 64, 71, 76], [57, 64, 69, 71]][k], gain=0.22, step=B / 2, span=2 * B)
    n("cb_sus", 33, 90.0, 7.2, vel=0.34, gain=0.6, attack=1.5, release=0.6)
    # Анар: фраза b валторной, в миксолидийском, низко-тепло; под ней арфа с солью
    p.mark(97.4, "Anar — валторна")
    t = line("hn_sus", B_GOLD[:-1], 97.4, vel=0.55, gain=0.42, pan=-0.2, attack=0.1, release=0.6)
    n("hn_sus", 57, t, 102.9 - t, vel=0.5, gain=0.40, pan=-0.2, release=0.6)
    for k, notes in enumerate([[45, 52, 57, 61], [45, 50, 54, 57], [43, 50, 55, 59]]):   # A | D | G (♭VII) → A
        harp_slot(97.4 + k * 2 * B, notes, gain=0.24, span=2 * B if k < 2 else 101.5 - (97.4 + 4 * B))
    n("vc_sus", 45, 97.4, 5.5, vel=0.36, gain=0.7, attack=1.2, release=0.8)
    # титул: хор на аккорде камней, арфа последний раз
    p.mark(100.8, "Aldudénië")
    T_END = 97.4 + 5 * B                                     # = 101,57: валторна приходит на ля (♭VII → I)
    for m, g in [(57, 0.22), (64, 0.2), (71, 0.18)]:
        n("choir", m, T_END, 1.6, vel=0.3, gain=g, attack=0.8, release=0.6)
    harp_slot(T_END, [45, 52, 59, 64, 69, 71], gain=0.22, step=0.12, ring=1.6)
    n("crotales", 93, T_END, 1.6, vel=0.35, gain=0.12)

    p.balance({"Celesta": +9, "Crotales": +7, "Violin harmonics": +12, "Glockenspiel": +6, "Violins": +3, "Violin solo": +9, "Bass clarinet": +3})
    return p
