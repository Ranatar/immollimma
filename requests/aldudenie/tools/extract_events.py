"""Прогон полного обряда aldudenie.html пошаговыми часами: журнал событий и кривые света.
Запуск: python3 extract_events.py aldudenie.html out_dir [шаг_с]"""
import asyncio, json, sys, pathlib
from playwright.async_api import async_playwright

async def main(page_path, out_dir, h):
    out = pathlib.Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 1600, "height": 900})
        errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto(pathlib.Path(page_path).resolve().as_uri())
        await pg.wait_for_function("window.__rite && __rite.rt > 0", timeout=30000)
        res = await pg.evaluate("""(h) => {
          paused = true; loopOn = false; riteRestart();
          const R = window.__rite, curve = []; let nextS = 0;
          while (rt < R.RITE_LEN - 1e-6) {
            R.step(Math.min(h, R.RITE_LEN - rt));
            if (rt >= nextS - 1e-9) { const I = intensities(); curve.push({ t: +rt.toFixed(3), h: +I.h.toFixed(3), iT: +I.iT.toFixed(4), iL: +I.iL.toFixed(4), band: +I.band.toFixed(3),
              silm: silms.map(S => +S.charge.toFixed(3)) }); nextS += 0.05; }
          }
          return { events: R.EVLOG(), curve, rite_len: R.RITE_LEN, stages: R.STAGES.map(s => [s[0], s[1].lat]) };
        }""", h)
        await b.close()
    if errs: print("ошибки страницы:", errs)
    (out / "events.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))
    return res

if __name__ == "__main__":
    page, out_dir = sys.argv[1], sys.argv[2]
    h = float(sys.argv[3]) if len(sys.argv) > 3 else 1 / 240
    res = asyncio.run(main(page, out_dir, h))
    print(len(res["events"]), "событий")
