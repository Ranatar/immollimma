"""Ainulindalë — нотный текст (темп 60: доля = секунда, время — в долях от начала пьесы).

Голоса Великой Музыки: S, A, T, B (свободные голоса — поиск по гармоническому плану, counterpoint.py);
отдельно — обрывки одиноких голосов, унисон Мелькора, рябь третьей темы, видение, Эа.

    python3 music.py          — печать проверок голосоведения → music.json
"""
import json
import os

from counterpoint import Chord, Harmony, Key, auto_harmony, ch, check, dmap, generate, nm, slots_between, tmap

HERE = os.path.dirname(os.path.abspath(__file__))
D, A, Dm = Key(2, "major"), Key(9, "major"), Key(2, "minor")

# Тема Илуватара (D мажор, D4–D5): квинта вверх, опевание, ход вниз, скачок к B и подъём к верхней D
THEME = [(0, 2, 62), (2, 2, 69), (4, 1, 71), (5, 1, 69), (6, 1.5, 67), (7.5, .5, 66),
         (8, 1, 64), (9, 1, 66), (10, 2, 71), (12, 1, 69), (13, 1, 73), (14, 2, 74)]
# гармония темы по долям: I I vi I6 IV ii I6 vi IV V V I
PLAN = [(0, 0, "M", 0), (2, 0, "M", 0), (4, 5, "m", 0), (5, 0, "M", 1), (6, 3, "M", 0), (8, 1, "m", 0),
        (9, 0, "M", 1), (10, 5, "m", 0), (11, 3, "M", 0), (12, 4, "M", 0), (14, 0, "M", 0)]
# в миноре: i i VI i6 iv ii°→iv i6 VI iv V V i
PLAN_MIN = [(0, 0, "m", 0), (2, 0, "m", 0), (4, 5, "M", 0), (5, 0, "m", 1), (6, 3, "m", 0), (8, 1, "d", 1),
            (9, 0, "m", 1), (10, 5, "M", 0), (11, 3, "m", 0), (12, 4, "M", 0), (14, 0, "m", 0)]
MELKOR = [(0, 1, 63), (1, 1, 63), (2, .5, 58), (2.5, .5, 61), (3, 1, 63)]  # E♭ E♭ B♭ D♭ E♭ — такт за тактом

ORDER = ["S", "A", "T", "B"]
RANGE = {"S": (60, 81), "A": (53, 74), "T": (46, 69), "B": (36, 60)}


def theme(key, t0, shift=0, minor_leading=False):
    notes = tmap(THEME, D, key, shift=shift, dt=t0)
    if minor_leading:  # в миноре вводный тон перед финальной D — повышенный (C♯)
        notes = [(t, d, m + 1 if abs(t - (t0 + 13)) < 1e-9 else m) for t, d, m in notes]
    return notes


def inversion(t0, shift_deg=0):
    """вторая тема — «подобная и неподобная»: диатоническое обращение Темы вокруг D"""
    d0 = D.degree(62)[0]
    out = []
    for t, d, m in THEME:
        deg = D.degree(m)[0]
        out.append((t0 + t, d, D.pitch(2 * d0 - deg + shift_deg)))
    return out


def plan(key, t0, spec=PLAN):
    return [(t0 + t, ch(key, deg, q, inv), key) for t, deg, q, inv in spec]


