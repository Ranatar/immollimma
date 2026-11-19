#!/usr/bin/env python3
"""Devoratio — музыка к анимации devoratio.html (Разум Улья пожирает один мир; цикл 110 с).

Времена — из журнала прогона анимации (events.json → cues.json; инструменты — tools/):
  heart_beats (95 ударов сердца Улья), beacons (маяки мира), world_turns (повороты решётки мира), метки событий.

Два мира звука:
  Мир   — органная пассакалья в ре миноре: остинатный бас-ламенто D C B♭ A | G F E A половинными (1,6 с),
          такт решётки 3,2 с = такт 4/4, повороты — сильные доли. Клавесин отбивает такт мира (0,8 с) и дробит его
          по вариациям: четверти → восьмые → шестнадцатые tutti с громким органом; маяк — соборный колокол с арфой.
  Улей  — без лада: двойной удар сердца (литавры, большой барабан, контрабасы) точно по ударам анимации,
          дыхание, хоровые кластеры с расстройкой, жилы-глиссандо низких струнных, рой, споры.
Пожирание: последний аккорд мира (орган) рвётся голосами; крошки — щелчки в звуках ре-минорного аккорда.
Переваривание: Улей играет ту же пассакалью на тон выше, своими тембрами (тубы, хор, валторны), в ритме сердца.

    python3 -m kit run requests/devoratio/piece.py --sketch --parts
    python3 -m kit run requests/devoratio/piece.py --parts
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from kit.devices import Composer  # noqa: E402
from kit.events import Piece  # noqa: E402

LEN = 110.0
TICK = 0.8
SILENT = 46.4          # мир замолкает
WORLD_PAN = 0.45       # мир — справа
SEED_PAN = -0.45       # Улей рождается слева
HIVE_PC = 4            # «нижняя точка» Улья — E
# бас пассакальи мира (ламенто в ре миноре) и верхние голоса: Dm, Am/C, Gm/B♭, A, Gm, Dm/F, A7/E, A
GROUND = [(50, (62, 65, 69)), (48, (64, 69, 72)), (46, (62, 67, 70)), (45, (61, 64, 69)),
          (43, (62, 67, 70)), (41, (62, 65, 69)), (40, (61, 67, 70)), (45, (61, 64, 69))]


def lin(a, b, x):
    return max(0.0, min(1.0, (x - a) / (b - a)))


def build(ctx):
    cues = ctx.cues
    beats = cues["heart_beats"]
    beacons = cues["beacons"]
    turns = sorted(cues["world_turns"])
    ev = {}
    for c in cues["cues"]:
        ev.setdefault(c["label"], []).append(c["t"])
    order_wave = ev["order_wave"][0]
    order_turns = sorted(ev["order_turn"])
    order_release = ev["order_release"][0]
    world_dark = ev["world_dark"][0]
    landing = ev["landing"][0]
    departure = ev["departure"][0]

    p = Piece("Devoratio", bpm=75, meter=(4, 4), key="D minor", seed=23)
    p.meta["length"] = LEN
    c = Composer(p, lib="vsco", seed=23)
    rng = p.rng
    for e in cues["cues"]:
        if e["kind"] == "section":
            p.mark(e["t"], e["label"])

    # ------------------------------------------------------------------ мир: органная пассакалья
    # остинатный бас-ламенто D C B♭ A | G F E A половинными (1,6 с = 2 такта мира), гармония — на каждую половинную;
    # такт решётки 3,2 с = такт 4/4, повороты — сильные доли. Затакт 0–1,6 — доминанта A.
    def world_fade(t):                   # мир проступает 0–4.5, глохнет 40–46.4
        return lin(0.0, 4.5, t) * (1 - 0.8 * lin(40.0, SILENT, t))

    mute = lambda t: lin(40.0, SILENT, t)  # noqa: E731

    def harm(n):                         # n-я половинная от 1,6 с: (бас, верхние голоса)
        return GROUND[n % 8]

    def half_at(t):
        return int((t - 1.6) // 1.6 + 1e-6) if t >= 1.6 - 1e-6 else -1

    def var_at(t):                       # вариация: 0 — четверти, 1 — восьмые, 2 — шестнадцатые tutti, 3 — Тень
        return 3 if t >= 40.0 - 1e-6 else min(2, max(0, int((t - 1.6) // 12.8)))

    n = -1
    while True:
        t0 = 1.6 + 1.6 * n
        if t0 >= SILENT - 1e-6:
            break
        t1 = t0 + 1.6
        bass, up = harm(n)
        v = var_at(t0)
        f, mu = world_fade(t0 + 0.3), mute(t0)
        dt = lambda j: 0.3 * mu * (j - 1)  # noqa: E731
        bend = -0.7 * mu
        # педаль (бас): тихий орган + контрабасы; в третьей вариации — громкий орган октавой ниже
        p.note("org_quiet", bass, t0, 1.62, vel=0.55, gain=0.3 * f, pan=WORLD_PAN - 0.1, attack=0.05, release=0.25,
               detune=dt(0), bend=bend)
        p.note("cb_sus", bass - 12, t0, 1.55, vel=0.5, gain=(0.12 + 0.1 * (v >= 1)) * f, pan=WORLD_PAN, attack=0.08,
               release=0.3, bend=bend)
        if v == 2:
            p.note("org_loud", bass - 12, t0, 1.62, vel=0.6, gain=0.22 * f, pan=WORLD_PAN, attack=0.05, release=0.3)
        # аккорд мануала
        for j, m in enumerate(up):
            p.note("org_loud" if v == 2 else "org_quiet", m, t0, 1.62, vel=0.5, gain=(0.2 if v < 2 else 0.17) * f,
                   pan=WORLD_PAN + 0.08 * (j - 1), attack=0.05, release=0.25, detune=dt(j), bend=bend)
        if v in (1, 2):                  # струнные держат аккорд октавой выше
            for j, m in enumerate(up):
                p.note("vln_sus" if j else "vla_sus", m + 12 if j else m, t0, 1.6, vel=0.5, gain=0.1 * f,
                       pan=WORLD_PAN + 0.1 * (j - 1), attack=0.15, release=0.3)
        # клавесин — такт мира: четверти (каждые 0,8 с) всегда, дробление — по вариации
        fig = [up[0], up[1], up[2], up[0] + 12, up[2], up[1], up[0], up[1]]
        step = {0: 0.8, 1: 0.4, 2: 0.2, 3: 0.8}[v]
        k_ = 0
        while k_ * step < 1.6 - 1e-6:
            tt = round(t0 + k_ * step, 2)
            on_tick = abs(tt / TICK - round(tt / TICK)) < 1e-3
            m = (fig[k_ % 8] if v == 2 else fig[(2 * k_) % 8] if v == 1 else fig[(4 * k_) % 8 + (1 if k_ else 0)]) + 12
            m = min(m, 89)
            p.note("hpsd", m, tt, step * 0.9, vel=0.6 if on_tick else 0.45, gain=(0.3 if on_tick else 0.2) * f,
                   pan=WORLD_PAN + 0.12, release=0.25, detune=0.3 * mu * (k_ % 2 - 0.5), bend=bend)
            if on_tick and v < 3:
                p.note("vln_pizz", min(96, bass + 24), tt, 0.3, vel=0.45, gain=0.12 * f, pan=WORLD_PAN, release=0.3)
            k_ += 1
        n += 1
    # маяк: колокол собора + арфа аккордом, раз в три такта (поперёк такта 4/4 — гемиола)
    for t in beacons:
        if t >= SILENT:
            continue
        bass, up = harm(half_at(t))
        f = world_fade(t) * (1 - 0.6 * mute(t))
        p.note("tubular", 62, t, 3.0, vel=0.5, gain=0.22 * f, pan=WORLD_PAN + 0.2, release=2.5, detune=0.4 * mute(t))
        for j, m in enumerate([bass + 12] + list(up)):
            p.note("harp", m, t + 0.03 * j, 2.0, vel=0.45, gain=0.2 * f, pan=WORLD_PAN, release=1.6)
    # повороты решётки — сильная доля: во второй и третьей вариациях низкая медь подкрепляет бас
    for ts in turns:
        if 14.4 <= ts < 40.0:
            bass, up = harm(half_at(ts))
            g = 0.1 if ts < 27.2 else 0.16
            p.note("tbn_sus", bass - 12 if bass - 12 >= 40 else bass, ts, 1.5, vel=0.55, gain=g * world_fade(ts),
                   pan=WORLD_PAN - 0.15, attack=0.06, release=0.4)

    # ------------------------------------------------------------------ спора: прилёт (6–12)
    p.note("vln_harm", 98, 6.0, 6.2, vel=0.4, gain=0.16, pan=SEED_PAN - 0.25, attack=1.2, release=0.5, bend=-12.0)
    p.note("fl_sus", 86, 7.0, 4.8, vel=0.3, gain=0.1, pan=SEED_PAN - 0.2, attack=1.5, release=0.6, bend=-7.0, detune=0.3)
    c.fx("glass", 8.4, gain=0.08, pan=SEED_PAN - 0.3, shift=-5, bus="fx")
    c.fx("glass", 10.6, gain=0.07, pan=SEED_PAN, shift=-9, bus="fx")

    # ------------------------------------------------------------------ сердце Улья: точно по ударам
    for b in beats:
        t, amp, second = b["t"], b["amp"], b["second"]
        if t >= 104:
            continue
        frenzy = lin(58, 64, t) * (1 - lin(78, 82, t))
        v = (0.35 + 0.5 * amp) * (0.7 if second else 1.0)
        c.timp(t, HIVE_PC, vel=min(1.0, v * (1 + 0.25 * frenzy)))
        c.fx("bd_soft" if frenzy < .5 else "bd", t, gain=(0.18 + 0.2 * amp) * (0.6 if second else 1.0), pan=SEED_PAN * (1 - lin(30, 70, t)),
             bus="perc")
        p.note("cb_pizz", 28, t, 0.5, vel=min(1.0, v), gain=0.5 * amp * (0.7 if second else 1.0), pan=SEED_PAN * (1 - lin(30, 70, t)),
               release=0.5)
        if t >= 40 and not second:
            c.fx("logdrum", t, gain=0.12 + 0.12 * frenzy, pan=-0.2, shift=-4, bus="perc")
        if frenzy > 0.3 and not second:
            for m in (40, 41, 46):
                p.note("tbn_stac", m, t, 0.35, vel=0.85, gain=0.32 * frenzy, release=0.3)
            p.note("tba_stac", 28, t, 0.35, vel=0.85, gain=0.32 * frenzy, release=0.3)
    # посадка: рождается сердце
    c.fx("tamtam", landing, gain=0.18, pan=SEED_PAN, bus="perc")
    p.note("cbsn_sus", 28, landing, 6.0, vel=0.6, gain=0.32, pan=SEED_PAN, attack=0.05, release=2.0, bend=-1.0)
    c.breath(landing + 0.3, 8.0, gain=0.32)

    # ------------------------------------------------------------------ ткань: хор, жилы, споры, рой
    # хоровые кластеры — растут голосами 16 → 40, темнеют в Тени, поднимаются в обхвате
    def choir_block(t0, t1, notes, vel, gain, bend=0.0, detune=0.3, attack=2.5, pan=SEED_PAN):
        for j, m in enumerate(notes):
            if not 40 <= m <= 81:
                continue
            pn = pan + 0.12 * (j - len(notes) / 2)
            p.note("choir", m, t0, t1 - t0, vel=vel, gain=gain, pan=max(-1, min(1, pn)), attack=attack, release=1.5, bend=bend)
            p.note("choir", m, t0 + 0.07, t1 - t0, vel=vel * 0.9, gain=gain * 0.55, pan=max(-1, min(1, -pn * 0.6)),
                   attack=attack * 1.2, release=1.5, bend=bend, detune=detune * (1 if j % 2 else -1))
    choir_block(16.0, 24.0, [40, 41], 0.4, 0.3)
    choir_block(23.0, 31.0, [40, 41, 43], 0.45, 0.32, bend=1.0, pan=-0.35)
    choir_block(30.0, 38.0, [41, 42, 44, 45], 0.5, 0.33, bend=-1.0, pan=-0.25)
    choir_block(37.0, 44.0, [43, 44, 46, 47, 49], 0.55, 0.34, bend=-2.0, pan=-0.15)
    choir_block(43.5, 51.0, [40, 41, 42, 45, 46], 0.5, 0.32, bend=-1.0, pan=-0.1)        # Тень: ниже
    choir_block(50.0, 62.5, [44, 45, 47, 50, 51, 53], 0.6, 0.34, bend=3.0, attack=4.0, pan=0.0)   # обхват: поднимается
    choir_block(62.0, 78.0, [42, 43, 46, 49, 50, 55, 56, 61, 62, 67], 0.85, 0.3, bend=2.0, detune=0.45, attack=3.0, pan=0.05)
    # жилы: глиссандо низких струнных вверх, чаще по мере роста
    t = 19.0
    while t < 62.0:
        dens = 0.35 + 0.65 * lin(19, 50, t)
        inst = "vc_sus" if rng.random() < 0.55 else "cb_sus"
        m = rng.randint(36, 50) if inst == "vc_sus" else rng.randint(28, 40)
        d = rng.uniform(2.6, 4.6)
        p.note(inst, m, t, d, vel=0.55, gain=0.28 * dens, pan=max(-0.9, SEED_PAN + rng.uniform(-0.3, 0.5) + 0.6 * lin(20, 60, t)),
               attack=d * 0.4, release=0.8, bend=rng.uniform(3.0, 8.0), detune=rng.uniform(-0.2, 0.2))
        t += rng.uniform(1.6, 3.2) / dens
    c.spores(26.0, 14.0, density=16, gain=0.16, curve="rise")
    c.spores(50.0, 12.0, density=28, gain=0.2, curve="rise")
    # рог с сурдиной — рык роста
    for m in (40, 41, 47):
        p.note("hn_mute", m, 31.0, 9.0, vel=0.6, gain=0.18, attack=6.0, release=1.0, pan=-0.2, detune=0.2)

    # ------------------------------------------------------------------ IV Тень: мир глохнет
    c.shepard(40.0, 50.0, up=False, gain=0.2)
    c.breath(41.0, 9.0, gain=0.4)
    p.note("org_quiet", 40, 40.0, 10.5, vel=0.45, gain=0.22, attack=3.0, release=1.5, detune=0.3)
    p.note("org_quiet", 47, 41.0, 9.5, vel=0.45, gain=0.16, attack=3.0, release=1.5, detune=-0.3)

    # ------------------------------------------------------------------ V обхват → VI пожирание: последний аккорд мира
    # последний аккорд мира — ре минор органом (струнные тремоло вторят); голоса рвутся снизу вверх, орган теряет воздух
    world_voices = [("org_quiet", 50), ("org_quiet", 57), ("org_quiet", 62), ("org_quiet", 65), ("org_quiet", 69),
                    ("org_quiet", 74), ("org_quiet", 77), ("org_quiet", 81)]
    brk = [62.6 + 14.4 * j / (len(world_voices) - 1) + rng.uniform(-0.4, 0.4) for j in range(len(world_voices))]
    order_ = sorted(range(len(world_voices)), key=lambda j: world_voices[j][1])     # снизу вверх: от касания к сердцевине
    for rank, j in enumerate(order_):
        inst, m = world_voices[j]
        tb = min(77.6, brk[rank]) if rank < len(order_) - 1 else world_dark            # верхний — сердцевина: до 78
        ts_ = 50.0 + 0.3 * rank
        pn = WORLD_PAN + 0.05 * (rank - 3)
        p.note(inst, m, ts_, tb - 0.7 - ts_, vel=0.55, gain=0.2, pan=pn, attack=2.0, release=0.12)
        p.note(inst, m, tb - 0.75, 0.75, vel=0.6, gain=0.22, pan=WORLD_PAN - 0.2, attack=0.04, release=0.3,
               bend=-5.0 - rank * 0.4, detune=0.4)
        if m >= 57:
            s_ = "vla_trem" if m < 67 else "vln_trem"
            p.note(s_, m + (12 if m >= 67 else 0), ts_, tb - 0.7 - ts_, vel=0.5, gain=0.1, pan=pn, attack=2.5, release=0.12)
            p.note(s_, m + (12 if m >= 67 else 0), tb - 0.75, 0.75, vel=0.6, gain=0.11, pan=WORLD_PAN - 0.2, attack=0.04,
                   release=0.3, bend=-5.0 - rank * 0.4, detune=0.4)
    c.buzz(51.0, 11.0, notes=(74, 77, 81), gain=0.2)
    c.buzz(62.0, 16.0, notes=(73, 80, 86), gain=0.26, rates=(47.0, 59.0, 83.0))
    # крошки порядка: откол — цифровой щелчок в высотах последнего аккорда мира (справа), на каждом толчке к сердцу —
    # отголосок ниже и ближе к середине (перекликивание), на ударе прихода — глоток: звуки мира падают в регистр сердца
    crumbs = sorted(cues["crumbs"], key=lambda q: q["t"])
    rip = [86 + d for d in (0, 3, 7, 10, 14)]                  # ре минор с ноной — выклёванные звуки хорала
    main_beats = [b["t"] for b in beats if not b["second"]]
    arrivals = {}
    for i, q in enumerate(crumbs):
        m = rip[i % 5]
        inst = "crotales" if i % 7 == 3 else ("xylo" if i % 2 == 0 else "vln_colleg")
        mm = m if inst != "vln_colleg" else min(96, m - 12)
        if inst == "crotales":
            mm = max(84, min(108, m + 12))
        p.note(inst, mm, q["t"], 0.08, vel=0.5, gain=0.12 if inst != "crotales" else 0.06, pan=max(-1, min(1, q["pan"])), release=0.25)
        surges = [b_ for b_ in main_beats if q["t"] < b_ <= q["arrive"]]
        for j, b_ in enumerate(surges[:-1]):                 # отголоски на толчках
            f = (j + 1) / len(surges)
            te = b_ - 0.35 + 0.33 * ((i * 0.618) % 1)
            p.note("xylo" if j % 2 else "vln_colleg", max(55, mm - round(12 * f)) if inst != "crotales" else m - 12, te, 0.07, vel=0.4,
                   gain=0.08 * (1 - 0.4 * f), pan=max(-1, min(1, q["pan"] * (1 - f) + SEED_PAN * f)), release=0.2)
        arrivals.setdefault(q["arrive"], []).append(m)
    for tb, ms in sorted(arrivals.items()):                  # глоток на ударе прихода
        n = len(ms)
        for j, m in enumerate(sorted(set(ms))[:5]):
            p.note("marimba", m - 36, tb + 0.025 * j, 0.6, vel=0.6, gain=0.045 * n ** 0.5, pan=SEED_PAN * 0.6, release=0.6)
        p.note("vc_pizz", 40, tb, 0.4, vel=0.65, gain=0.07 * n ** 0.5, pan=SEED_PAN * 0.6, release=0.4)
        c.fx("bubbles", tb, gain=0.03 * n ** 0.5, pan=SEED_PAN * 0.5, shift=-14, bus="fx")
    c.shepard(64.0, 78.0, up=True, gain=0.16)
    for m, inst in ((28, "cb_trem"), (31, "cb_trem"), (40, "vc_trem"), (41, "vc_trem"), (47, "vc_trem")):
        p.note(inst, m, 62.0, 16.0, vel=0.75, gain=0.26, attack=10.0, release=0.2, detune=0.3, pan=rng.uniform(-0.5, 0.3))
    p.note("cbsn_sus", 26, 62.0, 16.0, vel=0.7, gain=0.3, attack=8.0, release=0.2)
    p.note("tba_sus", 28, 64.0, 14.0, vel=0.7, gain=0.28, attack=8.0, release=0.2, detune=0.3)
    # 78 — гаснет сердцевина мира
    c.fx("gong_hit", world_dark, gain=0.3, bus="perc")
    c.timp(world_dark, HIVE_PC, vel=1.0)
    c.fx("tamtam", world_dark, gain=0.3, bus="perc")
    p.note("cbsn_sus", 26, world_dark, 4.5, vel=0.7, gain=0.32, release=2.0)

    # ------------------------------------------------------------------ VII переваривание: Улей играет пассакалью мира
    # тот же бас-ламенто, но на тон выше (в ми — своя точка Улья) и своими тембрами; ноты баса — на двойные удары сердца
    # (основной + второй), аккорд держится до следующего основного удара: порядок идёт в ритме сердца, не мира.
    for m in (28, 35):
        p.note("org_quiet", m + 12, 79.0, order_wave - 79.0 + 0.6, vel=0.45, gain=0.2, attack=1.0, release=0.6)
    pulses = [order_wave] + order_turns                   # 81.4 (волна), 82.9, 84.6, 86.5
    seconds = {b["t"] for b in beats if b["second"]}
    for i, t0 in enumerate(pulses):
        t1 = pulses[i + 1] if i + 1 < len(pulses) else order_release
        t2 = min((s for s in seconds if t0 < s < t1), default=t0 + 0.3)
        wave = i == 0
        for half, (ta, tb_) in enumerate(((t0, t2), (t2, t1))):
            bass, up = GROUND[2 * i + half]
            bass, up = bass + 2, [u + 2 for u in up]
            dur = tb_ - ta + 0.35
            g = 0.6 if wave else 1.0
            # бас Улья: тубы, контрафагот, контрабасы, тромбоны — с лёгкой расстройкой
            p.note("tba_sus", bass - 12 if bass - 12 >= 28 else bass, ta, dur, vel=0.85, gain=0.32 * g, attack=0.06, release=0.4,
                   detune=0.15)
            p.note("cb_sus", bass - 12, ta, dur, vel=0.8, gain=0.3 * g, attack=0.06, release=0.4, detune=-0.15)
            p.note("cbsn_sus", bass - 12 if bass - 12 >= 26 else bass, ta, dur, vel=0.7, gain=0.18 * g, attack=0.06, release=0.4)
            p.note("tbn_sus", bass, ta, dur, vel=0.85, gain=0.28 * g, attack=0.05, release=0.4, pan=-0.15)
            # верхние голоса: хор и валторны вместо мануала органа
            for j, m in enumerate(up):
                mm = m if 40 <= m <= 81 else m - 12
                p.note("choir", mm - 12 if mm - 12 >= 48 else mm, ta, dur, vel=0.8, gain=0.3 * g, attack=0.12 if not wave else 0.8,
                       release=0.5, pan=-0.3 + 0.3 * j, detune=0.25 * (j - 1))
                p.note("hn_sus", mm - 12 if mm - 12 >= 50 else mm, ta, dur, vel=0.75, gain=0.22 * g, attack=0.08, release=0.4,
                       pan=0.2 - 0.15 * j)
            p.note("vc_sus", up[0] - 12, ta, dur, vel=0.75, gain=0.22 * g, attack=0.08, release=0.4)
        c.timp(t0, (GROUND[2 * i][0] + 2) % 12, vel=0.75 if wave else 0.95)
        if not wave:
            c.fx("tamtam", t0, gain=0.2, bus="perc")
        # «клавесин» мира в Улье: его фигура восьмыми — пиццикато басов и фаготами
        tt = t0 + 0.2
        j = 0
        while tt < t1 - 0.05:
            bass, up = GROUND[2 * i + (1 if tt >= t2 else 0)]
            fig = [up[0], up[1], up[2], up[1]]
            m = fig[j % 4] + 2 - 24
            p.note("vc_pizz" if m >= 36 else "cb_pizz", m if m >= 28 else m + 12, tt, 0.2, vel=0.6, gain=0.26 * (0.5 if wave else 1),
                   pan=-0.2 + 0.1 * (j % 4), release=0.2)
            if j % 2 == 0:
                p.note("bsn_stac", m + 12, tt, 0.18, vel=0.55, gain=0.06, pan=0.2, release=0.2)
            tt = round(tt + 0.2, 2)
            j += 1
    # отпуск: тоника Улья (ми минор) оплывает вниз, каждый голос — своим ходом
    for j, (inst, m) in enumerate([("choir", 52), ("choir", 59), ("choir", 64), ("tbn_sus", 40),
                                   ("hn_sus", 55), ("vc_sus", 40), ("cb_sus", 28), ("tba_sus", 28)]):
        p.note(inst, m, order_release, 2.6, vel=0.6, gain=0.24, attack=0.15, release=1.2, bend=-(2.0 + 1.3 * j), detune=0.35)
    c.timp(order_release, HIVE_PC, vel=0.9)
    c.spores(order_release, 4.0, density=22, gain=0.18)

    # ------------------------------------------------------------------ VIII исход
    choir_block(91.0, 101.0, [40, 41, 44], 0.4, 0.26, bend=-3.0, attack=3.0, pan=-0.2)
    for i in range(6):
        t = 92.0 + 1.6 * i
        m = rng.randint(30, 46)
        p.note("vc_sus" if m >= 36 else "cb_sus", m, t, 3.4, vel=0.5, gain=0.24 * (1 - i / 7), pan=rng.uniform(-0.4, 0.4),
               attack=1.2, release=0.8, bend=-rng.uniform(3, 7))
    c.breath(93.0, 9.0, gain=0.34)
    c.spores(92.0, 9.0, density=14, gain=0.14)
    # уход споры: обратный прилёт — вверх и вправо
    p.note("org_quiet", 40, 96.0, 9.0, vel=0.4, gain=0.32, attack=2.5, release=2.0, detune=0.25)      # мост к уходу
    p.note("vln_harm", 86, departure, 5.0, vel=0.5, gain=0.5, pan=0.6, attack=0.15, release=0.4, bend=12.0)
    p.note("fl_sus", 79, departure + 0.6, 4.0, vel=0.35, gain=0.2, pan=0.7, attack=0.8, release=0.4, bend=9.0, detune=0.3)

    # ------------------------------------------------------------------ IX тишина: призрак аккорда мира
    for j, m in enumerate((74, 77, 81)):
        p.note("vln_harm", m, 104.4 + 0.3 * j, 3.6, vel=0.35, gain=0.15, pan=WORLD_PAN, attack=1.6, release=0.9)
    p.note("org_quiet", 62, 104.6, 3.4, vel=0.3, gain=0.12, pan=WORLD_PAN, attack=1.8, release=1.0)

    # баланс по замеру --parts (эскиз 0–60 с): сердце (литавры, контрабасы) и такт мира — вровень с хором
    p.balance({"Contrabassoon": -9, "Cellos": -2.5, "Violas": +8, "Marimba": +8, "Vibraphone": +12, "Harp": +1,
               "Flute": +2, "Basses": +10, "Timpani": +15, "Tuba": +10, "Organ": +7, "Trombone": +14, "Choir": -3,
               "Xylophone": +22, "Crotales": +20,
               "Harpsichord": +15, "Tubular bells": +20})
    return p
