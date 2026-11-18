#!/usr/bin/env python3
"""Devoratio — музыка к анимации devoratio.html (Разум Улья пожирает один мир; цикл 110 с).

Времена — из журнала прогона анимации (events.json → cues.json; инструменты — tools/):
  heart_beats (95 ударов сердца Улья), beacons (маяки мира), world_turns (повороты решётки мира), метки событий.

Два мира звука:
  Мир   — ровный такт 0,8 с (пиццикато + маримба рябью от центра), маяк каждые 2,4 с (вибрафон + арфа),
          флажолетовый аккорд maj7♯11; аккорд поворачивается целотоновым кругом на каждом повороте решётки.
  Улей  — без лада: двойной удар сердца (литавры, большой барабан, контрабасы) точно по ударам анимации,
          дыхание, хоровые кластеры с расстройкой, жилы-глиссандо низких струнных, рой, споры.
Кульминация переваривания: Улей играет круг мира своими тембрами и поворачивает его ударами сердца.

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

    p = Piece("Devoratio", bpm=75, meter=(4, 4), key="C major", seed=23)
    p.meta["length"] = LEN
    c = Composer(p, lib="vsco", seed=23)
    rng = p.rng
    for e in cues["cues"]:
        if e["kind"] == "section":
            p.mark(e["t"], e["label"])

    # ------------------------------------------------------------------ мир: целотоновый круг
    def turn_index(t):
        return sum(1 for ts in turns if ts <= min(t, SILENT) + 1e-6)

    def root(idx):                       # C → D → E → F♯ → G♯ → A♯ → C …
        return (2 * idx) % 12

    def world_fade(t):                   # мир проступает 0.8–4.5, глохнет 40–46.4
        return lin(0.0, 4.5, t) * (1 - 0.8 * lin(40.0, SILENT, t))

    mute = lambda t: lin(40.0, SILENT, t)  # noqa: E731

    def ripple(r):                       # 5 ступеней аккорда снизу вверх — рябь огней от центра к краю
        return [60 + r, 64 + r, 67 + r, 71 + r, 74 + r]

    # такт мира: пиццикато + маримба, точно каждые 0,8 с, до молчания
    k = 0
    while k * TICK < SILENT - 1e-6:
        t = k * TICK
        r = root(turn_index(t))
        m = ripple(r)[k % 5]
        f, mu = world_fade(t), mute(t)
        p.note("vln_pizz", m + 12 if m + 12 <= 96 else m, t, 0.3, vel=0.55 - 0.25 * mu, gain=0.4 * f, pan=WORLD_PAN,
               detune=rng.uniform(-0.3, 0.3) * mu, bend=-0.6 * mu, release=0.3)
        p.note("marimba", m, t, 0.5, vel=0.45 - 0.2 * mu, gain=0.3 * f, pan=WORLD_PAN + 0.1, release=0.6,
               detune=rng.uniform(-0.25, 0.25) * mu)
        k += 1
    # маяк: вибрафон + арфа, раз в три такта
    for t in beacons:
        r = root(turn_index(t))
        f = world_fade(t) * (1 - 0.6 * mute(t))
        for j, d in enumerate((0, 7, 11)):
            p.note("vibes", 64 + (r + d) % 12 + (12 if (r + d) % 12 < 4 else 0), t + 0.02 * j, 2.2, vel=0.45, gain=0.32 * f,
                   pan=WORLD_PAN + 0.15, release=2.0, detune=0.3 * mute(t) * (j - 1))
        for j, d in enumerate((0, 4, 7, 11, 14)):
            p.note("harp", 55 + r + d, t + 0.035 * j, 2.0, vel=0.45, gain=0.28 * f, pan=WORLD_PAN, release=1.6)
    # дробление: 16-е пиццикато альтов волной в «светлую» половину цикла 9,6 с (спицы прорастают и гаснут)
    t = 2.4
    while t < SILENT:
        ph = (t - 2.4) % 9.6
        if ph < 4.8:
            r = root(turn_index(t))
            arc = min(lin(0.0, 1.0, ph), 1 - lin(3.8, 4.8, ph))
            seq = [74 + r, 71 + r, 67 + r, 64 + r]
            idx = int(round((t - 2.4) / 0.2))
            if idx % 4:                                   # на четвертях — такт, между ними — дробление
                p.note("vla_pizz", seq[idx % 4] - 12 if seq[idx % 4] - 12 >= 48 else seq[idx % 4], t, 0.18, vel=0.45,
                       gain=0.22 * arc * world_fade(t), pan=WORLD_PAN - 0.1, release=0.2)
        t = round(t + 0.2, 1)
    # держащийся флажолетовый аккорд, меняется на каждом повороте (плавно, 0,6 с — как решётка)
    pts = [0.0] + [ts for ts in turns if ts <= SILENT] + [SILENT + 4.0]
    for i in range(len(pts) - 1):
        t0, t1 = pts[i], pts[i + 1]
        r = root(i)
        for j, d in enumerate((19, 23, 26, 30)):          # квинта, септима, нона, ♯11 — над корнем
            m = 60 + r + d
            while m > 100:
                m -= 12
            p.note("vln_harm", m, t0, t1 - t0 + 0.6, vel=0.4, gain=0.16 * world_fade(t0 + 0.5), pan=WORLD_PAN + 0.1 * (j - 1.5),
                   attack=0.6, release=0.6, detune=0.25 * mute(t0) * (j - 1.5), bend=-0.5 * mute(t0))
        p.note("fl_sus", 72 + r + (4 if r < 8 else -8), t0, t1 - t0 + 0.6, vel=0.35, gain=0.18 * world_fade(t0 + 0.5),
               pan=WORLD_PAN, attack=0.6, release=0.6)
    last_r = root(turn_index(SILENT))

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
    world_voices = [("vln_trem", 79 + last_r % 12), ("vln_trem", 83 + last_r % 12), ("vln_trem", 86 + last_r % 12),
                    ("vla_trem", 67 + last_r % 12), ("vla_trem", 71 + last_r % 12), ("hn_sus", 55 + last_r % 12),
                    ("hn_sus", 62 + last_r % 12), ("vln_trem", 90 + last_r % 12)]
    world_voices = [(i_, m - 12 if m > 96 else m) for i_, m in world_voices]
    brk = [62.6 + 14.4 * j / (len(world_voices) - 1) + rng.uniform(-0.4, 0.4) for j in range(len(world_voices))]
    order_ = sorted(range(len(world_voices)), key=lambda j: world_voices[j][1])     # снизу вверх: от касания к сердцевине
    for rank, j in enumerate(order_):
        inst, m = world_voices[j]
        tb = min(77.6, brk[rank]) if rank < len(order_) - 1 else world_dark            # верхний — сердцевина: до 78
        g = 0.2 if inst != "hn_sus" else 0.24
        p.note(inst, m, 50.0 + 0.3 * rank, tb - 0.7 - 50.0 - 0.3 * rank, vel=0.6, gain=g, pan=WORLD_PAN + 0.05 * (rank - 3),
               attack=2.0, release=0.12)
        p.note(inst, m, tb - 0.75, 0.75, vel=0.7, gain=g * 1.1, pan=WORLD_PAN - 0.2, attack=0.04, release=0.3,
               bend=-5.0 - rank * 0.4, detune=0.4)
    c.buzz(51.0, 11.0, notes=(78 + last_r % 12, 84 + last_r % 12 - 12, 89 + last_r % 12 - 12), gain=0.2)
    c.buzz(62.0, 16.0, notes=(73, 80, 86), gain=0.26, rates=(47.0, 59.0, 83.0))
    # обломки текут к сердцу: стекло и пузыри — справа налево
    t = 62.6
    while t < 77.6:
        prog = lin(62.6, 77.6, t)
        c.fx("glass" if rng.random() < 0.6 else "bubbles", t, gain=0.05 + 0.05 * rng.random(), pan=WORLD_PAN - 0.9 * rng.random() * (0.5 + prog),
             shift=rng.uniform(-10, 3), bus="fx")
        t += rng.uniform(0.25, 0.55)
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

    # ------------------------------------------------------------------ VII переваривание: Улей играет круг мира
    for m in (28, 35):
        p.note("org_quiet", m + 12, 79.0, order_wave - 79.0 + 0.6, vel=0.45, gain=0.2, attack=1.0, release=0.6)
    c.swell(order_turns[0], inst="org_quiet", midi_=52, dur=order_turns[0] - order_wave, gain=0.22)
    choir_block(order_wave, order_turns[0] + 0.3, [52, 56, 59], 0.6, 0.3, attack=1.4, pan=0.0, detune=0.15)
    seg = [order_turns[0]] + order_turns[1:] + [order_release]
    k0 = turn_index(SILENT) + 1
    for i in range(len(seg) - 1):
        t0, t1 = seg[i], seg[i + 1]
        r = root(k0 + i)
        last = i == len(seg) - 2
        # аккорд мира maj7♯11 — в теле Улья: хор, тромбоны, туба, валторны, низкие струнные
        lay = [("choir", 48 + r, 0.36), ("choir", 52 + r, 0.32), ("choir", 55 + r, 0.32), ("choir", 59 + r, 0.3),
               ("choir", 62 + r, 0.28), ("choir", 66 + r, 0.26),
               ("tbn_sus", 40 + r, 0.32), ("tbn_sus", 47 + r, 0.3), ("tba_sus", 28 + r, 0.32), ("hn_sus", 55 + r, 0.26),
               ("hn_sus", 59 + r, 0.24), ("cb_sus", 28 + r, 0.32), ("vc_sus", 40 + r, 0.3)]
        for inst, m, g in lay:
            if inst == "choir" and not 40 <= m <= 81:
                m -= 12
            dur = (t1 - t0) + (1.6 if last else 0.45)
            p.note(inst, m, t0, dur, vel=0.8, gain=g, attack=0.12, release=0.5 if not last else 1.2,
                   bend=0.0, pan=rng.uniform(-0.3, 0.3))
        c.timp(t0, r % 12, vel=0.95)
        c.fx("tamtam", t0, gain=0.2, bus="perc")
        # рябь мира — его же пятиступенная фигура, но басами и фаготами, 16-ми сетки мира
        tt = t0 + 0.2
        j = 0
        while tt < t1 - 0.05:
            m = ripple(r)[j % 5] - 24
            p.note("vc_pizz" if m >= 36 else "cb_pizz", m if m >= 28 else m + 12, tt, 0.2, vel=0.6, gain=0.3, pan=-0.2 + 0.1 * (j % 5),
                   release=0.2)
            if j % 2 == 0:
                p.note("bsn_stac", m + 12, tt, 0.18, vel=0.55, gain=0.06, pan=0.2, release=0.2)
            tt = round(tt + 0.2, 2)
            j += 1
    # отпуск: аккорд оплывает вниз, каждый голос — своим ходом
    r = root(k0 + len(seg) - 2)
    for j, (inst, m) in enumerate([("choir", 52 + r), ("choir", 59 + r), ("choir", 66 + r - 12), ("tbn_sus", 40 + r),
                                   ("hn_sus", 55 + r), ("vc_sus", 40 + r), ("cb_sus", 28 + r)]):
        if inst == "choir" and not 40 <= m <= 81:
            m -= 12
        p.note(inst, m, order_release, 2.6, vel=0.6, gain=0.24, attack=0.3, release=1.2, bend=-(2.0 + 1.3 * j), detune=0.35)
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
    for j, d in enumerate((19, 23, 26)):
        p.note("vln_harm", 60 + d, 104.4 + 0.3 * j, 3.6, vel=0.35, gain=0.15, pan=WORLD_PAN, attack=1.6, release=0.9)

    # баланс по замеру --parts (эскиз 0–60 с): сердце (литавры, контрабасы) и такт мира — вровень с хором
    p.balance({"Contrabassoon": -9, "Cellos": -2.5, "Violas": -2, "Marimba": +8, "Vibraphone": +12, "Harp": +1,
               "Flute": +2, "Basses": +10, "Timpani": +15, "Tuba": +10, "Organ": +7, "Trombone": +9, "Choir": -3})
    return p
