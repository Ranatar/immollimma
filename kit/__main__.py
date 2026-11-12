"""python3 -m kit <command>

  check                              what is installed (libraries, sfizz, LilyPond)
  plan REQUEST_DIR                   brief.json (+ cues.json) → REQUEST_DIR/plan.md, plan.json
  run PIECE.py [--out DIR]           build → events.json → WAV/MP3 → MIDI/MusicXML/PDF → report → credits
        [--backend plain|vsco|sso] [--from S --to S] [--sketch] [--stems] [--no-pdf] [--ref-buses F] [--parts]
  qa WAV [--events F] [--out DIR]    instrument report of any rendering
  scenes VIDEO [--out cues.json]     cue sheet from the scene changes of a video
  mux AUDIO VIDEO OUT                put the music under the video
  calibrate [--only a,b]             re-measure the SFZ instruments (tools/calibrate.py)

A piece is a Python file with build(ctx) → Piece. ctx.brief, ctx.cues, ctx.plan come from the files next to
the piece (brief.json, cues.json, plan.json) when they exist.
"""
import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time

from . import export, mix, qa
from .events import Piece
from .instruments import LICENSES
from .paths import REPO, status
from .request import find, load_cues, scenes_from_video


class Ctx:
    def __init__(self, folder):
        self.dir = folder
        self.brief, self.defaults, self.cues = find(folder)
        p = os.path.join(folder, "plan.json")
        self.plan = json.load(open(p)) if os.path.exists(p) else None

    def path(self, *a):
        return os.path.join(self.dir, *a)


