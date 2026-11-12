"""Фуга «Die Grenzen meiner Sprache bedeuten die Grenzen meiner Welt» (Tractatus 5.6) — нотный текст.

Тема — по слогам: ударный слог на доле, «Gren-zen» и «mei-ner» — пунктир, «Welt» — итог. Диапазон темы — ровно
октава, и оба «Grenzen» стоят на её краях: первое — на нижнем D, второе — на верхнем D. Тема ни разу не выходит за
свою октаву: язык не выходит за свои границы.

    python3 fugue.py     — печать голосов и проверки
"""
from counterpoint import (Chord, Harmony, auto_harmony, Key, ch, check, dmap, generate, nm, slots_between, sounding, tmap, transpose)

Dm, Am, F, Gm = Key(2, "minor"), Key(9, "minor"), Key(5, "major"), Key(7, "minor")
Cmaj, Bb = Key(0, "major"), Key(10, "major")

# тема (D минор, от D4): (доля относительно начала такта темы, длительность, высота)
#   Die | GREN-zen MEI-ner SPRA-che be- | DEU-ten die GREN-zen MEI-ner | WELT
SUBJECT = [(-0.5, 0.5, 69),                                                       # Die        A4
           (0, 0.75, 62), (0.75, 0.25, 64), (1, 0.75, 65), (1.75, 0.25, 67),     # Grenzen meiner  D4 — нижняя граница
           (2, 1, 69), (3, 0.5, 70), (3.5, 0.5, 69),                             # Sprache be-
           (4, 1, 73), (5, 0.5, 70), (5.5, 0.5, 67),                             # -deuten die (ум. септаккорд)
           (6, 0.75, 74), (6.75, 0.25, 72), (7, 0.75, 70), (7.75, 0.25, 67),     # Grenzen meiner  D5 — верхняя граница
           (8, 1, 69)]                                                            # Welt       A4
SYLL = ["Die", "Gren-", "zen", "mei-", "ner", "Spra-", "che", "be-", "deu-", "ten", "die", "Gren-", "zen", "mei-",
        "ner", "Welt"]


def subject_harmony(key, B, tonal_from=None, scale_t=1.0):
    """гармония темы. Минор: i i6 III VI | V vii°7 i iv | V; мажор: I I6 iii vi | V ii I ii | V"""
    if key.mode == "minor":
        plan = [(-0.5, 0, "m", 0), (0, 0, "m", 0), (1, 0, "m", 1), (2, 2, "M", 0), (3, 5, "M", 0),
                (4, 4, "M", 0), (5, 6, "d7", 0), (6, 0, "m", 0), (7, 3, "m", 0), (8, 4, "M", 0)]
    else:
        plan = [(-0.5, 0, "M", 0), (0, 0, "M", 0), (1, 0, "M", 1), (2, 2, "m", 0), (3, 5, "m", 0),
                (4, 4, "M", 0), (5, 6, "hd7", 0), (6, 0, "M", 0), (7, 1, "m", 0), (8, 4, "M", 0)]
    h = []
    for t, deg, q, inv in plan:
        if tonal_from is not None and t < 0:
            h.append((B + t * scale_t, ch(tonal_from, 0, "m" if tonal_from.mode == "minor" else "M"), tonal_from))
        else:
            h.append((B + t * scale_t, ch(key, deg, q, inv), key))
    return h


def subject(key, B, octave_deg=0):
    """тема в ладу key (D минор → key по ступеням), начало такта темы — доля B"""
    return tmap(SUBJECT, Dm, key, shift=octave_deg, dt=B)


def answer(key_from, B, octave_deg=0):
    """тональный ответ: Die и первое Grenzen меняются местами (V→I, I→V), остальное — в доминанте"""
    dom = Key((key_from.tonic + 7) % 12, key_from.mode)
    notes = tmap(SUBJECT, Dm, dom, shift=octave_deg, dt=B)
    # Die: доминанта лада → тоника (вместо II в доминанте), Grenzen: тоника → доминанта
    t0, d0, m0 = notes[0]
    notes[0] = (t0, d0, m0 - 2)  # E → D (в D миноре)
    return notes


