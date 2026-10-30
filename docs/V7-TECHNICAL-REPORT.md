# V7 — технический отчёт

Дата: 2026-10-30. База: V6.020. Сборка: `source/build.py` (VERSION
`7.000`), OTF — `source/tools/otf.py`. Хинтинг TTF — ttfautohint
1.8.4.16-eb64, тот же, что у латинского донора.

## 1. Файлы

| Файл | Размер | SHA-256 |
|---|---|---|
| `fonts/CutiveMono-Cyrillic-Regular.ttf` | 129 912 | `466f19055cc0ddc73cdcc1ac04143b22713d173e65dc70ee73fbc7bfcaf1d07a` |
| `fonts/CutiveMono-Cyrillic-Large.ttf` | 132 656 | `ba9be42f71675611af2e62c33d82de4fa6ab5cdcba7baa546af6c8ba283ed411` |
| `fonts/CutiveMono-Cyrillic-Regular.otf` | 146 228 | `8a425b70f53d2408ab0536b4b44a23d889c8c97c6c704bfbe5783c6d3bff0d24` |
| `fonts/CutiveMono-Cyrillic-Large.otf` | 146 544 | `c23d2061e7a094e5d3b76f44a6b614b24646863416f09b8158f045e4bb67ab60` |

Копии релиза: `backup/v7.000-installed/` (те же хеши,
`SHA256SUMS.txt`).

V6.020, которая остаётся для отката:

| Файл | SHA-256 |
|---|---|
| `backup/v6.020-installed/installed-regular.ttf` | `aaf8154e9983c661e88c4a3769266d2c4c1f3ff55a2cc063c5f1f397faac55f7` |
| `backup/v6.020-installed/installed-large.ttf` | `620a90ea7fa2d037a12341d65e46d811b8cf75ddd57008969423d6ab5910e730` |
| `backup/v6.020-installed/CutiveMono-Cyrillic-Regular.otf` | `d9ce6485a7987598eadc252328b189f1a28c14f126fb79e31732d4bdf5013a69` |
| `backup/v6.020-installed/CutiveMono-Cyrillic-Large.otf` | `442b3b01b60b068f47a9874518f8b314a699f226568180123f630ed896248c42` |

## 2. Состав

| Параметр | Значение |
|---|---|
| UPM | 2048 |
| Глифов | 582 |
| cmap | 577 |
| Латинских исходных | 452 (452/452 не изменены) |
| Кириллических | 128 (U+0400–U+052F) |
| Advance 1240 | 560 глифов |
| Нулевая ширина | 16 комбинируемых знаков (U+0300…U+0328) |
| `periodcentered` | 165 — как в оригинале, не трогали |
| cap / x-height | 1171 / 813 |
| Стемы / горизонтали / чаши | 96 / 86–82 / 92 |
| Засечка | 396×86 |
| Версия | 7.000, `head.fontRevision` 7.0 |
| fc-scan fontversion | 458752 |

## 3. Проверки

`source/tools/verify.py` (обе семьи):

```
Latin glyphs checked: 452, changed: 0
advance width 1240 for 560 glyphs
cmap entries: 577
hinted Cyrillic glyphs: 128, unhinted: 0
OK: all checks passed
```

`source/tools/audit.py`: `clean; latin ink ref=0.063; 66 glyphs checked`.
Ни одной буквы с «островом» или выходом заливки за пределы 0,55–1,95 от
латинской медианы.

Дополнительно:

* **GSUB и GDEF** — побайтно совпадают с V6.020;
* **GPOS** — 7 lookup’ов, фичи `kern`, `mark`, `mkmk`; латинские
  позиционирования (`AVATAR To Wa`, `The quick brown fox`, цифры) дают
  те же advances/offsets, что V6.020;
* **Latin hmtx** — 0 отличий у 392 латинских cmap-глифов;
* **NFC/NFD** — `й` = `и`+U+0306, `ё` = `е`+U+0308, `Ѐ` = `Е`+U+0300,
  `ӣ` = `и`+U+0304, `ї` = `і`+U+0308; NFD-последовательности
  раскладываются в те же композиты или позиционируются GPOS;
* **U+04B6/04B7** — `uni04B6`/`uni04B7`, yMin −350/−330, настоящий
  нижний выносной; **U+04C1/04C2** — контуры совпадают с V6.020;
