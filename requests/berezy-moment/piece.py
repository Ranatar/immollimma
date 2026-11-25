#!/usr/bin/env python3
"""Moment musical «18 берёз» — драматургия песни «18 берёз» (Чиж & Co), в стиле и гармонии третьего
«Музыкального момента» Рахманинова (op. 16 № 3, h-moll). Фортепиано соло, ≈ 4:50. Вторая редакция (2026-11-25):
первая была «рахманиновским скелетом» — квадратная тема, гармония по тактам, один шаблон аккомпанемента; и
последний куплет звучал тихо, а в песне он почти на крике.

Из песни — только драматургия и форма (мелодия Чижа не цитируется). Тема — своя: 10 тактов (4 + 6), псалмодическое
начало на повторяемом фа#, вторая фраза той же интонацией терцией выше (D-dur), хроматический бас c – h – b
(D7/C – G/B – Gm6/B♭), вершина e³ на уменьшённом, задержание sus4 → доминанта. Гармония по полутактам и долям:
Bm – Bm/A – A7 | E7/G# – Gmaj7 | Em7 – F#7 | … Голоса: мелодия с терцией/секстой, тенор-подголосок большим
пальцем левой (движется, где мелодия стоит), бас с октавой; во II куплете — мелодия октавами и широкие триоли
левой (бас – квинта – децима); в рефрене — альт децимами над басом-ламенто. Из Рахманинова — и одна настоящая
цитата: такты 1–3 op. 16 № 3 «из динамика» (Ван Клиберн) — через полосу частот старого репродуктора.

  Рассвет          ломаные аккорды Bm(add9) – Gmaj7 – Em9 – F#7 снизу вверх
  I куплет         тема с терциями, тенор, бас
  «не спится»      вздох-задержание над басом-ламенто h – ais – a – gis – g – fis, альт децимами, триоли
  II куплет        мелодия октавами, триоли; посредине — из динамика сам Рахманинов; вторая фраза;
                   «пацифистский значок» — чистый до-мажор высоко, чужой
  «не спится»      вздох дважды в такте, в сексту, бас в октавах
  «Поезд»          октавы левой восьмыми (колёса) с разгоном; «поезд» ×4; «знаю» ×3; «ну и что?» — фермата на A7;
                   «надо быть вместе» — вторая фраза темы в D-dur октавами, f; g-moll → Fis7 → октавы вниз с
                   нарастанием — прямо в крик
  III куплет       почти крик, ff: мелодия октавами в полных аккордах, бас октавами на каждую долю — восемнадцать
                   ударов подряд, и счёт обрывается; северный ветер — хроматические спуски; «последний патрон» —
                   цезура и один сухой удар внизу
  «не спится»      вздох расплывается: сбит с долей, тянется, рояль понемногу расстраивается
  Рассвет-кода     ломаные аккорды вверх; уменьшённое над ми → Fis7 → пустая квинта h, ppp (жест самого op. 16 № 3)

    python3 -m kit run requests/berezy-moment/piece.py --parts
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

BPM = NB.BPM        # 58 — у Рахманинова ♩ = 56
SPB = NB.SPB
BAR = NB.BAR
chord = NB.chord

H_NAT = {11, 1, 2, 4, 6, 7, 9}          # h-moll натуральный
H_HARM = {11, 1, 2, 4, 6, 7, 10}        # гармонический (ais)
D_MAJ = {2, 4, 6, 7, 9, 11, 1}

NB.QUAL.update({"maj7": (0, 4, 7, 11), "7sus4": (0, 5, 7, 10), "9": (0, 4, 7, 10, 2), "m9": (0, 3, 7, 10, 2),
                "madd9": (0, 3, 7, 2), "7b9": (0, 4, 7, 10, 1)})

# ===================================================================== тема (своя), h-moll, 10 тактов (4 + 6)
# Псалмодическое начало на повторяемом фа# с соседним соль; вторая фраза — та же интонация терцией выше (D-dur),
# хроматический спуск баса c – h – b (D7/C – G/B – Gm6/B♭: мажор темнеет одноимённым минором), вершина e³
# на уменьшённом, задержание sus4 → доминанта, каданс. Гармония по полутактам (а где надо — по долям).
THEME = [
    [(0, 1, 78), (1, .5, 78), (1.5, .5, 79), (2, 1, 78), (3, .5, 76), (3.5, .5, 74)],
    [(0, 1.5, 76), (1.5, .5, 78), (2, 1, 79), (3, 1, 78)],
    [(0, 1, 76), (1, 1, 74), (2, 1, 73), (3, 1, 70)],
    [(0, 1.5, 71), (1.5, .5, 73), (2, 1, 74), (3, 1, 76)],
    [(0, 1, 81), (1, .5, 81), (1.5, .5, 83), (2, 1, 81), (3, 1, 78)],
    [(0, 1.5, 79), (1.5, .5, 81), (2, 1, 82), (3, 1, 79)],
    [(0, 1, 83), (1, 1, 88), (2, 1.5, 85), (3.5, .5, 82)],
    [(0, 1, 83), (1, 1, 82), (2, .5, 85), (2.5, .5, 83), (3, 1, 82)],
    [(0, 1.5, 78), (1.5, .5, 76), (2, 1, 74), (3, 1, 73)],
    [(0, 3, 71)],
]
THEME_H = [
    [(0, "Bm"), (2, "Bm/A"), (3, "A7")],
    [(0, "E7/G#"), (2, "Gmaj7")],
    [(0, "Em7"), (2, "F#7")],
    [(0, "Bm"), (3, "A7")],
    [(0, "D"), (2, "D7/C")],
    [(0, "G/B"), (2, "Gm6/Bb")],
    [(0, "Em/G"), (2, "A#dim7")],
    [(0, "F#7sus4"), (1, "F#7")],
    [(0, "Bm"), (2, "G"), (3, "F#7")],
    [(0, "Bm")],
]
# «не спится»: бас-ламенто по полутонам, над ним вздох; альт идёт за басом децимами (D – Cis – C – H – B – Ais)
LAMENT = [("Bm", 35, 74), ("F#7/A#", 34, 73), ("D7/A", 33, 72), ("E7/G#", 32, 71), ("Gm", 31, 70), ("F#7", 30, 70)]
SIGH = {"E7/G#": (78, 76), "Gm": (81, 79)}  # иначе соль → фа#


def harm_at(hl, beat):
    return [h for b, h in hl if b <= beat + 1e-9][-1]


def spans(hl):
    out = []
    for k, (b, h) in enumerate(hl):
        e = hl[k + 1][0] if k + 1 < len(hl) else 4
        out.append((b, e - b, h))
    return out


def scale_of(h, base=None):
    """лад под аккорд: звуки аккорда вытесняют свои «неальтерированные» соседи (E7 — gis вместо g, F#7 — ais)"""
    pcs = chord(h)[0]
    base = set(base if base is not None else H_NAT)
    for x in pcs:
        if x not in base:  # повышенная ступень (gis, ais, dis) вытесняет свою натуральную
            base.discard((x - 1) % 12)
            base.add(x)
    return base


def step(m, sc, d):
    x = m + d
    while x % 12 not in sc:
        x += d
    return x


class Moment(NB.Noct):
    def __init__(self):
        super().__init__()
        self.p = Piece("Moment musical «18 берёз»", bpm=BPM, meter=(4, 4), key="B minor", seed=1896)
        self.p.meta["subtitle"] = "драматургия «18 берёз» (Чиж & Co) — в духе op. 16 № 3 Рахманинова"
        self.p.meta["sends"] = {"keys": 0.42, "radio": 0.18}
        self.p.meta["gains"] = {"radio": 6.0}  # полоса репродуктора съедает низ — поднять шину целиком
        self.detune = 0.0
        self.harm_log = []  # (доля, аккорд) — для проверки созвучий на долях

    def H(self, beat, name):
        self.harm_log.append((beat, name))

    def note(self, m, beat, dur, vel, part, late=0.0, wdur=None):
        e = super().note(m, beat, dur, vel + 0.08, part, late=late, wdur=wdur)
        if self.detune:  # расстроенный рояль: каждая нота — на свою долю «мимо»
            e["detune"] = self.detune * (self.rng.random() * 2 - 1)
        return e

    def hand(self, m):
        return "Piano RH" if m >= 60 else "Piano LH"

    # ---------------------------------------------------------------- мелодия и её голоса
    def melody(self, bar, notes, hl, vel=0.5, octave=False, inner=1, inner_vel=-0.12, top_gap=3):
        """мелодия; под ней inner голосов: на аккордовом звуке — аккордовые звуки ниже (терция/секста первыми),
        на проходящем — параллельно по ладу; octave — мелодия ещё и октавой ниже (кульминации)"""
        b0 = bar * BAR
        for b, d, m in notes:
            h = harm_at(hl, b)
            pcs = chord(h)[0]
            sc = scale_of(h)
            late = 0.03 if b == 0 else 0.0
            accent = 0.04 if d >= 1.5 else 0.0
            self.note(m, b0 + b, d, vel + accent, "Piano RH", late=late)
            if octave:
                self.note(m - 12, b0 + b, d, vel - 0.06, "Piano RH", late=late)
            lo_bound = m - 12 if octave else m - 10
            if m % 12 in pcs:
                below = [x for x in range(m - top_gap, lo_bound, -1) if x % 12 in pcs and x % 12 != m % 12]
            else:
                x = step(step(m, sc, -1), sc, -1)
                below = [x] + [y for y in range(x - 3, lo_bound, -1) if y % 12 in sc and y % 12 != x % 12][:1]
            for x in below[:inner]:
                self.note(x, b0 + b, d, vel + inner_vel, "Piano RH", late=late)

    def bass(self, bar, hl, vel=0.44, octave=True, lo=28):
        """бас по смене гармонии: слэш-бас или основной тон, с октавой"""
        b0 = bar * BAR
        out = []
        for b, d, h in spans(hl):
            pcs, bp = chord(h)
            self.ped(b0 + b)
            self.H(b0 + b, h)
            x = next(y for y in range(lo, lo + 12) if y % 12 == bp)
            self.note(x, b0 + b, d, vel, "Piano LH")
            if octave:
                self.note(x + 12, b0 + b, d, vel - 0.06, "Piano LH")
            out.append((b0 + b, d, x))
        return out

    def tenor(self, bar, hl, notes, vel=0.34, lo=50, hi=62):
        """тенор-подголосок большим пальцем левой: на долях — аккордовые звуки, плавно, против движения мелодии;
        где мелодия держит долгий звук — тенор движется восьмыми (проходящие по ладу), где мелодия идёт — стоит"""
        b0 = bar * BAR
        prev = self.prev.get("tenor", 56)
        busy = {int(b) for b, d, m in notes if d < 1 or b % 1}
        t = 0
        while t < 4:
            h = harm_at(hl, t)
            pcs = chord(h)[0]
            mel = [m for b, d, m in notes if b <= t + 1e-9 < b + d]
            cands = [x for x in range(lo, hi + 1) if x % 12 in pcs
                     and all(abs(x - y) % 12 not in (1, 2, 11) for y in mel) and (not mel or x < min(mel) - 4)]
            if not cands:
                t += 1
                continue
            x = min(cands, key=lambda y: (abs(y - prev) if y != prev else 2.5, y))
            moving = int(t) not in busy and t + 1 < 4
            if moving:
                nxt_h = harm_at(hl, t + 1)
                npcs = chord(nxt_h)[0]
                n_c = [y for y in range(lo, hi + 1) if y % 12 in npcs and y != x]
                nx = min(n_c, key=lambda y: abs(y - x)) if n_c else x
                sc = scale_of(h)
                mid = [y for y in range(min(x, nx) + 1, max(x, nx)) if y % 12 in sc]
                self.note(x, b0 + t, 0.5, vel, "Piano LH")
                if mid:
                    self.note(mid[0] if nx > x else mid[-1], b0 + t + 0.5, 0.5, vel - 0.04, "Piano LH")
                else:
                    self.note(x, b0 + t + 0.5, 0.5, vel - 0.06, "Piano LH")
            else:
                self.note(x, b0 + t, 1, vel, "Piano LH")
            prev = x
            t += 1
        self.prev["tenor"] = prev

    def triplets(self, bar, hl, vel=0.36, lo=28, span10=True):
        """левая рука триолями восьмых на каждую долю: бас – квинта – дециму (широко, по-рахманиновски)"""
        b0 = bar * BAR
        for b, d, h in spans(hl):
            pcs, bp = chord(h)
            self.ped(b0 + b)
            self.H(b0 + b, h)
            x = next(y for y in range(lo, lo + 12) if y % 12 == bp)
            fifth = next((y for y in range(x + 5, x + 9) if y % 12 in pcs), x + 12)
            tenth = next((y for y in range(x + 14, x + 18) if y % 12 in pcs), x + 12)
            up = next((y for y in range(tenth + 2, tenth + 6) if y % 12 in pcs), tenth)
            pat = [x, fifth, tenth] if span10 else [x, fifth, x + 12]
            for k in range(int(d)):
                fig = pat if k % 2 == 0 else [fifth, tenth, up]
                if k == 0:
                    fig = pat
                for j, m in enumerate(fig):
                    self.note(m, b0 + b + k + j / 3, 1 / 3 if j else 1, vel + (0.05 if j == 0 else -0.04), "Piano LH")

    # ---------------------------------------------------------------- «не спится»
    def sleepless(self, bar, vel=0.5, twice=False, blur=0.0, octave_bass=False):
        """вздох-задержание над басом-ламенто (h – ais – a – gis – g – fis; последние четыре — по полтакта), альт
        децимами над басом, левая — триолями; twice — вздох дважды в такте; blur — сбит с долей и тянется"""
        layout = [(0, 0, 4), (1, 0, 4), (2, 0, 2), (2, 2, 2), (3, 0, 2), (3, 2, 2)]
        for k, ((h, bass, alto), (bb, off, dur)) in enumerate(zip(LAMENT, layout)):
            t = (bar + bb) * BAR + off
            self.ped(t)
            self.H(t, h)
            pcs = chord(h)[0]
            self.note(bass, t, dur, vel + 0.04, "Piano LH")
            if octave_bass:
                self.note(bass - 12, t, dur, vel, "Piano LH")
            fifth = next(y for y in range(bass + 5, bass + 9) if y % 12 in pcs)
            tenth = next((y for y in range(bass + 14, bass + 18) if y % 12 in pcs), bass + 12)
            for kk in range(dur):
                for j, m in enumerate((fifth, tenth, fifth) if kk % 2 else (bass + 12, fifth, tenth)):
                    if kk == 0 and j == 0:
                        continue
                    self.note(m, t + kk + j / 3, 1 / 3, vel - 0.12, "Piano LH")
            hi_, res = SIGH.get(h, (79, 78))
            self.note(alto, t + 0.5, dur - 0.5, vel - 0.06, "Piano RH")   # альт децимами — вступает после удара
            reps = (0, 2) if twice and dur >= 4 else (0,)
            for j, r in enumerate(reps):
                shift, stretch = 0.0, 1.0
                if blur:
                    shift = blur * (0.25 + 0.3 * ((k * 2 + j) % 3))
                    stretch = 1 + blur * 0.6 * (k + 1) / len(LAMENT)
                d1 = min(1.0 * stretch, 1.5)
                d2 = min(1.0, max(0.5, (2 if (twice and dur >= 4) else dur) - shift - d1 - 0.05))
                self.note(hi_, t + r + shift, d1, vel + 0.08, "Piano RH")
                self.note(res, t + r + shift + d1, d2, vel, "Piano RH")
                if twice:  # вздох в сексту: под ним — второй голос
                    lo2 = next(y for y in range(res - 3, res - 10, -1) if y % 12 in pcs and y != alto)
                    self.note(lo2, t + r + shift + d1, d2, vel - 0.1, "Piano RH")

    # ---------------------------------------------------------------- «поезд»
    def wheels(self, bar, harm, vel=0.42, n=8):
        """октавы левой руки восьмыми по ладу: вверх от основного тона и назад, как в середине op. 16 № 3"""
        b0 = bar * BAR
        self.H(b0, harm)
        pcs, bp = chord(harm)
        sc = scale_of(harm, D_MAJ if harm in ("D", "D/F#", "G", "A7") else H_NAT)
        x = next(y for y in range(30, 43) if y % 12 == bp)
        cts = [y for y in range(x, x + 13) if y % 12 in pcs][:4]          # на долях — звуки аккорда,
        up = []
        for a, c in zip(cts, cts[1:]):                                     # между ними — проходящие по ладу
            mid = [y for y in range(a + 1, c) if y % 12 in sc]
            up += [a, mid[len(mid) // 2] if mid else a]
        path = up + [cts[-1]] + up[::-1][:-1]
        for j in range(n):
            m = path[j % len(path)]
            if j % 2 == 0 or m % 12 in pcs:  # на долях и полудолях-аккордовых — как есть; проходящие слабее
                v = vel + (0.06 if j == 0 else 0)
            else:
                v = vel - 0.06
            self.note(m, b0 + j / 2, 0.5, v, "Piano LH")
            self.note(m + 12, b0 + j / 2, 0.5, v - 0.05, "Piano LH")
        self.ped(b0)

    def train_call(self, bar, harm, vel=0.5, top=None):
        """«поезд, поезд, поезд…» — один и тот же аккорд пятью восьмыми, затем вдох"""
        b0 = bar * BAR
        pcs = chord(harm)[0]
        top = top or next(x for x in range(74, 86) if x % 12 in pcs)
        v3 = [x for x in range(top - 9, top + 1) if x % 12 in pcs][-3:]
        for j in range(5):
            for m in v3:
                self.note(m, b0 + j / 2, 0.4, vel + (0.08 if j == 0 else 0) + 0.01 * j, "Piano RH")
        return v3[-1]

    def know(self, bar, harm, start, vel=0.5):
        """«знаю, знаю, знаю» — мотив из трёх звуков вверх, терциями"""
        b0 = bar * BAR
        pcs = chord(harm)[0]
        sc = scale_of(harm, D_MAJ if harm in ("D", "G", "A7") else H_NAT)
        a = next(x for x in range(start, start + 5) if x % 12 in pcs)   # мотив опирается на аккордовые звуки
        b = step(a, sc, 1)
        c = next(x for x in range(b + 1, b + 5) if x % 12 in pcs)
        for k, (t, d, m) in enumerate(((0, .5, a), (.5, .5, b), (1, 1, c), (2, .5, a), (2.5, .5, b), (3, 1, c))):
            if m % 12 in pcs:
                lo = next(y for y in range(m - 3, m - 6, -1) if y % 12 in pcs)
            else:
                lo = step(step(m, sc, -1), sc, -1)
            for x in (m, lo):
                self.note(x, b0 + t, d, vel + 0.03 * k, "Piano RH")
        return c

    # ---------------------------------------------------------------- цитата «из динамика»
    def radio(self, bar, quote, beats=11, vel_scale=1.0):
        """начало op. 16 № 3, как есть, — через отдельную шину «radio» (полоса репродуктора, шорох, треск)"""
        t0 = bar * BAR
        for b, d, m, v in quote:
            if b >= beats:
                continue
            t = self.perf(t0 + b)
            e = self.p.note("piano", m, t, max(0.05, self.perf(t0 + b + d) - t), vel=max(0.1, v * vel_scale),
                            gain=0.5, release=0.4, pan=0.0, bus="radio", part="Piano (из динамика)")
            e["wt"], e["wdur"] = (t0 + b) * SPB, d * SPB
            e["notate"] = False
        return t0 + beats


QUOTE = [  # op. 16 № 3, такты 1–3 (общественное достояние): (доля, длит., midi)
    (0, 0.748, 59), (0, 0.748, 62), (0, 0.948, 35), (0, 0.948, 42), (0, 0.948, 47), (0, 0.998, 50),
    (0, 0.998, 54), (0.75, 0.248, 58), (0.75, 0.248, 61), (1, 0.998, 59), (1, 0.998, 62), (1, 1.898, 40),
    (1, 1.898, 47), (1, 1.998, 55), (2, 0.948, 61), (2, 0.948, 64), (4, 0.748, 59), (4, 0.748, 62),
    (4, 0.948, 35), (4, 0.948, 42), (4, 0.948, 47), (4, 0.998, 50), (4, 0.998, 54), (4.75, 0.248, 58),
    (4.75, 0.248, 61), (5, 0.331, 59), (5, 0.331, 62), (5, 1.898, 40), (5, 1.898, 47), (5, 1.998, 55),
    (5.333, 0.331, 58), (5.333, 0.331, 61), (5.667, 0.331, 59), (5.667, 0.331, 62), (6, 0.948, 61), (6, 0.948, 64),
    (8, 0.331, 59), (8, 0.331, 62), (8, 0.948, 35), (8, 0.948, 42), (8, 0.948, 47), (8, 0.998, 54),
    (8.333, 0.331, 61), (8.333, 0.331, 64), (8.667, 0.331, 62), (8.667, 0.331, 66), (9, 1.898, 28), (9, 1.898, 40),
    (9, 1.898, 55), (9, 1.898, 59), (9, 1.898, 62), (9, 1.998, 66), (9, 1.998, 69),
]


# ===================================================================== разделы
def dawn(o, bar, n=4, vel=0.26, end_chord=None):
    """рассвет: ломаные аккорды снизу вверх; теплеет на G-dur"""
    harms = ["Bmadd9", "Gmaj7", "Em9", "F#7"] if end_chord is None else end_chord
    for i, h in enumerate(harms[:n]):
        t = (bar + i) * BAR
        o.ped(t)
        o.H(t, h)
        pcs, bp = chord(h)
        bs = next(x for x in range(28, 41) if x % 12 == bp)
        ladder = [bs] + [x for x in range(bs + 7, bs + 40) if x % 12 in pcs][:8]
        for j, m in enumerate(ladder):
            o.note(m, t + j * 0.42, BAR - j * 0.42, vel + 0.012 * j + (0.04 if h.startswith("G") else 0), o.hand(m))
    return bar + n


def verse_a(o, bar, rows, vel=0.5):
    """фактура I куплета (как в начале op. 16 № 3): мелодия с терцией/секстой, тенор-подголосок, бас с октавой"""
    for k, i in enumerate(rows):
        b = bar + k
        o.melody(b, THEME[i], THEME_H[i], vel=vel + (0.05 if i in (5, 6, 7) else 0), inner=1)
        o.tenor(b, THEME_H[i], THEME[i], vel=vel - 0.14)
        o.bass(b, THEME_H[i], vel=vel - 0.08)
    return bar + len(rows)


def verse_b(o, bar, rows, vel=0.54):
    """II куплет гуще: мелодия октавами с внутренним голосом, левая — широкие триоли"""
    for k, i in enumerate(rows):
        b = bar + k
        o.melody(b, THEME[i], THEME_H[i], vel=vel + (0.05 if i in (5, 6, 7) else 0), octave=True, inner=1)
        o.triplets(b, THEME_H[i], vel=vel - 0.14)
    return bar + len(rows)


def verse_shout(o, bar, vel=0.8):
    """III куплет — почти крик: мелодия октавами в полных аккордах, бас октавами на каждую долю, колокольно;
    восемнадцать берёз — восемнадцать ударов басовых октав подряд, и счёт обрывается; северный ветер —
    хроматические спуски октавами; «последний патрон» — обрыв, тишина, один сухой удар"""
    count = 0
    for i in range(10):
        b = bar + i
        b0 = b * BAR
        o.melody(b, THEME[i], THEME_H[i], vel=vel + (0.04 if i in (6, 7) else 0), octave=True, inner=2,
                 inner_vel=-0.1, top_gap=3)
        for bb, d, h in spans(THEME_H[i]):
            pcs, bp = chord(h)
            o.ped(b0 + bb)
            o.H(b0 + bb, h)
            x = next(y for y in range(23, 35) if y % 12 == bp)
            for k in range(int(d)):
                t = b0 + bb + k
                if count < 18:  # счёт: удар басовых октав на каждую долю
                    for m in (x, x + 12):
                        o.note(m, t, 1, vel - 0.02 + (0.06 if k == 0 else 0), "Piano LH")
                    count += 1
                elif k == 0:  # после счёта — только смены гармонии, тихо выдержанные
                    for m in (x + 12, x + 19 if (x + 19) % 12 in pcs else x + 12):
                        o.note(m, t, d, vel - 0.3, "Piano LH")
            mid = [y for y in range(x + 19, x + 31) if y % 12 in pcs][:2]
            for k in range(int(d)):
                for m in mid:
                    o.note(m, b0 + bb + k + 0.5, 0.5, vel - 0.2, "Piano LH")
    # северный ветер: хроматические спуски там, где мелодия дышит
    o.cascade((bar + 3) * BAR + 3.5, 0.5, 88, 82, vel=0.5)
    o.cascade((bar + 9) * BAR + 3, 0.75, 94, 83, vel=0.5)
    # «последний патрон»: обрыв (тишина полдоли) и один сухой удар внизу, без педали
    t = (bar + 9) * BAR + 3.9
    for m in (23, 35):
        e = o.note(m, t, 0.2, 0.85, "Piano LH")
        e["release"] = 0.1
    return bar + 10


def train(o, bar):
    """«Поезд»: колёса — октавы восьмыми; «поезд» ×4; «знаю ×3»; «ну и что?»; «надо быть вместе» — D-dur;
    гаснет в g-moll; обвал"""
    b = bar
    for i, h in enumerate(["Bm", "G", "Em", "F#7"]):  # «поезд, поезд, поезд, поезд, поезд»
        o.wheels(b, h, vel=0.36 + 0.03 * i)
        o.train_call(b, h, vel=0.44 + 0.03 * i)
        b += 1
    top = 74
    for i, h in enumerate(["Bm", "E7", "A7"]):          # «знаю, знаю, знаю» — секвенция вверх
        o.wheels(b, h, vel=0.46 + 0.03 * i)
        top = o.know(b, h, (74, 76, 79)[i], vel=0.52 + 0.04 * i)
        b += 1
    # «ну и что?» — вопрос: A7 без разрешения, колёса стоят, фермата
    o.ped(b * BAR)
    o.H(b * BAR, "A7")
    for m in (33, 45, 55, 61, 67, 73, 79):
        o.note(m, b * BAR, 3, 0.6, o.hand(m))
    b += 1
    # «нам надо быть вместе» — вторая фраза темы (D-dur) октавами в полных аккордах, f, единственный свет
    for i in (4, 5):
        o.melody(b, THEME[i], THEME_H[i], vel=0.62, octave=True, inner=1, inner_vel=-0.08)
        for bb, d, h in spans(THEME_H[i]):
            pcs, bp = chord(h)
            o.ped(b * BAR + bb)
            o.H(b * BAR + bb, h)
            x = next(y for y in range(26, 38) if y % 12 == bp)
            for m in (x, x + 12):
                o.note(m, b * BAR + bb, d, 0.6, "Piano LH")
            for k in range(int(d)):  # аккорды левой — на каждую долю, колокольно
                for m in [y for y in range(x + 19, x + 31) if y % 12 in pcs][:2]:
                    o.note(m, b * BAR + bb + k + (0.5 if k == 0 else 0), 0.5 if k == 0 else 1, 0.5, "Piano LH")
        b += 1
    # свет гаснет: g-moll → Fis7, и с разгона — вниз, в крик последнего куплета (не стихая)
    o.ped(b * BAR)
    o.H(b * BAR, "Gm")
    o.H(b * BAR + 2, "F#7")
    for m in (31, 43, 58, 62, 67, 70, 74, 79, 82):
        o.note(m, b * BAR, 2, 0.6, o.hand(m))
    for m in (30, 42, 58, 61, 64, 70, 73, 78):        # F#7
        o.note(m, b * BAR + 2, 2, 0.64, o.hand(m))
    o.ped(b * BAR + 2)
    b += 1
    o.H(b * BAR, "F#7")   # обвал октавами вниз по аккорду и ладу доминанты — crescendo
    path = [x for x in range(85, 52, -1) if x % 12 in {6, 10, 1, 4, 7, 11, 2} ][:16]
    for j, m in enumerate(path):
        t = b * BAR + j / 4
        o.note(m, t, 0.25, 0.6 + 0.014 * j, "Piano RH")
        o.note(m - 24, t, 0.25, 0.58 + 0.014 * j, "Piano LH")
    o.ped(b * BAR)
    return b + 1


def badge(o, bar):
    """пацифистский значок: один чистый до-мажор высоко, pp, — чужой (неаполитанский) в h-moll"""
    o.ped(bar * BAR)
    o.H(bar * BAR, "C")
    for j, m in enumerate((72, 76, 79, 84)):
        o.note(m, bar * BAR + 0.08 * j, 3.5, 0.52, "Piano RH")
    for j, m in enumerate((67, 72, 76)):  # отблеск: тот же до-мажор ниже, тише
        o.note(m, bar * BAR + 2 + 0.1 * j, 1.7, 0.42, "Piano RH")
    return bar + 1


def coda(o, bar):
    """рассвет снова; затем — как кончает сам Рахманинов: уменьшённое над ми (E – G – Ais – Cis) → Fis с септимой →
    пустая квинта h, без терции, ppp"""
    b = dawn(o, bar, n=2, vel=0.24, end_chord=["Bmadd9", "Gmaj7"])
    o.ped(b * BAR)
    o.H(b * BAR, "A#dim7")
    o.H(b * BAR + 2, "F#7")
    for m in (28, 40, 55, 58, 61):
        o.note(m, b * BAR, 2, 0.24, o.hand(m))
    o.ped(b * BAR + 2)
    for m in (30, 42, 52, 58, 61):
        o.note(m, b * BAR + 2, 2, 0.22, o.hand(m))
    b += 1
    o.ped(b * BAR)
    o.H(b * BAR, "Bm")
    for j, m in enumerate((23, 35, 42, 47, 54, 59)):
        o.note(m, b * BAR + 0.05 * j, 4, 0.24, o.hand(m))
    return b + 1


def build(ctx):
    o = Moment()
    quote = [(b, d, m, 0.42 + 0.1 * (m < 48)) for b, d, m in QUOTE]
    plan, ends = [], []
    b = 0
    plan.append((b, "Рассвет"))
    b = dawn(o, b)
    plan.append((b, "I куплет"))
    b = verse_a(o, b, range(10))
    ends += [b - 7, b - 1]
    plan.append((b, "Не спится"))
    o.sleepless(b, vel=0.52)
    b += 4
    ends.append(b - 1)
    plan.append((b, "II куплет"))
    b = verse_b(o, b, range(4))
    ends.append(b - 1)
    plan.append((b, "Из динамика — Рахманинов"))
    o.radio(b, quote, beats=11)
    b += 3
    plan.append((b, "II куплет, вторая фраза"))
    b = verse_b(o, b, range(4, 10), vel=0.56)
    ends.append(b - 1)
    plan.append((b, "Пацифистский значок"))
    b = badge(o, b)
    plan.append((b, "Не спится (настойчиво)"))
    o.sleepless(b, vel=0.58, twice=True, octave_bass=True)
    b += 4
    plan.append((b, "Поезд"))
    tr = b
    b = train(o, b)
    plan.append((b, "III куплет: восемнадцать берёз"))
    v3 = b
    b = verse_shout(o, b)
    plan.append((b, "Не спится (расплывается)"))
    start = b
    o.sleepless(b, vel=0.46, blur=0.6)
    for e in o.p.events:  # рояль расстраивается к концу рефрена
        if e["kind"] == "note" and e.get("wt", 0) >= start * BAR * SPB:
            k = (e["wt"] / SPB - start * BAR) / (4 * BAR)
            e["detune"] = 0.22 * k * (o.rng.random() * 2 - 1)
    b += 4
    plan.append((b, "Рассвет — кода"))
    end = coda(o, b)
    # рубато: концы фраз; «поезд» разгоняется; «ну и что?» — фермата; «быть вместе» шире; крик — широко,
    # «последний патрон» — после цезуры; кода замирает
    for bb in ends:
        o.slow.append((bb * BAR + 2, bb * BAR + 4, 1.0, 1.35))
    o.slow += [(tr * BAR, (tr + 7) * BAR, 0.95, 0.72),
               ((tr + 7) * BAR, (tr + 8) * BAR, 1.3, 2.2),
               ((tr + 8) * BAR, (tr + 10) * BAR, 1.12, 1.2),
               ((tr + 10) * BAR, (tr + 12) * BAR, 1.0, 0.9),
               (v3 * BAR, (v3 + 9) * BAR, 1.05, 1.15),
               ((v3 + 9) * BAR, (v3 + 10) * BAR, 1.4, 2.4),
               ((end - 3) * BAR, end * BAR, 1.1, 1.4)]
    for bt, label in plan:
        o.p.mark(o.perf(bt * BAR), label)["wt"] = bt * BAR * SPB
    o.p.meta["keys"] = [[0, "B minor"]]
    o.p.meta["notation_divisors"] = [[8, 3], [4, 3], [8], [4]]  # триоли левой — триолями
    # репродуктор: полоса 380–3200 Гц, моно, шорох и треск только пока звучит цитата
    q0 = o.perf([x for x, l in plan if l.startswith("Из динамика")][0] * BAR)
    q1 = o.perf([x for x, l in plan if l.startswith("II куплет, вторая")][0] * BAR)
    o.p.meta["bus_post"] = {"radio": [{"kind": "archive", "points": [
        {"t": 0, "lp": 3200, "hp": 380, "width": 0.0, "crackle": 0.0, "hiss": -120},
        {"t": q0 - 0.5, "lp": 3200, "hp": 380, "width": 0.0, "crackle": 0.0, "hiss": -120},
        {"t": q0 + 0.6, "lp": 3200, "hp": 380, "width": 0.0, "crackle": 0.3, "hiss": -36},
        {"t": q1 - 0.6, "lp": 3200, "hp": 380, "width": 0.0, "crackle": 0.3, "hiss": -36},
        {"t": q1 + 0.3, "lp": 3200, "hp": 380, "width": 0.0, "crackle": 0.0, "hiss": -120}]}]}
    o.p.meta["harmony"] = sorted([b_, h_] for b_, h_ in o.harm_log)
    o.apply_pedal(o.perf(end * BAR) + 2)
    o.p.meta["beats"] = end * BAR
    return o.p
