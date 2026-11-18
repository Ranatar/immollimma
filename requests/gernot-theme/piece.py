#!/usr/bin/env python3
"""«Холодный мир» — тема Гернота (≈ 2:05). Инвариант персонажа — роль против человека: через мальчика говорят
другие (боги и конклав — неразличимо), его истина — не о его мире; под ролью — свой голос, слабый и упрямый.

Материал — одна формула культа: речитация на тоне фа# (выросла из головы темы мира опенинга: F# F# E F#), 16 долей,
16-я пуста — тоники си культ не достигает (как облик Рейха в опенинге, где фраза шкатулки обрывается до тоники).
Верхний изгиб — на ля, а не на соль: в каноне через долю соль против фа# давала полутон; с ля между ведущим и
ведомым остаются только целые тоны (ми/фа#, ре/ми) — гетерофония обряда, а не фальшь.

Форма: огонь (педаль, тамтам) — обряд (ведущий один: тихий орган в унисон с засурдиненной валторной, низкие
струнные) — рука на руке (Гернот повторяет каноном через долю на две октавы выше флажолетами) — пророчество
(речитация ускоряется, вступления копятся стреттой, проступает тень формулы на полутон выше — до минор, тональность
войны в опенинге) — обрыв, тишина — свой голос (формула в метре у скрипки соло, рабочий шаг пиццикато; гармония
песенная, по тактам: Bm | Bm | Bm | G Em — без V–I) — ведущий начинает формулу, мальчик не повторяет — кларнет один
заполняет 16-ю долю: ми – ре – до# – си, без аккорда.

    python3 -m kit run requests/gernot-theme/piece.py --parts
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from kit.devices import Composer  # noqa: E402
from kit.events import Piece  # noqa: E402

BPM = 60
SPB = 60.0 / BPM

# формула культа (доля, длительность, midi) на фа# малой октавы (54); 16-я доля (15–16) пуста
D, E, Fs, A = 50, 52, 54, 57
H1 = [(0, .5, D), (.5, .5, E), (1, 1, Fs), (2, .5, Fs), (2.5, .5, Fs), (3, 1, Fs),
      (4, .5, Fs), (4.5, .5, A), (5, 1, Fs), (6, 1, E), (7, 1, Fs)]
H2 = [(8, 1, Fs), (9, .5, Fs), (9.5, .5, Fs), (10, 1, Fs), (11, 1, E), (12, 1, D), (13, 2, E)]
FORMULA = H1 + H2
# его окончание: та же формула, но последний ми — на долю, и 16-я доля заполнена: ре – до# – си
OWN_END = H1 + H2[:-1] + [(13, 1, E), (14, .5, D), (14.5, .5, D - 1), (15, 1, D - 3)]


def tr(notes, semis=0, dt=0.0, scale=1.0):
    return [(dt + b * scale, d * scale, m + semis) for b, d, m in notes]


class G:
    def __init__(self):
        self.p = Piece("«Холодный мир» — тема Гернота", bpm=BPM, meter=(4, 4), key="B minor", seed=16)
        self.p.meta["subtitle"] = "формула культа и свой голос"
        self.p.meta["sends"] = {"strings": 0.45, "brass": 0.4, "winds": 0.35, "perc": 0.4, "keys": 0.5}
        self.c = Composer(self.p, lib="vsco", seed=15)
        self.slow = []          # (доля0, доля1, множитель длительности)
        self.cut = None         # доля обрыва: всё, что звучит дальше, срезается
        self.level = 1.0        # общий уровень раздела (свой голос — тише вершины пророчества)

    def perf(self, beat):
        s = 0.0
        for b0, b1, f in sorted(self.slow):
            if beat <= b0:
                break
            s += (min(beat, b1) - b0) * (f - 1)
        return (beat + s) * SPB

    def n(self, inst, m, beat, dur, part, legato=0.96, **kw):
        if self.cut is not None:
            lo, hi = self.cut
            if lo <= beat < hi:
                return None
            if beat < lo < beat + dur:
                dur = lo - beat
                kw["release"] = 0.15
                legato = 1.0
        kw.setdefault("release", 0.5)
        kw["gain"] = kw.get("gain", 1.0) * self.level
        t0, t1 = self.perf(beat), self.perf(beat + dur)
        e = self.p.note(inst, m, t0, max(0.06, (t1 - t0) * legato), part=part, **kw)
        e["wt"], e["wdur"] = beat * SPB, dur * SPB
        return e

    def voice(self, inst, notes, part, vel, gain, stress=0.08, **kw):
        """речитация: начальные и изгибные звуки чуть сильнее, повторы фа# — ровнее и тише"""
        prev = None
        for b, d, m in notes:
            acc = stress if (m != prev) else 0.0
            self.n(inst, m, b, d, part, vel=vel + acc, gain=gain * (1 + acc), **kw)
            prev = m

    def fx(self, kind, beat, **kw):
        return self.c.fx(kind, self.perf(beat), bus="perc", **kw)


