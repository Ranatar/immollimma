"""Прогон полного цикла protocol.html пошаговыми часами: журнал событий + моменты пробуждения/ухода каждой ниши."""
import asyncio, json, sys, pathlib
from playwright.async_api import async_playwright
async def main(page, out, h):
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={"width": 1920, "height": 1080})
        await pg.goto(pathlib.Path(page).resolve().as_uri()); await pg.wait_for_function("window.__protocol", timeout=15000)
        res = await pg.evaluate("""(h) => { paused = true; loopOn = false; riteRestart(); const P = window.__protocol; P.EVLOG().length = 0;
          while (P.rt < P.RITE_LEN - 1e-6) P.step(Math.min(h, P.RITE_LEN - P.rt));
          return { events: P.EVLOG(), niches: P.niches(), cells: cells.map(q => ({ side: q.side, r: q.r, c: q.c, t: +(T_WALL + q.d / (H * V_WALL)).toFixed(3) })), rite_len: P.RITE_LEN, stages: P.STAGES, beats: P.BEATS, beats_acc: P.BEATS_ACC }; }""", h)
        await b.close()
    pathlib.Path(out).write_text(json.dumps(res, ensure_ascii=False, indent=1)); return res
if __name__ == "__main__":
    r = asyncio.run(main(sys.argv[1], sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 1/240))
    print(len(r["events"]), "событий,", len(r["niches"]), "ниш")
