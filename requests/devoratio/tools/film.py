"""Съёмка полного цикла devoratio.html пошаговыми часами: кадр → JPEG → ffmpeg.
python3 film.py devoratio.html out.mp4 [fps] [секунды] [ширина высота]"""
import asyncio, subprocess, sys, os, pathlib, time
from playwright.async_api import async_playwright
SYNC = "document.getElementById('gl').getContext('webgl2').readPixels(0,0,1,1,6408,5121,new Uint8Array(4))"

async def film(path, out, fps, seconds, W, H):
    n = int(round(seconds * fps)); tmp = out[:-4] + ".part.mp4"
    ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "image2pipe", "-c:v", "mjpeg", "-framerate", str(fps), "-i", "-",
                           "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(fps), tmp], stdin=subprocess.PIPE)
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        pg = await b.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
        await pg.goto(pathlib.Path(path).resolve().as_uri())
        await pg.wait_for_function("window.__dev", timeout=20000)
        await pg.evaluate("__dev.paused = true; __dev.loop = false; __dev.restart(); document.getElementById('ui').style.display='none'")
        T = time.time()
        for f in range(n):
            await pg.evaluate("(T) => { const D = window.__dev; D.render(1/30); while (D.rt < T - 1e-7) D.step(Math.min(1/60, T - D.rt)); }", (f + 1) / fps)
            await pg.evaluate(SYNC)
            ff.stdin.write(await pg.screenshot(type="jpeg", quality=92))
            if f % 150 == 0: print(f"{f}/{n} {time.time() - T:.0f}s", flush=True)
        await b.close()
    ff.stdin.close()
    if ff.wait() == 0: os.replace(tmp, out); print("done", out, flush=True)
    else: print("ffmpeg failed", flush=True)

if __name__ == "__main__":
    a = sys.argv
    fps = int(a[3]) if len(a) > 3 else 30; sec = float(a[4]) if len(a) > 4 else 110.0
    W, H = (int(a[5]), int(a[6])) if len(a) > 6 else (1920, 1080)
    asyncio.run(film(a[1], a[2], fps, sec, W, H))
