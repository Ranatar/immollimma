"""events.json (журнал прогона aldudenie.html) → cues.json для immollimma.
Разделы — шесть ступеней обряда; удары и подписи — события страницы; часы Древ — отдельным списком (hours)."""
import json, sys

src, dst = sys.argv[1], sys.argv[2]
d = json.load(open(src)); ev = d["events"]
MOOD = {
    "Telperion ar Laurelin": ("Счёт Древ: серебро и золото попеременно, час за часом; ясность, покой", 0.35,
                              "часы — каждые 1,67 с (пуста под рядом ромбов); слово lúmë в 8 с"),
    "silima": ("Сотворение Сильмарилей: свет Древ по нитям стекается в три камня; мастерство, нарастание", 0.55,
               "потоки бусин 22–38; камни загораются в 30, 33, 36; подпись Silmarilli в 37,5"),
    "Valinórë": ("Полдень Валинора: оба света в полную силу, смешение; полнота, слава", 0.85,
                 "слова malta (41) и telpë (46,6)"),
    "Ungoliantë": ("Унголиант: Не-Свет пьёт Древа; паутина ползёт из букв ungwë, роса течёт вспять; Древа гаснут", 0.9,
                   "паутина с 52,6; Úcala Ungolianteva (54), Ungoliantë yúla i Aldu (58,4); Древа мертвы в 62 (lómë); "
                   "в 65 Сильмарилли вспыхивают и не даются тьме"),
    "nainië": ("Плач: тьма, остались формы букв, звуки ушли; утрата", 0.3,
               "þ→s (74), ñ→n (79), anna без звука (84), vanwa (85,2)"),
    "Isil ar Anar": ("Исиль и Анар: серебро и золото сменяют друг друга, не смешиваясь; смешанный свет — только в камнях", 0.5,
                     "Isil (90,8), Anar (97,4); титул Aldudénië (100,8); уход в темноту 103,6–109,6"),
}
cues = []
stages = [e for e in ev if e["type"] == "stage"]
for i, e in enumerate(stages):
    end = stages[i + 1]["t"] if i + 1 < len(stages) else d["rite_len"]
    mood, inten, note = MOOD[e["name"]]
    cues.append(dict(t=e["t"], end=end, label=f'{["I","II","III","IV","V","VI"][i]} {e["name"]}', kind="section",
                     mood=mood, intensity=inten, note=note))

def add(t, label, kind, intensity=0.5, note="", end=None):
    c = dict(t=round(t, 4), label=label, kind=kind, intensity=intensity, note=note)
    if end is not None: c["end"] = end
    cues.append(c)

add(0.0, "вход из темноты", "swell", 0.2, "чёрное до 2,2 с", end=2.2)
for e in ev:
    k = e["type"]
    if k == "word": add(e["t"], e["word"], "document", 0.45, "слово тенгваром проступает по буквам (5–6,5 с)")
    elif k == "making": add(e["t"], "свет течёт к камням", "transition", 0.4, "потоки до 38,5", end=38.5)
    elif k == "silmaril": add(e["t"], f'Сильмариль {e["n"] + 1}', "hit", 0.7 + 0.1 * e["n"], "камень загорается, кольцо-вспышка")
    elif k == "ungoliant": add(e["t"], "Унголиант", "hit", 0.8, "Древа мерцают и гаснут 52–62, пелена с 54")
    elif k == "trees-dead": add(e["t"], "Древа мертвы", "silence", 0.1, "свет Древ = 0; остаются камни", end=64.8)
    elif k == "silmarils-refuse": add(e["t"], "Сильмарилли не даются", "hit", 0.9, "кольца-вспышки трёх камней")
    elif k == "mote": add(e["t"], e["label"], "accent", 0.35, "звук покидает букву: дуга к другой букве (или вверх — anna)")
    elif k == "title": add(e["t"], "Aldudénië", "document", 0.5, "титул")
for t, s in [(37.5, "Silmarilli"), (54.0, "Úcala Ungolianteva"), (58.4, "Ungoliantë yúla i Aldu"), (62.4, "lómë"),
             (66.0, "Silmarilli uir túrimë mornienen")]:
    add(t, s, "document", 0.45, "надпись тенгваром и латиницей")
add(103.6, "уход в темноту", "swell", 0.0, "медленно в чёрное к 109,6; затем цикл повторяется", end=110.0)
cues.sort(key=lambda c: (c["t"], c["kind"] != "section"))
hours = [dict(t=e["t"], h=e["h"]) for e in ev if e["type"] == "hour"]
json.dump(dict(version=1, duration_s=d["rite_len"], fps=None, video="aldudenie.html (анимация, цикл 104 с)",
               cues=cues, hours=hours, light_curve=[{k: c[k] for k in ("t", "iT", "iL", "band")} for c in d["curve"]]),
          open(dst, "w"), ensure_ascii=False, indent=1)
print(len(cues), "меток,", len(hours), "часов")
