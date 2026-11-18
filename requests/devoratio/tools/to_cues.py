"""events.json (журнал прогона devoratio.html) → cues.json для immollimma.
Разделы — стадии обряда; удары — посадка споры, начало пожирания, гибель мира, волна порядка и её повороты;
отдельно: удары сердца Улья (heart_beats), маяки мира (beacons), повороты мира (world_turns)."""
import json, sys
d = json.load(open(sys.argv[1])); ev = d["events"]
MOOD = {
 "I": ("пустота; мир-добыча проступает: холодный правильный порядок со своим ровным тактом", .1, "такт мира 0,8 с, маяк каждые 2,4 с, повороты решётки каждые 3,2 с с 4,8"),
 "II": ("из угла приплывает спора; садится — рождается сердце Улья, первый удар", .2, "спора летит 6–12; посадка 12.0"),
 "III": ("рост: ткань расползается рваным фронтом, сеть ветвится, сердце учащается", .5, "двойные удары; интервал 3,0 → 1,8 с"),
 "IV": ("Тень в варпе: мир глохнет и замолкает", .55, "мир замолкает в 46.4"),
 "V": ("Улей обнимает мир кольцом; мир мерцает, держит оборону", .7, "интервал 1,8 → 1,4"),
 "VI": ("пожирание: решётка распадается звено за звеном, обломки текут к сердцу", 1.0, "распад 62.6–77.6; сердце раз в 1,2 с; 78 — гаснет сердцевина мира"),
 "VII": ("переваривание; весь организм на миг строится решёткой мира и поворачивает её ударами сердца", .8, "волна 81.4→82.9, повороты 82.9/84.6/86.5, отпуск 88.6"),
 "VIII": ("исход: ткань отмирает, сеть втягивается, сердце сжимается в спору и улетает", .3, "уход 103.2"),
 "IX": ("тишина; на месте мира — тусклый след", .05, "тьма к 109.4, цикл повторяется"),
}
cues = []
stages = [e for e in ev if e["type"] == "stage"]
for i, e in enumerate(stages):
    end = stages[i + 1]["t"] if i + 1 < len(stages) else d["rite_len"]
    m, it, note = MOOD[e["num"]]
    cues.append(dict(t=e["t"], end=end, label=f'{e["num"]} {e["name"]}', kind="section", mood=m, intensity=it, note=note))
KIND = {"landing": ("hit", .5, "спора села: сердце Улья"), "shadow_falls": ("transition", .5, "опускается Тень"),
        "world_silent": ("accent", .4, "мир замолк"), "embrace": ("accent", .6, "обхват"),
        "devour_begin": ("hit", .9, "начало пожирания"), "world_dark": ("hit", .8, "гаснет сердцевина мира"),
        "adaptation": ("accent", .6, "на месте мира — перенятый строй"), "order_wave": ("swell", .8, "волна порядка от сердца"),
        "order_turn": ("hit", .8, "Улей поворачивает решётку ударом"), "order_release": ("accent", .6, "порядок отпущен"),
        "exodus": ("transition", .4, "исход"), "departure": ("accent", .3, "спора улетает")}
for e in ev:
    if e["type"] in KIND:
        k, it, note = KIND[e["type"]]
        cues.append(dict(t=e["t"], label=e["type"], kind=k, intensity=it, note=note))
cues.append(dict(t=6.0, end=12.0, label="спора летит", kind="transition", intensity=.2, note="из левого верхнего угла к посадке"))
cues.append(dict(t=108.6, end=d["rite_len"], label="тишина до повтора", kind="silence", intensity=0))
cues.sort(key=lambda c: (c["t"], c["kind"] != "section"))
out = dict(version=1, duration_s=d["rite_len"], video="devoratio.html (анимация, цикл 110 с)", cues=cues, loop=True,
           heart_beats=[dict(t=e["t"], amp=e["amp"], second=e["second"]) for e in ev if e["type"] == "beat"],
           beacons=[e["t"] for e in ev if e["type"] == "beacon"],
           world_turns=[e["t"] for e in ev if e["type"] == "world_turn"],
           crumbs=[dict(t=e["t"], arrive=e["arrive"], pan=e["pan"]) for e in ev if e["type"] == "crumb"],
           world_tick=0.8, grid=dict(bpm=75, meter="4/4", note="такт мира 0,8 с = четверть; все отметки кратны 0,1 с (тридцатьвторая)"))
json.dump(out, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
print(len(cues), "меток,", len(out["heart_beats"]), "ударов,", len(out["beacons"]), "маяков,", len(out["world_turns"]), "поворотов")
