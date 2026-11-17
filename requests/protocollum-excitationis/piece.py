#!/usr/bin/env python3
"""Protocollum Excitationis — музыка к анимации protocol.html (пробуждение гробницы некронов, цикл 96 с).

Все времена — из журнала прогона анимации (events.json → cues.json; инструменты — tools/):
  стадии и метки — cues; удары сердца — cues["hearts"]; ряды легиона — cues["rows"] (пробуждение и уход
  центральной ниши, ряд 12 — дальний); сбои спящих — cues["bad_niches"]; тиканье счётчика — cues["counter_ticks"];
  вписывание глифов стены — cues["cells"].
Сетка 100 уд/мин, 4/4: такт = 2,4 с = два удара сердца; ключевые метки кратны 0,3 с.

Без голосов: у некронов нет душ. Материал — квинтовая стопка C–G–D–A–E–B–F♯ (холод, совершенство) и узник-звезда
(альтовая флейта, солирующая скрипка: E F B C — тепло, но неправильно).
Сквозные процессы: стопка собирается и разбирается (рёбра, обереги, легион, имя, приказ, распад, обратный порядок);
сердце (accelerando, затем ровно); тиканье счётчика (замедляется до остановки — и заново с нуля).

    python3 -m kit run requests/protocollum-excitationis/piece.py --sketch --parts
    python3 -m kit run requests/protocollum-excitationis/piece.py --parts
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from kit.devices import Composer  # noqa: E402
from kit.events import Piece  # noqa: E402

LEN = 96.0
STACK = [48, 55, 62, 69, 76, 83, 90]          # C3 G3 D4 A4 E5 B5 F♯6
STAR = [(76, .9), (77, .6), (71, .9), (72, 1.8)]  # E5 F5 B4 C5 — узник
NAME = [(48, "tbn_sus"), (55, "tbn_sus"), (62, "hn_sus"), (69, "hn_sus"), (76, "tpt_sus")]
# ряд → тон легиона (12 — дальний, просыпается первым и звучит выше всех)
ROW_PITCH = {12: 78, 11: 71, 10: 64, 9: 57, 8: 50, 7: 43, 6: 36, 5: 48, 4: 43, 3: 36, 2: 31, 1: 36, 0: 24}


def row_inst(m):
    if m >= 64:
        return ("vln_sus", "vln_harm")
    if m >= 50:
        return ("vla_sus", "hn_sus")
    if m >= 36:
        return ("vc_sus", "tbn_sus")
    return ("cb_sus", "cbsn_sus")


def build(ctx):
    cues = ctx.cues
    p = Piece("Protocollum Excitationis", bpm=100, meter=(4, 4), key="C major", seed=11)
    p.meta["length"] = LEN
    c = Composer(p, lib="vsco", seed=11)
    rng = p.rng
    for e in cues["cues"]:
        if e["kind"] == "section":
            p.mark(e["t"], e["label"])
    hearts = cues["hearts"]
    rows = {r["row"]: r for r in cues["rows"]}
    cells = sorted(cues["cells"], key=lambda q: q["t"])
    nr = max(q["r"] for q in cells) + 1

    def star(t0, scale=1.0, vel=0.45, gain=0.5, solo=False, bend=0.0, rev=False):
        seq = list(reversed(STAR)) if rev else STAR
        t = t0
        for m, d in seq:
            d *= scale
            p.note("afl_sus", m, t, d * .96, vel=vel, gain=gain, attack=.25, release=.9, pan=.15, bend=bend)
            if solo:
                p.note("vln_solo", m, t + .03, d * .96, vel=vel, gain=gain * .7, attack=.3, release=.8, pan=-.2,
                       detune=.15, bend=bend * 1.3)
            t += d
        return t

    # ================================================================ I ТЬМА (0–8.1): счётчик сна замедляется и встаёт
    p.note("cbsn_sus", 24, 1.2, 7.4, vel=.4, gain=.22, attack=2.5, release=1.5)         # субтон
    for k, tt in enumerate(cues["counter_ticks"]):
        late = (tt - 1.2) / 6.0
        p.note("vln_colleg", 96 if k % 2 else 91, tt, .08, vel=.4 + .35 * late, gain=.22 + .25 * late, pan=.3 - .6 * (k % 2),
               release=.12)
        if k % 3 == 0:
            c.fx("wood_click", tt, gain=.04 + .1 * late, pan=-.2, bus="perc")
    p.note("crotales", 96, 7.2, 2.5, vel=.55, gain=.3, release=2.5)                     # встал
    p.note("vibes", 84, 7.2, 3.0, vel=.45, gain=.3, release=2.5)

    # ================================================================ II СКЛЕП (8.1–15)
    p.note("vln_harm", 88, 8.1, 2.6, vel=.4, gain=.18, attack=.08, release=1.6, pan=.3)     # узник загорелся
    p.note("crotales", 100, 8.1, 2.0, vel=.4, gain=.18, release=2.0)
    star(8.7, vel=.38, gain=.42)
    for k in range(32):                                                                 # рёбра тессеракта
        m = STACK[k % 7] + (12 if (k // 7) % 2 else 0)
        if m > 96:
            m -= 24
        p.note("harp", m, 8.4 + .1 * k, .6, vel=.42 + .2 * (k / 31), gain=.34, pan=-.45 + .9 * (k % 7) / 6, release=1.2)
    p.note("vln_harm", 76, 11.4, 1.5, vel=.35, gain=.14, attack=.3, release=.8, bend=12.0, pan=-.3)   # поле
    for k in range(24):                                                                 # обереги по кольцу
        m = STACK[6 - k % 7] + (0 if (k // 7) % 2 else -12)
        while m > 89:
            m -= 12
        while m < 53:
            m += 12
        p.note("vibes", m, 12.6 + .1 * k, 1.6, vel=.35, gain=.22, pan=-.6 + 1.2 * k / 23, release=1.6)
    for m, inst in ((48, "vc_harm"), (55, "vla_harm")):
        p.note(inst, m, 9.0, 6.6, vel=.35, gain=.2, attack=2.0, release=1.2)

    # ================================================================ III СТЕНА (15–21): глифы вписываются точками
    tmax = max(q["t"] for q in cells)
    for k, q in enumerate(cells):
        if k % 4 or q["t"] > 21.0:
            continue
        m = STACK[(nr - 1 - q["r"]) % 7] + 12 * ((nr - 1 - q["r"]) // 7)
        inst = "vln_pizz" if m >= 67 else "vla_pizz" if m >= 55 else "vc_pizz"
        p.note(inst, m, q["t"], .25, vel=.5, gain=.3, pan=.55 * q["side"], release=.4)
        if k % 12 == 0:
            p.note("harp", m + 12, q["t"] + .02, .5, vel=.4, gain=.18, pan=.55 * q["side"], release=1.0)
    for m, inst in ((36, "cb_sus"), (43, "vc_sus")):
        p.note(inst, m, 15.0, 6.4, vel=.4, gain=.32, attack=3.0, release=.6)
    p.note("vln_harm", 79, 15.0, 2.4, vel=.35, gain=.14, attack=.2, release=.6, bend=7.0, pan=-.3)    # свет бежит по шинам
    p.note("vln_harm", 79, 15.05, 2.4, vel=.35, gain=.14, attack=.2, release=.6, bend=7.0, pan=.3)

    # ================================================================ IV/VI СЕРДЦЕ ГРОБНИЦЫ (21–57.6)
    for k, tb in enumerate(hearts):
        steady = tb >= 28.8 - 1e-6
        v = .45 + .35 * min(1.0, (tb - 21) / 7.8) if not steady else .62
        if tb >= 57.6 - 1e-6:
            continue                                                                    # последний удар — приказ
        c.timp(tb, 0, vel=v)
        c.fx("bd_soft", tb, gain=.18 + .15 * v, bus="perc")
        p.note("cb_pizz", 36, tb, .4, vel=v, gain=.5, pan=-.15, release=.4)
        p.note("vc_pizz", 48, tb + .22, .3, vel=v * .8, gain=.35, pan=.1, release=.3)       # «тук-тук»
        c.fx("bd_soft", tb + .22, gain=(.18 + .15 * v) * .55, bus="perc")

    # ================================================================ V ЗАЛ (28.8–31.2)
    for m, inst in ((36, "cb_sus"), (43, "vc_sus"), (50, "vla_sus")):
        p.note(inst, m, 28.8, 2.6, vel=.55, gain=.3, attack=2.2, release=.5)
    c.fx("gong_scrape", 28.9, gain=.22, bus="perc")

    # ================================================================ VI ЛЕГИОН (31.2–): квинтовый аккорд по рядам
    for rnum, r in sorted(rows.items(), key=lambda kv: kv[1]["wake"]):
        m = ROW_PITCH[rnum]
        a, b = row_inst(m)
        near = 1 - rnum / 12                                                            # ближние громче
        tw, td = r["wake"], r["depart"]
        ping = m
        while ping < 72:
            ping += 12
        p.note("crotales" if ping >= 84 else "vibes", min(ping, 104), tw, 1.2, vel=.5, gain=.18, release=1.4, pan=rng.uniform(-.5, .5))
        p.note("vibes", min(ping, 89) if ping <= 89 else ping - 12, tw + .08, .8, vel=.35, gain=.12, release=1.0)
        p.note("vc_colleg", 50 + (rnum % 5) * 2, tw, .1, vel=.5, gain=.2, release=.1)
        for seg in ((tw, 57.25), (57.6, td)):                                          # вдох перед приказом
            if seg[1] - seg[0] < .2:
                continue
            g = .2 + .2 * near
            p.note(a, m, seg[0], seg[1] - seg[0], vel=.5 + .2 * near, gain=g, attack=.35 if seg[0] == tw else .05,
                   release=.12, pan=rng.uniform(-.3, .3))
            p.note(b, m if b != "vln_harm" else m + 12, seg[0], seg[1] - seg[0], vel=.45 + .2 * near, gain=g * .7,
                   attack=.5 if seg[0] == tw else .05, release=.12)
    for tb in cues["bad_niches"]:                                                      # неисправные спящие
        c.fx("zap", tb, gain=.05, shift=7, pan=rng.uniform(-.7, .7), bus="fx")
        p.note("vln_harm", 95, tb + .1, .12, vel=.3, gain=.05, release=.1, detune=.4)
    # минимализм: медленное арпеджио стопки, каждый такт на звук длиннее
    t, n = 40.8, 3
    while t < 47.9:
        bar_end = t + 2.4
        k = 0
        while t < bar_end - 1e-6 and t < 47.9:
            m = STACK[1 + k % n]
            while m > 89:
                m -= 12
            p.note("vibes", m, t, .9, vel=.38, gain=.18, pan=.4 - .8 * (k % 2), release=1.0)
            t += .3
            k += 1
        n = min(6, n + 1)

    # ================================================================ VII ИМЯ (48–52.8): пять квинт меди
    for i, (m, inst) in enumerate(NAME):
        t0 = 48.0 + .9 * i
        p.note(inst, m, t0, 57.25 - t0, vel=.72, gain=.42, attack=.03, release=.12, pan=-.4 + .2 * i)
        p.note("tubular", [60, 67, 62, 69, 76][i], t0, 3.0, vel=.6, gain=.3, release=2.5)
    c.timp(48.0, 0, vel=.8)
    c.fx("tamtam", 51.6, gain=.3, bus="perc")

    # ================================================================ VIII ДАВЛЕНИЕ (52.8–57.3)
    star(52.8, scale=1.0, vel=.62, gain=.55, solo=True, bend=.6)
    for m in (76, 77, 83, 84):
        p.note("vln_trem", m, 52.9, 4.35, vel=.7, gain=.09, attack=4.2, release=.05, detune=.2)
    p.note("vln_harm", 88, 53.4, 3.85, vel=.5, gain=.15, attack=3.0, release=.05)
    p.note("vln_harm", 88, 53.4, 3.85, vel=.5, gain=.15, attack=3.0, release=.05, detune=.35)   # биения
    t, k = 54.45, 0
    while t < 57.2:                                                                     # цепь оберегов
        m = STACK[k % 7] + 24
        while m > 108:
            m -= 12
        while m < 84:
            m += 12
        p.note("crotales", m, t, .4, vel=.4 + .3 * (t - 54.45) / 2.8, gain=.11, pan=-.6 + 1.2 * (k % 7) / 6, release=.4)
        t += .15
        k += 1
    c.timp(55.5, 0, vel=.75, roll=1.75)
    c.fx("susp_scrape", 54.6, gain=.18, bus="perc", dur=2.6, fade=.05)
    # 57.25–57.6 — вдох (тишина)

    # ================================================================ IX ПРИКАЗ (57.6)
    for m, inst, g in ((24, "cbsn_sus", .5), (36, "tba_sus", .5), (36, "cb_sus", .45), (43, "tbn_sus", .45),
                       (50, "tbn_sus", .45), (57, "hn_sus", .42), (64, "hn_sus", .42), (71, "tpt_sus", .4),
                       (78, "tpt_sus", .38), (83, "vln_sus", .32), (90, "vln_sus", .3)):
        p.note(inst, m, 57.6, 1.6, vel=1.0, gain=g * 1.4, attack=.01, release=1.4)
    c.timp(57.6, 0, vel=1.0)
    c.fx("tamtam", 57.6, gain=.45, bus="perc")
    c.fx("gong_hit", 57.6, gain=.3, bus="perc")
    c.fx("clash", 57.6, gain=.2, bus="perc")
    p.note("vln_harm", 96, 57.6, 2.0, vel=.6, gain=.16, release=1.5)
    p.note("afl_sus", 84, 57.65, 1.4, vel=.6, gain=.32, attack=.05, release=1.0)       # вспышка узника

    # ================================================================ X УХОД (59.4–69.6): аккорд распадается снизу вверх
    for rnum, r in rows.items():
        m = ROW_PITCH[rnum]
        td = r["depart"]
        ping = m
        while ping < 79:
            ping += 12
        p.note("crotales" if ping >= 84 else "vibes", min(ping, 104), td - .5, .5, vel=.5, gain=.2, reverse=True)
        p.note("vln_harm", min(max(ping, 67), 100), td, .15, vel=.4, gain=.08, release=.2)
    sample = sorted(rng.sample(range(40), 0)) if False else None
    for k in range(18):                                                                  # боковые ряды — раньше
        tt = 59.4 + rng.uniform(0, 3.0)
        p.note("vibes", rng.choice([77, 81, 83, 86, 88]), tt - .35, .35, vel=.35, gain=.06, reverse=True)

    # ================================================================ XI ВОЗВРАЩЕНИЕ В СОН (72–86.4)
    star(73.2, scale=1.6, vel=.35, gain=.4, rev=True)
    span = tmax - 15 + .833
    for k, q in enumerate(cells):                                                       # глифы стираются
        if k % 5:
            continue
        tu = 72 + 8.4 * (1 - (q["t"] - 15) / span)
        m = STACK[(nr - 1 - q["r"]) % 7] + 12 * ((nr - 1 - q["r"]) // 7)
        p.note("vln_pizz" if m >= 67 else "vla_pizz", m, tu, .2, vel=.38, gain=.18, pan=.55 * q["side"], release=.3)
    p.note("cbsn_sus", 24, 70.0, 21.0, vel=.4, gain=.2, attack=3.0, release=2.0)
    for m, inst in ((48, "vc_harm"), (55, "vla_harm")):                                  # пустой зал: чистая квинта
        p.note(inst, m, 69.2, 7.0, vel=.35, gain=.2, attack=1.5, release=1.5)
    c.swell(72.0, inst="vibes", midi_=76, dur=1.8, gain=.22)
    for k in range(24):                                                                 # обереги гаснут
        m = STACK[k % 7] + (0 if (k // 7) % 2 else -12)
        while m > 89:
            m -= 12
        while m < 53:
            m += 12
        p.note("vibes", m, 80.4 + .1 * k, 1.0, vel=.28, gain=.15, pan=.6 - 1.2 * k / 23, release=1.2)
    p.note("vln_harm", 88, 82.2, 1.5, vel=.32, gain=.12, attack=.05, release=.6, bend=-12.0)   # поле
    for k in range(32):                                                                 # рёбра уходят
        m = STACK[(31 - k) % 7] + (12 if ((31 - k) // 7) % 2 else 0)
        if m > 96:
            m -= 24
        p.note("harp", m, 83.4 + .094 * k, .5, vel=.4 - .15 * k / 31, gain=.28, pan=.45 - .9 * ((31 - k) % 7) / 6, release=1.0)
    p.note("vln_harm", 96, 86.4, 3.6, vel=.3, gain=.1, attack=.1, release=.6, pan=.2)    # точка-узник

    # ================================================================ XII НОВЫЙ СОН (86.4–96)
    k, tt = 0, 86.4 + 1 / 3.7
    while tt < 92.3:
        fade = 1 - (tt - 86.4) / 6.0
        p.note("vln_colleg", 96 if k % 2 else 91, tt, .08, vel=.35, gain=.1 * fade + .02, pan=.3 - .6 * (k % 2), release=.12)
        tt += 1 / 3.7
        k += 1

    # баланс по замеру --parts (эскиз 0–60 с)
    p.balance({"Cellos": -10, "Contrabassoon": -10, "Trumpet": -5, "Horn": -1, "Violas": +1, "Tuba": +2,
               "Violins": +4, "Timpani": +8, "Violin solo": +6, "Basses": +10, "Trombone": +13, "Crotales": +11,
               "Tubular bells": +15, "Vibraphone": +19})
    return p
