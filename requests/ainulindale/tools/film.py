"""Снять анимацию кадр за кадром (кадр n — ровно n/FPS с) и наложить музыку.
    python3 tools/film.py SILENT.html AUDIO.wav OUT.mp4 [--w 1920 --h 1080 --fps 30 --jobs 2]"""
import argparse, asyncio, os, subprocess, sys
from playwright.async_api import async_playwright

ap = argparse.ArgumentParser()
ap.add_argument("html"); ap.add_argument("audio"); ap.add_argument("out")
ap.add_argument("--w", type=int, default=1920); ap.add_argument("--h", type=int, default=1080)
ap.add_argument("--fps", type=int, default=30); ap.add_argument("--jobs", type=int, default=2)
ap.add_argument("--len", type=float, default=304.0); ap.add_argument("--seg", type=float, default=19.0)
ap.add_argument("--work", default="/tmp/film_work")
a = ap.parse_args()
os.makedirs(a.work, exist_ok=True)
N = int(round(a.len * a.fps))
segs = []
step = int(a.seg * a.fps)
for i, f0 in enumerate(range(0, N, step)):
    segs.append((i, f0, min(N, f0 + step)))


async def render(seg, br):
    i, f0, f1 = seg
    out = f"{a.work}/seg{i:03d}.mp4"
    if os.path.exists(out):
        return
    pg = await br.new_page(viewport={"width": a.w, "height": a.h})
    await pg.goto("file://" + os.path.abspath(a.html))
    await pg.wait_for_timeout(800)
    await pg.evaluate("window.__manual = true; document.getElementById('start').style.display='none';"
                      "document.getElementById('bar').style.display='none'")
    tmp = out[:-4] + ".part.mp4"
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "image2pipe", "-framerate", str(a.fps), "-c:v", "mjpeg",
                           "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
                           "-r", str(a.fps), tmp], stdin=subprocess.PIPE)
    for f in range(f0, f1):
        await pg.evaluate(f"window.__frame({f / a.fps})")
        ff.stdin.write(await pg.screenshot(type="jpeg", quality=92))
        if (f - f0) % 150 == 0:
            print(f"seg {i}: {f - f0}/{f1 - f0}", flush=True)
    ff.stdin.close(); ff.wait()
    if ff.returncode == 0:
        os.rename(tmp, out)
    await pg.close()


async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch()
        queue = list(segs)

        async def worker():
            while queue:
                await render(queue.pop(0), br)
        await asyncio.gather(*[worker() for _ in range(a.jobs)])
        await br.close()

asyncio.run(main())
lst = f"{a.work}/list.txt"
open(lst, "w").write("".join(f"file '{a.work}/seg{i:03d}.mp4'\n" for i, _, _ in segs))
silent = f"{a.work}/silent.mp4"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", silent], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", silent, "-i", a.audio, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                "-c:a", "aac", "-b:a", "256k", "-t", str(a.len), "-movflags", "+faststart", a.out], check=True)
print("done", a.out)
