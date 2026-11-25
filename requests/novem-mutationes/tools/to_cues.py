"""events.json (журнал прогона novem.html) → cues.json для immollimma.
Разделы — девять стадий; удары — перемены закона, каскады, очи, точка, исчезновение; document — надписи
с окнами читаемости латиницей; отдельно: mutations (n, длительность волны), cascades, legible, eyes."""
import json, sys
d = json.load(open(sys.argv[1])); ev = d["events"]
MOOD = {
 "I": ("тьма; загорается точка света", .03, "точка 0.4"),
 "II": ("из точки вырастает кристалл", .25, "рост 2–14; надпись «In principio erat aenigma» читается 5.6–8.8"),
 "III": ("закон утверждается: строгая мозаика, первые нити", .4, "нити 15.2 и 17.6; «Lex una est» (ложь) 17.6–20.4"),
 "IV": ("девять перемен закона, всё чаще (интервалы 7.2 → 1.6)", .7, "n: 7, 9, 11, 5, 9, 7, 11, 5, 9; девятая — возврат к первому закону"),
 "V": ("откровение: сдвиги сходятся, мозаика строго девятикратна; девять нитей — нонаграмма; загадка и её разгадка-анаграмма", .8, "Quid est veritas? → Est vir qui adest (буквы едут 64.8–66.6)"),
 "VI": ("Око: большое в центре, девять малых в вершинах нонаграммы", .6, "большое 66.4–76.0; малые 68.0 + 0.4·i"),
 "VII": ("буря: девять каскадов по очереди, всё переворачивается", 1.0, "каскады 74.4 + 0.8·j, по 3.2 с"),
 "VIII": ("ничего не изменилось: мозаика в точности прежняя", .35, "«Omnia mutata sunt» (ложь)"),
 "IX": ("возврат: симметрия распадается, кристалл сворачивается в точку", .15, "ромбы счётчика гаснут 88.8 + 0.8·i; последний ромб гаснет 102.4; тьма до 108.8"),
}
cues = []
stages = [e for e in ev if e["type"] == "stage"]
for i, e in enumerate(stages):
    end = stages[i + 1]["t"] if i + 1 < len(stages) else d["rite_len"]
    m, it, note = MOOD[e["num"]]
    cues.append(dict(t=e["t"], end=end, label=f'{e["num"]} {e["name"]}', kind="section", mood=m, intensity=it, note=note))
for e in ev:
    if e["type"] == "mutation":
        cues.append(dict(t=e["t"], label=f'перемена {e["index"]} (n={e["n"]})', kind="hit", intensity=.5 + .05 * e["index"], note=f'волна {e["dur"]} с'))
    elif e["type"] == "caption":
        cues.append(dict(t=e["t"], label=e["text"], kind="document", intensity=.4,
                         note=(f'читается {e["legible"][0]}–{e["legible"][1]}' if e["legible"] else "только шифр")
                         + (f'; анаграмма в {e["anagram_at"]} → {e["anagram"]}' if e.get("anagram") else "")))
    elif e["type"] == "eye" and e["big"]:
        cues.append(dict(t=e["t"], label="Око открывается", kind="hit", intensity=.8))
for t, lab, k, it in [(0.4, "точка света", "accent", .2), (60.8, "сдвиги сходятся", "swell", .8), (64.0, "мозаика девятикратна", "accent", .7),
                      (84.0, "буря обрывается", "accent", .6), (102.4, "последний ромб гаснет", "accent", .2)]:
    cues.append(dict(t=t, label=lab, kind=k, intensity=it))
cues.append(dict(t=105.6, end=d["rite_len"], label="тишина до повтора", kind="silence", intensity=0))
cues.sort(key=lambda c: (c["t"], c["kind"] != "section"))
out = dict(version=1, duration_s=d["rite_len"], video="novem.html (анимация, цикл 108,8 с)", cues=cues, loop=True,
           mutations=[dict(t=e["t"], n=e["n"], dur=e["dur"], index=e["index"]) for e in ev if e["type"] == "mutation"],
           cascades=[dict(t=e["t"], family=e["family"], dur=e["dur"]) for e in ev if e["type"] == "cascade"],
           captions=[dict(t=e["t"], text=e["text"], until=e["until"], legible=e["legible"], anagram=e.get("anagram"), anagram_at=e.get("anagram_at")) for e in ev if e["type"] == "caption"],
           eyes=[dict(t=e["t"], big=e["big"], until=e["until"]) for e in ev if e["type"] == "eye"],
           threads=[dict(t=e["t"], until=e["until"], family=e["family"]) for e in ev if e["type"] == "thread"],
           grid=dict(bpm=75, meter="4/4", beat_s=.8, note="перемены, стадии, каскады и очи — на долях 0,8 с; надписи — на шестнадцатых 0,2 с"))
json.dump(out, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
print(len(cues), "меток")
