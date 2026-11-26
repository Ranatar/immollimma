"""Собрать самодостаточную страницу: tools/anim.html + out/anim.json + музыка (mp3) + шрифт для «Эа».
    python3 tools/build_html.py out/anim.json AUDIO.mp3 FONT.ttf OUT.html  (AUDIO = '-' — без музыки)"""
import base64, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
data, audio, font, out = sys.argv[1:5]
s = open(os.path.join(HERE, "anim.html")).read()
s = s.replace("/*DATA*/", open(data).read())
s = s.replace("/*FONT*/", base64.b64encode(open(font, "rb").read()).decode())
s = s.replace("/*AUDIO*/", "" if audio == "-" else base64.b64encode(open(audio, "rb").read()).decode())
open(out, "w").write(s)
print(out, len(s) // 1024, "KB")
