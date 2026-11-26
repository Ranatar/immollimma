"""Ноты пьесы с происхождением: какая строка build() их породила и с какими локальными (vi, sh, k…).
Нужно анимации: голос, роль, октавный сдвиг дублировки, эхо.   python3 tools/trace_notes.py > /tmp/trace.json"""
import inspect, json, os, sys, types
HERE = os.path.dirname(os.path.abspath(__file__))
REQ = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REQ, "..", ".."))
from kit import events as kev  # noqa: E402
PIECE = os.path.join(REQ, "piece.py")
orig = kev.Piece.note


def traced(self, *a, **k):
    e = orig(self, *a, **k)
    fr = inspect.currentframe().f_back
    chain = []
    while fr:
        if os.path.abspath(fr.f_code.co_filename) == PIECE:
            loc = {n: fr.f_locals[n] for n in ("vi", "sh", "k", "bar", "wi", "j", "n_", "inst") if n in fr.f_locals
                   and isinstance(fr.f_locals[n], (int, float, str))}
            chain.append([fr.f_code.co_name, fr.f_lineno, loc])
        fr = fr.f_back
    e["_src"] = chain
    return e


kev.Piece.note = traced
spec = __import__("importlib.util").util.spec_from_file_location("piece", PIECE)
mod = __import__("importlib.util").util.module_from_spec(spec)
spec.loader.exec_module(mod)
p = mod.build(types.SimpleNamespace(brief={}, cues=[], plan={}))
src = open(PIECE).read().split("\n")
out = []
for e in p.events:
    if e["kind"] != "note":
        continue
    ch = e.pop("_src")
    e["src"] = [[f, ln, src[ln - 1].strip()[:70], loc] for f, ln, loc in ch]
    out.append(e)
json.dump(out, sys.stdout, ensure_ascii=False)