class Comp:
    def __init__(self):
        self.v = {k: [] for k in ORDER}
        self.H = Harmony()
        self.roles = []

    def put(self, voice, notes, role=None):
        if notes:
            t_new = notes[0][0]
            self.v[voice] = [n if n[0] + n[1] <= t_new + 1e-9 or n[0] >= t_new - 1e-9 else (n[0], t_new - n[0], n[2])
                             for n in self.v[voice]]
        self.v[voice].extend(notes)
        self.v[voice].sort()
        if role and notes:
            self.roles.append((notes[0][0], notes[-1][0] + notes[-1][1], voice, role))

    def harm(self, segs):
        for s in segs:
            self.H.add(*s)

    def free(self, voice, t0, t1, *, role="upper", end=None, ignore=(), rest_after=0.0, seed=0, pace=None):
        others = [self.v[k] for k in ORDER if k != voice and k not in ignore]
        i = ORDER.index(voice)
        above = [self.v[k] for k in ORDER[:i] if k not in ignore]
        below = [self.v[k] for k in ORDER[i + 1:] if k not in ignore]
        busy = [n[0] + n[1] for n in self.v[voice] if n[0] < t1 - 1e-9]
        if busy:
            t0 = max(t0, max(busy))
        if t0 >= t1 - 0.24:
            return []
        lo, hi = RANGE[voice]
        slots = (slots_between(t0, t1 - rest_after, others, seed=seed) if pace is None
                 else slow_slots(t0, t1 - rest_after, pace, seed))
        prevn = [n for n in self.v[voice] if n[0] < t0 - 1e-9]
        prev = prevn[-1][2] if prevn else None
        pv = (prevn[-1][0], prevn[-1][2]) if prevn and t0 - (prevn[-1][0] + prevn[-1][1]) < 0.01 else None
        start = None if prev is None else set(range(prev - 5, prev + 6))
        line, _ = generate(slots, self.H, others, lo, hi, role=role, above=above, below=below, start=start, end=end,
                           center=prev, prev=pv, pedals=[self.v[k] for k in ignore])
        self.put(voice, line)
        return line

    def tie_repeats(self):
        for k in ORDER:
            out = []
            for n in self.v[k]:
                if out and out[-1][2] == n[2] and abs(out[-1][0] + out[-1][1] - n[0]) < 1e-6 and n[1] < 4:
                    out[-1] = (out[-1][0], out[-1][1] + n[1], n[2])
                else:
                    out.append(n)
            self.v[k] = out


SLOW = {"calm": ([[1.0, 1.0], [2.0], [1.0, 0.5, 0.5], [1.5, 0.5]], [0.35, 0.25, 0.2, 0.2]),
        "solemn": ([[2.0], [1.0, 1.0], [2.0]], [0.4, 0.3, 0.3])}


def slow_slots(t0, t1, pace, seed=0):
    """медленный ритм для третьей темы: по две доли — половинные, четверти, редкие восьмые; слоты не через такт"""
    import random
    rng = random.Random(int(t0 * 8) * 977 + seed)
    pats, w = SLOW[pace]
    out, t = [], t0
    while t < t1 - 1e-9:
        if abs(t - round(t)) > 1e-9 or t1 - t < 2 - 1e-9:
            step = min(1.0 if abs(t - round(t)) < 1e-9 else 0.5, t1 - t)
            out.append((t, step))
            t += step
            continue
        for d in rng.choices(pats, weights=w)[0]:
            out.append((t, d))
            t += d
    return out


def chord_set(key, t0, items):
    """items: [(t, Chord)] — явные аккорды (неаполитанский и пр.)"""
    return [(t0 + t, c, key) for t, c in items]


