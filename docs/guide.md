# Руководство по комплекту

## Устройство

```
заказ (requests/<имя>/brief.json, cues.json)
   │  python3 -m kit plan requests/<имя>          → plan.md, plan.json   (умолчания, разделы, контрасты, лицензия)
   ▼
piece.py: build(ctx) → Piece (список событий)       ← пишет Claude по плану
   │  python3 -m kit run requests/<имя>/piece.py --sketch     (эскиз: первые N секунд)
   │  python3 -m kit run requests/<имя>/piece.py              (целиком)
   ▼
out/: events.json · audio.wav/mp3 · score.mid/musicxml/pdf · report.md/png · credits.txt · render.json
```

| Модуль | Что делает |
|---|---|
| `kit/instruments.py` | 74 инструмента и штриха с едиными именами (`vln_sus`, `hn_mute`, `celesta`…), из какой библиотеки брать, настоящий диапазон, шина, партия для нот |
| `kit/events.py` | `Piece`: события `note`, `sample`, `grains`, `mark`; время в секундах; `p.b(beats)`, `p.bar(n)`; сохранение в JSON |
| `kit/devices.py` | приёмы (`Composer`): `pad` (с «гнилью» detune/drift), `motif`, `arpeggio`, `chorale`, `ostinato`, `melody`, `music_box`, `timp`, `heartbeat`, `march`, `spores`, `breath`, `shepard`, `buzz`, `swell`, `fx` |
| `kit/harmony.py` | высоты (`midi("D4")`), лады, ступени (`roman(2, "V7", "minor")`), `in_range`, голосоведение `voice` |
| `kit/fx.py` | каталог шумов и ударных: 49 видов (`alien`, `siren`, `chain`, `glass`, `gong_scrape`, `tamtam`, `ratchet`…) |
| `kit/render.py` | события → шины → WAV; выбор библиотеки на каждую ноту; окно `t0..t1`; выравнивание шин по эталону |
| `kit/sampler.py` | прежний семплер (сырые записи VSCO, ресемплинг от ближайшей ноты, склейка длинных нот, гранулярика) |
| `kit/sfz_engine.py` | sfizz через `libsfizz.so`: нота по SFZ-разметке → те же преобразования |
| `kit/mix.py` | шины, общий зал (свёртка), стемы, громкость (−16 LUFS), MP3, наложение на видео |
| `kit/export.py` | MIDI, MusicXML (квантование, divisi, техники текстом), PDF через LilyPond |
| `kit/qa.py` | отчёт приборов (§ ниже) |
| `kit/plan.py` | план: умолчания, разделы, таблица контрастов, библиотека и лицензия |
| `kit/request.py` | чтение брифа с умолчаниями из схемы, меток, разделов; смены сцен из видео (ffmpeg) |
| `kit/styles/*.json` | 12 карточек стилей |

## Библиотеки и выбор источника

`library` в брифе (или `--backend`): `plain` (по умолчанию) — прежний семплер VSCO; `vsco` — VSCO через
SFZ; `sso` — Sonatina через SFZ. Если у выбранной библиотеки нет инструмента, нота берётся у другой; в
`render.json` видно, кто что сыграл (`by_instrument`). Реклама (`commercial_ad`) — только VSCO.

## Пьеса

```python
from kit.events import Piece
from kit.devices import Composer
from kit.harmony import MIN, MAJ, roman, in_range

def build(ctx):                      # ctx.brief, ctx.cues, ctx.plan — из файлов рядом
    p = Piece("Название", bpm=72, meter=(4, 4), key="D minor")
    c = Composer(p)                  # lib="sso" — споры из семплов Sonatina
    p.mark(0, "A")
    c.pad(0, p.bar(4), (2, MIN), vel=0.4)
    p.line("ob_sus", [(74, 2), (73, 2), (74, 4)], t=0)
    c.timp(p.bar(4), 2, vel=0.8)
    c.fx("glass", p.bar(4) + 0.1, gain=0.3)
    return p
```

Высота — **звучащая** MIDI (дроби можно: 62.5 = четверть тона). Громкость — `vel` (0..1, выбирает слой и
тембр) и `gain` (уровень). Шина по умолчанию — из реестра; своя — `bus="deep"` и т. п.
Уровни шин и посылы в зал: `p.meta["gains"]`, `p.meta["sends"]` (умолчания в `kit/mix.py`).

## Отчёт приборов (`report.md`, `report.png`)

| Строка | Как читать |
|---|---|
| level p10/p50/p90 | разброс громкости; у живой пьесы p90 − p10 ≈ 12–20 дБ |
| gaps | провалы ниже −50 дБ дольше секунды (кроме объявленной тишины) — дыра или утонувший голос |
| clipped / clicks | должны быть 0 / нет |
| centroid, >2 kHz | яркость; длинный ровный участок — тембр не меняется |
| flat stretches | 20-секундные окна, где тембр и гармония почти не меняются — кандидат в скуку (для минимализма норма) |
| novelty peaks | где музыка меняется сильнее всего — сравнить с задуманными разделами (зелёные линии меток) |
| score | ноты вне настоящего диапазона (важно для живых), растянутые далеко за запись (звучат искусственно) |

Нижняя панель картинки — карта занятости партий: видно, кто когда играет и где все играют одно и то же.

## Формы

`forms/brief.html`, `forms/cues.html` (GitHub Pages: https://ranatar.github.io/immollimma/). Схемы —
`schemas/*.schema.json`; любое поле брифа можно опустить. Метки можно сделать и из видео командой
`python3 -m kit scenes видео.mp4 --out requests/<имя>/cues.json`.

## Обслуживание

- `tools/setup.sh` — среда с нуля; `python3 -m kit check` — что установлено.
- `tools/calibrate.py` — перемерить SFZ-инструменты (после правки реестра); `--only a,b`.
- `tools/index_samples.py` — пересобрать индекс прежнего семплера (≈ 10 мин).
- `tools/export_registry.py` — реестр для форм (`kit/data/instruments.json`).
- `tools/selftest.sh` — собрать три эталона и проверить отчёты.