# ===================================================================== голоса

def alien(o, notes, vel=0.42, gain=0.32, with_strings=True):
    """чужой голос — боги и конклав неразличимо: тихий орган (8′ и 4′) в унисон с засурдиненной валторной;
    низкие струнные держат тот же звук октавой ниже — опора баса"""
    o.voice("org_quiet", notes, "Organo", vel=vel, gain=gain, attack=0.05)
    o.voice("org_quiet", tr(notes, 12), "Organo", vel=vel - 0.08, gain=gain * 0.55, attack=0.05)
    o.voice("hn_mute", notes, "Corno con sord.", vel=vel, gain=gain * 0.9, attack=0.06)
    if with_strings:
        o.voice("cb_sus", tr(notes, -12), "Contrabassi", vel=vel - 0.04, gain=gain * 0.8, attack=0.12, stress=0.0)


def boy_role(o, notes, vel=0.36, gain=0.26):
    """Гернот в роли: флажолеты скрипок на две октавы выше ведущего — бесцветный «холодный свет»"""
    o.voice("vln_harm", tr(notes, 24), "Violini (flag.)", vel=vel, gain=gain, attack=0.08, stress=0.05)


# ===================================================================== разделы

def fire(o, t0):
    """огонь: педаль органа фа# вырастает из тишины; тамтам и скрежет гонга — обряд обновления огня"""
    o.n("org_quiet", 42, t0, 4, "Organo", vel=0.35, gain=0.28, attack=2.5, release=0.3)
    o.n("cb_sus", 30, t0 + 1, 3, "Contrabassi", vel=0.36, gain=0.3, attack=2.0, release=0.3)
    o.fx("tamtam", t0, gain=0.07)
    o.fx("gong_scrape", t0 + 2.2, gain=0.05)


def ritual(o, t0):
    """обряд: формула одна, ведущий без отклика; 16-я доля пуста — в ней только хвост тамтама"""
    alien(o, tr(FORMULA, 0, t0))
    o.n("org_quiet", 42, t0, 15, "Organo", vel=0.33, gain=0.22, attack=0.5, release=0.3)  # педаль: тот же фа#
    o.fx("tamtam", t0 + 15, gain=0.035)


def hand_on_hand(o, t0):
    """рука на руке: мальчик повторяет каждую фразу через долю на две октавы выше; ведущий чуть тише —
    его ведут, но слышно, что звук один"""
    alien(o, tr(FORMULA, 0, t0), vel=0.4, gain=0.28)
    o.n("org_quiet", 42, t0, 15, "Organo", vel=0.33, gain=0.2, attack=0.5, release=0.3)
    boy_role(o, tr(FORMULA, 0, t0 + 1))
    o.fx("tamtam", t0 + 15.5, gain=0.03)


