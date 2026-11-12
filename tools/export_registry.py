#!/usr/bin/env python3
"""kit/instruments.py → kit/data/instruments.json (read by the forms on GitHub Pages)."""
import json
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT)
from kit.instruments import INSTR  # noqa: E402

out = [dict(id=k, part=v["part"], range=list(v["range"]), libs=[x for x in ("plain", "vsco", "sso") if v[x]],
            sso_only=not v["plain"] and not v["vsco"]) for k, v in INSTR.items()]
json.dump(out, open(os.path.join(ROOT, "kit", "data", "instruments.json"), "w"), ensure_ascii=False, indent=0)
print(len(out), "instruments")
