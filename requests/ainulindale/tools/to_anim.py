"""Ноты пьесы → данные анимации: нити (мелодические голоса), кольца (созвучия, педали, волны), вспышки.
    python3 tools/trace_notes.py > /tmp/trace.json && python3 tools/to_anim.py /tmp/trace.json out/anim.json"""
import json, sys
from collections import defaultdict

notes = json.load(open(sys.argv[1]))
ev = json.load(open(sys.argv[2].replace("anim.json", "events.json")))["events"]


def amp(e):
    return round(min(1.5, e["vel"] * e["gain"] * 2.2), 3)


threads = defaultdict(list)     # ключ → ноты
tinfo = {}
rings, fx = [], []
solo_i = expo_i = 0
EXPO_CLASS = [0, 1, 1, 0, 2, 1, 3]
for e in notes:
    src = e["src"]
    top = src[-1][2]
    loc = {}
    for f, ln, txt, l in src:
        for k, v in l.items():
            loc.setdefault(k, v)
    inner = [s[2] for s in src]
    m = e["midi"] + e["detune"]
    rec = [round(e["t"], 3), round(e["dur"], 3), round(m, 3), amp(e), round(e["attack"], 2), round(e["release"], 2)]
    echo = any(x.startswith("note(inst, m + sh, tt + echo[0]") for x in inner)

    def th(key, fam, **info):
        threads[key].append(rec)
        tinfo.setdefault(key, dict(fam=fam, **info))

    def ring(fam, **x):
        rings.append(rec + [fam] + ([x] if x else []))

    def flash(fam):
        fx.append(rec + [fam])

    if top.startswith("note(inst, base + iv"):
        th(f"solo{solo_i // 4}", "solo", i=solo_i // 4, pan=e["pan"]); solo_i += 1
    elif top.startswith('note("org_quiet", m, 22.0') or top.startswith('note("choir", m, 22.0'):
        ring("bloom")
    elif top.startswith("note(inst, mm, t, d * 0.98"):
        th(f"expo{EXPO_CLASS[expo_i % 7]}", "expo", cls=EXPO_CLASS[expo_i % 7]); expo_i += 1
    elif top.startswith("note(inst, m, T_ST"):
        ring("pad")
    elif top.startswith('note("vln_sus" if m >= 74') or top.startswith('note("harp", 74, t_end'):
        ring("splend")
    elif top.startswith("play(cantus_lo"):
        th("can_lo", "cantus", unit=2.0)
    elif top.startswith("play(cantus_mid"):
        if not echo: th("can_mid", "cantus", unit=1.0)
    elif top.startswith("play(cantus_A,"):
        if not echo: th(f"can_A{loc.get('sh', 0)}", "cantus", unit=1.15)
    elif top.startswith("play(cantus_A_lo") or top.startswith("play(cantus_ret_lo"):
        ring("pedal")
    elif top.startswith("play(ret_head"):
        if not echo: th(f"ret{loc.get('sh', 0)}", "cantus", unit=1.25)
    elif top.startswith("play(notes, insts, 0.5, gain, pan=pan, echo=echo"):
        if not echo: th(f"dev{loc['vi']}", "dev", vi=loc["vi"])
    elif "melkor_line" in top:
        key = f"mel{src[-1][1]}_{loc.get('sh', 0)}"
        th(key, "mel")
    elif top.startswith("waves(") or top.startswith('note("cb_trem", 38 + rng') or top.startswith('note("choir", m, 123.0'):
        ring("wave", bend=e["bend"])
    elif top.startswith("note(inst, mm, tt, d * 0.45"):
        th(f"str{loc['k']}_{e['inst']}", "str", k=loc["k"], pan=e["pan"])
    elif top.startswith("play(sec_cantus"):
        if not echo: th(f"sec_c{loc.get('sh', 0)}", "sec", unit=0.8)
    elif top.startswith("play([n for n in sec_lo"):
        th(f"sec_lo{loc.get('sh', 0)}", "sec", unit=1.6)
    elif top.startswith("play(sec_peak"):
        if not echo: th("sec_pk", "sec", unit=0.7)
    elif top.startswith("play(notes, insts, 0.5, gain, pan=pan, echo=(0.4, 0.25), vel_fn=sec_gr"):
        if not echo: th(f"secv{loc['vi']}", "secv", vi=loc["vi"])
    elif top.startswith("t3("):
        call = src[-1][1]
        if inner[1].startswith("note(inst, m + mel_shift"):
            th(f"t3_{call}", "t3", stmt={0: 0}.get(0), line=call, beat=0.75 if "T_THIRD," in top else 1.0,
               hi="12, 0.5" in top or "12, 0.6" in top)
        elif inner[1].startswith("note(inst, mm2"):
            ring("harm3")
        else:
            flash("ripple")
    elif top.startswith("note(inst, m + sh, bar + tt"):
        th(f"uni{loc['sh']}", "uni")
    elif top.startswith("note(inst, mm, t0, d * 0.99") or top.startswith("note(inst, mm + (12 if inst"):
        ring("abs")
    elif top.startswith("note(inst, m, T_CHORD") or top.startswith('note("harp", 50, T_CHORD'):
        ring("part", n=loc.get("n_", 4))
    elif top.startswith("timp("):
        flash("timp")
    elif top.startswith('note("harp", m, tt, min(0.9'):
        flash("vharp")
    elif top.startswith('note("vln_harm", m, V'):
        ring("vharm")
    elif top.startswith('note("hn_sus", base + iv, tt'):
        th(f"ulmo{int(e['t'] > 268)}", "ulmo")
    elif top.startswith('note("fl_sus", m, V + dt'):
        th("manwe", "manwe")
    elif top.startswith('note("vc_pizz"'):
        flash("aule")
    elif top.startswith('note("vln_pizz"'):
        flash("rain")
    elif top.startswith('note("cb_trem", 38, V') or top.startswith('note("vc_trem", 45, V'):
        ring("vsea")
    elif top.startswith('note("vln_solo", m, tt'):
        th("child", "child")
    elif top.startswith("note(inst, m, E + dt") or top.startswith('note("choir", 62, E') or top.startswith('note("choir", 69, E'):
        ring("cloud")
    elif top.startswith('note("harp", 38, t + 0.28') or top.startswith('note("cb_pizz", 38'):
        flash("pulse")
    else:
        raise SystemExit("unmapped: " + top)

# дублировки одного голоса в унисон — одна нить: сливаем ноты с одинаковым началом и высотой
out_threads = []
for key, ns in threads.items():
    ns.sort()
    merged = []
    for n in ns:
        if merged and abs(merged[-1][0] - n[0]) < 0.02 and abs(merged[-1][2] - n[2]) < 0.5:
            merged[-1][3] = round(max(merged[-1][3], n[3]) * 1.15, 3)
            continue
        merged.append(list(n))
    out_threads.append(dict(key=key, **tinfo[key], notes=merged))
for e in ev:
    if e["kind"] == "sample":
        fx.append([e["t"], e["dur"] or 6.0, 38, e["gain"], e["attack"], 1.0, "tamtam" if "tamtam" in e["path"] else "cymbal"])
marks = [[e["t"], e["label"]] for e in ev if e["kind"] == "mark"]
json.dump(dict(length=304.0, marks=marks, threads=out_threads, rings=rings, fx=fx), open(sys.argv[2], "w"),
          ensure_ascii=False, separators=(",", ":"))
print(len(out_threads), "threads", sum(len(t["notes"]) for t in out_threads), "thread notes,", len(rings), "rings,",
      len(fx), "fx", file=sys.stderr)
for t in out_threads:
    print(f'{t["key"]:14} {t["fam"]:7} {len(t["notes"]):4}  {t["notes"][0][0]:7.2f}–{t["notes"][-1][0]:7.2f}', file=sys.stderr)