def prophecy(o, t0):
    """пророчество: три формулы подряд, всё быстрее; к ведущему и мальчику добавляются вступления через
    полдоли и полторы (флажолеты виолончелей — у альтов записаны только от до5, засурдиненная труба, виолончели), с второй формулы проступает тень —
    та же формула на полутон выше (до минор) флажолетами альтов и тихим органом сверху; к третьей — тремоло
    низких струнных на фа# и тень громче. Обрыв в начале пустой 16-й доли третьей формулы."""
    for k in range(3):
        s = t0 + 16 * k
        v = 0.42 + 0.06 * k
        alien(o, tr(FORMULA, 0, s), vel=v, gain=0.3 + 0.05 * k)
        boy_role(o, tr(FORMULA, 0, s + 1), vel=0.38 + 0.05 * k, gain=0.27 + 0.04 * k)
        o.voice("vc_harm", tr(FORMULA, 12, s + .5), "Violoncelli (flag.)", vel=0.34 + 0.05 * k, gain=0.18 + 0.05 * k,
                attack=0.06)
        if k >= 1:
            o.voice("tpt_mute", tr(FORMULA, 12, s + 2), "Tromba con sord.", vel=0.36 + 0.06 * k,
                    gain=0.16 + 0.06 * k, attack=0.05)
            o.voice("vc_sus", tr(FORMULA, 0, s + 1.5), "Violoncelli", vel=0.4 + 0.05 * k, gain=0.12 + 0.03 * k,
                    attack=0.08)
            # тень: истина из другого мира — на полутон выше, со своим запаздыванием (две с половиной доли)
            o.voice("vln_harm", tr(FORMULA, 25, s + 2.5), "Ombra (flag.)", vel=0.3 + 0.06 * k,
                    gain=0.1 + 0.08 * (k - 1), attack=0.1, stress=0.0)
            o.voice("org_quiet", tr(FORMULA, 37, s + 2.5), "Ombra (flag.)", vel=0.28, gain=0.05 + 0.05 * (k - 1),
                    attack=0.1, stress=0.0)
        if k == 2:
            o.n("cb_trem", 42, s, 15, "Contrabassi", vel=0.45, gain=0.26, attack=6.0)
            o.n("vc_trem", 54, s + 4, 11, "Violoncelli", vel=0.45, gain=0.2, attack=5.0)
        o.n("org_quiet", 42, s, 16, "Organo", vel=0.36 + 0.04 * k, gain=0.22 + 0.04 * k, attack=0.4, release=0.3)


def own_voice(o, t0):
    """свой голос: формула в метре у скрипки соло, на октаву ниже роли — «рабочий шаг»; бас пиццикато по
    основным тонам и квинтам, виолончели держат основной тон ниже темы. Гармония по тактам: Bm | Bm | Bm | G Em.
    В конце он ещё останавливается на ми — 16-я доля пуста."""
    mel = tr(FORMULA, 12, t0)
    o.voice("vln_solo", mel, "Violino solo", vel=0.5, gain=0.42, stress=0.06, attack=0.04)
    roots = [(0, 47), (4, 47), (8, 47), (12, 43), (13, 40)]
    for i, (b, r) in enumerate(roots):
        d = (roots[i + 1][0] if i + 1 < len(roots) else 15) - b
        o.n("vc_sus", r, t0 + b, d, "Violoncelli", vel=0.36, gain=0.24, attack=0.3, release=0.6)
    steps = [(0, 35), (2, 42), (4, 35), (6, 35), (8, 35), (10, 42), (12, 31), (13, 28)]  # на 6-й доле в теме ми —
    # не фа# в басу (секунда), а основной тон
    for b, r in steps:
        o.n("cb_pizz", r, t0 + b, 1, "Contrabassi", vel=0.55, gain=0.5, release=0.8)
    for b in (1, 3, 5, 7, 9, 11):  # рабочий шаг: слабые доли — тише, у виолончелей
        o.n("vc_pizz", 47 if b < 12 else 43, t0 + b, 1, "Violoncelli pizz.", vel=0.4, gain=0.22, release=0.5)


