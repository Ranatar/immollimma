"""Проверка созвучий на долях (taste.md, правило 8): полутоны и тритоны между звучащими нотами в моменты долей.
python3 vertical.py — печатает подозрительные доли по разделам (кроме разделов, где диссонанс задуман)."""
import sys, importlib.util, collections, pathlib
root = pathlib.Path(__file__).resolve().parents[3]; sys.path.insert(0, str(root))
from kit.__main__ import Ctx
req = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('pc', req / 'piece.py'); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
p = m.build(Ctx(str(req)))
notes = [e for e in p.events if e.get('kind') == 'note']
SKIP = [(43.2, 57.6), (91.2 + 4.8, 100.8)]            # вихрь и двоедушная маска — диссонанс задуман
UNPITCHED = {'timp', 'timp_roll'}
def sounding(t):
    return sorted({e['midi'] for e in notes if e['inst'] not in UNPITCHED and e['t'] <= t + 1e-6 < e['t'] + e['dur'] - .02})
bad = collections.defaultdict(list)
for k in range(int(108 / .4)):
    t = round(k * .4, 3)
    if (4.8 <= t < 24 or 72 <= t < 96) and abs((t / .8) - round(t / .8)) > 1e-6: continue   # сарабанда: доли по 0,8 с
    if any(a <= t < b for a, b in SKIP): continue
    s = sounding(t)
    pcs = sorted({x % 12 for x in s})
    iv = {(b - a) % 12 for a in pcs for b in pcs if a != b}
    flag = [x for x in (1, 6, 11) if x in iv]
    if flag: bad[int(t // 2.4)].append((t, [x for x in s], flag))
for bar in sorted(bad):
    for t, s, f in bad[bar][:2]:
        print(f'{t:6.1f}  {f}  {s}')
print('всего долей с полутоном/тритоном:', sum(len(v) for v in bad.values()))
