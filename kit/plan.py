"""The plan of a piece, made before any note: the brief with every default spelled out, the sections (from
cues or from the duration), a contrast table, the library and licence decision. Written as plan.md (for the
user) and plan.json (for the score code).

The contrast table is the cure for the first R.S.F.G.R. edition's monotony: neighbouring sections must
differ in at least three of five attributes — leader, texture, register, pulse, dynamic."""
import json
import os
import random

from .instruments import INSTR
from .paths import STYLES
from .request import sections

ATTRS = ("leader", "texture", "register", "pulse", "dynamic")
DEFAULT_SECONDS = 90


def styles():
    return {c["id"]: c for c in json.load(open(os.path.join(STYLES, "index.json")))}


def card(cid):
    return json.load(open(os.path.join(STYLES, cid + ".json")))


def pick_cards(brief):
    ids = brief["style"]["cards"]
    if ids:
        return [card(i) for i in ids if os.path.exists(os.path.join(STYLES, i + ".json"))]
    # no card chosen: match words of the brief against card names and summaries
    text = " ".join([brief["style"]["mood"], brief["style"]["references"], brief["notes"], brief["dramaturgy"]["arc"]]).lower()
    best, score = None, 0
    for cid, c in styles().items():
        words = [w for w in (c["name"] + " " + c["summary"]).lower().replace(",", " ").split() if len(w) > 4]
        s = sum(1 for w in words if w[:6] in text)
        if s > score:
            best, score = cid, s
    return [card(best or "ambient_film")]


AVOID_WORDS = {"мед": "brass", "труб": "brass", "удар": "perc", "барабан": "perc", "литавр": "perc", "струн": "strings",
               "хор": "choir", "орган": "organ", "шум": "fx", "дерев": "winds", "клавес": "keys", "фортепиан": "keys"}


def contrast(n, palette, seed=1, need=3, intensity=None, palettes=None):
    """n rows of attributes, neighbours differing in ≥ need attributes; intensity (0..1 per row) pushes the
    dynamic choice; palettes: one palette per row (several style cards: calm rows from the first)"""
    rng = random.Random(seed)
    dyn_order = ["pp", "p", "mf", "f", "ff"]
    rows = []
    for i in range(n):
        pal = palettes[i] if palettes else palette
        for _ in range(200):
            r = {a: rng.choice(pal[a + "s"] if a + "s" in pal else pal[a]) for a in ATTRS}
            if intensity is not None:
                dyns = [d for d in dyn_order if d in pal["dynamics"]] or dyn_order
                r["dynamic"] = dyns[min(len(dyns) - 1, int(intensity[i] * len(dyns)))]
            if not rows or sum(r[a] != rows[-1][a] for a in ATTRS) >= need:
                if len(rows) < 2 or r["leader"] != rows[-2]["leader"] or len(pal["leaders"]) < 3:
                    break
        rows.append(r)
    return rows


def library_decision(brief, insts):
    lib = brief["library"]
    sso_only = sorted(i for i in insts if i in INSTR and not INSTR[i]["plain"] and not INSTR[i]["vsco"])
    notes = []
    if brief["commercial_ad"]:
        if lib == "sso":
            notes.append("Реклама: Sonatina запрещена лицензией — переключаю на VSCO.")
        lib = "plain" if lib in ("auto", "sso") else lib
        if sso_only:
            notes.append(f"Реклама: инструментов {', '.join(sso_only)} нет в VSCO — заменить или убрать.")
    elif lib == "auto":
        lib = "plain"
        if sso_only:
            notes.append(f"{', '.join(sso_only)} есть только в Sonatina — для них Sonatina (не для рекламы).")
    return lib, notes