def load_piece(path):
    spec = importlib.util.spec_from_file_location("piece", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def cmd_check(a):
    st = status()
    st["LilyPond"] = bool(shutil.which("lilypond") and shutil.which("musicxml2ly"))
    st["ffmpeg"] = bool(shutil.which("ffmpeg"))
    for k, v in st.items():
        print(f"{'ok ' if v else 'NO '} {k}")
    if st["libsfizz"]:
        try:
            from .sfz_engine import Sfizz  # noqa: F401
            import ctypes
            ctypes.CDLL(__import__("kit.paths", fromlist=["SFIZZ_LIB"]).SFIZZ_LIB)
            print("ok  libsfizz loads")
        except OSError as ex:
            print("NO  libsfizz does not load here:", ex, "— run tools/setup.sh --build-sfizz")
    return 0 if all(st.values()) else 1


def cmd_plan(a):
    from . import plan as pl
    brief, used, cues = find(a.request)
    p = pl.make(brief, used, cues)
    json.dump(p, open(os.path.join(a.request, "plan.json"), "w"), ensure_ascii=False, indent=1)
    md = pl.to_markdown(p, brief)
    open(os.path.join(a.request, "plan.md"), "w").write(md)
    print(md)


def credits(rep, piece):
    lines = [f"Music: «{piece.title}»"]
    lines += ["Samples: " + x for x in rep["licenses"]]
    if any("Sampling Plus" in x for x in rep["licenses"]):
        lines.append("Note: contains Sonatina samples (CC Sampling Plus 1.0) — not to be used in advertising.")
    return "\n".join(lines) + "\n"


def cmd_run(a):
    folder = os.path.dirname(os.path.abspath(a.piece))
    out = a.out or os.path.join(folder, "out")
    os.makedirs(out, exist_ok=True)
    ctx = Ctx(folder)
    mod = load_piece(a.piece)
    t = time.time()
    piece = mod.build(ctx)
    piece.to_json(os.path.join(out, "events.json"))
    backend = a.backend or (ctx.plan or {}).get("library") or "plain"
    t0, t1 = a.start, a.end
    if a.sketch and t1 is None:
        sk = ctx.brief["iteration"]["sketch_seconds"]
        t1 = min(piece.end(), t0 + sk)
    tag = "" if t1 is None and t0 == 0 else f"_{t0:.0f}-{t1:.0f}"
    wav = os.path.join(out, f"audio{tag}.wav")
    from .render import render
    rep = render(piece, wav, backend=backend, t0=t0, t1=t1, ref_buses=a.ref_buses,
                 stems_dir=os.path.join(out, "stems") if a.stems else None)
    mp3 = mix.encode(wav, os.path.join(out, f"audio{tag}.mp3"))
    rep["mp3"] = mp3
    if not a.no_notation:
        rep["notation"] = export.export_all(piece, out, pdf=not a.no_pdf)
    silences = [(s["t"], s["t"] + s["dur"]) for s in ctx.brief.get("silences", [])]
    if ctx.cues:
        silences += [(c["t"], c.get("end") or c["t"] + 1) for c in ctx.cues["cues"] if c["kind"] == "silence"]
    view = piece
    if tag:  # report on the window: shift the events
        view = Piece(piece.title, piece.bpm, piece.meter)
        for e in piece.window(t0, t1):
            e = dict(e, t=e["t"] - t0)
            if "t1" in e:
                e["t1"] -= t0
            view.events.append(e)
    parts = qa.parts_loudness(view, backend) if a.parts else None
    rep["qa"] = qa.report(wav, out, piece=view, silences=[(a_ - t0, b_ - t0) for a_, b_ in silences], title=piece.title,
                          balance=parts)
    if parts:
        rep["parts_lufs"] = parts
    open(os.path.join(out, "credits.txt"), "w").write(credits(rep, piece))
    rep["seconds_taken"] = round(time.time() - t, 1)
    json.dump(rep, open(os.path.join(out, "render.json"), "w"), ensure_ascii=False, indent=1, default=str)
    print(json.dumps({k: rep[k] for k in ("backend", "libraries", "substitutions", "missing", "lengthened", "seconds_taken")},
                     ensure_ascii=False))
    print("qa:", {k: rep["qa"][k] for k in ("gaps", "clipped", "clicks", "flat")})
    print("out:", out)


def cmd_qa(a):
    piece = Piece.from_json(a.events) if a.events else None
    print(qa.report(a.wav, a.out or os.path.dirname(os.path.abspath(a.wav)), piece=piece))


def cmd_scenes(a):
    c = scenes_from_video(a.video, a.threshold)
    json.dump(c, open(a.out, "w"), ensure_ascii=False, indent=1)
    print(len(c["cues"]), "cues →", a.out)


def main():
    ap = argparse.ArgumentParser(prog="python3 -m kit", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check")
    p = sub.add_parser("plan")
    p.add_argument("request")
    p = sub.add_parser("run")
    p.add_argument("piece")
    p.add_argument("--out")
    p.add_argument("--backend", choices=["plain", "vsco", "sso"])
    p.add_argument("--from", dest="start", type=float, default=0.0)
    p.add_argument("--to", dest="end", type=float)
    p.add_argument("--sketch", action="store_true")
    p.add_argument("--stems", action="store_true")
    p.add_argument("--no-pdf", action="store_true")
    p.add_argument("--no-notation", action="store_true")
    p.add_argument("--ref-buses")
    p.add_argument("--parts", action="store_true", help="balance: loudness of every part alone (one render per part)")
    p = sub.add_parser("qa")
    p.add_argument("wav")
    p.add_argument("--events")
    p.add_argument("--out")
    p = sub.add_parser("scenes")
    p.add_argument("video")
    p.add_argument("--out", default="cues.json")
    p.add_argument("--threshold", type=float, default=0.3)
    p = sub.add_parser("mux")
    p.add_argument("audio")
    p.add_argument("video")
    p.add_argument("out")
    p = sub.add_parser("calibrate")
    p.add_argument("--only")
    a = ap.parse_args()
    if a.cmd == "mux":
        mix.mux(a.audio, a.video, a.out)
    elif a.cmd == "calibrate":
        sys.exit(subprocess.call([sys.executable, os.path.join(REPO, "tools", "calibrate.py")] + (["--only", a.only] if a.only else [])))
    else:
        sys.exit({"check": cmd_check, "plan": cmd_plan, "run": cmd_run, "qa": cmd_qa, "scenes": cmd_scenes}[a.cmd](a) or 0)


if __name__ == "__main__":
    main()