def refusal(o, t0):
    """ведущий начинает формулу (ре – ми – фа#… ) и ждёт отклика; мальчик молчит"""
    alien(o, tr(H1[:4], 0, t0), vel=0.4, gain=0.3)
    o.n("org_quiet", 54, t0 + 2, 1.5, "Organo", vel=0.36, gain=0.22, release=0.8)


def to_tonic(o, t0):
    """кларнет один: формула в метре, первую половину ещё держит пиццикато, вторую — никто; окончание
    заполняет 16-ю долю: ми – ре – до# – си; си тянется и гаснет, без аккорда"""
    mel = tr(OWN_END, 12, t0)
    *body, last = mel
    o.voice("cl_sus", body, "Clarinetto", vel=0.48, gain=0.46, stress=0.05, attack=0.05)
    b, d, m = last
    o.n("cl_sus", m, b, 6, "Clarinetto", vel=0.42, gain=0.4, attack=0.05, release=2.5)
    for b2, r in [(0, 35), (2, 42), (4, 35), (6, 35)]:
        o.n("cb_pizz", r, t0 + b2, 1, "Contrabassi", vel=0.5 - 0.03 * b2 / 2, gain=0.44 - 0.04 * b2 / 2,
            release=0.8)
    o.n("vc_sus", 47, t0, 8, "Violoncelli", vel=0.34, gain=0.2, attack=0.3, release=1.2)


# замер `--parts` без баланса: кларнет −27.0, виолончели −28.4, орган −37.1, скрипка соло −37.8, валторна −38.7,
# труба −40.3, флажолеты скрипок −45.6, альтов −46.0, тень −48.6, контрабасы −52.0, пиццикато виолончелей −56.2 LUFS:
# (четвёртый замер: стретта виолончелей −31 — громче ведущего; вдвое тише)
# (второй замер: тень −50, флажолеты виолончелей −29 — громче темы, пиццикато −46.5, контрабасы −37.5 при теме −30 — добавлено)
# свой голос скрипки на 10 дБ тише кларнета, мальчик в роли почти не слышен, басы утонули; тамтам на 20 дБ громче всего
BAL = {"Clarinetto": -3, "Violino solo": +8, "Organo": +3, "Corno con sord.": +2, "Violini (flag.)": +10,
       "Violoncelli (flag.)": -8, "Ombra (flag.)": +10, "Contrabassi": +18, "Violoncelli pizz.": +18, "Violoncelli": -3}


def build(ctx):
    o = G()
    # доли: огонь 0–4 | обряд 4–20 | рука на руке 20–36 | пророчество 36–84 (обрыв на 83) | тишина 83–87 |
    #       свой голос 87–103 | не повторяет 103–109 | до си 109–125 (+6)
    o.slow += [(0, 4, 1.2), (4, 36, 1.15),
               (36, 52, 1.0), (52, 68, 0.84), (68, 84, 0.7),
               (87, 109, 0.86), (109, 120, 0.86), (120, 131, 1.15)]
    plan = [(0, "Огонь"), (4, "Обряд"), (20, "Рука на руке"), (36, "Пророчество"), (83, "Обрыв"),
            (87, "Свой голос"), (103, "Не повторяет"), (109, "До си")]
    fire(o, 0)
    ritual(o, 4)
    hand_on_hand(o, 20)
    o.cut = (83, 87)
    prophecy(o, 36)
    o.cut = None
    o.level = 0.5  # третий замер: свой голос (−15 dBFS) звучал громче вершины пророчества (−20) — он mp, не кульминация
    own_voice(o, 87)
    o.level = 1.0
    refusal(o, 103)
    o.level = 0.5
    to_tonic(o, 109)
    o.p.balance(BAL)
    for bt, label in plan:
        o.p.mark(o.perf(bt), label)["wt"] = bt * SPB
    o.p.meta["beats"] = 131
    o.p.meta["length"] = o.perf(131) + 4
    return o.p
