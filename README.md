# Cutive Mono Cyrillic V7

Полная кириллическая версия **Cutive Mono** (Vernon Adams): русский,
украинский, белорусский и расширенный кириллический набор в характере
оригинального печатного typewriter-шрифта.

* Версия: **7.000** (2026-10-30)
* Семьи: `Cutive Mono Cyrillic`, `Cutive Mono Cyrillic Large`
* Форматы: TTF (хинченный, для терминалов) и OTF (CFF)
* UPM 2048, advance 1240, 582 глифа, 577 cmap, 128 кириллических
* Латиница: 452/452 исходных контура не изменены
* 25 кириллических глифов используют готовые латинские контуры

Репозиторий: https://github.com/AlanMillerSora/Cutive-Mono-Cyrillic-V7

## Документы

| Файл | Содержание |
|---|---|
| `docs/V7.md` | что изменено и почему |
| `docs/V7-GLYPH-AUDIT.md` | решение по каждому глифу |
| `docs/V7-LATIN-REUSE.md` | таблица «кириллица → латинский контур» |
| `docs/V7-TECHNICAL-REPORT.md` | проверки, приложения, хеши |
| `docs/V7-INSTALL-ROLLBACK.md` | установка и откат на V6 |
| `docs/CHANGELOG.md` | история версий |
| `specimens/v7/` | сравнения V6/V7 и скриншоты приложений |

## Сборка

```bash
python3 source/build.py          # TTF Regular + Large, с ttfautohint
python3 source/tools/otf.py      # OTF из готовых TTF
python3 source/tools/verify.py   # 452/452 латиницы, 128/128 хинтинга
python3 source/tools/audit.py    # растровый аудит
```

Исходники: `source/design/*.py` (рабочий источник), плюс экспорт
`source/CutiveMonoCyrillic.ufo` и `.glyphs`.

## Установка

```bash
install -Dm644 fonts/CutiveMono-Cyrillic-Regular.ttf \
  ~/.local/share/fonts/CutiveMonoCyrillic/CutiveMono-Cyrillic-Regular.ttf
install -Dm644 fonts/CutiveMono-Cyrillic-Large.ttf \
  ~/.local/share/fonts/CutiveMonoCyrillic/CutiveMono-Cyrillic-Large.ttf
fc-cache -f
```

Откат — `docs/V7-INSTALL-ROLLBACK.md`; V6.020 лежит в
`backup/v6.020-installed/`.

## Лицензия

SIL Open Font License 1.1, см. `docs/LICENSE`. Это неофициальный форк,
не связанный с автором оригинала.
