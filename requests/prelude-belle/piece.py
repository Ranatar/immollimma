#!/usr/bin/env python3
"""Prélude «Belle» — драматургия «Belle» (Кочанте), какой её написал бы Рахманинов (≈ 4:30).

Тема и схема — те же, что в «Nocturne à trois» (requests/nocturne-belle; мелодии, гармония и мелодия-движок берутся
оттуда): три куплета на малую терцию выше (d → f → gis), припев — терцией ниже куплета с выходом в одноимённый
мажор, общий припев-кульминация, кода. Каждому персонажу — фактура одной из прелюдий Рахманинова (по MIDI от
заказчика):

  Квазимодо   op. 23 № 4 (D-dur): мелодия над широкими триолями левой руки; во второй фразе мелодия уходит
              в альт, над ней — триоли правой руки, в басу — восьмые (3 против 2); внутренний голос сползает
              хроматически (d – cis – c – h) под стоящей мелодией
  Фролло      op. 32 № 10 (h-moll): колокола — два аккорда качаются в ритме «долго – коротко – триоль – долго»,
              на третью долю — низкий аккорд-удар; тема — в теноре октавами; медленно
  Фебюс       op. 32 № 12 (gis-moll): мерцание шестнадцатыми (основной тон – квинта – основной тон) в правой,
              долгая поступенная мелодия в левой; быстро
  трио        «точка» (слово Рахманинова): колокольная кульминация — полные аккорды обеих рук, тема наверху октавами,
              бас бьёт на каждую долю; затем обвал аккордов вниз
  кода        колокола pp внизу, обрывок темы Квазимодо, плагальный iv⁶ – i, d-moll

    python3 -m kit run requests/prelude-belle/piece.py --backend sso --parts
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
_spec = importlib.util.spec_from_file_location("nocturne_belle", os.path.join(HERE, "..", "nocturne-belle", "piece.py"))
NB = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(NB)

from kit.events import Piece  # noqa: E402

BPM = 58
SPB = NB.SPB
BAR = NB.BAR
chord, VERSE, REFR, LINK = NB.chord, NB.VERSE, NB.REFR, NB.LINK
hm, maj = NB.hm, NB.maj

# гармония по-рахманиновски: девятые у доминант, iv с секстой, «нисходящая линия» внутри минорных аккордов
VERSE_H = [["Dm"], ["A7"], ["Dm"], ["Gm6", "A7"], ["Dm"], ["Bb"], ["Gm6", "A7"], ["Dm"]]
VERSE_H_FROLLO = [["Dm"], ["A7"], ["Dm"], ["Gm6", "A7"], ["Dm"], ["Bb7"], ["Em7b5", "A7"], ["Dm"]]
REFR_H = [["Bm"], ["Em7"], ["F#7"], ["Bm"], ["G"], ["A7"]]
LINK_H = [["D"], ["C7"]]


class Prel(NB.Noct):
    def __init__(self):
        super().__init__()
        self.p = Piece("Prélude «Belle»", bpm=BPM, meter=(4, 4), key="D minor", seed=1910)
        self.p.meta["subtitle"] = "«Belle», как написал бы Рахманинов"
        self.p.meta["sends"] = {"keys": 0.45}

    # ---------------------------------------------------------------- op. 23 № 4: широкие триоли
    def triplets(self, bar, harms, k, vel=0.28, part="Piano LH", lo=None, hi=None):
        """бас на сильную долю и широкая ломаная триолями вверх-вниз (на две доли — шесть нот)"""
        b0 = bar * BAR
        span = BAR / len(harms)
        for i, h in enumerate(harms):
            t = b0 + i * span
            self.ped(t)
            pcs = chord(h, k)[0]
            if lo is None:
                bs = self.bass_of(h, k)
                up = [x for x in range(bs + 7, bs + 32) if x % 12 in pcs][:4]
                fig = [bs] + up + up[-2:0:-1]
            else:  # фигурация правой руки над мелодией (вторая фраза)
                up = [x for x in range(lo, hi + 1) if x % 12 in pcs][:3]
                fig = up + up[-2:0:-1]
            for j in range(int(span * 3)):
                m = fig[j % len(fig)]
                self.note(m, t + j / 3, 1 / 3, vel + (0.06 if j == 0 and lo is None else 0) - 0.01 * (j % 3), part)

    def duplets(self, bar, harms, k, vel=0.26):
        """бас восьмыми (3 против 2 с триолями правой): бас – квинта – терция-децима – квинта"""
        b0 = bar * BAR
        span = BAR / len(harms)
        for i, h in enumerate(harms):
            t = b0 + i * span
            self.ped(t)
            pcs, b = chord(h, k)
            bs = self.bass_of(h, k)
            up = [x for x in range(bs + 7, bs + 24) if x % 12 in pcs][:3]
            fig = [bs] + up
            for j in range(int(span * 2)):
                self.note(fig[j % len(fig)], t + j / 2, 0.5, vel + (0.06 if j == 0 else 0), "Piano LH")

    def cliche(self, bar, harms, k, lo=55, hi=67, vel=0.3):
        """внутренний голос под мелодией: в минорном аккорде основной тон сползает по полутону каждую долю
        (d – cis – c – h), в остальных — держится ближайший звук аккорда"""
        b0 = bar * BAR
        span = BAR / len(harms)
        for i, h in enumerate(harms):
            pcs, bs = chord(h, k)
            root_m = h.split("/")[0]
            t = b0 + i * span
            if root_m.endswith("m") and span >= 2:
                r = next(x for x in range(hi, lo - 1, -1) if x % 12 == (NB.NAMES[h[0]] + k + (-1 if h[1:2] == "b" else 1 if h[1:2] == "#" else 0)) % 12)
                for j in range(int(span)):
                    self.note(r - j, t + j, 1, vel, "Piano RH")
            else:
                prev = self.prev.get("cliche", (lo + hi) // 2)
                m = min((x for x in range(lo, hi + 1) if x % 12 in pcs), key=lambda x: abs(x - prev))
                self.prev["cliche"] = m
                self.note(m, t, span, vel, "Piano RH")

    # ---------------------------------------------------------------- op. 32 № 10: колокола
    def bells(self, bar, harms, k, vel=0.42, lo=62, hi=80, low=True, rock=True):
        """два аккорда качаются в ритме «долго – коротко – триоль – долго» (0, ½, ⅔, 1), на третью долю —
        низкий аккорд-удар, который держится; второй аккорд — соседний (квартсекстаккорд субдоминанты сверху)"""
        b0 = bar * BAR
        h = harms[0]
        pcs, bs = chord(h, k)
        a = self.voicing(h, k, lo, hi, "bellA", 4)
        # соседний аккорд: верхние голоса поднимаются к ближайшим звукам аккорда на кварту выше (IV⁶₄ над тем же басом)
        nb = {(x + 5) % 12 for x in pcs}
        b = [min((y for y in range(x, x + 4) if y % 12 in nb), default=x) for x in a] if rock else a
        self.ped(b0)
        for t, d, v in ((0, .5, a), (.5, 1 / 6, b), (2 / 3, 1 / 3, a), (1, 1, b)):
            for m in v:
                self.note(m, b0 + t, d, vel + (0.05 if t == 0 else 0), "Piano RH")
        last = harms[-1]
        self.ped(b0 + 2)
        if low:
            pcs2, b2 = chord(last, k)
            bass = next(x for x in range(28, 40) if x % 12 == b2)
            low_ch = [bass, bass + 7, bass + 12] + [x for x in range(bass + 13, bass + 26) if x % 12 in pcs2][:2]
            for m in low_ch:
                self.note(m, b0 + 2, 2, vel + 0.08, "Piano LH")
        for m in self.voicing(last, k, lo, hi, "bellC", 4):
            self.note(m, b0 + 2, 2, vel - 0.05, "Piano RH")

    # ---------------------------------------------------------------- op. 32 № 12: мерцание
    def flicker(self, bar, harms, k, vel=0.3, lo=68, hi=82):
        """шестнадцатые: основной тон сверху – квинта – основной тон снизу – квинта, с вариантами по долям"""
        b0 = bar * BAR
        span = BAR / len(harms)
        pats = [(2, 1, 0, 1), (2, 1, 2, 1), (0, 1, 2, 1), (2, 1, 0, 1)]
        for i, h in enumerate(harms):
            t = b0 + i * span
            self.ped(t)
            pcs, bs = chord(h, k)
            root = [x for x in range(lo, hi + 1) if x % 12 == next(iter(sorted(pcs, key=lambda p: (p - bs) % 12)))]
            r1 = root[0] if root else lo
            r2 = r1 + 12 if r1 + 12 <= hi + 6 else r1
            fifth = min((x for x in range(r1 + 1, r2) if x % 12 in pcs and (x - r1) % 12 in (6, 7)), default=r1 + 7)
            tones = (r1, fifth, r2)
            for q in range(int(span)):
                pat = pats[(i * int(span) + q) % 4]
                for j, s_ in enumerate(pat):
                    self.note(tones[s_], t + q + j / 4, 0.25, vel + (0.04 if j == 0 else 0), "Piano RH")


# ===================================================================== строфы
def nxt_of(seq, i, after=None):
    return seq[i + 1][0][2] if i + 1 < len(seq) and seq[i + 1] else after


def strophe_quasimodo(o, bar):
    """op. 23 № 4: первая фраза — мелодия над триолями, внутренний голос сползает; вторая — мелодия в альте,
    триоли сверху, в басу восьмые (3 : 2); припев — мелодия наверху октавами над триолями"""
    for i in range(8):
        if i < 4:
            o.triplets(bar + i, VERSE_H[i], 0, vel=0.27)
            o.melody(bar + i, VERSE[i], 0, vel=0.46 + 0.03 * (i == 2), sc=hm(2))
            o.cliche(bar + i, VERSE_H[i], 0)
        else:
            o.duplets(bar + i, VERSE_H[i], 0, vel=0.26)
            o.triplets(bar + i, VERSE_H[i], 0, vel=0.24, part="Piano RH", lo=74, hi=86)
            o.melody(bar + i, VERSE[i], 0, vel=0.52, sc=hm(2))
    for i in range(6):
        o.triplets(bar + 8 + i, REFR_H[i], 0, vel=0.3)
        o.melody(bar + 8 + i, REFR[i], 0, vel=0.56 + 0.02 * i, double=True, sc=NB.refr_scale(i, 0))
    return bar + 14


def link(o, bar, k, vel=0.45, texture="triplets"):
    for i in range(2):
        if texture == "triplets":
            o.triplets(bar + i, LINK_H[i], k, vel=0.27)
        else:
            o.bells(bar + i, LINK_H[i], k, vel=0.36)
        o.melody(bar + i, LINK[i], k, vel=vel)
    return bar + 2


def strophe_frollo(o, bar):
    """op. 32 № 10: колокола в правой, тема в теноре октавами, низкий удар на третью долю; припев — колокола
    громче, тема наверху октавами"""
    k = 3
    for i in range(8):
        o.bells(bar + i, VERSE_H_FROLLO[i], k, vel=0.36 + 0.02 * (i in (4, 5, 6)), lo=64, hi=79)
        o.melody(bar + i, VERSE[i], k, part="Piano LH", vel=0.56, oct=-12, double=True)
    for i in range(6):
        o.bells(bar + 8 + i, REFR_H[i], k, vel=0.46, lo=60, hi=74)
        o.melody(bar + 8 + i, REFR[i], k, vel=0.7 + 0.01 * i, oct=12, double=True)
    return bar + 14


def strophe_phoebus(o, bar):
    """op. 32 № 12: мерцание шестнадцатыми в правой, долгая мелодия в левой (тенор); бас на смену гармонии"""
    k = 6
    for i in range(8):
        o.flicker(bar + i, VERSE_H[i], k, vel=0.27, lo=68, hi=82)
        o.melody(bar + i, VERSE[i], k, part="Piano LH", vel=0.52, oct=-12)
        for j, h in enumerate(VERSE_H[i]):
            o.note(o.bass_of(h, k, 30, 42), (bar + i) * BAR + j * BAR / len(VERSE_H[i]), BAR / len(VERSE_H[i]),
                   0.36, "Piano LH")
    for i in range(6):
        o.flicker(bar + 8 + i, REFR_H[i], k, vel=0.3, lo=72, hi=86)
        o.melody(bar + 8 + i, REFR[i], k, part="Piano LH", vel=0.58 + 0.01 * i, oct=-12, double=True)
    return bar + 14


def trio(o, bar):
    """«точка»: припев в f-moll — полные колокола обеих рук, тема наверху октавами, бас бьёт каждую долю;
    затем обвал: аккорды вниз восьмыми через три октавы на C7"""
    k = 6
    harms = REFR_H[:5] + [["G", "F#7"]]  # (+6) → Des | C7
    for i in range(6):
        o.bells(bar + i, harms[i], k, vel=0.56 + 0.02 * i, lo=64, hi=80, low=False, rock=False)
        o.melody(bar + i, REFR[i] if i < 5 else [(0, 2, 71), (2, 2, 70)], k, vel=0.8, double=True)
        for j, h in enumerate(harms[i]):
            span = BAR / len(harms[i])
            bs = o.bass_of(h, k, 29, 41)
            for q in range(int(span)):
                for m in (bs, bs + 12):
                    o.note(m, (bar + i) * BAR + j * span + q, 1, 0.62 + (0.05 if q == 0 else 0), "Piano LH")
    # обвал: C7 аккордами восьмыми вниз, с ферматой на нижнем
    t = (bar + 6) * BAR
    o.ped(t)
    tones = sorted(x for x in range(40, 90) if x % 12 in (0, 4, 7, 10))
    for j in range(12):
        top = tones[-1 - j * 2] if len(tones) > 1 + j * 2 else tones[0]
        ch = [x for x in tones if top - 12 <= x <= top][-4:]
        for m in ch:
            o.note(m, t + j / 2, 0.5, 0.7 - 0.025 * j, "Piano RH" if m >= 60 else "Piano LH")
    for m in (24, 36, 43, 46, 52):
        o.note(m, t + 6, 2, 0.45, "Piano LH")
    return bar + 8


def coda(o, bar):
    """колокола pp внизу; обрывок темы Квазимодо в альте; плагальный iv⁶ – i; d-moll"""
    o.bells(bar, ["Dm"], 0, vel=0.38, lo=50, hi=65)
    o.melody(bar, VERSE[0], 0, vel=0.48)
    o.bells(bar + 1, ["A7"], 0, vel=0.36, lo=50, hi=65)
    o.melody(bar + 1, VERSE[1], 0, vel=0.44)
    o.bells(bar + 2, ["Gm6"], 0, vel=0.34, lo=50, hi=65)
    o.melody(bar + 2, [(0, 2, 70), (2, 2, 64)], 0, vel=0.42)
    o.bells(bar + 3, ["Dm"], 0, vel=0.32, lo=50, hi=65)
    o.melody(bar + 3, [(0, 4, 62)], 0, vel=0.4)
    t = (bar + 4) * BAR
    o.ped(t)
    for m in (26, 38, 43, 46, 52, 55, 58, 62):  # iv⁶ над тоникой (g – b – d – e над D)
        o.note(m, t, 2, 0.42, "Piano LH" if m < 60 else "Piano RH")
    t2 = t + 2
    o.ped(t2)
    for j, m in enumerate((26, 38, 45, 50, 53, 57, 62)):  # d-moll, арпеджато снизу
        o.note(m, t2, 8, 0.4, "Piano LH" if m < 60 else "Piano RH", late=0.05 * j)
    return bar + 6.5


def build(ctx):
    o = Prel()
    plan = [(0, "Вступление"), (2, "I. Квазимодо: d-moll (op. 23 № 4)"), (10, "припев: h → D"), (16, "Связка"),
            (18, "II. Фролло: f-moll (op. 32 № 10)"), (26, "припев: d → F"), (32, "Связка"),
            (34, "III. Фебюс: gis-moll (op. 32 № 12)"), (42, "припев: f → As"), (48, "«Точка»: f-moll"),
            (54, "Обвал"), (56, "Кода: d-moll")]
    # темп по разделам (множитель длительности): Фролло — lento, Фебюс — allegro, «точка» — maestoso, кода — lento
    o.slow += [(2 * BAR, 16 * BAR, 1.0, 1.0), (18 * BAR, 32 * BAR, 1.3, 1.3), (34 * BAR, 48 * BAR, 0.62, 0.62),
               (48 * BAR, 54 * BAR, 1.12, 1.12), (54 * BAR, 56 * BAR, 1.15, 1.8), (56 * BAR, 60 * BAR, 1.35, 1.5),
               (60 * BAR, 62.5 * BAR, 1.6, 2.0)]
    for bb in (5, 9, 15, 25, 31, 47):  # концы фраз оттянуты
        o.slow.append((bb * BAR + 2.0, bb * BAR + 4 - 1e-3, 1.0, 1.3))
    o.p.meta["keys"] = [[b_ * BAR * SPB, k_] for b_, k_ in
                        ((10, "B minor"), (18, "F minor"), (26, "D minor"), (34, "G-sharp minor"), (42, "F minor"),
                         (56, "D minor"))]
    o.p.meta["notation_divisors"] = [[8, 3], [4, 3], [4]]
    o.triplets(0, ["Dm"], 0, vel=0.25)
    o.triplets(1, ["A7"], 0, vel=0.25)
    b = strophe_quasimodo(o, 2)
    b = link(o, b, 0)
    b = strophe_frollo(o, b)
    b = link(o, b, 3, vel=0.6, texture="bells")
    b = strophe_phoebus(o, b)
    b = trio(o, b)
    end = coda(o, b)
    for bt, label in plan:
        o.p.mark(o.perf(bt * BAR), label)["wt"] = bt * BAR * SPB
    o.apply_pedal(o.perf(end * BAR) + 2)
    o.p.meta["beats"] = end * BAR
    return o.p