def inversion(B, shift_semis=0):
    """зеркало темы (вокруг D, по ступеням натурального минора), в соль миноре"""
    out = []
    for t, d, m in SUBJECT:
        deg, alt = Dm.degree(m)
        axis = Dm.degree(62)[0]  # D4
        out.append((B + t, d, Dm.pitch(2 * axis - deg, -alt) + shift_semis))
    return out


def show(name, line):
    print(name, " ".join(f"{nm(m)}@{t:g}" for t, d, m in line))


# ================================================================ построение
# противосложение (найдено поиском против темы в D миноре, затем закреплено): нисходящие шестнадцатые, пока тема
# стоит на «Sprache», встречное движение под «bedeuten», восходящий ход к вводному тону под «Welt»
CS = [(1, 1, 62), (2, .25, 60), (2.25, .25, 59), (2.5, .25, 57), (2.75, .25, 60), (3, 1, 62),
      (4, .25, 64), (4.25, .25, 65), (4.5, .25, 64), (4.75, .25, 62), (5, 1, 61),
      (6, .5, 57), (6.5, .5, 53), (7, .5, 55), (7.5, .5, 58), (8, 1, 61)]

ORDER = ["S", "A", "T", "B"]
RANGE = {"S": (60, 81), "A": (53, 74), "T": (46, 69), "B": (36, 60)}


class Fugue:
    def __init__(self):
        self.v = {k: [] for k in ORDER}
        self.H = Harmony()
        self.marks = []
        self.roles = []  # (t0, t1, voice, роль) — для партитуры и отчёта

    # -- запись
    def put(self, voice, notes, role=None):
        if notes:
            t_new = notes[0][0]
            self.v[voice] = [n if n[0] + n[1] <= t_new + 1e-9 or n[0] >= t_new - 1e-9 else (n[0], t_new - n[0], n[2])
                             for n in self.v[voice]]
        self.v[voice].extend(notes)
        self.v[voice].sort()
        if role and notes:
            self.roles.append((notes[0][0], notes[-1][0] + notes[-1][1], voice, role))

    def tie_repeats(self):
        """повторы одной высоты подряд — залиговать (кроме темы: у неё повторов нет)"""
        for k in ORDER:
            out = []
            for n in self.v[k]:
                if out and out[-1][2] == n[2] and abs(out[-1][0] + out[-1][1] - n[0]) < 1e-6 and n[1] < 4:
                    out[-1] = (out[-1][0], out[-1][1] + n[1], n[2])
                else:
                    out.append(n)
            self.v[k] = out

    def to_chord(self, notes):
        """последняя нота — к ближайшему звуку аккорда в этот момент (стык проведений)"""
        t, d, m = notes[-1]
        pcs = self.H.at(t)[1].pcs
        best = min((x for x in range(m - 3, m + 4) if x % 12 in pcs), key=lambda x: (abs(x - m), x))
        return notes[:-1] + [(t, d, best)]

    def harm(self, segs):
        for s in segs:
            self.H.add(s[0], s[1], s[2])

    def chords(self, key, spec):
        """spec: [(t, deg, qual, inv)]"""
        for t, deg, q, inv in spec:
            self.H.add(t, ch(key, deg, q, inv), key)

    def last(self, voice, before):
        ns = [n for n in self.v[voice] if n[0] < before - 1e-9]
        return ns[-1][2] if ns else None

    def free(self, voice, t0, t1, *, role="upper", slots=None, end=None, near=None, lo=None, hi=None, rest_after=0.0,
             ignore=()):
        """свободный контрапункт голоса на [t0, t1); ignore — голоса, которые не учитывать (органный пункт)"""
        others = [self.v[k] for k in ORDER if k != voice and k not in ignore]
        i = ORDER.index(voice)
        above = [self.v[k] for k in ORDER[:i] if k not in ignore]
        below = [self.v[k] for k in ORDER[i + 1:] if k not in ignore]
        busy = [n[0] + n[1] for n in self.v[voice] if n[0] < t1 - 1e-9]
        if busy:
            t0 = max(t0, max(busy))
        if t0 >= t1 - 0.24:
            return [], 0
        r0, r1 = RANGE[voice]
        lo, hi = lo or r0, hi or r1
        if slots is None:
            slots = slots_between(t0, t1 - rest_after, others)
        prevn = [n for n in self.v[voice] if n[0] < t0 - 1e-9]
        prev = near if near is not None else (prevn[-1][2] if prevn else None)
        pv = (prevn[-1][0], prevn[-1][2]) if prevn and t0 - (prevn[-1][0] + prevn[-1][1]) < 0.01 else None
        start = None if prev is None else set(range(prev - 5, prev + 6))
        line, cost = generate(slots, self.H, others, lo, hi, role=role, above=above, below=below, start=start,
                              end=end, center=(prev if prev is not None else None), prev=pv,
                              pedals=[self.v[k] for k in ignore])
        self.put(voice, line)
        return line, cost


