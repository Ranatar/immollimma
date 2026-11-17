"""Съёмка полного цикла ritus.html пошаговыми часами: кадр → JPEG → ffmpeg (без PNG на диск).
python3 film.py capture.html out.mp4 [fps] [секунды]   |   python3 film.py capture.html --stills t1,t2,..."""
import asyncio, subprocess, sys, os, pathlib
from playwright.async_api import async_playwright

W, H = 1920, 1080

async def open_page(p, path):
    b = await p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
    pg = await b.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
    await pg.goto(pathlib.Path(path).resolve().as_uri())
    await pg.wait_for_function("window.__ritus && typeof rt !== 'undefined' && rt > 0", timeout=20000)
    await pg.evaluate("document.fonts.ready")
    await pg.evaluate("paused = true; loopOn = false; build(); riteRestart(); document.getElementById('ui').style.display='none'")
    return b, pg

async def stills(path, times):
    async with async_playwright() as p:
        b, pg = await open_page(p, path)
        fps = 30
        for T in times:
            await pg.evaluate("(T) => { const R = window.__ritus; while (rt < T - 1e-6) { R.step(1/30); } R.render(); }", T)
            await pg.screenshot(path=f"still_{T:05.1f}.jpg", type="jpeg", quality=92)
        await b.close()

async def film(path, out, fps, seconds):
    n = int(round(seconds * fps))
    tmp = out[:-4] + ".part.mp4"
    ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "image2pipe", "-c:v", "mjpeg", "-framerate", str(fps), "-i", "-",
                           "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(fps), tmp],
                          stdin=subprocess.PIPE)
    async with async_playwright() as p:
        b, pg = await open_page(p, path)
        for k in range(n):
            await pg.evaluate("(T) => { const R = window.__ritus; while (rt < T - 1e-7) R.step(Math.min(1/120, T - rt)); R.render(); }", k / fps)
            ff.stdin.write(await pg.screenshot(type="jpeg", quality=92))
            if k % 150 == 0:
                print(f"{k}/{n}", flush=True)
        await b.close()
    ff.stdin.close()
    if ff.wait() == 0:
        os.replace(tmp, out)
        print("done", out)
    else:
        print("ffmpeg failed")

if __name__ == "__main__":
    if sys.argv[2] == "--stills":
        asyncio.run(stills(sys.argv[1], [float(x) for x in sys.argv[3].split(",")]))
    else:
        fps = int(sys.argv[3]) if len(sys.argv) > 3 else 30
        sec = float(sys.argv[4]) if len(sys.argv) > 4 else 102.0
        asyncio.run(film(sys.argv[1], sys.argv[2], fps, sec))