def compose():
    c = Comp()
    marks = []

    # ---------------- I. Пустота и одинокие голоса (0–20): голова темы в чужих тональностях, порознь
    HEAD = [(0, 1.2, 0), (1.2, 1.2, 7), (2.4, .8, 9), (3.2, 1.6, 7)]
    solos = []
    for inst, t0, base in (("fl_sus", 1.0, 74), ("cl_sus", 5.4, 65), ("vla_sus", 9.6, 59), ("harp", 12.2, 76),
                           ("hn_sus", 14.6, 55)):
        for t, d, iv in HEAD:
            solos.append(dict(inst=inst, t=t0 + t, d=d, m=base + iv))
    marks.append((0, "I Пустота и одинокие голоса"))

    # ---------------- II. Тема Илуватара (20–36) и экспозиция Великой Музыки (36–84)
    marks.append((20, "II Тема Илуватара"))
    c.put("A", theme(D, 20), "тема (D)")
    c.harm(plan(D, 20))
    marks.append((36, "III Великая Музыка"))
    c.put("S", theme(A, 36), "ответ (A)")
    c.harm(plan(A, 36))
    c.free("A", 36, 52)
    c.put("B", theme(D, 52, shift=-14), "тема (D, бас)")
    c.harm(plan(D, 52))
    c.free("S", 52, 68)
    c.free("A", 52, 68, seed=1)
    c.put("T", theme(D, 68, shift=-7), "тема (D, тенор), tutti")
    c.harm(plan(D, 68))
    c.free("S", 68, 84, seed=2)
    c.free("A", 68, 84, seed=3)
    c.free("B", 68, 84, role="bass", seed=4)

    # ---------------- IV. Разлад (84–112): сопрано держит тему, остальные голоса втягиваются в унисон Мелькора
    marks.append((84, "IV Разлад Мелькора"))
    c.put("S", theme(D, 84), "тема (D) против разлада")
    c.harm(plan(D, 84))
    c.free("A", 84, 92, seed=5)          # с 92 альт — в унисоне Мелькора
    c.free("T", 84, 88, seed=6)          # с 88 тенор — в унисоне
    c.free("B", 84, 96, role="bass", seed=7)  # с 96 бас — в унисоне
    entrain = {"T": 88, "A": 92, "B": 96}

    # ---------------- V. Вторая тема (112–136): обращение темы, затем смятение — голоса умолкают
    marks.append((112, "V Вторая тема"))
    sec = inversion(112, shift_deg=7)    # от D5 вниз
    c.put("S", sec, "вторая тема (обращение)")
    h2 = auto_harmony([sec], D, 112, 128)
    c.harm([(t, cc, k) for t, cc, k, _ in h2])
    c.free("A", 112, 128, seed=8)
    c.free("T", 112, 128, seed=9)
    c.free("B", 112, 128, role="bass", seed=10)
    head2 = [n for n in inversion(128, shift_deg=0) if n[0] < 128 + 8]
    c.put("T", head2, "голова второй темы")
    c.harm([(t, cc, k) for t, cc, k, _ in auto_harmony([head2], D, 128, 136)])
    c.free("S", 128, 134.5, seed=11)     # голоса умолкают один за другим
    c.free("A", 128, 131, seed=12)
    c.free("B", 128, 132.5, role="bass", seed=13)
    marks.append((124, "Va Разлад поднимается снова"))

    # ---------------- VI. Третья тема (136–176)
    marks.append((136, "VI Третья тема"))
    # 136–144: рябь — арфа и скрипка соло (рукописно, см. ripple)
    # 144–160: Тема в миноре, «глубокая, широкая, медленная»: в теноре, остальные — свободно
    c.put("T", theme(Dm, 144, shift=-7), "третья тема (d)")
    c.harm(plan(Dm, 144, PLAN_MIN))
    c.free("S", 144, 160, seed=24, pace="calm")
    c.free("A", 144, 160, seed=15, pace="calm")
    c.free("B", 144, 160, role="bass", seed=16, pace="solemn")
    # 160–176: ноты Мелькора, вобранные в узор: бас E♭–B♭–C♯–D в увеличении = N6 – VI – V6 – I
    marks.append((160, "VIb Вбирание: E♭–B♭–C♯–D"))
    absorb = [(160, 4, 51), (164, 4, 46), (168, 4, 49), (172, 4, 50)]
    c.put("B", absorb, "мотив Мелькора в басе")
    c.harm(chord_set(Dm, 0, [(160, Chord(3, "M", 7)), (164, Chord(10, "M")), (168, Chord(9, "M", 1)),
                             (170, Chord(9, "7", 1)), (172, Chord(2, "M"))]))
    c.free("S", 160, 176, seed=17, pace="calm")
    c.free("A", 160, 176, seed=18, pace="solemn")
    c.free("T", 160, 176, seed=19, pace="solemn")
    marks.append((176, "VII Последний аккорд"))

    c.tie_repeats()
    print("проверка голосоведения:")
    probs = check(c.v, c.H)
    # унисон Мелькора: такт за тактом от 84 до 172
    melkor = []
    for bar in range(84, 172, 4):
        melkor += [(bar + t, d, m) for t, d, m in MELKOR]
    harmony = [(s[0], s[1].root, s[1].qual, sorted(s[1].pcs), s[2].tonic, s[2].mode) for s in c.H.seg]
    marks += [(184, "VIII Видение: отзвук в водах"), (210, "IX Эа")]
    return dict(voices=c.v, roles=c.roles, solos=solos, melkor=melkor, entrain=entrain, marks=marks,
                harmony=harmony, problems=[(t, p) for t, p in probs])


if __name__ == "__main__":
    res = compose()
    for k in ORDER:
        v = res["voices"][k]
        print(k, len(v), "нот;", " ".join(nm(n[2]) for n in v[:12]), "…")
    print(len(res["problems"]), "замечаний")
    json.dump(res, open(os.path.join(HERE, "music.json"), "w"), ensure_ascii=False, indent=0)
