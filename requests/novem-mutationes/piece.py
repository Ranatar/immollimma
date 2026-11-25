#!/usr/bin/env python3
"""Novem Mutationes — музыка к обряду Тзинча (novem.html, цикл 108,8 с).

Времена — из журнала прогона страницы (events.json → cues.json; инструменты — tools/): перемены закона (mutations:
время, n — число семейств мозаики, длительность волны), каскады, надписи с окнами читаемости, анаграмма, очи.
Сетка: 75 уд/мин, доля 0,8 с — на долях стоят перемены, каскады, стадии; надписи — на шестнадцатых.

Лад — Мессиан № 3 от D: D E F F♯ G♯ A B♭ C C♯. Девять звуков; лад переходит сам в себя при переносе на большую
терцию. Отсюда главный обман: всё время переносится — и звукоряд остаётся прежним.

  Загадка   — D A B♭ F♯ F C♯ E G♯ C: каждый звук лада по разу, в конце — увеличенное трезвучие без разрешения.
  Разгадка  — анаграмма загадки: A G♯ F♯ E F B♭ C C♯ D, хорал с каденцией C♯→D.
  Смысл     — чистый унисон хора на основном тоне, пока надпись читается латиницей.

Процессы: кристалл-аккорд встаёт по звуку (II) и уходит в обратном порядке (IX); канон per tonos — каждая перемена
закона поднимает загадку на большую терцию «бесконечно» (октавы перетекают, как в тоне Шепарда), а через девять
перемен она в точности на прежней высоте; бегущая фигура делит полутакт на n по закону мозаики.

    python3 -m kit run requests/novem-mutationes/piece.py --sketch --parts
    python3 -m kit run requests/novem-mutationes/piece.py --parts
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from kit.devices import Composer  # noqa: E402
from kit.events import Piece  # noqa: E402

LEN = 108.8
Q = 0.8                                   # доля
MODE = [2, 4, 5, 6, 8, 9, 10, 0, 1]       # Мессиан № 3 от D (классы высот)
THEME = [62, 69, 70, 66, 65, 61, 64, 68, 72]          # D A B♭ F♯ F C♯ E G♯ C
THEME_Q = [1, 1, .5, .5, 1, 1.5, .5, 1, 1]            # в долях: 8 долей = 2 такта = 6,4 с
ANSWER = [69, 68, 66, 64, 65, 70, 72, 73, 74]         # A G♯ F♯ E F B♭ C C♯ D
ANSWER_Q = [1, .5, .5, 1, .5, .5, .5, .5, 2]          # 7 долей = 5,6 с
# хорал разгадки: бас и средние голоса под каждый звук ответа (всё — в ладу)
ANSWER_CH = [(45, (61, 64)), (48, (60, 64)), (50, (62, 57)), (49, (57, 61)), (50, (62, 57)),
             (46, (62, 65)), (41, (65, 68)), (45, (64, 61)), (38, (62, 66))]
# девять голосов кристалла: (высота, инструмент) — в порядке звуков загадки
CRYSTAL = [(38, "org_quiet"), (57, "org_quiet"), (70, "vla_harm"), (78, "vln_harm"), (65, "vc_harm"),
           (73, "vln_harm"), (88, "vln_harm"), (68, "org_quiet"), (84, "vln_harm")]
GLASS_LAWS = {0, 3, 4, 6, 8}              # законы со стеклом (заливкой); остальные — лабиринт (дуги)


def in_mode(m):
    return m % 12 in MODE


def mode_scale(lo, hi):
    return [m for m in range(lo, hi + 1) if in_mode(m)]


def build(ctx):
    cues = ctx.cues
    muts = cues["mutations"]
    casc = [c for c in cues["cascades"] if c["t"] >= 74.0]
    caps = cues["captions"]
    eyes = [e for e in cues["eyes"] if not e["big"]]
    p = Piece("Novem Mutationes", bpm=75, meter=(4, 4), key="D minor", seed=9)
    p.meta["length"] = LEN
    c = Composer(p, lib="vsco", seed=9)
    rng = p.rng
    for e in cues["cues"]:
        if e["kind"] == "section":
            p.mark(e["t"], e["label"])

    def root_at(t):                       # основной тон: D, а в переменах — по переносу канона
        r = 2
        for k, m in enumerate(muts):
            if t >= m["t"]:
                r = (2 + 4 * (k + 1)) % 12
        return r if 24.0 <= t < 60.8 else 2

    def theme(t0, pitches, qs, inst, shift=0, scale=1.0, vel=.55, gain=.4, until=None, pan=0.0, legato=.95, release=.5,
              attack=.02, bus=None):
        t = t0
        for m, q in zip(pitches, qs):
            d = q * Q * scale
            if until is not None and t >= until - 1e-6:
                break
            dd = d * legato if until is None else min(d * legato, until - t)
            p.note(inst, m + shift, t, max(.06, dd), vel=vel, gain=gain, pan=pan, release=release, attack=attack, bus=bus)
            t += d
        return t

    def shepard_theme(t0, rise, until, inst="org_quiet", gain=.34, vel=.5, scale=1.0, center=68.0, width=9.0):
        """загадка, поднятая на rise полутонов, — в нескольких октавах с колоколообразными весами:
        каждый перенос звучит как подъём, а регистр никуда не уходит"""
        for o in range(-4, 5):
            sh = rise - 12 * o
            mid = sum(THEME) / 9 + sh
            w = math.exp(-((mid - center) / width) ** 2)
            if w < .12:
                continue
            theme(t0, THEME, THEME_Q, inst, shift=sh, scale=scale, vel=vel, gain=gain * w, until=until)

    # ===================================================================== I TENEBRAE: точка света
    p.note("vln_harm", 86, 0.4, 3.6, vel=.3, gain=.16, attack=.8, release=1.2, pan=.1)

    # ===================================================================== II INITIUM: девять звуков встают в кристалл
    crystal_entry = [2.0 + 1.2 * k for k in range(9)]
    for k, ((m, inst), te) in enumerate(zip(CRYSTAL, crystal_entry)):
        p.note(inst, m, te, 14.2 - te, vel=.4, gain=.3 if inst == "org_quiet" else .2, attack=.5, release=1.2,
               pan=-.5 + k / 8)
        if 40 <= m <= 96:
            p.note("harp", m if m <= 88 else m - 12, te, 1.8, vel=.45, gain=.22, release=1.5, pan=-.5 + k / 8)
        c.fx("glass", te, gain=.05, pan=-.5 + k / 8, bus="fx")

    # ===================================================================== III LEX: строгий канон на загадке
    def lex(t_shift=0.0, upto=None):
        """закон: dux в органе с 14.4, comes октавой ниже (орган + виолончели) с 17.6; педаль D"""
        lim = None if upto is None else upto + t_shift
        p.note("org_quiet", 38, 14.0 + t_shift, (24.0 if upto is None else upto) - 14.0 - .05, vel=.45, gain=.36,
               attack=.3, release=.4)
        theme(14.4 + t_shift, THEME, THEME_Q, "org_quiet", vel=.55, gain=.42, until=lim, pan=.25)
        theme(17.6 + t_shift, THEME, THEME_Q, "org_quiet", shift=-12, vel=.55, gain=.38, until=lim, pan=-.25)
        theme(17.6 + t_shift, THEME, THEME_Q, "vc_sus", shift=-12, vel=.5, gain=.24, until=lim, pan=-.3, attack=.04)
    lex()

    # ===================================================================== IV MUTATIONES: девять перемен закона
    for k, m in enumerate(muts):
        t0 = m["t"]
        t1 = muts[k + 1]["t"] if k + 1 < len(muts) else 60.8
        seg = t1 - t0
        n = m["n"]
        rise = 4 * (k + 1)                 # per tonos по большим терциям: 4, 8 … 36 ≡ 0
        r = (2 + rise) % 12
        g = .7 + .075 * k                  # нарастание: перемены всё чаще — и всё громче
        # волна новой закона: стеклянный удар, взлёт арфы по ладу, тарелка на всю волну
        c.fx("glass", t0, gain=.12 * g, pan=rng.uniform(-.5, .5), bus="fx")
        run = mode_scale(55 + r % 4, 90)[:12]
        for j, mm in enumerate(run):
            p.note("harp", mm, t0 + .035 * j, .9, vel=.55, gain=.24 * g, release=1.0, pan=-.4 + j / 14)
        c.fx("susp", t0, gain=.12 * g, dur=min(m["dur"], seg), fade=.4, bus="perc")
        c.timp(t0, r, vel=.45 + .03 * k)
        # опора: аккорд нового основного тона (мажор и минор сразу) и бас
        b = 38 + (r - 2) % 12
        b = b - 12 if b > 45 else b
        for mm, inst, gg in ((b, "cb_sus", .34), (b + 12, "org_quiet", .3), (b + 24 + 4, "org_quiet", .2),
                             (b + 24 + 7, "org_quiet", .2), (b + 12 + 3, "vla_sus", .12)):
            p.note(inst, mm, t0, seg - .04, vel=.45, gain=gg * g, attack=.08, release=.35)
        # канон per tonos: загадка, поднятая на rise, «бесконечный подъём»
        shepard_theme(t0, rise, until=t1, gain=.36 * g)
        if seg > 4.5:                      # comes на такт позже, октавой ниже — пока перемены редки
            shepard_theme(t0 + 3.2, rise, until=t1, gain=.22 * g, center=56.0)
        # деление полутакта на n: стекло — арфа, лабиринт — струнные legato
        step = 1.6 / n
        sc = mode_scale(60 + r % 4, 88)
        pat = list(range(len(sc))) + list(range(len(sc) - 2, 0, -1))
        t = t0
        i = 0
        glass = k in GLASS_LAWS
        while t < t1 - .02:
            mm = sc[pat[(i * 2) % len(pat)]] if n > 7 else sc[pat[i % len(pat)]]
            acc = i % n == 0
            if glass:
                p.note("harp", mm, t, .7, vel=.5 + (.15 if acc else 0), gain=.2 * g, release=.9, pan=.35)
                p.note("vla_pizz", mm - 12, t, .3, vel=.5, gain=.1 * g, release=.3, pan=.35)
            else:
                p.note("vln_sus", mm, t, step * 1.15, vel=.45 + (.12 if acc else 0), gain=.16 * g, attack=.03,
                       release=.15, pan=-.35)
                p.note("vla_sus", mm - 12, t, step * 1.15, vel=.45, gain=.09 * g, attack=.03, release=.15, pan=-.25)
            i += 1
            t = t0 + i * step

    # ===================================================================== V REVELATIO: загадка и разгадка
    # 60.8–64.0: сдвиги сходятся — все девять звуков лада в струнных, нарастая; 64.0 — мозаика девятикратна
    for j, mm in enumerate([62, 64, 65, 66, 68, 69, 70, 72, 73]):
        inst = "vln_sus" if mm >= 67 else "vla_sus"
        p.note(inst, mm + 12, 60.8, 4.0, vel=.65, gain=.16, attack=1.2, release=.8, pan=-.6 + j * .15)
    for mm in (38, 45, 50):                 # опора, пока сдвиги сходятся
        p.note("org_quiet", mm, 60.8, 3.2, vel=.5, gain=.3, attack=.1, release=.3)
    c.timp(61.6, 2, vel=.55, roll=2.4)
    p.note("org_quiet", 38, 64.0, 2.6, vel=.5, gain=.38, release=.6)
    p.note("cb_sus", 38, 64.0, 2.6, vel=.5, gain=.34, release=.6)
    c.fx("gong_hit", 64.0, gain=.22, bus="perc")
    # вопрос: хор поёт загадку (61.6–64.8), органум в кварту
    theme(61.6, THEME, THEME_Q, "choir", scale=.5, vel=.62, gain=.5, legato=.92)
    theme(61.6, THEME, THEME_Q, "choir", shift=-5, scale=.5, vel=.55, gain=.3, legato=.92)
    # анаграмма (64.8–66.6): девять голосов держат звуки загадки и съезжают каждый на звук ответа той же позиции —
    # голоса меняются местами, а звучащее множество почти не меняется
    an = [x for x in caps if x.get("anagram")][0]
    ta = an["anagram_at"]
    for j, (a, b2) in enumerate(zip(THEME, ANSWER)):
        inst = "vln_sus" if a >= 66 else "vla_sus" if a >= 58 else "vc_sus"
        p.note(inst, a, ta - .4, 2.2, vel=.6, gain=.16, attack=.25, release=.25, bend=float(b2 - a), pan=-.6 + j * .15)
    # ===================================================================== VI OCULUS: хорал-разгадка, очи
    theme(66.4, ANSWER, ANSWER_Q, "choir", vel=.66, gain=.55, legato=.96)
    theme(66.4, ANSWER, ANSWER_Q, "org_quiet", vel=.55, gain=.3, legato=.96)
    t = 66.4
    for (bass, mid), q in zip(ANSWER_CH, ANSWER_Q):
        d = q * Q
        p.note("org_quiet", bass, t, d * .96, vel=.5, gain=.36, release=.3)
        p.note("cb_sus", bass - 12 if bass >= 40 else bass, t, d * .96, vel=.5, gain=.3, release=.3)
        for mm in mid:
            p.note("choir", mm, t, d * .96, vel=.55, gain=.3, release=.3)
            p.note("tbn_sus", mm - 12, t, d * .96, vel=.45, gain=.16, release=.3)
        t += d
    c.fx("gong_hit", 66.4, gain=.18, bus="perc")
    for e, mm in zip(eyes, THEME):         # девять малых очей — звуки загадки в истинном порядке
        p.note("vln_harm", mm + 24, e["t"], 1.6, vel=.4, gain=.14, attack=.05, release=1.0, pan=rng.uniform(-.6, .6))
    for mm in (38, 45):                     # тишина взгляда
        p.note("org_quiet", mm, 72.0, 2.35, vel=.4, gain=.3, attack=.4, release=.3)
    c.fx("tamtam", 72.0, gain=.12, bus="perc")

    # ===================================================================== VII TEMPESTAS: стретта из девяти вступлений
    VOICES = [("tbn_sus", -12), ("hn_sus", -12), ("vc_sus", -12), ("org_loud", 0), ("tpt_sus", 0),
              ("vla_sus", 0), ("choir", 0), ("vln_sus", 12), ("org_loud", -24)]
    for j, cs in enumerate(casc[:9]):
        inst, octv = VOICES[j]
        sh = 4 * (j % 3) - (12 if 4 * (j % 3) + octv + 72 > 84 else 0) + octv
        theme(cs["t"], THEME, THEME_Q, inst, shift=sh, scale=.5, vel=.8, gain=.34 + .02 * j, until=83.95,
              pan=-.7 + j * .175, attack=.02)
        c.timp(cs["t"], (2 + 4 * (j % 3)) % 12, vel=.65 + .03 * j)
    for mm in (38, 45, 50, 57, 62, 66, 69):
        p.note("org_loud", mm, 74.4, 9.55, vel=.75, gain=.16, attack=2.5, release=.2)
    for mm, inst in ((26, "cbsn_sus"), (38, "cb_sus"), (38, "tba_sus")):
        p.note(inst, mm, 74.4, 9.55, vel=.7, gain=.32, attack=1.5, release=.2)
    c.timp(78.4, 2, vel=.7, roll=5.5)
    c.fx("susp", 77.6, gain=.2, dur=6.3, fade=.1, bus="perc")
    c.fx("tamtam", 80.8, gain=.3, bus="perc")
    t = 74.6
    while t < 83.8:                         # осколки перевёртышей — чаще к концу бури
        c.fx("glass", t, gain=.05 + .07 * (t - 74.4) / 9.6, pan=rng.uniform(-.9, .9), bus="fx")
        t += .55 - .35 * (t - 74.4) / 9.6 + rng.uniform(0, .15)

    # ===================================================================== VIII NIHIL MUTATUM: дословный повтор закона
    lex(t_shift=70.0, upto=18.0)            # 84.0–88.0 = 14.0–18.0, нота в ноту

    # ===================================================================== IX REDITUS: ракоход
    for k, (m, inst) in enumerate(CRYSTAL):  # кристалл снова целиком — и теряет звуки в обратном порядке под ромбы;
        off = 88.8 + .8 * (8 - k) if k else 100.0   # первый звук (D) держится до последнего ромба
        p.note(inst, m, 88.0, off - 88.0 + .3, vel=.4, gain=(.3 if inst == "org_quiet" else .2), attack=.6,
               release=1.0, pan=-.5 + k / 8)
    theme(89.6, THEME[::-1], THEME_Q[::-1], "org_quiet", scale=1.0, vel=.5, gain=.34, pan=.2)
    p.note("cb_sus", 38, 88.0, 8.0, vel=.4, gain=.26, attack=.5, release=1.5)
    # правдивая строка шифром: целиком она встаёт лишь на миг — загадка мелькает в истинном порядке
    last = caps[-1]
    tflash = last["until"] - .6 - 1.3
    for j, mm in enumerate(THEME):
        p.note("vln_harm", mm + 24, tflash + .066 * j, .5, vel=.35, gain=.12, attack=.02, release=.6, pan=-.4 + j * .1)
    # последний ромб: один звук, гаснет в точку
    p.note("vln_harm", 86, 100.0, 2.4, vel=.3, gain=.14, attack=.4, release=.8)
    p.note("org_quiet", 62, 100.0, 2.4, vel=.35, gain=.18, attack=.4, release=.8)
    p.note("crotales", 98, 102.4, 2.0, vel=.35, gain=.12, release=2.0)

    # ===================================================================== смысл: унисон хора, пока надпись читается
    for cp in caps:
        if not cp["legible"]:
            continue
        a, b = cp["legible"]
        t = a
        while t < b - .05:                   # основной тон может смениться внутри окна (перемена закона)
            r = root_at(t)
            nxt = min([b] + [m["t"] for m in muts if t < m["t"] < b])
            for mm in (38 + 12 + (r - 2) % 12, 38 + 24 + (r - 2) % 12):
                mm = mm - 12 if mm > 66 else mm
                p.note("choir", mm, t, nxt - t - .02, vel=.4, gain=.22, attack=.3, release=.5)
            t = nxt

    # баланс по замеру --parts: загадка в органе — ведущая, басовая группа вровень с ней, краски ниже
    p.balance({"Organ": +10.5, "Harp": -1, "Basses": +20, "Choir": +1, "Timpani": +8, "Violins": +10, "Violas": -7,
               "Contrabassoon": -11.5, "Trumpet": -8, "Trombone": +17, "Tuba": +8.5, "Crotales": +20})
    return p
