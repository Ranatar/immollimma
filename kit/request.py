"""A request = a folder with brief.json (and cues.json). Loading fills every missing field with the default
from schemas/brief.schema.json and remembers which fields were defaulted, so the plan can say what was
decided without asking."""
import json
import os
import subprocess

from .paths import REPO

SCHEMAS = os.path.join(REPO, "schemas")


def _defaults(schema):
    out = {}
    for k, v in schema.get("properties", {}).items():
        if v.get("type") == "object" and "properties" in v:
            out[k] = _defaults(v)
        elif "default" in v:
            out[k] = v["default"]
    return out


def _merge(defaults, given, path="", used=None):
    used = [] if used is None else used
    out = {}
    for k, dv in defaults.items():
        gv = given.get(k) if isinstance(given, dict) else None
        if isinstance(dv, dict):
            out[k] = _merge(dv, gv or {}, path + k + ".", used)[0]
        elif gv is None or gv == "" or gv == []:
            out[k] = dv
            used.append(path + k)
        else:
            out[k] = gv
    for k, gv in (given or {}).items():  # keep unknown fields
        out.setdefault(k, gv)
    return out, used


def load_brief(path_or_dict):
    schema = json.load(open(os.path.join(SCHEMAS, "brief.schema.json")))
    given = path_or_dict if isinstance(path_or_dict, dict) else json.load(open(path_or_dict))
    brief, used = _merge(_defaults(schema), given)
    return brief, used


def load_cues(path):
    d = json.load(open(path))
    cues = sorted(d.get("cues", []), key=lambda c: c["t"])
    for c in cues:
        c.setdefault("kind", "section")
        c.setdefault("label", "")
        c.setdefault("mood", "")
        c.setdefault("intensity", 0.5)
        c.setdefault("characters", [])
    d["cues"] = cues
    if not d.get("duration_s") and cues:
        d["duration_s"] = max(c.get("end") or c["t"] for c in cues) + 5.0
    return d


def sections(cues, total=None):
    """[(t0, t1, cue)] from the 'section' cues (all cues if there are no sections)"""
    cs = cues["cues"]
    sec = [c for c in cs if c["kind"] == "section"] or cs
    total = total or cues.get("duration_s") or (sec[-1]["t"] + 10 if sec else 0)
    if sec and sec[0]["t"] > 0.5:  # music before the first cue is a section too
        sec = [{"t": 0.0, "label": "начало", "kind": "section", "mood": "", "intensity": 0.4, "characters": []}] + sec
    out = []
    for i, c in enumerate(sec):
        t1 = sec[i + 1]["t"] if i + 1 < len(sec) else total
        out.append((c["t"], t1, c))
    return out


def scenes_from_video(video, threshold=0.3, min_gap=2.0):
    """scene changes found by ffmpeg → a cues dict (sections); fps and duration from ffprobe"""
    pr = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                         "stream=r_frame_rate:format=duration", "-of", "json", video], capture_output=True, text=True)
    info = json.loads(pr.stdout or "{}")
    dur = float(info.get("format", {}).get("duration", 0) or 0)
    fr = info.get("streams", [{}])[0].get("r_frame_rate", "0/1")
    a, b = fr.split("/")
    fps = float(a) / float(b) if float(b) else None
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", video, "-vf", f"select='gt(scene,{threshold})',showinfo",
                        "-an", "-f", "null", "-"], capture_output=True, text=True)
    times = []
    for line in r.stderr.splitlines():
        if "pts_time:" in line:
            t = float(line.split("pts_time:")[1].split()[0])
            if not times or t - times[-1] >= min_gap:
                times.append(round(t, 3))
    cues = [{"t": 0.0, "label": "начало", "kind": "section"}]
    cues += [{"t": t, "label": f"сцена {i + 2}", "kind": "section"} for i, t in enumerate(times)]
    return {"version": 1, "duration_s": dur or None, "fps": fps, "video": os.path.basename(video), "cues": cues}


def find(request_dir):
    """brief and cues of a request folder (either may be missing)"""
    b = os.path.join(request_dir, "brief.json")
    c = os.path.join(request_dir, "cues.json")
    brief, used = load_brief(b) if os.path.exists(b) else load_brief({})
    if not os.path.exists(b):
        used = ["(no brief.json — everything by default)"]
    cues = load_cues(c) if os.path.exists(c) else None
    return brief, used, cues
