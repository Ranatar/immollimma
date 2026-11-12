# immollimma

Сочинение оркестровой музыки через Claude: партитура пишется кодом и исполняется **настоящими
оркестровыми записями** (VSCO-2 Community Edition, Sonatina Symphonic Orchestra), выходят звук, ноты
(MIDI, MusicXML, PDF) и отчёт приборов — замена слуха, которого у Claude нет.

**Формы заказа:** https://ranatar.github.io/immollimma/ — [бриф](forms/brief.html) и [метки по видео](forms/cues.html).

## Как заказать музыку

1. Заполни [бриф](forms/brief.html). Всё необязательно: пустое решается умолчаниями, и план скажет, что выбрано.
2. Музыка к видео — [расставь метки](forms/cues.html) прямо по видео (файл не покидает компьютер), или
   не расставляй: смены сцен найдутся сами.
3. Положи `brief.json` (и `cues.json`) в `requests/<имя>/` — кнопкой «Открыть загрузку в GitHub» в форме —
   или приложи файлы к беседе.
4. Напиши Claude: «сделай музыку по `requests/<имя>`» (в беседе с подключённым репозиторием или с
   навыком immollimma). Дальше: план → эскиз → полная версия → MP3, партитура, отчёт.
5. Отзыв — по таймкодам: «1:40–2:05 пиццикато назойливо, тише и реже». Он попадает в [`taste.md`](taste.md),
   и следующие заказы учитывают его без вопросов.

Пример заказа — [`requests/_example`](requests/_example) (колыбельная, которая портится).

## Что внутри

| Путь | Что |
|---|---|
| `.claude/skills/immollimma/SKILL.md` | порядок работы Claude: что читать, когда спрашивать, как проверять и отдавать |
| `taste.md` | вкус заказчика: реакции, правила, гипотезы |
| `kit/` | ядро: инструменты (74 штриха), события, приёмы, рендер, сведение, ноты, отчёт, план — [docs/guide.md](docs/guide.md) |
| `kit/styles/` | 12 карточек стилей (барокко … архивный гротеск … русская стилизация) |
| `schemas/` | JSON-схемы брифа и меток с умолчаниями |
| `forms/` | HTML-формы (GitHub Pages) |
| `examples/` | эталоны: `chorale_prelude` (барокко, ноты), `nocturne` (импрессионизм, две библиотеки), `phase` (минимализм), `rsfgr` (музыка к видео Р.С.Ф.Г.Р. 1920–2000) |
| `requests/` | заказы: бриф, метки, план, партитура-код, отчёт, ноты |
| `tools/` | `setup.sh` (среда с нуля), `calibrate.py`, `index_samples.py`, `export_registry.py`, `selftest.sh` |
| `docs/` | [libraries.md](docs/libraries.md) — разбор библиотек и возможностей; [guide.md](docs/guide.md) — устройство; [pitfalls.md](docs/pitfalls.md) — грабли |
| `bin/libsfizz.so` | движок SFZ (sfizz, BSD-2, собран под Ubuntu 24.04 x86-64) |

## Запуск вручную

```sh
sh tools/setup.sh                                  # библиотеки (≈ 4,4 ГБ) в libs/, пакеты, проверка
python3 -m kit plan requests/_example              # план
python3 -m kit run examples/nocturne/piece.py      # звук, ноты, отчёт → examples/nocturne/out/
python3 -m kit run piece.py --sketch --parts       # эскиз (первые sketch_seconds) + баланс партий
python3 -m kit run piece.py --from 120 --to 180    # кусок длинной пьесы
python3 -m kit run piece.py --backend sso          # всё через Sonatina
python3 -m kit scenes clip.mp4 --out cues.json     # метки по сменам сцен
python3 -m kit mux out/audio.mp3 clip.mp4 out/clip_music.mp4
```

Это работает и на Ubuntu-виртуалке (Python 3.10+, ffmpeg; LilyPond — для PDF).

## Лицензии

- Код — MIT (`LICENSE`).
- **VSCO-2 CE** — CC0: что угодно, включая рекламу. В титрах: «Samples: VSCO 2 Community Edition (Versilian Studios), CC0».
- **Sonatina Symphonic Orchestra** — CC Sampling Plus 1.0: музыка из семплов — свободно, **кроме рекламы**
  (можно рекламировать саму работу и автора). Для рекламы — `commercial_ad: true` в брифе, тогда только VSCO.
- **sfizz** — BSD-2-Clause (`bin/LICENSE.sfizz`).

Каждый рендер пишет `credits.txt` с нужными строками.
