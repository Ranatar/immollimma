#!/bin/sh
# Build the three reference pieces and check the reports (≈ 1 min). Run after changing kit/.
set -e
cd "$(dirname "$0")/.."
python3 tools/export_registry.py > /dev/null
git diff --quiet -- kit/data/instruments.json 2>/dev/null || echo "note: kit/data/instruments.json changed — commit it (the forms read it)"
python3 -m kit check
for ex in chorale_prelude nocturne phase; do
  python3 -m kit run examples/$ex/piece.py > /tmp/selftest_$ex.log 2>&1 || { echo "FAIL $ex"; tail -20 /tmp/selftest_$ex.log; exit 1; }
  python3 - "$ex" <<'PY'
import json, sys
ex = sys.argv[1]
r = json.load(open(f"examples/{ex}/out/render.json"))
q = r["qa"]
bad = []
if q["gaps"]: bad.append(f"gaps {q['gaps']}")
if q["clipped"]: bad.append(f"clipped {q['clipped']}")
if q["clicks"]: bad.append(f"clicks {q['clicks']}")
if r["missing"]: bad.append(f"missing {r['missing']}")
if not r["notation"].get("pdf"): bad.append(f"no pdf: {r['notation'].get('notation_error')}")
print(("FAIL " if bad else "ok   ") + ex + (": " + "; ".join(bad) if bad else f"  ({r['seconds_taken']} s, {', '.join(r['libraries'])})"))
sys.exit(1 if bad else 0)
PY
done
