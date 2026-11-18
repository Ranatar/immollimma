"""Прогон полного цикла devoratio.html пошаговыми часами (без отрисовки) и снятие журнала событий.
python3 extract_events.py devoratio.html out_dir [шаг_с]"""
import asyncio, json, sys, pathlib
from playwright.async_api import async_playwright

async def main(page, out_dir, h):
    out = pathlib.Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        pg = await b.new_page(viewport={"width": 960, "height": 540})
        errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto(pathlib.Path(page).resolve().as_uri())
        await pg.wait_for_function("window.__dev", timeout=15000)
        res = await pg.evaluate("""(h) => {
          const D = window.__dev; D.paused = true; D.loop = false; D.restart(); D.EVLOG().length = 0;
          while (D.rt < D.RITE_LEN - 1e-6) D.step(Math.min(h, D.RITE_LEN - D.rt));
          return { events: D.EVLOG(), rite_len: D.RITE_LEN, stages: D.STAGES, beats: D.BEATS };
        }""", h)
        await b.close()
    if errs: print("ошибки страницы:", errs)
    res["events"].sort(key=lambda e: (e["t"], e["type"]))
    (out / "events.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))
    return res

if __name__ == "__main__":
    h = float(sys.argv[3]) if len(sys.argv) > 3 else 1 / 240
    r = asyncio.run(main(sys.argv[1], sys.argv[2], h))
    print(len(r["events"]), "событий;", sum(e["type"] == "beat" for e in r["events"]), "ударов;",
          sum(e["type"] == "beacon" for e in r["events"]), "маяков")