def compose():
    f = Fugue()
    SA = lambda key, B, sh=0: tmap(CS, Dm, key, shift=sh, dt=B)  # noqa: E731

    # ---------------- экспозиция
    f.marks.append((3.5, "Экспозиция"))
    f.put("A", subject(Dm, 4), "тема (D)")
    f.harm(subject_harmony(Dm, 4))
    f.put("S", answer(Dm, 12), "ответ (A)")
    f.harm(subject_harmony(Am, 12, tonal_from=Dm))
    f.put("A", SA(Am, 12)[:-1] + [(20, 0.5, 60)], "противосложение")  # к C — терция A минора
    # кодетта: A минор → D минор
    f.chords(Am, [(20, 4, "M", 0)])
    f.chords(Dm, [(21, 4, "m", 0), (22, 3, "m", 1), (23, 4, "7", 0)])
    f.free("S", 20, 23.5, end=None)
    f.free("A", 20.5, 24)
    f.put("T", subject(Dm, 24, -7), "тема (D)")
    f.harm(subject_harmony(Dm, 24))
    f.put("B", answer(Dm, 32, -14), "ответ (A)")
    f.harm(subject_harmony(Am, 32, tonal_from=Dm))
    f.put("S", f.to_chord(SA(Dm, 24, 7)), "противосложение")
    f.free("A", 24, 32)
    f.put("T", SA(Am, 32, -7), "противосложение")
    f.free("S", 32, 40)
    f.free("A", 32, 40)

    # ---------------- интермедия 1: «Grenzen meiner» восходит по секвенции, A минор → F мажор
    f.marks.append((40, "Интермедия 1"))
    f.H.add(40, Chord(9, "m", 4), Am)
    f.chords(Am, [(41, 0, "m", 0)])
    f.chords(F, [(42, 5, "m", 0), (44, 1, "m", 0), (46, 4, "7", 0), (47.5, 4, "7", 0)])
    head = lambda x, t, key: [(t, .75, x), (t + .75, .25, dmap(x, key, key, 1)),  # noqa: E731
                              (t + 1, .75, dmap(x, key, key, 2)), (t + 1.75, .25, dmap(x, key, key, 3))]
    f.put("A", head(60, 40, Am) + head(58, 44, F), "мотив головы")
    f.put("T", head(53, 42, F) + head(52, 46, F), "мотив головы")
    f.free("B", 40.0, 48, role="bass")
    f.free("S", 40, 46)
    f.free("A", 42, 44)

    # ---------------- среднее проведение 1: F мажор, сопрано
    f.marks.append((47.5, "Проведение в F"))
    f.put("S", subject(F, 48), "тема (F)")
    f.harm(subject_harmony(F, 48))
    f.put("A", SA(F, 48), "противосложение")
    f.free("B", 48, 56, role="bass")
    f.free("T", 48, 56)

    # ---------------- интермедия 2: хвост «meiner Welt» нисходит, F → G минор
    f.marks.append((56, "Интермедия 2"))
    f.chords(F, [(56, 4, "M", 0), (57, 0, "M", 0), (58, 3, "M", 0)])
    f.chords(Gm, [(59, 5, "M", 0), (60, 1, "hd7", 0), (61, 4, "7", 0), (62, 3, "m", 0), (63, 4, "7", 0),
                  (63.5, 0, "m", 0)])
    tail = lambda x, t, key: [(t, .75, x), (t + .75, .25, dmap(x, key, key, -1)),  # noqa: E731
                              (t + 1, .75, dmap(x, key, key, -2)), (t + 1.75, .25, dmap(x, key, key, -4))]
    f.put("S", tail(76, 56, F) + tail(74, 58, Gm) + [(60, .75, 72), (60.75, .25, 70), (61, .75, 69), (61.75, .25, 66)]
          + [(62, .75, 75), (62.75, .25, 74), (63, 1, 72)], "мотив хвоста")
    f.free("B", 56, 64, role="bass")
    f.free("A", 56, 64)

    # ---------------- среднее проведение 2: обращение темы в теноре, G минор (зеркало)
    f.marks.append((63.5, "Обращение (g)"))
    f.put("T", inversion(64), "обращение (g)")
    f.chords(Gm, [(64, 4, "M", 0), (65, 0, "m", 1), (66, 3, "m", 0), (67, 2, "M", 0), (68, 5, "M", 0),
                  (69, 6, "M", 0), (70, 2, "M", 0), (71, 4, "m", 0), (72, 0, "m", 0)])
    f.free("B", 64, 72, role="bass")
    f.free("S", 64, 72)
    f.free("A", 64, 72)

    # ---------------- интермедия 3: хвост нисходит секвенцией, G минор → A минор
    f.marks.append((72, "Интермедия 3"))
    f.chords(Gm, [(72, 0, "m", 0)])
    f.chords(Am, [(73, 2, "M", 0), (74, 5, "M", 0), (75, 1, "d", 0), (76, 4, "7", 0), (77, 0, "m", 0),
                  (78, 3, "m", 0), (79, 4, "7", 0)])
    f.put("S", tail(79, 72, Am) + tail(77, 74, Am) + tail(76, 76, Am) + tail(74, 78, Am)[:3]
          + [(79.75, .25, 68)], "мотив хвоста")
    f.free("A", 72, 80)
    f.free("B", 72, 79.5, role="bass", rest_after=0.0)

    # ---------------- среднее проведение 3: бас, A минор
    f.marks.append((79.5, "Проведение в a (бас)"))
    f.put("B", subject(Am, 80, -14), "тема (a)")
    f.harm(subject_harmony(Am, 80))
    f.put("T", SA(Am, 80, -7), "противосложение")
    f.free("S", 80, 88)
    f.free("A", 80, 88)

    # ---------------- интермедия 4: квинтовый круг к доминанте D минора
    f.marks.append((88, "Интермедия 4"))
    f.chords(Am, [(88, 4, "M", 0), (89, 0, "m", 0)])
    f.chords(Dm, [(90, 0, "m", 0), (91, 3, "M", 0), (92, 6, "M", 0), (93, 2, "M", 0), (94, 5, "M", 0),
                  (95, 4, "7", 0)])
    f.H.add(91, Chord(7, "7"), Dm)
    f.put("S", tail(72, 89, Am) + tail(71, 91, Cmaj) + tail(69, 93, Dm), "мотив хвоста")
    f.free("S", 88, 89, near=72)
    f.free("B", 88, 96, role="bass")
    f.free("T", 88, 95.5)
    f.free("A", 88, 95.5, rest_after=0.5)

    # ---------------- стретты: тема вступает, не дождавшись конца темы
    f.marks.append((95.5, "Стретта"))
    st = [("A", subject(Dm, 96)), ("B", subject(Dm, 101, -11)), ("T", subject(Dm, 108, -7)),
          ("S", subject(Dm, 114, 3))]
    for k, line in st:
        f.put(k, line, "стретта")
    for t, c, key, _ in auto_harmony([x[1] for x in st], Dm, 96, 123, 1.0):
        f.H.add(t, c, key)
    f.chords(Dm, [(95.5, 0, "m", 0), (100.5, 0, "m", 0)])
    f.free("S", 96, 113.5, rest_after=0.0)
    f.free("B", 96, 100.5, role="bass")
    f.free("T", 96, 107.5)
    f.free("A", 105, 123)
    f.free("B", 110, 123, role="bass")
    f.free("T", 117, 123)

    # ---------------- органный пункт на доминанте
    f.marks.append((123, "Органный пункт (A)"))
    f.chords(Dm, [(123, 4, "M", 0), (124, 0, "m", 2), (125, 4, "7", 0), (126, 3, "m", 2), (127, 4, "M", 0),
                  (128, 6, "d7", 0), (129, 4, "7", 0)])
    f.put("B", [(123, 7, 45)], "органный пункт")
    for k in ("S", "A", "T"):
        f.free(k, 123, 130, ignore=("B",))

    # ---------------- тема в увеличении в басе: границы мира — основание
    f.marks.append((130, "Увеличение (бас)"))
    aug = tmap(SUBJECT, Dm, Dm, shift=-14, dt=131, scale_t=2)
    aug[-1] = (aug[-1][0], 1.5, aug[-1][2])
    f.put("B", aug, "тема в увеличении")
    f.harm(subject_harmony(Dm, 131, scale_t=2))
    from counterpoint import candidates
    for t in range(131, 147):
        m = sounding(f.v["B"], t)
        if m is not None and m % 12 not in f.H.at(t)[1].pcs:
            c = min(((c, p) for c, p in candidates(Dm) if m % 12 in c.pcs), key=lambda x: x[1])[0]
            f.H.add(t, c, Dm)
    for k in ("S", "T", "A"):
        f.free(k, 130, 147)
    f.chords(Dm, [(147, 4, "M", 0)])
    for k in ("S", "A", "T"):
        f.free(k, 147, 149, rest_after=0.5 if k == "S" else 0.0)

    # ---------------- последнее проведение над тоническим органным пунктом; пикардийская терция
    f.marks.append((148.5, "Кода: тонический пункт"))
    f.put("S", subject(Dm, 149, 7)[:0] + subject(Dm, 149), "тема (последнее)")
    f.harm(subject_harmony(Dm, 149))
    f.put("B", [(148.5, 8.5, 38)], "органный пункт")
    for k in ("A", "T"):
        f.free(k, 149, 157, ignore=("B",))
    f.H.add(157, Chord(2, "M"), Key(2, "major"))
    f.v["S"] = [n if n[0] < 157 - 1e-9 else (n[0], 6, n[2]) for n in f.v["S"]]  # «Welt» — A4, квинта ре мажора
    for k, m in {"A": 66, "T": 62, "B": 38}.items():
        f.v[k] = [n for n in f.v[k] if n[0] < 157 - 1e-9]
        f.put(k, [(157, 6, m)])
    f.v["B"] = [n if n[0] != 148.5 else (n[0], 8.5, n[2]) for n in f.v["B"]]
    f.tie_repeats()
    return f


if __name__ == "__main__":
    import json
    import os
    f = compose()
    for k in ORDER:
        show(k, f.v[k])
    problems = check(f.v, f.H)
    out = dict(voices=f.v, marks=f.marks, roles=f.roles, problems=[(t, p) for t, p in problems])
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "fugue.json"), "w") as fh:
        json.dump(out, fh, ensure_ascii=False)
