"""events.json (прогон protocol.html) → cues.json для immollimma."""
import json, math, sys
d = json.load(open(sys.argv[1])); ev = d["events"]
MOOD = {
 "I": ("тьма; счётчик сна бежит, замедляется и встаёт", .05), "II": ("склеп: узник-звезда загорается, тессеракт чертится ребро за ребром", .3),
 "III": ("свет идёт по шинам, глифы вписываются в стену", .35), "IV": ("сердце гробницы учащается", .5),
 "V": ("зал проступает из тьмы", .5), "VI": ("легион просыпается ряд за рядом, от горизонта к зрителю", .7),
 "VII": ("имя повелителя: пять глифов", .75), "VIII": ("давление в склепе: узник рвётся, обереги держат", .9),
 "IX": ("приказ: белая волна через всю гробницу", 1.0), "X": ("легион уходит фазовым сдвигом, ближние ряды первыми", .6),
 "XI": ("свет отступает к склепу, всё гаснет в обратном порядке", .3), "XII": ("новый сон: счётчик с нуля, тьма", .05)}
stages = [e for e in ev if e["type"] == "stage"]
cues = []
for i, e in enumerate(stages):
    end = stages[i + 1]["t"] if i + 1 < len(stages) else d["rite_len"]
    m, it = MOOD[e["num"]]
    cues.append(dict(t=e["t"], end=end, label=f'{e["num"]} {e["name"]}', kind="section", mood=m, intensity=it))
KIND = {"counter_stop": ("hit", .4), "star_ignites": ("hit", .5), "command": ("hit", 1.0), "vault_pressure": ("swell", .9),
        "legion_wave": ("accent", .6), "legion_depart": ("accent", .5), "retract": ("transition", .3), "counter_zero": ("accent", .1)}
for e in ev:
    if e["type"] == "cue":
        n = e["name"]; k, it = KIND.get(n, ("hit" if n.startswith("name_") else "accent", .6 if n.startswith("name_") else .3))
        cues.append(dict(t=e["t"], label=n, kind=k, intensity=it))
cues.append(dict(t=92.4, end=96.0, label="тишина до повтора", kind="silence", intensity=0))
cues.sort(key=lambda c: (c["t"], c["kind"] != "section"))
rows = {}
for n in d["niches"]:
    if n["bad"]: continue
    r = rows.setdefault(n["row"], [99, 99])
    if n["ta"] < r[0]: r[0], r[1] = n["ta"], n["tg"]   # центральная ниша ряда: просыпается первой
# тики счётчика: смена разряда сотен в первой стадии (значение 65e6 + 4800·(1−e^(−(t−1.2)/1.7)))
ticks = []
for k in range(1, 48):
    q = 1 - 100 * k / 4800
    if q <= 0: break
    tt = 1.2 - 1.7 * math.log(q)
    if tt < 7.2: ticks.append(round(tt, 4))
out = dict(version=1, duration_s=d["rite_len"], video="protocol.html (анимация, цикл 96 с)", cues=cues,
           hearts=[e["t"] for e in ev if e["type"] == "heart"],
           rows=[{"row": k, "wake": round(v[0], 4), "depart": round(v[1], 4)} for k, v in sorted(rows.items())],
           bad_niches=sorted(round(n["ta"], 4) for n in d["niches"] if n["bad"]),
           counter_ticks=ticks, cells=d["cells"],
           grid=dict(bpm=100, meter="4/4", bar_s=2.4, note="удары сердца — каждые 1,2 с (две доли) с 28,8 по 57,6; ключевые метки кратны 0,3 с"),
           loop=True)
json.dump(out, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
print(len(cues), "меток;", len(out["rows"]), "рядов;", len(out["bad_niches"]), "неисправных;", len(ticks), "тиков")
print("rows:", [(r["row"], r["wake"], r["depart"]) for r in out["rows"]])
