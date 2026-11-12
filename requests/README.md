# Заказы

Каждый заказ — папка `requests/<имя>/` (имя латиницей):

| Файл | Кто кладёт | Что |
|---|---|---|
| `brief.json` | ты (форма [бриф](../forms/brief.html)) | что нужно; любое поле можно опустить |
| `cues.json` | ты (форма [метки](../forms/cues.html)) или Claude (`kit scenes`) | времена событий видео/сценария |
| `plan.md`, `plan.json` | Claude (`kit plan`) | решения: умолчания, разделы, контрасты, библиотека |
| `piece.py` | Claude | партитура-код |
| `out/` | Claude (`kit run`) | `report.md/png`, `score.pdf/.mid/.musicxml`, `credits.txt`, `render.json` (звук — в беседе, не в git) |

Загрузить файлы в папку без git: https://github.com/Ranatar/immollimma/upload/main/requests/ИМЯ
