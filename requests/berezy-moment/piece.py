#!/usr/bin/env python3
"""Moment musical «18 берёз» — драматургия песни «18 берёз» (Чиж & Co), в стиле и гармонии третьего
«Музыкального момента» Рахманинова (op. 16 № 3, h-moll). Фортепиано соло, ≈ 4:20.

Из песни — только драматургия и форма (мелодия Чижа не цитируется). Тема — своя. Из Рахманинова — фактура
op. 16 № 3 (по MIDI и нотам от заказчика): мелодия терциями в правой руке, сарабандный шаг левой (бас с октавой на
первую долю, тяжёлый аккорд на вторую, долгий), выдержанный тенор; в середине — октавы левой руки восьмыми, бегущие
по ладу, как колёса; конец — увеличенное созвучие над фа-диезом и пустая квинта си. И одна настоящая цитата:
начало op. 16 № 3 «из динамика» (Ван Клиберн) — через полосу частот старого репродуктора, шорох и треск.

  Рассвет          h-moll, ломаные аккорды снизу вверх, теплеет (G-dur)
  I куплет         тема-ламенто терциями, сарабанда левой
  «не спится»      навязчивый вздох фа-диез – ми над хроматическим басом-ламенто h – ais – a – gis – g – fis
  II куплет        тема гуще (пульсирующие аккорды, тенор в движении); посредине обрывается — из динамика чуть
                   слышно доносится сам Рахманинов; затем вторая фраза; «пацифистский значок» — один чистый
                   до-мажорный аккорд высоко, чужой в этой гармонии
  «не спится»      вздох дважды в такте, бас в октавах
  «Поезд»          октавы левой восьмыми (колёса) с ускорением; «поезд» — повторяющийся аккорд пятью восьмыми;
                   «знаю, знаю, знаю» — мотив секвенцией вверх, «ну и что?» — вопрос на A7; «надо быть вместе» —
                   тема в D-dur октавами, ff, единственный свет; гаснет в g-moll (iv мажора) и рушится октавами
  III куплет       реприза прорежена: мелодия одна, под ней — счёт: восемнадцать тихих ударов, и счёт обрывается;
                   северный ветер — хроматические спуски; «последний патрон» — один сухой удар внизу
  «не спится»      вздох расплывается: сбит с долей, тянется, рояль понемногу расстраивается
  Рассвет-кода     ломаные аккорды снова вверх; уменьшённое над ми → Fis7 → пустая квинта h, ppp (жест самого op. 16 № 3)

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

# ===================================================================== тема (своя), h-moll; такт → [(доля, длит., midi)]
THEME = [
    [(0, 1.5, 74), (1.5, .5, 76), (2, 1, 74), (3, 1, 71)],              # Bm      ре – (ми) – ре – си
    [(0, 1.5, 76), (1.5, .5, 78), (2, 2, 79)],                          # Em      ми – (фа#) – соль
    [(0, 1, 76), (1, 1, 79), (2, 1.5, 78), (3.5, .5, 76)],              # C | F#7 ми – соль | фа# – ми
    [(0, 2.5, 73)],                                                     # F#      до#, вдох
    [(0, 1, 74), (1, 1, 78), (2, 1.5, 83), (3.5, .5, 81)],              # Bm | G  ре – фа# | си – (ля)
    [(0, 1.5, 79), (1.5, .5, 78), (2, 1, 76), (3, 1, 73)],              # Em7 | A7
    [(0, 1, 74), (1, 1, 78), (2, 1, 76), (3, 1, 73)],                   # D | F#7
    [(0, 3, 71)],                                                       # Bm
]
THEME_H = [["Bm"], ["Em"], ["C", "F#7"], ["F#"], ["Bm", "G"], ["Em7", "A7"], ["D", "F#7"], ["Bm"]]
# второй куплет темнее: неаполитанский с септимой, уменьшённый вводный, ii° вместо iv
THEME_H2 = [["Bm"], ["Em"], ["C", "F#7"], ["F#"], ["Bm", "G"], ["Em7", "A7"], ["D", "F#7"], ["Bm"]]
# «не спится»: бас-ламенто по полутонам, над ним вздох фа# – ми
LAMENT = [("Bm", 35), ("F#7/A#", 34), ("D/A", 33), ("E7/G#", 32), ("G", 31), ("F#7", 30)]


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
        self.p.meta["gains"] = {"radio": 4.0}  # полоса репродуктора съедает низ — поднять шину целиком
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

    # ---------------------------------------------------------------- тема терциями + тенор
    def thirds(self, bar, notes, harms, vel=0.46, lower=True, tenor=True, oct=0):
        """мелодия терциями (как у Рахманинова: два верхних голоса правой руки вместе), выдержанный тенор"""
        b0 = bar * BAR
        span = BAR / len(harms)
        for b, d, m in notes:
            m += oct
            h = harms[min(int(b // span), len(harms) - 1)]
            pcs = chord(h)[0]
            sc = scale_of(h)
            late = 0.03 if b == 0 else 0.0
            self.note(m, b0 + b, d, vel + (0.04 if d >= 1.5 else 0), "Piano RH", late=late)
            if lower:
                if m % 12 in pcs:  # аккордовый звук — второй голос тоже аккордовый, на терцию (или кварту) ниже
                    lo = next(x for x in range(m - 3, m - 6, -1) if x % 12 in pcs)
                else:              # проходящий — параллельно, по ладу
                    lo = step(step(m, sc, -1), sc, -1)
                self.note(lo, b0 + b, d, vel - 0.12, "Piano RH", late=late)
        if tenor:
            for i, h in enumerate(harms):
                pcs = chord(h)[0]
                key = "tenor"
                prev = self.prev.get(key, 54)
                cands = [x for x in range(50, 62) if x % 12 in pcs]
                x = min(cands, key=lambda y: (abs(y - prev), y))
                self.prev[key] = x
                self.note(x, b0 + i * span, span, vel - 0.2, "Piano LH")

    def sarabande(self, bar, harms, vel=0.36, throb=False):
        """левая рука op. 16 № 3: на первую — бас с квинтой и октавой (коротко), на вторую — тяжёлый аккорд, долгий.
        throb — второй куплет: аккорд повторяется на каждую долю (пульс давит)"""
        b0 = bar * BAR
        span = BAR / len(harms)
        for i, h in enumerate(harms):
            t = b0 + i * span
            self.ped(t)
            self.H(t, h)
            pcs, bp = chord(h)
            bs = next(x for x in range(34, 47) if x % 12 == bp)
            fifth = next((x for x in range(bs + 6, bs + 9) if x % 12 in pcs), None)
            for m in [bs, bs + 12] + ([fifth] if fifth else []):
                self.note(m, t, 1, vel + 0.06, "Piano LH")
            if span >= 2:
                up = [x for x in range(bs + 7, bs + 20) if x % 12 in pcs and x != bs + 12][:2]
                if throb:
                    for j in range(1, int(span)):
                        for m in up:
                            self.note(m, t + j, 1, vel - 0.02 - 0.03 * (j > 1), "Piano LH")
                else:
                    for m in up:
                        self.note(m, t + 1, span - 1, vel, "Piano LH")

    # ---------------------------------------------------------------- «не спится»
    def sleepless(self, bar, n_bars=4, vel=0.42, twice=False, blur=0.0, octave_bass=False):
        """вздох фа# – ми над басом-ламенто (B – A# – A – G# – G – F#, последние два — по полтакта)"""
        steps = LAMENT if n_bars >= 6 else LAMENT[:2] + [LAMENT[2], LAMENT[3], LAMENT[4], LAMENT[5]]
        # раскладка по тактам: 4 такта → B | A# | A G# | G F#
        layout = [(0, 4)] * 6 if n_bars >= 6 else [(0, 4), (0, 4), (0, 2), (2, 2), (0, 2), (2, 2)]
        barno = [0, 1, 2, 2, 3, 3] if n_bars < 6 else list(range(6))
        for k, ((h, bass), (off, dur)) in enumerate(zip(steps, layout)):
            t = (bar + barno[k]) * BAR + off
            self.ped(t)
            self.H(t, h)
            self.note(bass, t, dur, vel + 0.02, "Piano LH")
            if octave_bass:
                self.note(bass - 12, t, dur, vel - 0.04, "Piano LH")
            pcs = chord(h)[0]
            res_pc = {"E7/G#": 4, "G": 7}.get(h, 6)  # звук разрешения вздоха не дублируется внизу
            mid = [x for x in range(52, 72) if x % 12 in pcs and x > bass + 6 and x % 12 != res_pc][-3:]
            for m in mid:
                self.note(m, t + 1, dur - 1, vel - 0.08, self.hand(m))
        # сам вздох — задержание сверху, разрешается в аккордовый звук: на h, ais, a, fis — соль → фа#; на gis —
        # фа# → ми; на g — ля → соль. Раз в такт (или дважды); при blur — сбит с долей и тянется
        times = [((bar + barno[k]) * BAR + off, dur, steps[k][0]) for k, (off, dur) in enumerate(layout)]
        SIGH = {"E7/G#": (78, 76), "G": (81, 79)}
        for i, (t0, dur, h) in enumerate(times):
            reps = (0, 2) if twice and dur >= 4 else (0,)
            for j, r in enumerate(reps):
                shift, stretch = 0.0, 1.0
                if blur:
                    shift = blur * (0.25 + 0.3 * ((i * 2 + j) % 3))     # опаздывает, всё сильнее
                    stretch = 1 + blur * 0.6 * (i + 1) / len(times)
                hi_, res = SIGH.get(h, (79, 78))
                t = t0 + r + shift
                d1 = min(1.0 * stretch, 1.5)
                d2 = min(1.0, max(0.5, (2 if twice else dur) - shift - d1 - 0.05))
                self.note(hi_, t, d1, vel + 0.06, "Piano RH")
                self.note(res, t + d1, d2, vel - 0.04, "Piano RH")

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
    harms = ["Bm", "G", "Em/B", "F#7/A#"] if end_chord is None else end_chord
    for i, h in enumerate(harms[:n]):
        t = (bar + i) * BAR
        o.ped(t)
        o.H(t, h)
        pcs, bp = chord(h)
        bs = next(x for x in range(28, 41) if x % 12 == bp)
        ladder = [bs] + [x for x in range(bs + 7, bs + 40) if x % 12 in pcs][:8]
        for j, m in enumerate(ladder):
            o.note(m, t + j * 0.42, BAR - j * 0.42, vel + 0.012 * j + (0.04 if h == "G" else 0), o.hand(m))
    return bar + n


