#!/usr/bin/env python3
"""«Холодный мир» — тема СССР, вторая редакция (≈ 3:00). Мелодия — заказчика (MIDI, 8 тактов, e-moll, натуральный
минор), в проведениях без изменений; оркестровка и драматургия — по образу СССР из опенинга
(requests/cold-peace-op/storyboard.md): старик у окна, снег, ветеран химической войны 1944 года, держава, которая
устала быть великой.

После отзыва («фон дисгармонирует, тема из ниоткуда, проведение искусственное и примитивное»):
- бас и подголоски ищет контрапунктический движок фуги (requests/fugue-grenzen/counterpoint.py) против самой
  темы, по гармонии на каждую долю, в натуральном миноре (без ре-диеза против ре темы);
- тема вырастает: во вступлении её голова звучит обрывками, перекличкой голосов, и только затем — целиком;
- проведения разные: соло — хор в a-moll с подголоском — разработка (голова темы секвенцией вверх, марш, обвал) —
  шкатулка одна, в тишине — апофеоз с контрапунктом — кода;
- фразировка: каждая двутактная фраза дышит (нарастание к вершине, спад), концы фраз оттянуты.

    python3 -m kit run requests/ussr-theme/piece.py --parts
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from kit.devices import Composer  # noqa: E402
from kit.events import Piece  # noqa: E402

_spec = importlib.util.spec_from_file_location("cp", os.path.join(HERE, "..", "fugue-grenzen", "counterpoint.py"))
cp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cp)

BPM = 72
SPB = 60.0 / BPM

# тема заказчика: (доля, длительность, midi) — 8 тактов по 4 доли, e-moll
THEME = [(0, 1, 71), (1, 1, 71), (2, 1, 72), (3, .5, 71), (3.5, .5, 69),
         (4, 1, 67), (5, 1, 69), (6, 1, 67), (7, 1, 64),
         (8, 1, 71), (9, 1, 71), (10, 1, 76), (11, 1, 76),
         (12, .5, 74), (12.5, .5, 76), (13, .5, 74), (13.5, .5, 72), (14, .5, 71), (14.5, .5, 72), (15, 1, 74),
         (16, 1, 76), (17, 1, 76), (18, 1, 72), (19, .5, 71), (19.5, .5, 69),
         (20, 1, 71), (21, 1, 69), (22, 1, 67), (23, 1, 64),
         (24, 1, 66), (25, .5, 67), (25.5, .5, 69), (26, .5, 67), (26.5, .5, 66), (27, 1, 64),
         (28, 1, 71), (29, 1, 69), (30, 2, 64)]
# гармония по долям (ступень натурального минора, качество): звук темы на доле — в аккорде
HARM_DEG = [(0, "m"), (0, "m"), (3, "m"), (0, "m"),        # Em Em | Am Em      (си си | до си-ля)
            (5, "M"), (3, "m7"), (0, "m"), (5, "M"),       # C Am7 | Em C       (соль ля | соль ми)
            (0, "m"), (2, "M"), (5, "M"), (5, "M"),        # Em G | C C         (си си | ми ми)
            (2, "M"), (2, "M"), (4, "m"), (4, "m"),        # G G | Bm Bm        (ре ми ре до | си до ре)
            (5, "M"), (5, "M"), (3, "m"), (0, "m"),        # C C | Am Em        (ми ми | до си-ля)
            (0, "m"), (6, "M"), (5, "M"), (3, "m"),        # Em D | C Am        (си ля | соль ми)
            (6, "M"), (0, "m"), (0, "m"), (5, "M"),        # D Em | Em C        (фа# соль-ля | соль фа# ми)
            (4, "m"), (4, "m7"), (0, "m"), (0, "m")]       # Bm Bm7 | Em Em     (си ля | ми)


class NatKey(cp.Key):
    """натуральный минор темы: без повышенных VI и VII (ре-диез против ре темы — тот «фон, который
    дисгармонирует»)"""

    def pcs(self):
        return {(self.tonic + x) % 12 for x in self.scale}


def harmony(key, t0, degs=HARM_DEG, step=1.0):
    h = cp.Harmony()
    for i, (dg, q) in enumerate(degs):
        h.add(t0 + i * step, cp.ch(key, dg, q), key)
    return h


def theme_in(semis=0, dt=0.0, scale_t=1.0, notes=THEME):
    return [(dt + b * scale_t, d * scale_t, m + semis) for b, d, m in notes]


def line(slots_spec, harm, fixed, lo, hi, role, **kw):
    """подбор голоса движком: slots_spec — [(t, d)]"""
    out, _cost = cp.generate(slots_spec, harm, fixed, lo, hi, role=role, strict=False, **kw)
    return out


def calm_slots(t0, t1, mel):
    """ритм подголоска — спокойный и дополняющий: на двух долях, где тема бежит восьмыми, — половинная; где тема
    идёт четвертями — две четверти со сдвигом (вторая на «и»); где тема держит — четверть и две восьмые"""
    out = []
    t = t0
    while t < t1 - 1e-9:
        ons = [b for b, d, m in mel if t - 1e-9 <= b < t + 2 - 1e-9]
        held = any(b <= t + 1e-9 and b + d >= t + 2 - 1e-9 for b, d, m in mel)
        if t + 2 > t1 - 1e-9:
            out.append((t, t1 - t))
        elif held:
            out += [(t, 1), (t + 1, .5), (t + 1.5, .5)]
        elif any(abs(b - round(b)) > 1e-9 for b in ons):
            out.append((t, 2))
        else:
            out += [(t, 1.5), (t + 1.5, .5)]
        t += 2
    return out


def half_slots(t0, bars):
    """бас: по половинным (последняя — тоника каданса v – i)"""
    return [(t0 + 4 * b + j, 2) for b in range(bars) for j in (0, 2)]


class U:
    def __init__(self):
        self.p = Piece("«Холодный мир» — тема СССР", bpm=BPM, meter=(4, 4), key="E minor", seed=1944)
        self.p.meta["subtitle"] = "мелодия заказчика; оркестровка по образу СССР из опенинга"
        self.p.meta["sends"] = {"strings": 0.35, "brass": 0.3, "winds": 0.3, "perc": 0.25, "choir": 0.5, "harp": 0.4,
                                "keys": 0.35}
        self.c = Composer(self.p, lib="vsco", seed=76)
        self.slow = []

    def perf(self, beat):
        s = 0.0
        for b0, b1, f in sorted(self.slow):
            if beat <= b0:
                break
            s += (min(beat, b1) - b0) * (f - 1)
        return (beat + s) * SPB

    def n(self, inst, m, beat, dur, part, legato=0.96, **kw):
        kw.setdefault("release", 0.4)
        t0, t1 = self.perf(beat), self.perf(beat + dur)
        e = self.p.note(inst, m, t0, max(0.06, (t1 - t0) * legato), part=part, **kw)
        e["wt"], e["wdur"] = beat * SPB, dur * SPB
        return e

    def fx(self, kind, beat, **kw):
        return self.c.fx(kind, self.perf(beat), bus="perc", **kw)

    def phrase(self, inst, notes, part, vel=0.55, gain=0.5, swell=0.12, t_phrase=8, **kw):
        """фраза дышит: в каждой двутактной фразе громкость растёт к вершине и спадает к концу"""
        for b, d, m in notes:
            u = (b % t_phrase) / t_phrase
            arc = max(0.0, 1 - abs(u - 0.45) / 0.55)
            self.n(inst, m, b, d, part, vel=vel + swell * arc, gain=gain * (0.85 + 0.3 * arc), **kw)

    def pad(self, inst, harm, t0, t1, lo, hi, part, melody, vel=0.4, gain=0.2, size=3, step=2.0, **kw):
        """аккорды по гармонии, без звуков, дающих секунду или септиму с мелодией, пока аккорд звучит"""
        t = t0
        prev = None
        while t < t1 - 1e-9:
            pcs = harm.at(t)[1].pcs
            mel = [m for b, d, m in melody if b < t + step - 1e-9 and b + d > t + 1e-9]
            cands = [x for x in range(lo, hi + 1) if x % 12 in pcs
                     and all(abs(x - m) % 12 not in (1, 2, 10, 11) for m in mel)]
            v = []
            for x in sorted(cands, key=lambda x: (abs(x - (prev[min(len(v), len(prev) - 1)] if prev else (lo + hi) // 2)), x)):
                if len(v) < size and all(abs(x - y) >= 3 for y in v):
                    v.append(x)
            for m in v:
                self.n(inst, m, t, step, part, vel=vel, gain=gain, **kw)
            prev = sorted(v) or prev
            t += step


# ===================================================================== разделы
def intro(o):
    """снег; голова темы обрывками — перекличка кларнета, гобоя, валторны — и вырастание в первое проведение;
    в басу — педаль E, колокол"""
    for i in range(6):
        o.n("tubular", 52 if i % 2 == 0 else 59, 4 * i, 4, "Campane", vel=0.42, gain=0.32, release=3.0)
    o.n("cb_sus", 28, 0, 24, "Contrabassi", vel=0.4, gain=0.4, attack=2.0)
    o.n("vln_harm", 76, 0, 22, "Violini", vel=0.33, gain=0.16, attack=3.0, release=2.0)
    o.n("vla_harm", 71, 2, 20, "Viole", vel=0.33, gain=0.14, attack=3.0, release=2.0)
    for j, m in enumerate([88, 83, 79, 76, 83, 79, 74, 71]):
        o.n("harp", m, 1 + j * 2.5, 2, "Arpa", vel=0.3, gain=0.24, release=2.5, pan=0.35)
    head = [(b, d, m) for b, d, m in THEME if b < 4]          # си си до си-ля
    o.phrase("cl_sus", theme_in(-12, 4, notes=head[:3]), "Clarinetti", vel=0.42, gain=0.36, attack=0.15)
    o.phrase("ob_sus", theme_in(0, 9, notes=head), "Oboe", vel=0.44, gain=0.34, attack=0.1)
    o.phrase("hn_sus", theme_in(-12, 14, notes=[(b - 8, d, m) for b, d, m in THEME if 8 <= b < 12]), "Corni",
             vel=0.45, gain=0.36, attack=0.12)
    for j, m in enumerate((52, 54, 55, 57)):  # затакт виолончели: ми – фа# – соль – ля к первой си темы
        o.n("vc_leg", m, 22 + j * 0.5, 0.5, "Violoncello solo", vel=0.5 + 0.03 * j, gain=0.55)


def statement_solo(o, t0):
    """первое проведение: виолончель соло; бас и подголосок альтов — движком против темы; тихие аккорды"""
    key = NatKey(4)
    mel = theme_in(-12, t0)                                   # виолончель: си3…ми4
    harm = harmony(key, t0)
    E = {28, 40}
    bass = line(half_slots(t0, 8), harm, [mel], 28, 45, "lower", above=[mel], start=E, end=E)
    counter = line(calm_slots(t0, t0 + 32, mel), harm, [mel, bass], 45, 59, "upper", above=[mel], below=[bass])
    o.phrase("vc_leg", mel, "Violoncello solo", vel=0.52, gain=0.62, attack=0.05)
    o.phrase("cb_sus", bass, "Contrabassi", vel=0.45, gain=0.5, attack=0.2, swell=0.06)
    o.phrase("vla_leg", counter, "Viole", vel=0.42, gain=0.3, attack=0.08, swell=0.08)
    o.pad("cl_sus", harm, t0, t0 + 32, 55, 67, "Clarinetti", mel + counter, vel=0.35, gain=0.14, size=2)
    return [mel, bass, counter], harm


def link_to_a(o, t0):
    """два такта: каданс темы эхом у валторны, E – E7 – a-moll"""
    tail = [(b - 28, d, m) for b, d, m in THEME if b >= 28]
    o.phrase("hn_sus", theme_in(-12, t0, notes=tail), "Corni", vel=0.45, gain=0.35, attack=0.1)
    for m in (52, 56, 59, 62):  # E7 над басом
        o.n("vla_sus" if m >= 55 else "vc_sus", m, t0 + 4, 4, "Viole" if m >= 55 else "Violoncelli",
            vel=0.42, gain=0.25, attack=0.6)
    o.n("cb_sus", 28, t0, 8, "Contrabassi", vel=0.45, gain=0.45, attack=0.5)
    o.n("timp", 40, t0 + 4, 1, "Timpani", vel=0.45, gain=0.3)


def statement_choir(o, t0):
    """второе проведение — в a-moll: мужской хор с валторнами; подголосок скрипок движком; колокола"""
    key = NatKey(9)
    mel = theme_in(5 - 12, t0)                                # ми4…ля4
    harm = harmony(key, t0)
    A = {33, 45}
    bass = line(half_slots(t0, 8), harm, [mel], 33, 48, "lower", above=[mel], start=A, end=A)
    counter = line(calm_slots(t0, t0 + 32, mel), harm, [mel, bass], 69, 81, "upper", below=[mel])
    o.phrase("choir", mel, "Coro (uomini)", vel=0.55, gain=0.55, attack=0.12)
    o.phrase("hn_sus", mel, "Corni", vel=0.52, gain=0.36, attack=0.05)
    o.phrase("cb_sus", bass, "Contrabassi", vel=0.5, gain=0.52, attack=0.15)
    o.phrase("vc_sus", [(b, d, m + 12) for b, d, m in bass], "Violoncelli", vel=0.45, gain=0.32, attack=0.15)
    o.phrase("vln_leg", counter, "Violini", vel=0.48, gain=0.34, attack=0.05)
    o.pad("vla_sus", harm, t0, t0 + 32, 57, 68, "Viole", mel + counter, vel=0.38, gain=0.18, size=2)
    for b in range(8):
        o.n("tubular", 57 if b % 2 == 0 else 64, t0 + 4 * b, 4, "Campane", vel=0.45, gain=0.3, release=3.0)
    return [mel, bass, counter], harm


def development(o, t0):
    """разработка — «1944»: голова темы (два такта) секвенцией вверх — a, h, c, d; под ней марш: бас пиццикато
    и литавры по четвертям, малый барабан; гармония и бас — движком; на вершине — обвал"""
    head = [(b, d, m) for b, d, m in THEME if b < 8]
    steps = [(9, 5), (11, 7), (0, 8), (2, 10)]               # (тоника, сдвиг темы в полутонах)
    out = []
    for i, (tonic, sh) in enumerate(steps):
        b0 = t0 + 8 * i
        key = NatKey(tonic)
        mel = theme_in(sh - 12, b0, notes=head)
        harm = harmony(key, b0, HARM_DEG[:8])
        bass = line([(b0 + j, 1) for j in range(8)], harm, [mel], 31, 47, "lower", above=[mel])
        insts = (("tbn_sus", 0, "Tromboni"), ("hn_sus", 0, "Corni")) if i < 2 else \
            (("tbn_sus", 0, "Tromboni"), ("tpt_sus", 12, "Trombe"), ("hns_sus", 0, "Corni"))
        for inst, sh2, part in insts:
            o.phrase(inst, [(b, d, m + sh2) for b, d, m in mel], part, vel=0.55 + 0.05 * i, gain=0.36 + 0.03 * i,
                     attack=0.04)
        for b, d, m in bass:
            o.n("cb_pizz", m, b, d, "Contrabassi", vel=0.6 + 0.04 * i, gain=0.5)
            o.n("vc_pizz", m + 12, b, d, "Violoncelli", vel=0.55, gain=0.35)
            o.n("timp", next(x for x in range(40, 52) if x % 12 == m % 12), b, 0.5, "Timpani",
                vel=0.5 + 0.05 * i, gain=0.28 + 0.03 * i)
        o.pad("vla_trem", harm, b0, b0 + 8, 60, 74, "Viole", mel, vel=0.4 + 0.04 * i, gain=0.12 + 0.03 * i, size=3,
              step=1.0)
        t = b0
        while t < b0 + 8 - 1e-9:  # малый барабан, марш: ♩ ♪♪
            o.fx("snare_soft" if i < 2 else "snare", t, gain=0.08 + 0.04 * i)
            o.fx("snare_soft" if i < 2 else "snare", t + 0.5, gain=0.05 + 0.03 * i)
            t += 1
        out.append((mel, bass, harm))
    o.fx("gong_hit", t0 + 32, gain=0.35)
    o.n("cb_sus", 28, t0 + 32, 4, "Contrabassi", vel=0.6, gain=0.5, attack=0.02, release=2.0)
    return out


def box_alone(o, t0):
    """шкатулка — одна, в тишине: тема мира из опенинга, в натуральном миноре e (без ре-диеза), замедляется"""
    box = [(0, .5, 4), (.5, .5, 4), (1, .5, 3), (1.5, 1, 4), (2.5, 1.5, 2), (4, .5, 1), (4.5, .5, 2), (5, .5, 4),
           (5.5, 1, 7), (6.5, 1.5, 6)]
    nat = [0, 2, 3, 5, 7, 8, 10]
    tune = [76 + nat[s % 7] + 12 * (s // 7) for _, _, s in box]
    o.c.music_box(o.perf(t0), tune, step=0.42, slow=0.035, flat=0.02, inst="celesta", double=None, gain=0.3)
    o.n("vln_harm", 76, t0, 8, "Violini", vel=0.3, gain=0.1, attack=1.5, release=2.0)


def apotheosis(o, t0):
    """держава: тема у труб, валторн и хора октавами; бас — движком, медь хоралом по долям (без звуков против
    мелодии); подголосок скрипок сверху; каданс v – i без мажора, расширение"""
    key = NatKey(4)
    mel = theme_in(0, t0)
    harm = harmony(key, t0)
    E = {28, 40}
    bass = line([(t0 + j, 1) for j in range(30)] + [(t0 + 30, 2)], harm, [mel], 28, 43, "lower", above=[mel],
                start=E, end=E)
    counter = line(calm_slots(t0, t0 + 32, mel), harm, [mel, bass], 79, 91, "upper", below=[mel])
    o.phrase("tpt_sus", mel, "Trombe", vel=0.66, gain=0.42, attack=0.03)
    o.phrase("hns_sus", [(b, d, m - 12) for b, d, m in mel], "Corni", vel=0.66, gain=0.44, attack=0.03)
    o.phrase("choir", [(b, d, m - 12) for b, d, m in mel], "Coro", vel=0.62, gain=0.5, attack=0.08)
    o.phrase("vln_leg", counter, "Violini", vel=0.56, gain=0.36, attack=0.04)
    o.phrase("tba_sus", bass, "Tuba", vel=0.6, gain=0.4, attack=0.04)
    o.phrase("cb_sus", bass, "Contrabassi", vel=0.6, gain=0.5, attack=0.04)
    o.phrase("vc_sus", [(b, d, m + 12) for b, d, m in bass], "Violoncelli", vel=0.55, gain=0.35, attack=0.04)
    o.pad("tbn_sus", harm, t0, t0 + 32, 50, 64, "Tromboni", mel + counter, vel=0.58, gain=0.26, size=3, step=1.0,
          legato=0.88)
    for b, d, m in bass:
        o.n("timp", next(x for x in range(40, 52) if x % 12 == m % 12), b, 1, "Timpani", vel=0.55, gain=0.32)
    for b in range(8):
        o.n("tubular", 52 if b % 2 == 0 else 59, t0 + 4 * b, 4, "Campane", vel=0.6, gain=0.38, release=3.0)
        o.fx("bd", t0 + 4 * b, gain=0.2)
    o.fx("clash", t0, gain=0.25)
    o.fx("tamtam", t0 + 30, gain=0.3)
    return [mel, bass, counter], harm


def coda(o, t0):
    """снег: голова темы у валторны издалека, каданс-отзвук у виолончели; колокол E, пустая квинта"""
    head = [(b, d, m) for b, d, m in THEME if b < 8]
    tail = [(b - 28, d, m) for b, d, m in THEME if b >= 28]
    o.phrase("hn_sus", theme_in(-12, t0, notes=head), "Corni", vel=0.4, gain=0.3, attack=0.12)
    o.phrase("vc_leg", theme_in(-24, t0 + 8, notes=tail), "Violoncello solo", vel=0.42, gain=0.5, attack=0.08)
    o.n("cb_sus", 28, t0, 16, "Contrabassi", vel=0.38, gain=0.4, attack=1.0, release=2.0)
    o.n("vln_harm", 76, t0, 16, "Violini", vel=0.3, gain=0.14, attack=2.0, release=2.5)
    o.n("vla_harm", 71, t0, 16, "Viole", vel=0.3, gain=0.12, attack=2.0, release=2.5)
    for i in range(4):
        o.n("tubular", 52 if i % 2 == 0 else 59, t0 + 4 * i, 4, "Campane", vel=0.4, gain=0.3, release=3.5)
    o.n("tubular", 40, t0 + 16, 4, "Campane", vel=0.45, gain=0.36, release=4.0)


def build(ctx):
    o = U()
    # доли: вступление 0–24 | соло 24–56 | связка 56–64 | хор (a) 64–96 | разработка 96–128 | обвал 128–132 |
    #       шкатулка 132–140 | апофеоз 140–172 | кода 172–192
    o.slow += [(0, 24, 1.15)]
    for s in (24, 64, 140):  # концы фраз оттянуты
        for ph in range(4):
            e = s + 8 * ph + 8
            o.slow.append((e - 1, e, 1.18 if ph < 3 else 1.35))
    o.slow += [(96, 128, 0.94), (128, 132, 1.4), (132, 140, 1.25), (172, 192, 1.3)]
    plan = [(0, "Снег"), (24, "Старик"), (56, "Связка"), (64, "Хор (a-moll)"), (96, "1944: разработка"),
            (128, "Обвал"), (132, "Шкатулка"), (140, "Держава"), (172, "Снег")]
    intro(o)
    o.checks = [statement_solo(o, 24)]
    link_to_a(o, 56)
    o.checks.append(statement_choir(o, 64))
    development(o, 96)
    box_alone(o, 132)
    o.checks.append(apotheosis(o, 140))
    coda(o, 172)
    for bt, label in plan:
        o.p.mark(o.perf(bt), label)["wt"] = bt * SPB
    o.p.meta["beats"] = 192
    # замер `--parts` без баланса: трубы −19.9, хор −23.0, мужской хор −24.5, виолончель соло −26.2,
    # виолончели −27.3, гобой −29.5, валторны −31.1, контрабасы −32.8, альты −33.0, кларнеты −35.5,
    # тромбоны −37.5, туба −38.1, скрипки −38.2, арфа −43.2, литавры −46.6, челеста −52.8, колокола −56.4 LUFS —
    # шкатулка в тишине почти не слышна (провал 116–122 с), колокола и бас тонули, трубы торчали
    o.p.balance({"Trombe": -4, "Violini": +6, "Tromboni": +6, "Tuba": +6, "Contrabassi": +5, "Timpani": +8,
                 "Arpa": +4, "Corni": +3, "Clarinetti": +2, "Celesta": +14, "Campane": +14})
    o.p.meta["length"] = o.perf(192) + 5
    return o.p
