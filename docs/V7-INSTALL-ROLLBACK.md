# V7 — установка и откат

## Что установлено сейчас

`~/.local/share/fonts/CutiveMonoCyrillic/`:

| Файл | Версия | SHA-256 |
|---|---|---|
| `CutiveMono-Cyrillic-Regular.ttf` | 7.000 | `466f19055cc0ddc73cdcc1ac04143b22713d173e65dc70ee73fbc7bfcaf1d07a` |
| `CutiveMono-Cyrillic-Large.ttf` | 7.000 | `ba9be42f71675611af2e62c33d82de4fa6ab5cdcba7baa546af6c8ba283ed411` |

Семьи: `Cutive Mono Cyrillic` и `Cutive Mono Cyrillic Large`.
OTF-файлы в установку не копировались (как и в V6); они лежат в
`fonts/` и `backup/v7.000-installed/`.

## Установка V7 (если понадобится повторить)

```bash
cd /home/sora/Projects/Cutive-Mono-Cyrillic-V7

install -Dm644 fonts/CutiveMono-Cyrillic-Regular.ttf \
  ~/.local/share/fonts/CutiveMonoCyrillic/CutiveMono-Cyrillic-Regular.ttf
install -Dm644 fonts/CutiveMono-Cyrillic-Large.ttf \
  ~/.local/share/fonts/CutiveMonoCyrillic/CutiveMono-Cyrillic-Large.ttf

fc-cache -f
fc-scan --format '%{family} | %{fontversion}\n' \
  ~/.local/share/fonts/CutiveMonoCyrillic/CutiveMono-Cyrillic-Regular.ttf
# ожидается: Cutive Mono Cyrillic | 458752
```

`fc-match "Cutive Mono Cyrillic"` должен указывать на файл в
`~/.local/share/fonts/CutiveMonoCyrillic/`, а не на системный Cutive Mono.

## Откат на V6.020

Резервная копия: `backup/v6.020-installed/`.

```bash
cd /home/sora/Projects/Cutive-Mono-Cyrillic-V7

install -Dm644 backup/v6.020-installed/installed-regular.ttf \
  ~/.local/share/fonts/CutiveMonoCyrillic/CutiveMono-Cyrillic-Regular.ttf
install -Dm644 backup/v6.020-installed/installed-large.ttf \
  ~/.local/share/fonts/CutiveMonoCyrillic/CutiveMono-Cyrillic-Large.ttf

fc-cache -f
sha256sum ~/.local/share/fonts/CutiveMonoCyrillic/*.ttf
# Regular: aaf8154e9983c661e88c4a3769266d2c4c1f3ff55a2cc063c5f1f397faac55f7
# Large:   620a90ea7fa2d037a12341d65e46d811b8cf75ddd57008969423d6ab5910e730
```

После `fc-cache` уже открытые терминалы/редакторы могут продолжать
показывать старый шрифт до перезапуска — это кеш приложения, не файла.

## Возврат на V7

Повторите команды раздела «Установка V7» и сверьте хеши из таблицы выше.

## Что нельзя делать без необходимости

* не менять системный Fontconfig и fallback;
* не встраивать Nerd Fonts в основной файл — символы должны приходить
  системным fallback;
* не запускать `maintenance/update.py` / `maintenance/install.py`:
  они делают `reset --hard` и копируют поверх `$HOME`.
