"""Съёмка полного цикла protocol.html пошаговыми часами: кадр → JPEG → ffmpeg.
python3 film.py protocol.html out.mp4 [fps] [секунды]"""
import asyncio, subprocess, sys, os, pathlib
from playwright.async_api import async_playwright
W, H = 1920, 1080
async def film(path, out, fps, seconds):
    n = int(round(seconds * fps)); tmp = out[:-4] + ".part.mp4"
    ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "image2pipe", "-c:v", "mjpeg", "-framerate", str(fps), "-i", "-",
                           "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(fps), tmp], stdin=subprocess.PIPE)
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        pg = await b.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
        await pg.goto(pathlib.Path(path).resolve().as_uri())
        await pg.wait_for_function("window.__protocol", timeout=20000)
        await pg.evaluate("paused = true; loopOn = false; riteRestart(); document.getElementById('ui').style.display='none'")
        for k in range(n):
            await pg.evaluate("(T) => { const P = window.__protocol; while (P.rt < T - 1e-7) P.step(Math.min(1/120, T - P.rt)); P.render(); }", k / fps)
            ff.stdin.write(await pg.screenshot(type="jpeg", quality=92))
            if k % 300 == 0: print(f"{k}/{n}", flush=True)
        await b.close()
    ff.stdin.close()
    if ff.wait() == 0: os.replace(tmp, out); print("done", out)
    else: print("ffmpeg failed")
if __name__ == "__main__":
    asyncio.run(film(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 30, float(sys.argv[4]) if len(sys.argv) > 4 else 96.0))
