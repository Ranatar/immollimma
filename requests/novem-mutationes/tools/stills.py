import asyncio, sys
from playwright.async_api import async_playwright
TIMES=[float(x) for x in sys.argv[1].split(',')]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        pg = await b.new_page(viewport={"width":1920,"height":1080})
        errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("file:///home/claude/tz/capture.html")
        await pg.wait_for_function("window.__ritus && rt>0", timeout=20000)
        await pg.evaluate("paused=true; loopOn=false; riteRestart(); document.getElementById('ui').style.display='none'")
        for T in TIMES:
            await pg.evaluate("""(T)=>{ const R=window.__ritus; while(rt < T-0.6) R.step(1/30); while(rt < T-1e-6){ R.step(1/30); R.render(); } }""", T)
            await pg.screenshot(path=f"r_{T:05.1f}.jpg", type="jpeg", quality=88)
        print(errs)
        await b.close()
asyncio.run(main())
