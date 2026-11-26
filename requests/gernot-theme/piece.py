#!/usr/bin/env python3
"""«Холодный мир» — тема Гернота, третья редакция (≈ 1:55). Портрет, без событий сюжета.

Первая редакция (речитация культа, канон, пророчество, отказ, приход в си) пересказывала путь героя — «экспликация
сюжета, а не сущность характера». Вторая дала портрет — сарабанду со своей мелодией (скачок вверх и спуск); заказчик:
«окружение и проведение темы не вызывает вопросов, но мне больше нравилась мелодическая линия Гернота из прошлой
версии». Третья: мелодия первой редакции в окружении второй.

- мелодия — формула первой редакции: речитация на фа# (ре–ми–фа#, повторы фа#, верхний изгиб на ля, спуск на ми),
  переложенная в сарабанду: долгие звуки — на вторую долю, повторы речитации — в её ритме (четверть, четверть с
  точкой, восьмая). Первое предложение кончается, как у культа, на ми — и следом пустой такт (бывшая пустая 16-я
  доля), под которым держится чужой аккорд. Второе — его окончание: ми – ре – до# – си;
- достоинство без власти — сарабанда: медленный трёхдольный шаг с тяжестью на второй доле;
- свой звук над чужим полом — мелодия всегда в си дорийском, но под её долгим звуком на третьей доле гармония
  съезжает в хроматическую медианту с тем же общим звуком (D → B, D → F, F#m → D, Em → C, A → F, Bm → G, D → B♭);
  чужие аккорды подкрашены флажолетами;
- дом без дома — си в конце звучит терцией соль мажора.

Тембр один — скрипка соло. Форма музыкальная: A (два предложения) — B (начальный подъём формулы секвенцией вверх с
речитацией на достигнутом звуке, вершина — ре третьей октавы) — A′ (второе предложение октавой ниже, тише).
Неаккордовы только восьмые на слабых половинах долей (ми в «ре–ми–фа#», проходящие).

    python3 -m kit run requests/gernot-theme/piece.py --parts
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from kit.devices import Composer  # noqa: E402
from kit.events import Piece  # noqa: E402

BPM = 58
SPB = 60.0 / BPM
BAR = 3

# ноты (midi): си дорийский
B4, Cs5, D5, E5, Fs5, Gs5, A5, B5 = 71, 73, 74, 76, 78, 80, 81, 83
A4 = 69
Cs6, D6 = 85, 86

# аккорды: имя → (основной тон, высотные классы)
PC = {"C": 0, "C#": 1, "D": 2, "Eb": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "Bb": 10, "B": 11}


def chord(name):
    minor = name.endswith("m")
    r = PC[name[:-1] if minor else name]
    return r, {r, (r + (3 if minor else 4)) % 12, (r + 7) % 12}


# такт: (мелодия [(доля в такте, длительность, midi)], гармония [(доля, длительность, аккорд)], чужой аккорд) —
# все звуки мелодии на долях — звуки аккорда; неаккордовы только восьмые на слабых половинах долей (проходящие)
def bar(mel, harm, slide=None):
    if not mel and slide:  # пустой такт: мелодия молчит, под ней держится чужой аккорд
        return (mel, [(0, 3, slide)], slide)
    if isinstance(harm, str):
        harm = [(0, 2 if slide else 3, harm)]
    if slide:
        harm = harm + [(2, 1, slide)]
    return (mel, harm, slide)


TWO = lambda x, y: [(0, 1, x), (1, 2, y)]  # noqa: E731 — смена гармонии на второй доле (сарабанда)
EACH = lambda x, y, z: [(0, 1, x), (1, 1, y), (2, 1, z)]  # noqa: E731 — аккорд на каждую долю

# мелодия Гернота — формула первой редакции (речитация на фа#: ре–ми–фа#, повторы, верхний изгиб на ля, спуск на ми,
# пустая доля), переложенная в сарабанду: долгие звуки — на вторую долю, пустая доля стала пустым тактом
INITIUM = lambda a, b, c: [(0, .5, a), (.5, .5, b), (1, 2, c)]  # noqa: E731 — ре–ми–фа# с долгим фа# на второй доле
RECITE = lambda m: [(0, 1, m), (1, 1.5, m), (2.5, .5, m)]  # noqa: E731 — повторы речитации в ритме сарабанды
CORE = [bar(INITIUM(D5, E5, Fs5), "D", "B"), bar(RECITE(Fs5), "Bm"),
        bar([(0, 1, Fs5), (1, 2, A5)], "D", "F"), bar([(0, 1, Fs5), (1, 1.5, E5), (2.5, .5, Fs5)], TWO("Bm", "A")),
        bar([(0, 1, Fs5), (1, 2, Fs5)], "F#m", "D"), bar([(0, 1, Fs5), (1, 1, E5), (2, 1, D5)], EACH("Bm", "A", "G"))]
# первое предложение кончается, как у культа: на ми, и следом — пустой такт
PHRASE1 = CORE + [bar([(0, 3, E5)], "Em", "C"), bar([], None, "C")]
# второе — его окончание: ми – ре – до# – си, си над соль мажором
PHRASE2 = CORE + [bar([(0, 1, E5), (1, 1, D5), (2, 1, Cs5)], EACH("Em", "Bm", "A")), bar([(0, 3, B4)], "G")]
# развитие: начальный подъём формулы секвенцией вверх (ми–фа#–ля, фа#–ля–си, ля–си–ре) с речитацией на
# достигнутом звуке, вершина — ре третьей октавы, спуск к ми
MIDDLE = [bar(INITIUM(E5, Fs5, A5), "A", "F"), bar(RECITE(A5), "D"),
          bar(INITIUM(Fs5, A5, B5), "Bm", "G"), bar(RECITE(B5), "E"),
          bar(INITIUM(A5, B5, D6), "D", "Bb"), bar([(0, 1, D6), (1, 1.5, Cs6), (2.5, .5, B5)], TWO("D", "A")),
          bar([(0, 1, A5), (1, 1, Fs5), (2, 1, E5)], EACH("D", "Bm", "A")), bar([(0, 3, E5)], "Em", "C")]


class G:
    def __init__(self):
        self.p = Piece("«Холодный мир» — тема Гернота", bpm=BPM, meter=(3, 4), key="B dorian", seed=16)
        self.p.meta["subtitle"] = "сарабанда"
        self.p.meta["sends"] = {"strings": 0.45, "winds": 0.35, "keys": 0.45}
        self.c = Composer(self.p, lib="vsco", seed=15)
        self.slow = []
        self.prev = [50, 57, 62]  # голоса фона (для плавного голосоведения)

    def perf(self, beat):
        s = 0.0
        for b0, b1, f in sorted(self.slow):
            if beat <= b0:
                break
            s += (min(beat, b1) - b0) * (f - 1)
        return (beat + s) * SPB

    def n(self, inst, m, beat, dur, part, legato=0.97, **kw):
        kw.setdefault("release", 0.6)
        t0, t1 = self.perf(beat), self.perf(beat + dur)
        e = self.p.note(inst, m, t0, max(0.06, (t1 - t0) * legato), part=part, **kw)
        e["wt"], e["wdur"] = beat * SPB, dur * SPB
        return e

    def voicing(self, pcs, top):
        """три голоса фона из звуков аккорда, все ниже `top`, ближайшие к прежним"""
        out = []
        for v in self.prev:
            cands = [m for m in range(40, top) if m % 12 in pcs and m not in out]
            out.append(min(cands, key=lambda m: (abs(m - v), m)))
        out.sort()
        self.prev = out
        return out


def statement(o, b0, bars, *, octave=0, vel=0.5, gain=0.42, pad_gain=0.16, bass_step=False, pad_top=None, hold=None):
    """проведение: скрипка соло, фон струнных ниже мелодии, бас по основным тонам; чужой аккорд на третьей доле
    подкрашен флажолетами"""
    for i, (mel, harm, slide) in enumerate(bars):
        t = b0 + i * BAR
        last = hold if (hold and i == len(bars) - 1) else None
        if last:
            mel = [(b, last, m) for b, _, m in mel]
        for b, d, m in mel:
            acc = 0.06 if b == 1 else 0.0  # тяжесть сарабанды — на второй доле
            o.n("vln_solo", m + octave, t + b, d, "Violino solo", vel=vel + acc, gain=gain * (1 + acc), attack=0.06)
        lo = min([m for _, _, m in mel] or [70]) + octave
        top = min(pad_top or 99, lo - 2)
        segs = [(0, last, harm[0][2])] if last else harm
        for sb, sd, name in segs:
            root, pcs = chord(name)
            foreign = name == slide
            for k, m in enumerate(o.voicing(pcs, top)):
                inst = "vla_sus" if m >= 55 else "vc_sus"
                o.n(inst, m, t + sb, sd, "Archi", vel=0.38, gain=pad_gain, attack=0.25 if sb == 0 else 0.4,
                    release=0.5, legato=1.0)
            bass = 36 + (root - 36) % 12  # основной тон в c – h большой октавы
            if bass > 43:
                bass -= 12
            if bass_step and not foreign and sd >= 2:  # сарабандный бас: основной тон, на второй доле — квинта
                o.n("cb_sus", bass, t + sb, 1, "Contrabassi", vel=0.42, gain=0.3, attack=0.1, release=0.4)
                o.n("cb_sus", bass + 7 if bass + 7 <= 47 else bass - 5, t + sb + 1, sd - 1, "Contrabassi",
                    vel=0.46, gain=0.32, attack=0.1, release=0.5)
            else:
                o.n("cb_sus", bass, t + sb, sd, "Contrabassi", vel=0.42, gain=0.3, attack=0.15, release=0.5)
            if foreign:  # чужой пол — флажолеты на две октавы выше двух верхних голосов фона
                for m in o.prev[1:]:
                    h = m + 24 if m + 24 >= 76 else m + 36  # флажолеты записаны от соль второй октавы
                    o.n("vln_harm", h, t + sb, sd, "Flautando (flag.)", vel=0.34, gain=0.12,
                        attack=0.3, release=0.25, legato=1.0)


# замер `--parts` без баланса: скрипка соло −35.5, фон −47.6, контрабасы −48.6, флажолеты −55.8 LUFS —
# бас утонул (правило: тема и бас в пределах ±3 дБ), фон и флажолеты почти не слышны; второй замер: фон −38.7
# (на 3 дБ под темой — громковато), флажолеты −48.6
BAL = {"Archi": +3, "Contrabassi": +12, "Flautando (flag.)": +13}


def build(ctx):
    o = G()
    # такты: вступление 0 | A 1–16 | B 17–24 | A′ 25–32 | хвост 33–34
    o.slow += [(21, 24, 1.12), (45, 48, 1.15), (69, 72, 1.15), (93, 105, 1.25)]
    # вступление: только фон — си минор, затем чужой соль минор
    r, pcs = chord("Bm")
    for m in o.voicing(pcs, 68):
        o.n("vla_sus" if m >= 55 else "vc_sus", m, 0, 3, "Archi", vel=0.36, gain=0.14, attack=1.2, legato=1.0)
    o.n("cb_sus", 35, 0, 3, "Contrabassi", vel=0.4, gain=0.28, attack=1.0)
    statement(o, 3, PHRASE1)
    statement(o, 27, PHRASE2, bass_step=True, pad_gain=0.18)
    statement(o, 51, MIDDLE, vel=0.6, gain=0.58, pad_gain=0.27, bass_step=True)  # вершина пьесы — mf
    o.prev = [40, 45, 50]
    statement(o, 75, PHRASE2, octave=-12, vel=0.42, gain=0.3, pad_gain=0.11, pad_top=58, hold=9)  # p
    # хвост: последний си (терция соль мажора) тянется и гаснет
    o.p.balance(BAL)
    for bt, label in [(0, "Вступление"), (3, "A: первое предложение"), (27, "A: второе предложение"),
                      (51, "B: развитие"), (75, "A′"), (96, "Хвост")]:
        o.p.mark(o.perf(bt), label)["wt"] = bt * SPB
    o.p.meta["beats"] = 105
    o.p.meta["length"] = o.perf(105) + 4
    return o.p
