"""Прогон полного цикла ludus.html пошаговыми часами и снятие журнала событий.
Запуск: python3 extract_events.py ludus.html out_dir [шаг_с]"""
import asyncio, json, sys, pathlib
from playwright.async_api import async_playwright

async def main(page_path, out_dir, h):
    out = pathlib.Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 1600, "height": 900})
        errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto(pathlib.Path(page_path).resolve().as_uri())
        await pg.wait_for_function("window.__ludus && window.__ludus.rt > 0", timeout=15000)
        res = await pg.evaluate("""(h) => {
          paused = true; loopOn = false; const S = window.__ludus; S.restart(); S.EVLOG().length = 0;
          while (S.rt < S.LEN - 1e-6) S.step(Math.min(h, S.LEN - S.rt));
          return { events: S.EVLOG(), len: S.LEN, bar: S.BAR, beat: S.BEAT, acts: S.ACTS };
        }""", h)
        await b.close()
    if errs: print("ошибки страницы:", errs)
    (out / "events.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))
    return res

if __name__ == "__main__":
    h = float(sys.argv[3]) if len(sys.argv) > 3 else 1 / 240
    res = asyncio.run(main(sys.argv[1], sys.argv[2], h))
    print(len(res["events"]), "событий")