def make(brief, used, cues=None, seed=1):
    cards = pick_cards(brief)
    c0 = cards[0]
    inc = brief["ensemble"]["include"]
    exc = set(brief["ensemble"]["exclude"])
    avoid = (brief["style"]["avoid"] or "").lower()
    banned_buses = {bus for w, bus in AVOID_WORDS.items() if w in avoid}

    def leaders_ok(xs):
        out = [x for x in list(dict.fromkeys(inc + xs)) if x in INSTR and x not in exc
               and (x in inc or INSTR[x]["bus"] not in banned_buses)]
        if brief["commercial_ad"]:  # advertising: only what VSCO has (Sonatina's licence forbids it)
            out = [x for x in out if INSTR[x]["plain"] or INSTR[x]["vsco"]]
        return out or ["vln_sus", "cl_sus", "harp"]

    def palette_of(cs):
        pal = {k: list(v) for k, v in cs[0]["palette"].items()}
        for c in cs[1:]:
            for k, v in c["palette"].items():
                pal[k] = list(dict.fromkeys(pal[k] + v))
        pal["leaders"] = leaders_ok(pal["leaders"])
        return pal

    pal = palette_of(cards)
    calm, tense = palette_of(cards[:1]), palette_of(cards[1:] or cards[:1])
    total = brief["duration_s"] or (cues or {}).get("duration_s") or DEFAULT_SECONDS
    if cues and cues["cues"]:
        secs = [(a, b, c) for a, b, c in sections(cues, total)]
    else:
        n = max(2, min(8, int(round(total / 25))))
        secs = [(total * i / n, total * (i + 1) / n, {"label": f"раздел {i + 1}", "mood": "", "intensity": 0.5, "kind": "section"})
                for i in range(n)]
        if brief["dramaturgy"]["climax_s"]:
            for s in secs:
                s[2]["intensity"] = max(0.2, 1 - abs((s[0] + s[1]) / 2 - brief["dramaturgy"]["climax_s"]) / total * 2)
    inten = [s[2].get("intensity", 0.5) for s in secs]
    # several cards: calm sections speak the first card's language, tense ones the others'
    palettes = [calm if x < 0.55 else tense for x in inten] if len(cards) > 1 else None
    rows = contrast(len(secs), pal, seed, intensity=inten, palettes=palettes)
    tempo = brief["tempo_bpm"] or round(sum(c0["tempo_bpm"]) / 2)
    meter = brief["meter"] or c0["meters"][0]
    lib, lib_notes = library_decision(brief, set(pal["leaders"]) | set(inc))
    plan = dict(title=brief["title"] or "untitled", styles=[c["id"] for c in cards], seconds=total, tempo_bpm=tempo,
                meter=meter, key=brief["key"], language=brief["language"] if brief["language"] != "any" else c0["harmony"]["language"],
                library=lib, library_notes=lib_notes, defaults=used,
                sections=[dict(t0=round(a, 2), t1=round(b, 2), label=c.get("label", ""), mood=c.get("mood", ""),
                               intensity=c.get("intensity", 0.5), **r) for (a, b, c), r in zip(secs, rows)],
                hits=[c for c in (cues or {}).get("cues", []) if c["kind"] in ("hit", "accent", "swell", "silence", "document")],
                silences=brief["silences"], themes=brief["themes"], characters=brief["characters"],
                avoid=c0["avoid"] + ([brief["style"]["avoid"]] if brief["style"]["avoid"] else []),
                devices=c0["devices"], ending=brief["dramaturgy"]["ending"], deliver=brief["deliver"],
                sketch=brief["iteration"])
    return plan


def to_markdown(plan, brief):
    L = [f"# План: {plan['title']}", "",
         f"- стиль: {', '.join(plan['styles'])}; язык: {plan['language']}; темп {plan['tempo_bpm']}, размер {plan['meter']}"
         + (f", тональность {plan['key']}" if plan['key'] else ""),
         f"- длительность {plan['seconds']:.0f} с; концовка: {plan['ending']}",
         f"- библиотека: {plan['library']}" + ("; " + " ".join(plan["library_notes"]) if plan["library_notes"] else ""),
         f"- отдать: {', '.join(plan['deliver'])}",
         f"- избегать: {'; '.join(plan['avoid'])}", ""]
    if plan["defaults"]:
        L += ["**Решено по умолчанию (не было в брифе):** " + ", ".join(plan["defaults"]), ""]
    L += ["## Разделы и контрасты", "", "| время | метка | настроение | ведущий | фактура | регистр | пульс | динамика |",
          "|---|---|---|---|---|---|---|---|"]
    for s in plan["sections"]:
        L.append(f"| {s['t0']:.1f}–{s['t1']:.1f} | {s['label']} | {s['mood']} | {s['leader']} | {s['texture']} | {s['register']} | "
                 f"{s['pulse']} | {s['dynamic']} |")
    if plan["hits"]:
        L += ["", "## Точки синхронизации", ""] + [f"- {h['t']:.2f} с — {h['kind']}: {h.get('label', '')}" for h in plan["hits"]]
    if plan["themes"] or plan["characters"]:
        L += ["", "## Темы и персонажи", ""]
        L += [f"- тема «{t.get('name', '')}» ({t.get('for', '')}): {t.get('notation', '')}; {t.get('transform', '')}" for t in plan["themes"]]
        L += [f"- {c.get('name', '')}: {c.get('description', '')}; {c.get('evolution', '')}" for c in plan["characters"]]
    L += ["", "## Приёмы стиля", "", ", ".join(plan["devices"]), ""]
    return "\n".join(L)
