"""Съёмка обряда aldudenie.html пошаговыми часами: кадр n = n/fps с → JPEG q92 → ffmpeg (кадры не пишутся на диск).
python3 film.py page.html out.mp4 [кадр_с кадр_по] [fps]   |   python3 film.py page.html --stills t1,t2,..
Кусок с кадра k0 сначала прокручивает обряд теми же шагами без отрисовки — состояние совпадает с прогоном с нуля."""
import asyncio, subprocess, sys, os, pathlib
from playwright.async_api import async_playwright

W, H = 1920, 1080
STEP = "(T) => { const R = window.__rite; while (R.rt < T - 1e-7) R.step(Math.min(1/120, T - R.rt)); }"

async def open_page(p, path):
    b = await p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
    pg = await b.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
    await pg.goto(pathlib.Path(path).resolve().as_uri())
    await pg.wait_for_function("window.__rite && __rite.rt > 0.05", timeout=30000)
    await pg.evaluate("document.fonts.ready")
    await pg.evaluate("paused = true; loopOn = false; riteRestart(); for (const id of ['ui','tl']) { const e = document.getElementById(id); if (e) e.style.display = 'none'; }")
    return b, pg

async def stills(path, times):
    async with async_playwright() as p:
        b, pg = await open_page(p, path)
        for T in times:
            await pg.evaluate(STEP, T); await pg.evaluate("__rite.render()")
            await pg.screenshot(path=f"still_{T:05.1f}.jpg", type="jpeg", quality=92)
        await b.close()

async def film(path, out, k0, k1, fps):
    tmp = out[:-4] + ".part.mp4"
    ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "image2pipe", "-c:v", "mjpeg", "-framerate", str(fps), "-i", "-",
                           "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(fps), tmp],
                          stdin=subprocess.PIPE)
    async with async_playwright() as p:
        b, pg = await open_page(p, path)
        for k in range(k0):                      # прокрутка теми же шагами, что и при съёмке
            await pg.evaluate(STEP, k / fps)
        for k in range(k0, k1):
            await pg.evaluate(STEP, k / fps); await pg.evaluate("__rite.render()")
            ff.stdin.write(await pg.screenshot(type="jpeg", quality=92))
            if k % 150 == 0: print(f"{out}: {k}/{k1}", flush=True)
        await b.close()
    ff.stdin.close()
    if ff.wait() == 0:
        os.replace(tmp, out); print("done", out, flush=True)
    else:
        print("ffmpeg failed", out, flush=True)

if __name__ == "__main__":
    if sys.argv[2] == "--stills":
        asyncio.run(stills(sys.argv[1], [float(x) for x in sys.argv[3].split(",")]))
    else:
        fps = int(sys.argv[5]) if len(sys.argv) > 5 else 30
        asyncio.run(film(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), fps))
