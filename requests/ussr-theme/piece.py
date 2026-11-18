#!/usr/bin/env python3
"""«Холодный мир» — тема СССР, пятая редакция (≈ 3:20). Мелодия — заказчика (MIDI, 8 тактов, e-moll, натуральный
минор), в песенных проведениях без изменений. Образ — по раскадровке опенинга (requests/cold-peace-op/storyboard.md):
старик у окна, снег, держава, которая устала быть великой. (Откуда в раскадровке подробности сюжета — со слов
заказчика или допущения сессии 2026-11-13, — в репозитории не записано: не опираться на них, пока заказчик не
подтвердит.)

Форма: снег (голова темы обрывками) — соло виолончели — хор в a-moll с подголоском — ФУГАТО на голове темы
(вступления снизу вверх с удержанным противосложением, интермедия, стретта через долю, вершина: тема в басах против
своего обращения наверху, марш) — обвал — шкатулка одна — апофеоз — кода с тихим каноном.

Гармонизация песенных проведений — по тактам, по функциям (HARM_DEG); фон ниже темы; бас по основным тонам;
подголоски — только консонансы к каждому звуку темы. В фугато гармонию задают сами голоса; бас подбирается под них.

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
HARM_DEG = (
    [(0, "m")] * 4 +                   # 1  Em        си си до си-ля   (до — вспомогательная, ля — проходящая)
    [(5, "M")] * 4 +                   # 2  C         соль ля соль ми
    [(0, "m")] * 2 + [(5, "M")] * 2 +  # 3  Em  C     си си | ми ми
    [(2, "M")] * 4 +                   # 4  G         ре ми ре до си до ре  (полукаданс в параллельный мажор)
    [(5, "M")] * 2 + [(3, "m")] * 2 +  # 5  C   Am    ми ми | до си-ля
    [(0, "m")] * 4 +                   # 6  Em        си ля соль ми
    [(6, "M")] * 2 + [(5, "M")] * 2 +  # 7  D   C     фа# соль-ля | соль-фа# ми   (VII – VI – V – i: русский каданс)
    [(4, "7")] * 2 + [(0, "m")] * 2)   # 8  H7  Em    си ля | ми   (ре-диез только здесь — в теме в этот миг ре нет)
# Прежде аккорд менялся на каждую долю — лишь бы звук темы на доле входил в аккорд (Em Em Am Em | C Am7 Em C …).
# Каждый звук формально «в аккорде», но гармония дёргалась без функции и логики: вспомогательные и проходящие
# звуки темы получали свои аккорды, фон метался — «отдельные моменты созвучны, а в целом не дополняет тему».
# Теперь — гармонический ритм песни: аккорд на такт или полтакта, со смыслом (t – s – t – D(параллельн.) …
# VII – VI – V – i).


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


def chord_pcs(harm, t, d):
    """звуки, общие для всех аккордов на отрезке [t, t+d) (шаг — доля)"""
    pcs, x = None, t
    while x < t + d - 1e-9:
        c = set(harm.at(x)[1].pcs)
        pcs = c if pcs is None else pcs & c
        x += 1.0
    return pcs or set()


def bells(o, harm, t0, count, prefer, vel, gain, every=4, dur=2, melody=()):
    """колокол — только звуком, который входит во все аккорды, пока колокол звенит; иначе пропуск.
    (прежде ми и си чередовались вслепую и звенели 4 доли + 3 с: си над до-мажором — большая септима)"""
    for i in range(count):
        t = t0 + every * i
        pcs = chord_pcs(harm, t, dur + 1)
        mel = [mm for b, d, mm in melody if b < t + dur + 1 - 1e-9 and b + d > t + 1e-9 and abs(b - round(b)) < 1e-9]
        m = next((x for x in prefer[i % len(prefer):] + prefer if x % 12 in pcs
                  and all(abs(x - mm) % 12 not in (1, 2, 6, 10, 11) for mm in mel)), None)
        if m is not None:
            o.n("tubular", m, t, dur, "Campane", vel=vel, gain=gain, release=1.2)


def timp_hits(o, harm, key_tonic, notes, vel, gain, dur=1):
    """литавры — только тоника и доминанта и только на сильных долях, когда этот звук в аккорде: у литавр
    неровные обертоны (сильный призвук на полутон выше), и бас-«гамма» на литаврах давала грязь"""
    td = {key_tonic % 12, (key_tonic + 7) % 12}
    for b, d, m in notes:
        if m % 12 in td and abs(b - round(b)) < 1e-9 and round(b) % 2 == 0 and m % 12 in harm.at(b)[1].pcs:
            o.n("timp", next(x for x in range(40, 52) if x % 12 == m % 12), b, dur, "Timpani", vel=vel, gain=gain)


def theme_in(semis=0, dt=0.0, scale_t=1.0, notes=THEME):
    return [(dt + b * scale_t, d * scale_t, m + semis) for b, d, m in notes]


def line(slots_spec, harm, fixed, lo, hi, role, **kw):
    """подбор голоса движком: slots_spec — [(t, d)]"""
    out, _cost = cp.generate(slots_spec, harm, fixed, lo, hi, role=role, strict=False, **kw)
    return out


def bass_line(harm, t0, t1, lo, hi, step=2.0, start=None, mel=()):
    """бас по гармонии: на смене аккорда — основной тон (ближайший к прежнему), внутри аккорда — квинта или
    основной тон через октаву; последний звук — основной тон"""
    out, prev, t = [], start, t0
    last_chord = None
    while t < t1 - 1e-9:
        c = harm.at(t)[1]
        d = min(step, t1 - t)
        final = t + d >= t1 - 1e-9
        if repr(c) != last_chord or final:
            pcs = {c.root}
        else:
            pcs = {(c.root + 7) % 12, c.root}
        ms = _over(mel, t, d)
        clean = {pc for pc in pcs if all(abs(pc - q) % 12 not in (1, 2, 10, 11) for q in ms)}
        pcs = clean or {c.root}
        cands = [x for x in range(lo, hi + 1) if x % 12 in pcs and x != (out[-1][2] if out and pcs != {c.root} else -1)]
        ref = prev if prev is not None else (lo + hi) // 2
        m = min(cands, key=lambda x: (abs(x - ref), x))
        out.append((t, d, m))
        prev, last_chord, t = m, repr(c), t + d
    return out


CONS = {0, 3, 4, 7, 8, 9}  # созвучия с темой, допустимые для подголоска и баса (кварта — только сверху)


def _over(notes, t, d):
    return [m for b, dd, m in notes if b < t + d - 1e-9 and b + dd > t + 1e-9]


def counter_line(harm, slots, mel, lo, hi, side, bass=()):
    """подголосок: только звуки аккорда, консонирующие со ВСЕМИ звуками темы, звучащими одновременно с ним
    (включая проходящие и вспомогательные), по одну сторону от темы. Линия ищется целиком (динамическое
    программирование): плавные шаги, без топтания на месте, без параллельных квинт и октав с темой, с поощрением
    противодвижения. (Движок фуги с strict=False пропускал секунды с темой на долях — «задняя партия не
    дополняет тему».)"""
    allowed = CONS | ({5} if side == "above" else set())
    cand, ms_of = [], []
    for t, d in slots:
        pcs, x = None, t
        while x < t + d - 1e-9:  # аккорд должен держаться всё время звучания
            c = set(harm.at(x)[1].pcs)
            pcs = c if pcs is None else pcs & c
            x += 0.5
        ms, bs = _over(mel, t, d), _over(bass, t, d)
        ok = [m for m in range(lo, hi + 1) if m % 12 in pcs
              and not (side == "below" and ms and m > min(ms) - 3)
              and not (side == "above" and ms and m < max(ms) + 3)
              and all(abs(m - q) % 12 in allowed for q in ms)
              and all(abs(m - q) % 12 not in (1, 2, 10, 11) for q in bs)]
        cand.append(ok)
        ms_of.append(ms[0] if ms else None)
    INF = 1e9
    best = [{m: (0.0 if True else INF, None) for m in cand[0]}] if cand and cand[0] else [{}]
    for k in range(1, len(slots)):
        cur = {}
        for m in cand[k]:
            bc, bp = INF, None
            prev_layer = best[k - 1]
            if not prev_layer:
                cur[m] = (0.0, None)
                continue
            for q, (cq, _) in prev_layer.items():
                step = abs(m - q)
                c = cq + {0: 2.5, 1: 0.0, 2: 0.0, 3: 0.6, 4: 0.8, 5: 1.2}.get(step, 1.5 + 0.4 * step)
                a, b = ms_of[k - 1], ms_of[k]
                if a is not None and b is not None:
                    i1, i2 = abs(q - a) % 12, abs(m - b) % 12
                    if i1 == i2 and i1 in (0, 7) and m != q:
                        c += 20
                    if (m - q) * (b - a) < 0:
                        c -= 0.4
                    if m == q and b == a:
                        c += 1.0
                if c < bc:
                    bc, bp = c, q
            cur[m] = (bc, bp)
        best.append(cur)
    out = [None] * len(slots)
    k = len(slots) - 1
    while k >= 0 and not best[k]:
        k -= 1
    if k < 0:
        return []
    m = min(best[k], key=lambda q: best[k][q][0])
    while k >= 0:
        out[k] = m
        prev = best[k][m][1] if m in best[k] else None
        k -= 1
        if prev is None:
            while k >= 0 and not best[k]:
                k -= 1
            if k >= 0:
                m = min(best[k], key=lambda q: best[k][q][0])
        else:
            m = prev
    res = []
    for (t, d), m in zip(slots, out):
        if m is None:
            continue
        if res and res[-1][2] == m and abs(res[-1][0] + res[-1][1] - t) < 1e-9:
            res[-1] = (res[-1][0], res[-1][1] + d, m)  # повтор — связываем лигой
        else:
            res.append((t, d, m))
    return res


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

    DROP = set(filter(None, os.environ.get("USSR_DROP", "").split(",")))  # замеры: рендер без этих инструментов

    def n(self, inst, m, beat, dur, part, legato=0.96, **kw):
        if inst in self.DROP:
            return {}
        kw.setdefault("release", 0.4)
        t0, t1 = self.perf(beat), self.perf(beat + dur)
        e = self.p.note(inst, m, t0, max(0.06, (t1 - t0) * legato), part=part, **kw)
        e["wt"], e["wdur"] = beat * SPB, dur * SPB
        return e

    def fx(self, kind, beat, **kw):
        if "fx" in self.DROP:
            return None
        return self.c.fx(kind, self.perf(beat), bus="perc", **kw)

    def phrase(self, inst, notes, part, vel=0.55, gain=0.5, swell=0.12, t_phrase=8, **kw):
        """фраза дышит: в каждой двутактной фразе громкость растёт к вершине и спадает к концу"""
        for b, d, m in notes:
            u = (b % t_phrase) / t_phrase
            arc = max(0.0, 1 - abs(u - 0.45) / 0.55)
            self.n(inst, m, b, d, part, vel=vel + swell * arc, gain=gain * (0.85 + 0.3 * arc), **kw)

    def pad(self, inst, harm, t0, t1, lo, hi, part, melody, vel=0.4, gain=0.2, size=3, step=2.0, others=(), **kw):
        """аккорды по гармонии — только ниже темы и без секунд, септим и тритонов с ней, пока аккорд звучит
        (в первых редакциях аккорды стояли над темой: верхний голос фона слышался как вторая мелодия и спорил с
        темой — «партия на заднем плане дисгармонирует»)"""
        t = t0
        prev = None
        while t < t1 - 1e-9:
            pcs = harm.at(t)[1].pcs
            mel = [m for b, d, m in melody if b < t + step - 1e-9 and b + d > t + 1e-9]
            top = min(mel) - 3 if mel else hi  # аккомпанемент — всегда ниже темы (не меньше малой терции)
            oth = [m for b, d, m in others if b < t + step - 1e-9 and b + d > t + 1e-9]
            cands = [x for x in range(lo, min(hi, top) + 1) if x % 12 in pcs
                     and all(abs(x - m) % 12 not in (1, 2, 6, 10, 11) for m in mel)
                     and all(abs(x - m) % 12 not in (1, 11) for m in oth)]
            v = []
            for x in sorted(cands, key=lambda x: (abs(x - (prev[min(len(v), len(prev) - 1)] if prev else (lo + hi) // 2)), x)):
                if len(v) < size and all(abs(x - y) >= 3 for y in v):
                    v.append(x)
            for m in v:
                self.n(inst, m, t, step, part, vel=vel, gain=gain, **kw)
            prev = sorted(v) or prev
            t += step


# ===================================================================== разделы
# колокола — только E4/A4/B4: у трубчатых колоколов ниже ля малой октавы (E3, B3) сильнейший обертон — квинта
# (у B3 громче основного звучит F#), и низкий колокол «фальшивит» против гармонии


def intro(o):
    """снег; голова темы обрывками — перекличка кларнета, гобоя, валторны — и вырастание в первое проведение;
    в басу — педаль E, колокол"""
    for i in range(0, 6, 2):
        o.n("tubular", 64, 4 * i, 2, "Campane", vel=0.42, gain=0.32, release=1.5)
    o.n("cb_sus", 28, 0, 24, "Contrabassi", vel=0.4, gain=0.4, attack=2.0)
    o.n("vln_harm", 76, 0, 22, "Violini", vel=0.33, gain=0.16, attack=3.0, release=2.0)
    o.n("vla_harm", 64, 2, 20, "Viole", vel=0.33, gain=0.14, attack=3.0, release=2.0)
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
    bass = bass_line(harm, t0, t0 + 32, 28, 45, start=40, mel=mel)
    counter = counter_line(harm, calm_slots(t0, t0 + 32, mel), mel, 48, 57, "below", bass=bass)
    o.phrase("vc_leg", mel, "Violoncello solo", vel=0.52, gain=0.62, attack=0.05)
    o.phrase("cb_sus", bass, "Contrabassi", vel=0.45, gain=0.5, attack=0.2, swell=0.06)
    o.phrase("vla_leg", counter, "Viole", vel=0.42, gain=0.3, attack=0.08, swell=0.08)
    o.pad("cl_sus", harm, t0, t0 + 32, 50, 60, "Clarinetti", mel, vel=0.35, gain=0.14, size=2, others=counter + bass)
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
    bass = bass_line(harm, t0, t0 + 32, 33, 48, start=45, mel=mel)
    counter = counter_line(harm, calm_slots(t0, t0 + 32, mel), mel, 69, 81, "above", bass=bass)
    o.phrase("choir", mel, "Coro (uomini)", vel=0.55, gain=0.55, attack=0.12)
    o.phrase("hn_sus", mel, "Corni", vel=0.52, gain=0.36, attack=0.05)
    o.phrase("cb_sus", bass, "Contrabassi", vel=0.5, gain=0.52, attack=0.15)
    o.phrase("vc_sus", [(b, d, m + 12) for b, d, m in bass], "Violoncelli", vel=0.45, gain=0.32, attack=0.15)
    o.phrase("vln_leg", counter, "Violini", vel=0.48, gain=0.34, attack=0.05)
    o.pad("vla_sus", harm, t0, t0 + 32, 48, 64, "Viole", mel, vel=0.38, gain=0.18, size=2, others=bass)
    bells(o, harm, t0, 8, [69, 64, 76], vel=0.45, gain=0.3, melody=mel)
    return [mel, bass, counter], harm


# ===================================================================== фугато (разработка)
NAT_E = {4, 6, 7, 9, 11, 0, 2}
SCALE_E = [x for x in range(20, 110) if x % 12 in NAT_E]
HEAD = [(b, d, m) for b, d, m in THEME if b < 8]       # тема фугато — голова темы: си си до си-ля | соль ля соль ми
# противосложение (удержанное): нисходящая линия против темы; над темой — с шагом «и», под темой — без кварт к ней
CS_HI = [(0, 1.5, 79), (1.5, .5, 78), (2, 1, 76), (3, .5, 74), (3.5, .5, 72), (4, 1, 71), (5, 1, 72),
         (6, .5, 76), (6.5, .5, 74), (7, 1, 72)]
CS_LO = [(0, 2, 79), (2, 1, 76), (3, .5, 74), (3.5, .5, 72), (4, 1, 71), (5, 1, 72), (6, 1, 76), (7, 1, 72)]
TRIADS = {}
for _r in NAT_E:
    _deg = sorted(NAT_E, key=lambda x: (x - 4) % 12)
    _i = _deg.index(_r)
    TRIADS[_r] = {_deg[_i], _deg[(_i + 2) % 7], _deg[(_i + 4) % 7]}


def dtr(notes, deg, octv=0, dt=0.0):
    """диатонический сдвиг в натуральном e-moll (ответ в квинту — +4 ступени: си→фа#, до→соль — без тритонов)"""
    return [(b + dt, d, SCALE_E[SCALE_E.index(m) + deg] + 12 * octv) for b, d, m in notes]


def inversion(notes, axis):
    """обращение в ладу вокруг звука axis"""
    a = SCALE_E.index(axis)
    return [(b, d, SCALE_E[2 * a - SCALE_E.index(m)]) for b, d, m in notes]


def bass_under(voices, t0, t1, step, lo, hi, start=40):
    """бас под уже написанными голосами: звук, над которым звуки голосов образуют трезвучие лада, без секунд,
    септим и тритонов ни с одним звуком отрезка; если на отрезке такого нет — дробит отрезок пополам"""
    out, prev, t = [], start, t0
    while t < t1 - 1e-9:
        d = min(step, t1 - t)
        while True:
            allm = [m for v in voices for b, dd, m in v if b < t + d - 1e-9 and b + dd > t + 1e-9]
            strong = {m % 12 for v in voices for b, dd, m in v
                      if (b <= t + 1e-9 < b + dd) or (t < b < t + d - 1e-9 and abs(b - round(b)) < 1e-9)}
            best = None
            for x in range(lo, hi + 1):
                if x % 12 not in NAT_E or any(abs(x - m) % 12 in (1, 2, 6, 10, 11) for m in allm):
                    continue
                c = 0 if strong <= TRIADS[x % 12] else 6
                c += abs(x - prev) * 0.15
                if best is None or c < best[0]:
                    best = (c, x)
            if best is not None or d <= 0.5:
                break
            d /= 2
        if best is not None:
            out.append((t, d, best[1]))
            prev = best[1]
        t += d
    return out


def fugato_voices(t0):
    """четыре вступления (тема – ответ – тема – ответ, снизу вверх), интермедия, стретта, вершина: тема против
    своего обращения. Все голоса проверены попарно: на сильных долях — ни секунд, ни септим, ни тритонов"""
    V = {k: [] for k in ("vc", "vla", "hn", "vln", "tpt", "bass")}
    S = lambda o: dtr(HEAD, 0, o)
    A = lambda o: dtr(HEAD, 4, o)
    V["vc"] += S(-1) + dtr(CS_LO, 4, -2, 8)             # 1: тема у виолончелей; 2: противосложение
    V["vla"] += dtr(A(-1), 0, 0, 8)                      # 2: ответ у альтов
    V["hn"] += dtr(S(0), 0, 0, 16) + dtr(CS_LO, 4, -1, 24)  # 3: тема у валторн; 4: противосложение
    V["vln"] += dtr(CS_HI, 0, 0, 16)                     # 3: противосложение у скрипок
    V["tpt"] += dtr(A(0), 0, 0, 24)                      # 4: ответ у труб
    mot = [(0, .5, 83), (.5, .5, 84), (1, .5, 83), (1.5, .5, 81)]  # интермедия: си-до-си-ля секвенцией вниз
    ep = dtr(mot, 0, 0, 32) + dtr(mot, -1, 0, 34)
    V["vln"] += ep
    V["hn"] += dtr(ep, -2, -1)
    V["tpt"] += dtr(S(0), 0, 0, 36)                      # стретта: трубы,
    V["hn"] += dtr(HEAD, -4, 0, 37)                      # валторны через долю квинтой ниже,
    strb = dtr(HEAD, -9, -1, 42)                         # басы — с шестой доли
    inv = inversion(S(1), 83)
    inv[-1] = (inv[-1][0], inv[-1][1], 79)               # конец обращения — соль (не фа# против ми)
    V["vln"] += dtr(inv, 0, 0, 50)                       # вершина: обращение наверху,
    V["tpt"] += dtr(inv, 0, -1, 50)
    clim = dtr(S(-2), 0, 0, 50)                          # тема внизу
    upper = [V[k] for k in ("vc", "vla", "hn", "vln", "tpt")]
    b1 = bass_under(upper, 16, 32, 2.0, 28, 43)
    b2 = bass_under(upper, 32, 36, 1.0, 28, 43, start=b1[-1][2] if b1 else 40)
    V["bass"] = b1 + b2 + strb + clim
    return {k: [(b + t0, d, m) for b, d, m in v] for k, v in V.items()}


FUGATO_LEN = 58  # долей; затем обвал (4)


def development(o, t0):
    """разработка — фугато на голове темы: вступления снизу вверх (виолончели — альты — валторны — трубы) с
    удержанным противосложением, интермедия на мотиве «си-до-си-ля», стретта (вступления через долю), вершина —
    тема в басах против своего обращения у скрипок и труб; под всем — марш малого барабана; затем обвал"""
    V = fugato_voices(t0)
    o.phrase("vc_sus", V["vc"], "Violoncelli", vel=0.48, gain=0.42, attack=0.06)
    o.phrase("vla_leg", V["vla"], "Viole", vel=0.56, gain=0.7, attack=0.06)
    o.phrase("hn_sus", V["hn"], "Corni", vel=0.56, gain=0.4, attack=0.05)
    o.phrase("vln_leg", V["vln"], "Violini", vel=0.58, gain=0.5, attack=0.04)
    o.phrase("tpt_sus", V["tpt"], "Trombe", vel=0.6, gain=0.4, attack=0.03)
    for b, d, m in V["bass"]:
        loud = b >= t0 + 42
        o.n("cb_sus", m, b, d, "Contrabassi", vel=0.55 + 0.1 * loud, gain=0.45 + 0.1 * loud, attack=0.04)
        if b >= t0 + 24:
            o.n("vc_sus", m + 12, b, d, "Violoncelli", vel=0.5, gain=0.3, attack=0.05)
        if loud:
            o.n("tba_sus", m, b, d, "Tuba", vel=0.62, gain=0.4, attack=0.04)
            o.n("tbn_sus", m + 12, b, d, "Tromboni", vel=0.6, gain=0.36, attack=0.04)
            if m % 12 in (4, 11) and abs(b - round(b)) < 1e-9 and round(b - t0) % 2 == 0:
                o.n("timp", 40 if m % 12 == 4 else 47, b, 1, "Timpani", vel=0.55, gain=0.3)
    t = t0 + 8
    while t < t0 + FUGATO_LEN - 1e-9:  # марш: ♩ ♪♪, нарастает
        k = (t - t0) / FUGATO_LEN
        o.fx("snare_soft" if k < 0.5 else "snare", t, gain=0.06 + 0.12 * k)
        o.fx("snare_soft" if k < 0.5 else "snare", t + 0.5, gain=0.04 + 0.08 * k)
        t += 1
    end = t0 + FUGATO_LEN
    o.fx("gong_hit", end, gain=0.35)
    o.n("cb_sus", 28, end, 4, "Contrabassi", vel=0.6, gain=0.5, attack=0.02, release=2.0)
    return V


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
    bass = bass_line(harm, t0, t0 + 30, 28, 43, step=1.0, start=40, mel=mel) + [(t0 + 30, 2, 28)]
    counter = counter_line(harm, calm_slots(t0, t0 + 32, mel), mel, 79, 91, "above", bass=bass)
    o.phrase("tpt_sus", mel, "Trombe", vel=0.66, gain=0.42, attack=0.03)
    o.phrase("hns_sus", [(b, d, m - 12) for b, d, m in mel], "Corni", vel=0.66, gain=0.44, attack=0.03)
    o.phrase("choir", [(b, d, m - 12) for b, d, m in mel], "Coro", vel=0.62, gain=0.5, attack=0.08)
    o.phrase("vln_leg", counter, "Violini", vel=0.56, gain=0.36, attack=0.04)
    o.phrase("tba_sus", bass, "Tuba", vel=0.6, gain=0.4, attack=0.04)
    o.phrase("cb_sus", bass, "Contrabassi", vel=0.6, gain=0.5, attack=0.04)
    o.phrase("vc_sus", [(b, d, m + 12) for b, d, m in bass], "Violoncelli", vel=0.55, gain=0.35, attack=0.04)
    o.pad("tbn_sus", harm, t0, t0 + 32, 48, 64, "Tromboni", mel, vel=0.58, gain=0.26, size=3, step=1.0, others=bass,
          legato=0.88)
    timp_hits(o, harm, 4, bass, vel=0.55, gain=0.32)
    bells(o, harm, t0, 8, [64, 71, 76], vel=0.6, gain=0.38, melody=mel)
    for b in range(8):
        o.fx("bd", t0 + 4 * b, gain=0.2)
    o.fx("clash", t0, gain=0.25)
    o.fx("tamtam", t0 + 30, gain=0.3)
    return [mel, bass, counter], harm


def coda(o, t0):
    """снег: голова темы у валторны издалека и тихий канон кларнета, каданс-отзвук у виолончели; колокол E"""
    head = [(b, d, m) for b, d, m in THEME if b < 8]
    tail = [(b - 28, d, m) for b, d, m in THEME if b >= 28]
    o.phrase("hn_sus", theme_in(-12, t0, notes=head), "Corni", vel=0.4, gain=0.3, attack=0.12)
    o.phrase("cl_sus", dtr(HEAD, 0, 0, t0 + 6), "Clarinetti", vel=0.34, gain=0.24, attack=0.15)  # канон: через
    # полтора такта октавой выше — единственная пара, чистая и между голосами, и с педалью ми (проверено перебором)
    o.phrase("vc_leg", theme_in(-24, t0 + 14, notes=tail), "Violoncello solo", vel=0.42, gain=0.5, attack=0.08)
    o.n("cb_sus", 28, t0, 16, "Contrabassi", vel=0.38, gain=0.4, attack=1.0, release=2.0)
    o.n("vln_harm", 76, t0, 16, "Violini", vel=0.3, gain=0.14, attack=2.0, release=2.5)
    o.n("vla_harm", 64, t0, 16, "Viole", vel=0.3, gain=0.12, attack=2.0, release=2.5)
    for i in range(0, 4, 2):
        o.n("tubular", 64, t0 + 4 * i, 2, "Campane", vel=0.4, gain=0.3, release=1.5)
    o.n("tubular", 64, t0 + 16, 4, "Campane", vel=0.45, gain=0.36, release=4.0)


def build(ctx):
    o = U()
    # доли: вступление 0–24 | соло 24–56 | связка 56–64 | хор (a) 64–96 | фугато 96–154 | обвал 154–158 |
    #       шкатулка 158–166 | апофеоз 166–198 | кода 198–218
    o.slow += [(0, 24, 1.15)]
    for s in (24, 64, 166):  # концы фраз оттянуты
        for ph in range(4):
            e = s + 8 * ph + 8
            o.slow.append((e - 1, e, 1.18 if ph < 3 else 1.35))
    o.slow += [(96, 154, 0.94), (154, 158, 1.4), (158, 166, 1.25), (198, 218, 1.3)]
    plan = [(0, "Снег"), (24, "Старик"), (56, "Связка"), (64, "Хор (a-moll)"), (96, "Фугато"),
            (154, "Обвал"), (158, "Шкатулка"), (166, "Держава"), (198, "Снег")]
    intro(o)
    o.checks = [statement_solo(o, 24)]
    link_to_a(o, 56)
    o.checks.append(statement_choir(o, 64))
    development(o, 96)
    box_alone(o, 158)
    o.checks.append(apotheosis(o, 166))
    coda(o, 198)
    for bt, label in plan:
        o.p.mark(o.perf(bt), label)["wt"] = bt * SPB
    o.p.meta["beats"] = 218
    # замер `--parts` без баланса: трубы −19.9, хор −23.0, мужской хор −24.5, виолончель соло −26.2,
    # виолончели −27.3, гобой −29.5, валторны −31.1, контрабасы −32.8, альты −33.0, кларнеты −35.5,
    # тромбоны −37.5, туба −38.1, скрипки −38.2, арфа −43.2, литавры −46.6, челеста −52.8, колокола −56.4 LUFS —
    # шкатулка в тишине почти не слышна (провал 116–122 с), колокола и бас тонули, трубы торчали
    o.p.balance({"Trombe": -4, "Violini": +6, "Tromboni": +6, "Tuba": +6, "Contrabassi": +5, "Timpani": +8,
                 "Arpa": +4, "Corni": +3, "Clarinetti": +2, "Celesta": +14, "Campane": +14})
    o.p.meta["length"] = o.perf(218) + 5
    return o.p