* **bbox** — у кириллицы x 47…1193, y −371…1638; выходы только
  десцендеры и акценты, как и задумано; латинские «родные» выходы
  (K/Q и т. п.) не трогались;
* **OTF** — 582 глифа, 577 cmap, GSUB/GPOS/GDEF на месте, CFF FontName
  `CutiveMonoCyrillic-Regular` / `CutiveMonoCyrillicLarge-Regular`,
  OS/2 v4.

## 4. Приложения

Все тесты — с реальным рендерингом, без масштабирования готовых картинок.
Скриншоты: `specimens/v7/app/`.

### foot 1.28.0 (fcft 3.3.3, FreeType 2.15.0, HarfBuzz 15.0.0)

Проверены 11, 12, 13, 14, 16, 18, 20, 24 px (`pixelsize`, не pt).
Скриншоты `foot-11.png` … `foot-24.png`. На 11–14 px буквы читаются,
засечки и внутренние просветы сохраняются; хвосты Ц/Щ/Џ/Ҷ не слипаются
с соседями, ь/ъ/ы не теряют чашу. `installed-foot-14.png` — та же
проверка уже с установленной семьёй `Cutive Mono Cyrillic`.

### kitty 0.4x (те же FreeType/HarfBuzz)

Проверены те же 8 размеров (`font_size` = px×0.75 pt): `kitty-11.png` …
`kitty-24.png`. `installed-kitty-14.png` — установленная семья. На 11 px
кириллица чуть светлее, чем в foot, но различима; на 14–24 px плотность
совпадает с латиницей.

### Редактор кода

* **Vim** (в foot, 14 px): `vim-14.png` — Python-файл с кириллическими
  идентификаторами, комментариями и смешанной строкой.
* **VS Code 1.144.0** (Electron 43.8.3, 14 px): `code-14.png` — тот же
  файл; шрифт `Cutive Mono Cyrillic` виден в редакторе, колонки и
  отступы моноширинные. VS Code пришлось проверять после установки:
  временная семья `…V7 Test` не подхватывалась процессом Electron,
  потому что он не наследовал `FONTCONFIG_FILE`; это ограничение
  тестового стенда, а не шрифта.

### Nerd Fonts

`extended-20.png`: строка `Nerd fallback:         `
отрисована системным fallback (Iosevka Nerd Font), в основной файл
символы не встроены.

### Large

`large-14.png` — семья `Cutive Mono Cyrillic Large` в foot на 14 px:
кириллическая строчная выше на 6,4 % (x-height 865), латиница та же.
На 12 px (`foot-12` из общего набора) и 14 px текст читается.

## 5. Установка и откат

Установлены только TTF (как и V6): `~/.local/share/fonts/CutiveMonoCyrillic/`.
OTF лежат в `fonts/` и `backup/v7.000-installed/` для поставки.

Проверено:

1. V6 → V7: скопированы TTF, `fc-cache -f`, `fc-scan` даёт
   `fontversion 458752`, `fc-match` — установленный файл.
2. V7 → V6: скопированы `installed-regular.ttf` / `installed-large.ttf`,
   `fc-cache -f`, хеши вернулись к `aaf8154e…` / `620a90ea…`,
   `fontversion 394527` (6.020).
3. V6 → V7 повторно: хеши `466f1905…` / `ba9be42f…`,
   `fontversion 458752`.

Системный Fontconfig, fallback и Nerd-символы не менялись; `fc-cache`
запускался только для пользовательского каталога шрифтов.

## 6. Ограничения и честные замечания

* VS Code с временной тестовой семьёй не запустился с нужным шрифтом
  (Electron не унаследовал `FONTCONFIG_FILE`); проверка выполнена после
  установки, с настоящей семьёй.
* `foot`/`kitty` на 11 px остаются тонкими: это серифная моноширинная
  гарнитура, а не замена Terminus; речь о читаемости, а не о плотности
  санса.
* В `Large` кириллица на 6,4 % крупнее латиницы — это осознанное
  решение варианта, а не ошибка метрик.
* Хинтинг есть только в TTF; OTF (CFF) не содержит TrueType-инструкций
  и на 11–14 px будет светлее. Для терминалов используйте TTF.
