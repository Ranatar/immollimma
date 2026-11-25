"""events.json (журнал прогона ludus.html) → cues.json для immollimma."""
import json, sys
d = json.load(open(sys.argv[1])); ev = d["events"]
MOOD = {
 "PROLOGUS": ("тьма; один золотой ромб", .05, "ромб 0.6–5; занавес открывается в 4.8"),
 "AUREA AETAS": ("согласие: благородная сарабанда, всё возвращается к себе", .4, "трое танцуют зеркально; знак согласия пишут двое зеркально 12–16.8"),
 "LUXURIA": ("соблазн: сладкий избыток, вальс Одиночки, па не возвращаются", .65, "Одиночка входит 24; её знак 31.2–36; всё в её цветах 38.4; её маска-половина 40.8"),
 "CASUS": ("Падение: вихрь стягивает всё к середине, ускоряясь", .95, "вихрь 43.2–55.2; вспышка 55.2; тьма до 57.6"),
 "RUINA": ("руины: пепел, пляска смерти Шута", .3, "пепел 57.6; Шут входит 59.2; обломки знака 62.4–67.2; плачущая половина 67.2–71.5"),
 "RISUS": ("смеётся Бог: сборка из середины в трауре, нити Паутины", .6, "сборка 72; знак смеха трое 81.6–86.4"),
 "LARVA": ("маска: двое обводят контур, третий черты; половины сходятся", .5, "обводка 91.2–96; схождение 96; смех маски 98.4"),
 "EXODIUM": ("занавес и последний ромб", .1, "занавес 100.8; ромб 103.2–107"),
}
KIND = [("вспышка", "hit", 1.0), ("занавес", "transition", .4), ("знак", "accent", .5), ("маска", "accent", .5),
        ("смех", "accent", .5), ("поворот", "accent", .35), ("скольжение", "accent", .3), ("волна", "transition", .35),
        ("тень маски", "accent", .25), ("ромб", "accent", .3), ("сборка", "hit", .7), ("пепел", "transition", .3),
        ("входит", "accent", .4), ("всё в её цветах", "hit", .8), ("половины сходятся", "hit", .7), ("вихрь", "swell", .8)]
cues = []
acts = [e for e in ev if e["type"] == "act"]
for i, a in enumerate(acts):
    end = acts[i + 1]["t"] if i + 1 < len(acts) else d["len"]
    m, inten, note = MOOD[a["name"]]
    cues.append(dict(t=a["t"], end=end, label=(a["num"] + " " if a["num"] else "") + a["name"], kind="section", mood=m, intensity=inten, note=note))
for e in ev:
    if e["type"] != "cue": continue
    lab = e["label"]; kind, inten = "accent", .3
    for k, kk, ii in KIND:
        if k in lab: kind, inten = kk, ii; break
    cues.append(dict(t=e["t"], label=lab, kind=kind, intensity=inten))
cues.append(dict(t=55.2, end=57.6, label="тьма после вспышки", kind="silence", intensity=0))
cues.append(dict(t=107.0, end=d["len"], label="тишина до повтора", kind="silence", intensity=0))
cues.sort(key=lambda c: (c["t"], c["kind"] != "section"))
glyphs = [dict(name="ordo", t0=12.0, t1=16.8, rel=17.6, who="двое зеркально"), dict(name="lux", t0=31.2, t1=36.0, rel=36.6, who="Одиночка"),
          dict(name="ruin", t0=62.4, t1=67.2, rel=69.6, who="Шут, обрывками"), dict(name="risus", t0=81.6, t1=86.4, rel=87.0, who="трое"),
          dict(name="mask", t0=91.2, t1=96.0, rel=None, who="двое контур, третий черты")]
out = dict(version=1, duration_s=d["len"], fps=None, video="ludus.html (анимация, цикл 108 с)", cues=cues, glyphs=glyphs,
           grid=dict(bpm=75, meter="3/4", bar_s=d["bar"], beat_s=d["beat"], note="такт страницы 2,4 с = три доли по 0,8 с; все события на сетке 0,4 с"),
           loop=True)
json.dump(out, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
print(len(cues), "меток")
