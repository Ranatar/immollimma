"""Прогон полного цикла ritus.html пошаговыми часами и снятие журнала событий.
Запуск: python3 extract_events.py ritus.html out_dir [шаг_с]"""
import asyncio, json, sys, pathlib
from playwright.async_api import async_playwright

async def main(page_path, out_dir, h):
    out = pathlib.Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 1600, "height": 900})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto(pathlib.Path(page_path).resolve().as_uri())
        await pg.wait_for_function("window.__ritus && typeof rt !== 'undefined' && rt > 0", timeout=15000)
        res = await pg.evaluate("""(h) => {
          paused = true; loopOn = false; riteRestart(); window.__ritus.EVLOG().length = 0;
          const R = window.__ritus, curve = []; let nextS = 0;
          while (rt < R.RITE_LEN - 1e-6) {
            R.step(Math.min(h, R.RITE_LEN - rt));
            if (rt >= nextS - 1e-9) { curve.push(R.state()); nextS += 0.05; }
          }
          const mtc = []; for (let x = 0; x <= R.RITE_LEN + 1e-9; x += 0.01) mtc.push(+R.mtAt(x).toFixed(5));
          return { events: R.EVLOG(), curve, mt_curve: { step: 0.01, values: mtc }, rite_len: R.RITE_LEN, beat: R.BEAT, stages: R.STAGES };
        }""", h)
        await b.close()
    if errs: print("ошибки страницы:", errs)
    (out / "events.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))
    return res

if __name__ == "__main__":
    page, out_dir = sys.argv[1], sys.argv[2]
    h = float(sys.argv[3]) if len(sys.argv) > 3 else 1 / 240
    res = asyncio.run(main(page, out_dir, h))
    ev = res["events"]
    print(len(ev), "событий;", sum(e["type"] == "beat" for e in ev), "ударов")
