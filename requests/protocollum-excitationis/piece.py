#!/usr/bin/env python3
"""Protocollum Excitationis — музыка к анимации protocol.html (пробуждение гробницы некронов, цикл 96 с).

Все времена — из журнала прогона анимации (events.json → cues.json; инструменты — tools/):
  стадии и метки — cues; удары сердца — cues["hearts"]; ряды легиона — cues["rows"] (пробуждение и уход
  центральной ниши, ряд 12 — дальний); сбои спящих — cues["bad_niches"]; тиканье счётчика — cues["counter_ticks"];
  вписывание глифов стены — cues["cells"].
Сетка 100 уд/мин, 4/4: такт = 2,4 с = два удара сердца; ключевые метки кратны 0,3 с.

Без голосов: у некронов нет душ. Материал — две квинтовые цепи на полутон друг от друга: C–G–D и D♭–A♭–E♭.
Каждая — чистые квинты (холод, совершенство), вместе они не складываются ни в какую тональность. Первая редакция
стояла на одной цепи C–G–D–A–E–B–F♯ — это диатоника (до-лидийский, мажорная пентатоника) и звучала светло, почти
празднично; заодно убран «блеск»: арфа шестнадцатыми и вибрафон заменены флажолетами и col legno.
Узник-звезда (альтовая флейта, солирующая скрипка): E F — B B♭, полутоны без разрешения, чужие гробнице звуки.
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
HI_A, HI_B = [79, 86, 84], [80, 87, 85]       # высокие звуки цепей: G5 D6 C6 | A♭5 E♭6 D♭6
HIGH = [79, 80, 86, 87, 84, 85]               # попеременно: цепь C–G–D, цепь D♭–A♭–E♭
MID = [60, 67, 74, 61, 68, 75]                # C4 G4 D5 D♭4 A♭4 E♭5
CROT = [96, 97, 103, 104, 98, 99]             # кроталы: C7 D♭7 G7 A♭7 D7 E♭7
STAR = [(76, .9), (77, .6), (71, .9), (70, 1.8)]  # E5 F5 B4 B♭4 — узник
NAME = [(48, "tbn_sus"), (55, "tbn_sus"), (62, "hn_sus"), (68, "hn_sus"), (75, "tpt_sus")]  # C3 G3 D4 → A♭4 E♭5
# ряд → тон легиона (12 — дальний, просыпается первым и звучит выше всех); цепи чередуются, наверху — полутоновые пары
ROW_PITCH = {12: 75, 11: 74, 10: 68, 9: 67, 8: 61, 7: 60, 6: 50, 5: 56, 4: 43, 3: 49, 2: 36, 1: 31, 0: 24}
WALL = [75, 74, 68, 67, 61, 60, 56, 50, 49, 43]  # регистры стены сверху вниз


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
    p = Piece("Protocollum Excitationis", bpm=100, meter=(4, 4), key="C major", seed=11)  # без знаков: язык атональный
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
    p.note("crotales", 97, 7.2, 2.5, vel=.55, gain=.3, release=2.5)                     # встал
    p.note("tubular", 60, 7.2, 3.0, vel=.4, gain=.25, release=2.5)

    # ================================================================ II СКЛЕП (8.1–15)
    p.note("vln_harm", 88, 8.1, 2.6, vel=.4, gain=.18, attack=.08, release=1.6, pan=.3)     # узник загорелся
    p.note("crotales", 100, 8.1, 2.0, vel=.4, gain=.18, release=2.0)
    star(8.7, vel=.38, gain=.42)
    for k in range(32):                                                                 # рёбра тессеракта: сухо
        if k % 2 == 0:
            p.note("vln_colleg", MID[(k // 2) % 3], 8.4 + .1 * k, .1, vel=.45 + .2 * (k / 31), gain=.3,
                   pan=-.45 + .9 * (k % 6) / 5, release=.12)
        else:
            p.note("vln_harm", HI_B[(k // 2) % 3], 8.4 + .1 * k, .14, vel=.45, gain=.2, pan=.45 - .9 * (k % 6) / 5,
                   release=.25)
    p.note("vln_harm", 74, 11.4, 1.5, vel=.35, gain=.14, attack=.3, release=.8, bend=12.0, pan=-.3)   # поле
    for k in range(24):                                                                 # обереги по кольцу
        p.note("vln_harm", HIGH[k % 6], 12.6 + .1 * k, .45, vel=.4, gain=.26, pan=-.6 + 1.2 * k / 23, release=.4)
        if k % 6 == 0:
            p.note("crotales", CROT[(k // 6) % 6], 12.6 + .1 * k, 1.2, vel=.3, gain=.12, release=1.2)
    for m, inst in ((48, "vc_harm"), (55, "vla_harm")):
        p.note(inst, m, 9.0, 6.6, vel=.35, gain=.2, attack=2.0, release=1.2)

    # ================================================================ III СТЕНА (15–21): глифы вписываются точками
    tmax = max(q["t"] for q in cells)
    for k, q in enumerate(cells):
        if k % 6 or q["t"] > 21.0:
            continue
        m = WALL[min(q["r"], len(WALL) - 1)] - 12
        inst = "vla_pizz" if m >= 55 else "vc_pizz"
        p.note(inst, m, q["t"], .25, vel=.5, gain=.3, pan=.55 * q["side"], release=.4)
    for m, inst in ((36, "cb_sus"), (43, "vc_sus")):
        p.note(inst, m, 15.0, 6.4, vel=.4, gain=.32, attack=3.0, release=.6)
    p.note("vln_harm", 74, 15.0, 2.4, vel=.35, gain=.14, attack=.2, release=.6, bend=1.0, pan=-.3)    # свет бежит по шинам
    p.note("vln_harm", 74, 15.05, 2.4, vel=.35, gain=.14, attack=.2, release=.6, bend=1.0, pan=.3, detune=.25)

    # ================================================================ IV/VI СЕРДЦЕ ГРОБНИЦЫ (21–57.6)
    for k, tb in enumerate(hearts):
        steady = tb >= 28.8 - 1e-6
        v = .45 + .35 * min(1.0, (tb - 21) / 7.8) if not steady else .62
        if tb >= 57.6 - 1e-6:
            continue                                                                    # последний удар — приказ
        c.timp(tb, 0, vel=v)
        c.fx("bd_soft", tb, gain=.18 + .15 * v, bus="perc")
        p.note("cb_pizz", 36, tb, .4, vel=v, gain=.5, pan=-.15, release=.4)
        c.fx("bd_soft", tb + .22, gain=(.18 + .15 * v) * .45, bus="perc")                # второй, глухой

    # ================================================================ V ЗАЛ (28.8–31.2)
    for m, inst in ((36, "cb_sus"), (43, "vc_sus"), (56, "vla_sus")):
        p.note(inst, m, 28.8, 2.6, vel=.55, gain=.3, attack=2.2, release=.5)
    c.fx("gong_scrape", 28.9, gain=.22, bus="perc")

    # ================================================================ VI ЛЕГИОН (31.2–): квинтовый аккорд по рядам
    for rnum, r in sorted(rows.items(), key=lambda kv: kv[1]["wake"]):
        m = ROW_PITCH[rnum]
        a, b = row_inst(m)
        near = 1 - rnum / 12                                                            # ближние громче
        tw, td = r["wake"], r["depart"]
        ping = m
        while ping < 79:
            ping += 12
        p.note("vln_harm", min(ping, 100), tw, .5, vel=.45, gain=.12, release=.6, pan=rng.uniform(-.5, .5))
        if rnum >= 9:
            p.note("crotales", min(ping + 12, 108), tw, 1.0, vel=.35, gain=.1, release=1.0)
        p.note("vc_colleg", m if 36 <= m <= 76 else 48, tw, .1, vel=.5, gain=.2, release=.1)
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
    # минимализм: медленный узор флажолетов по двум цепям, каждый такт на звук длиннее
    t, n = 40.8, 2
    while t < 47.9:
        bar_end = t + 2.4
        k = 0
        while t < bar_end - 1e-6 and t < 47.9:
            p.note("vln_harm", HIGH[k % n], t, .55, vel=.35, gain=.12, pan=.4 - .8 * (k % 2), release=.4)
            t += .6
            k += 1
        n = min(6, n + 1)

    # ================================================================ VII ИМЯ (48–52.8): пять квинт меди
    for i, (m, inst) in enumerate(NAME):
        t0 = 48.0 + .9 * i
        p.note(inst, m, t0, 57.25 - t0, vel=.72, gain=.42, attack=.03, release=.12, pan=-.4 + .2 * i)
        p.note("tubular", [60, 67, 62, 68, 75][i], t0, 3.0, vel=.6, gain=.3, release=2.5)
    c.timp(48.0, 0, vel=.8)
    c.fx("tamtam", 51.6, gain=.3, bus="perc")

    # ================================================================ VIII ДАВЛЕНИЕ (52.8–57.3)
    star(52.8, scale=1.0, vel=.62, gain=.55, solo=True, bend=.6)
    for m in (76, 77, 82, 83):
        p.note("vln_trem", m, 52.9, 4.35, vel=.7, gain=.09, attack=4.2, release=.05, detune=.2)
    p.note("vln_harm", 86, 53.4, 3.85, vel=.5, gain=.15, attack=3.0, release=.05)
    p.note("vln_harm", 86, 53.4, 3.85, vel=.5, gain=.15, attack=3.0, release=.05, detune=.35)   # биения
    t, k = 54.45, 0
    while t < 57.2:                                                                     # цепь оберегов
        m = CROT[k % 6]
        p.note("crotales", m, t, .4, vel=.4 + .3 * (t - 54.45) / 2.8, gain=.11, pan=-.6 + 1.2 * (k % 7) / 6, release=.4)
        t += .15
        k += 1
    c.timp(55.5, 0, vel=.75, roll=1.75)
    c.fx("susp_scrape", 54.6, gain=.18, bus="perc", dur=2.6, fade=.05)
    # 57.25–57.6 — вдох (тишина)

    # ================================================================ IX ПРИКАЗ (57.6)
    for m, inst, g in ((24, "cbsn_sus", .5), (36, "tba_sus", .5), (36, "cb_sus", .45), (43, "tbn_sus", .45),
                       (49, "tbn_sus", .42), (56, "hn_sus", .42), (62, "hn_sus", .42), (63, "hn_sus", .36),
                       (67, "tpt_sus", .4), (68, "tpt_sus", .36), (74, "vln_sus", .32), (75, "vln_sus", .3)):
        p.note(inst, m, 57.6, 1.6, vel=1.0, gain=g * 1.4, attack=.01, release=1.4)
    c.timp(57.6, 0, vel=1.0)
    c.fx("tamtam", 57.6, gain=.45, bus="perc")
    c.fx("gong_hit", 57.6, gain=.3, bus="perc")
    c.fx("clash", 57.6, gain=.2, bus="perc")
    p.note("vln_harm", 88, 57.6, 2.0, vel=.6, gain=.16, release=1.5)
    p.note("afl_sus", 88, 57.65, 1.4, vel=.6, gain=.32, attack=.05, release=1.0)       # вспышка узника (E)

    # ================================================================ X УХОД (59.4–69.6): аккорд распадается снизу вверх
    for rnum, r in rows.items():
        m = ROW_PITCH[rnum]
        td = r["depart"]
        ping = m
        while ping < 84:
            ping += 12
        if rnum >= 6:
            p.note("crotales", min(ping, 108), td - .5, .5, vel=.5, gain=.2, reverse=True)
        else:
            tb_ = m
            while tb_ < 60:
                tb_ += 12
            p.note("tubular", min(tb_, 77), td - .6, .6, vel=.5, gain=.22, reverse=True)
        p.note("vln_harm", min(max(ping - 12, 67), 100), td, .15, vel=.4, gain=.08, release=.2)
    for k in range(18):                                                                  # боковые ряды — раньше
        tt = 59.4 + rng.uniform(0, 3.0)
        p.note("crotales", rng.choice(CROT), tt - .35, .35, vel=.3, gain=.05, reverse=True)

    # ================================================================ XI ВОЗВРАЩЕНИЕ В СОН (72–86.4)
    star(73.2, scale=1.6, vel=.35, gain=.4, rev=True)
    span = tmax - 15 + .833
    for k, q in enumerate(cells):                                                       # глифы стираются
        if k % 5:
            continue
        tu = 72 + 8.4 * (1 - (q["t"] - 15) / span)
        m = WALL[min(q["r"], len(WALL) - 1)] - 12
        p.note("vla_pizz" if m >= 55 else "vc_pizz", m, tu, .2, vel=.38, gain=.18, pan=.55 * q["side"], release=.3)
    p.note("cbsn_sus", 24, 70.0, 21.0, vel=.45, gain=.3, attack=3.0, release=2.0)
    for m, inst in ((36, "cb_sus"), (49, "vc_sus")):                                   # холодный низ под угасанием
        p.note(inst, m, 79.8, 7.0, vel=.4, gain=.22, attack=1.5, release=1.5)
    for m, inst in ((48, "vc_harm"), (55, "vla_harm")):                                  # пустой зал: чистая квинта
        p.note(inst, m, 69.2, 7.0, vel=.35, gain=.2, attack=1.5, release=1.5)
    c.swell(72.0, inst="crotales", midi_=97, dur=1.8, gain=.18)
    for k in range(24):                                                                 # обереги гаснут
        p.note("vln_harm", HIGH[(23 - k) % 6], 80.4 + .1 * k, .45, vel=.35, gain=.24, pan=.6 - 1.2 * k / 23, release=.4)
    p.note("vln_harm", 86, 82.2, 1.5, vel=.32, gain=.12, attack=.05, release=.6, bend=-12.0)   # поле
    for k in range(32):                                                                 # рёбра уходят
        kk = 31 - k
        if kk % 2 == 0:
            p.note("vln_colleg", MID[(kk // 2) % 3], 83.4 + .094 * k, .1, vel=.42 - .15 * k / 31, gain=.26, release=.12)
        else:
            p.note("vln_harm", HI_B[(kk // 2) % 3], 83.4 + .094 * k, .14, vel=.4, gain=.18, release=.25)
    p.note("vln_harm", 88, 86.4, 3.6, vel=.3, gain=.1, attack=.1, release=.6, pan=.2)    # точка-узник (E)

    # ================================================================ XII НОВЫЙ СОН (86.4–96)
    k, tt = 0, 86.4 + 1 / 3.7
    while tt < 92.3:
        fade = 1 - (tt - 86.4) / 6.0
        p.note("vln_colleg", 96 if k % 2 else 91, tt, .08, vel=.35, gain=.1 * fade + .02, pan=.3 - .6 * (k % 2), release=.12)
        tt += 1 / 3.7
        k += 1

    # баланс по замеру --parts (эскиз 0–60 с)
    p.balance({"Cellos": -10, "Contrabassoon": -10, "Trumpet": -8, "Horn": -1, "Violas": +1, "Tuba": +2,
               "Violins": +4, "Timpani": +8, "Violin solo": +6, "Basses": +10, "Trombone": +13, "Crotales": +11,
               "Tubular bells": +15})
    return p