def verse(o, bar, harm=THEME_H, throb=False, vel=0.46, quote=None, phrase2_only=False, phrase1_only=False):
    rng = range(4, 8) if phrase2_only else range(0, 4) if phrase1_only else range(8)
    b = bar
    for i in rng:
        o.thirds(b, THEME[i], harm[i], vel=vel + (0.04 if i in (4, 5) else 0))
        o.sarabande(b, harm[i], vel=vel - 0.1, throb=throb)
        b += 1
    return b


def verse_three(o, bar, vel=0.46):
    """реприза прорежена: мелодия одна (без терций), счёт — 18 ударов и обрыв; ветер; «последний патрон»"""
    count = 0
    for i in range(8):
        b0 = (bar + i) * BAR
        harms = THEME_H[i]
        o.thirds(bar + i, THEME[i], harms, vel=vel, lower=False, tenor=i < 4)
        span = BAR / len(harms)
        for j, h in enumerate(harms):
            pcs, bp = chord(h)
            o.ped(b0 + j * span)
            o.H(b0 + j * span, h)
            bs = next(x for x in range(35, 48) if x % 12 == bp)
            o.note(bs, b0 + j * span, span, vel - 0.06, "Piano LH")
            if i == 7:  # последний такт: тихий аккорд в середине держит звучание до «патрона»
                for m in (59, 62, 66):
                    o.note(m, b0 + 1.5, 2.2, vel - 0.02, "Piano RH")
        # счёт: тихий высокий звук на каждую долю — аккордовый, ближайший к фа#6 — 18 раз, потом нет
        for beat in range(4):
            if count >= 18:
                break
            h = harms[min(int(beat // span), len(harms) - 1)]
            pcs = chord(h)[0]
            mel = [m for bb, d, m in THEME[i] if bb <= beat < bb + d]
            cands = [x for x in range(84, 94) if x % 12 in pcs
                     and all(abs(x - y) % 12 not in (1, 2, 6, 10, 11) for y in mel)]
            if cands:
                x = min(cands, key=lambda y: abs(y - 90))
                o.note(x, b0 + beat, 0.25, 0.2 + 0.005 * (count % 4 == 0), "Piano RH")
            count += 1
    # северный ветер: хроматические спуски там, где мелодия молчит (после «вдоха» 4-го такта и в конце)
    o.cascade((bar + 3) * BAR + 2.5, 1.5, 95, 79, vel=0.22)
    o.cascade((bar + 7) * BAR + 3, 1.0, 92, 80, vel=0.2)
    # «последний патрон»: один сухой удар внизу, без педали
    t = (bar + 7) * BAR + 3.5
    for m in (23, 35):
        e = o.note(m, t, 0.18, 0.78, "Piano LH")
        e["release"] = 0.12
    return bar + 8


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
    # «нам надо быть вместе» — голова темы в D-dur, октавами, полными аккордами
    climax = [[(0, 1.5, 78), (1.5, .5, 79), (2, 1, 78), (3, 1, 74)],
              [(0, 1.5, 79), (1.5, .5, 81), (2, 2, 83)]]
    for i, (notes, harms) in enumerate(zip(climax, (["D"], ["G"]))):
        o.ped(b * BAR)
        o.H(b * BAR, harms[0])
        pcs, bp = chord(harms[0])
        bs = next(x for x in range(26, 39) if x % 12 == bp)
        for m in (bs, bs + 12):
            o.note(m, b * BAR, 4, 0.66, "Piano LH")
        for beat in range(4):  # аккорды левой — на каждую долю, колокольно
            for m in [x for x in range(bs + 19, bs + 31) if x % 12 in pcs][:3]:
                o.note(m, b * BAR + beat, 1, 0.6 - 0.03 * beat, "Piano LH")
        for bb, d, m in notes:
            for x in (m, m - 12):
                o.note(x, b * BAR + bb, d, 0.7, "Piano RH")
            inner = [x for x in range(m - 9, m - 2) if x % 12 in pcs][-2:]
            for x in inner:
                o.note(x, b * BAR + bb, d, 0.62, "Piano RH")
        b += 1
    # гаснет: g-moll (iv минорная) — свет уходит
    o.ped(b * BAR)
    o.H(b * BAR, "Gm")
    o.H(b * BAR + 2, "F#7")
    for m in (31, 43, 58, 62, 67, 70, 74, 79, 82):
        o.note(m, b * BAR, 2, 0.52, o.hand(m))
    for m in (30, 42, 58, 61, 64, 70, 73, 78):        # F#7
        o.note(m, b * BAR + 2, 2, 0.5, o.hand(m))
    o.ped(b * BAR + 2)
    b += 1
    # обвал октавами вниз — обе руки, по гармоническому минору, к си
    o.H(b * BAR, "*")  # обвал — гамма, гармонии нет
    path = [x for x in range(78, 46, -1) if x % 12 in H_HARM]
    for j, m in enumerate(path[:16]):
        t = b * BAR + j / 4
        o.note(m, t, 0.25, 0.55 - 0.018 * j, "Piano RH")
        o.note(m - 24, t, 0.25, 0.5 - 0.018 * j, "Piano LH")
    o.ped(b * BAR)
    return b + 1


def badge(o, bar):
    """пацифистский значок: один чистый до-мажор высоко, pp, — чужой (неаполитанский) в h-moll"""
    o.ped(bar * BAR)
    o.H(bar * BAR, "C")
    for j, m in enumerate((72, 76, 79, 84)):
        o.note(m, bar * BAR + 0.08 * j, 3.5, 0.52, "Piano RH")
    for j, m in enumerate((67, 72, 76)):  # отблеск: тот же до-мажор ниже, тише
        o.note(m, bar * BAR + 2 + 0.1 * j, 2, 0.42, "Piano RH")
    return bar + 1


def coda(o, bar):
    """рассвет снова; затем — как кончает сам Рахманинов: уменьшённое над ми (E – G – Ais – Cis) → Fis с септимой →
    пустая квинта h, без терции, ppp"""
    b = dawn(o, bar, n=2, vel=0.22, end_chord=["Bm", "G"])
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
        o.note(m, b * BAR + 0.05 * j, 5, 0.24, o.hand(m))
    return b + 2


def build(ctx):
    o = Moment()
    quote = [(b, d, m, 0.42 + 0.1 * (m < 48)) for b, d, m in QUOTE]
    plan = []
    b = 0
    plan.append((b, "Рассвет"))
    b = dawn(o, b)
    plan.append((b, "I куплет"))
    b = verse(o, b)
    plan.append((b, "Не спится"))
    o.sleepless(b, 4, vel=0.54)
    b += 4
    plan.append((b, "II куплет"))
    b = verse(o, b, harm=THEME_H2, throb=True, vel=0.5, phrase1_only=True)
    plan.append((b, "Из динамика — Рахманинов"))
    end = o.radio(b, quote, beats=11)
    b += 3
    plan.append((b, "II куплет, вторая фраза"))
    b = verse(o, b, harm=THEME_H2, throb=True, vel=0.52, phrase2_only=True)
    plan.append((b, "Пацифистский значок"))
    b = badge(o, b)
    plan.append((b, "Не спится (настойчиво)"))
    o.sleepless(b, 4, vel=0.56, twice=True, octave_bass=True)
    b += 4
    plan.append((b, "Поезд"))
    b = train(o, b)
    plan.append((b, "III куплет: восемнадцать берёз"))
    b = verse_three(o, b)
    plan.append((b, "Не спится (расплывается)"))
    o.detune = 0.0
    start = b
    o.sleepless(b, 4, vel=0.52, blur=0.6)
    for e in o.p.events:  # рояль расстраивается к концу рефрена
        if e["kind"] == "note" and e.get("wt", 0) >= start * BAR * SPB:
            k = (e["wt"] / SPB - start * BAR) / (4 * BAR)
            e["detune"] = 0.22 * k * (o.rng.random() * 2 - 1)
    b += 4
    plan.append((b, "Рассвет — кода"))
    end = coda(o, b)
    # рубато: концы фраз, «ну и что?» — фермата, кульминация шире, «поезд» разгоняется, кода — замирает
    for bb in (7, 11, 15, 19, 26, 31, 47, 51):
        o.slow.append((bb * BAR + 2, bb * BAR + 4, 1.0, 1.35))
    tr = [x for x, l in plan if l == "Поезд"][0]
    o.slow += [(tr * BAR, (tr + 7) * BAR, 0.95, 0.72),          # разгон колёс
               ((tr + 7) * BAR, (tr + 8) * BAR, 1.3, 2.2),      # «ну и что?»
               ((tr + 8) * BAR, (tr + 10) * BAR, 1.12, 1.25),   # «быть вместе» — широко
               ((tr + 10) * BAR, (tr + 12) * BAR, 1.2, 1.0),
               ((end - 4) * BAR, end * BAR, 1.15, 1.6)]
    for bt, label in plan:
        o.p.mark(o.perf(bt * BAR), label)["wt"] = bt * BAR * SPB
    o.p.meta["keys"] = [[0, "B minor"]]
    o.p.meta["notation_divisors"] = [[8], [4]]
    # репродуктор: полоса 380–3200 Гц, моно, шорох и треск только пока звучит цитата
    q0 = o.perf([x for x, l in plan if l.startswith("Из динамика")][0] * BAR)
    q1 = o.perf([x for x, l in plan if l.startswith("II куплет, вторая")][0] * BAR)
    o.p.meta["bus_post"] = {"radio": [{"kind": "archive", "points": [
        {"t": 0, "lp": 3200, "hp": 380, "width": 0.0, "crackle": 0.0, "hiss": -120},
        {"t": q0 - 0.5, "lp": 3200, "hp": 380, "width": 0.0, "crackle": 0.0, "hiss": -120},
        {"t": q0 + 0.6, "lp": 3200, "hp": 380, "width": 0.0, "crackle": 0.22, "hiss": -46},
        {"t": q1 - 0.6, "lp": 3200, "hp": 380, "width": 0.0, "crackle": 0.22, "hiss": -46},
        {"t": q1 + 0.3, "lp": 3200, "hp": 380, "width": 0.0, "crackle": 0.0, "hiss": -120}]}]}
    o.p.meta["harmony"] = sorted([b_, h_] for b_, h_ in o.harm_log)
    o.apply_pedal(o.perf(end * BAR) + 2)
    o.p.meta["beats"] = end * BAR
    return o.p
