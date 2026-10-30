# Установка в Arch Linux

Всё ставится в домашний каталог, без sudo и без изменения системных
файлов. Откат — одной командой.

## 1. Шрифт

```bash
mkdir -p ~/.local/share/fonts/CutiveMonoCyrillic
cp fonts/CutiveMono-Cyrillic-Regular.ttf ~/.local/share/fonts/CutiveMonoCyrillic/
cp fonts/CutiveMono-Cyrillic-Regular.otf ~/.local/share/fonts/CutiveMonoCyrillic/  # опционально
fc-cache -f ~/.local/share/fonts
```

Проверка:

```bash
fc-match "Cutive Mono Cyrillic"
# -> CutiveMono-Cyrillic-Regular.ttf: "Cutive Mono Cyrillic" "Regular"
```

Достаточно TTF; OTF ставьте, только если он нужен конкретному приложению.
Оба файла содержат одинаковый набор глифов.

## 2. Fontconfig (опционально)

Файл `config/50-cutive-mono-cyrillic.conf` делает гарнитуру предпочтительной
для `monospace` и добавляет fallback на Nerd Font Symbols.

```bash
mkdir -p ~/.config/fontconfig/conf.d
cp config/50-cutive-mono-cyrillic.conf ~/.config/fontconfig/conf.d/
fc-cache -f
```

**Важно.** Если у вас уже есть `~/.config/fontconfig/fonts.conf`,
fontconfig может не читать `conf.d/` автоматически. Тогда добавьте внутрь
элемента `<fontconfig>` в `fonts.conf` одну строку:

```xml
<include ignore_missing="yes">conf.d</include>
```

Не хотите трогать `fonts.conf` — не копируйте конфиг вообще: шрифт уже
установлен и доступен по имени `Cutive Mono Cyrillic`. Конфиг нужен только
для того, чтобы он подхватывался как `monospace` по умолчанию.

## 3. Терминал

foot (`~/.config/foot/foot.ini`):

```ini
font=Cutive Mono Cyrillic:size=14
```

kitty (`~/.config/kitty/kitty.conf`):

```conf
font_family Cutive Mono Cyrillic
font_size 11.0
```

Перезапустите терминал. Для проверки одной сессии:

```bash
foot -o font="Cutive Mono Cyrillic:size=14"
kitty --override font_family="Cutive Mono Cyrillic"
```

## 4. Nerd Fonts

Иконки не встроены в шрифт — это отдельный fallback, как и задумано.

```bash
# symbols-only вариант с сайта Nerd Fonts:
# https://github.com/ryanoasis/nerd-fonts/releases  (NerdFontsSymbolsOnly.zip)
mkdir -p ~/.local/share/fonts/NerdFontsSymbols
unzip NerdFontsSymbolsOnly.zip -d ~/.local/share/fonts/NerdFontsSymbols
fc-cache -f
fc-match "Symbols Nerd Font"
```

Если у вас уже стоит полный Nerd Font (например, Iosevka NF), отдельный
Symbols Only не обязателен: kitty и foot сами находят подходящий шрифт
для недостающих кодпоинтов.

Проверка одной строкой:

```bash
echo 'Привет  󰊢  󰣇  error' | foot -o font="Cutive Mono Cyrillic:size=14"
```

## 5. Проверка раскладки EN/RU

```bash
# переключение раскладки в Hyprland
hyprctl switchxkblayout all next
```

Наберите подряд:

```
The quick brown fox
Съешь же ещё этих мягких булок
English + Русский + 1234567890
```

Буквы должны стоять в одной сетке, без скачка кегля, веса и ширины.

## 5a. Обновление до V2 и откат

V2 уже установлен в `~/.local/share/fonts/CutiveMonoCyrillic/`.

Установить заново (из папки проекта):

```bash
cp fonts/CutiveMono-Cyrillic-Regular.ttf ~/.local/share/fonts/CutiveMonoCyrillic/
fc-cache -f ~/.local/share/fonts
```

Обновить до V6 (установлена, см. также `backup/v5-fonts/`):

```bash
cp fonts/CutiveMono-Cyrillic-Regular.ttf ~/.local/share/fonts/CutiveMonoCyrillic/
fc-cache -f ~/.local/share/fonts
```

Откатиться на V5:

```bash
cp backup/v5-fonts/CutiveMono-Cyrillic-Regular.ttf ~/.local/share/fonts/CutiveMonoCyrillic/
fc-cache -f ~/.local/share/fonts
```

Откатиться на V4:

```bash
cp backup/v4-fonts/CutiveMono-Cyrillic-Regular.ttf ~/.local/share/fonts/CutiveMonoCyrillic/
fc-cache -f ~/.local/share/fonts
```

Откатиться на V3:

```bash
cp backup/v3-fonts/CutiveMono-Cyrillic-Regular.ttf ~/.local/share/fonts/CutiveMonoCyrillic/
fc-cache -f ~/.local/share/fonts
```

Откатиться на V2:

```bash
cp backup/v2-fonts/CutiveMono-Cyrillic-Regular.ttf ~/.local/share/fonts/CutiveMonoCyrillic/
fc-cache -f ~/.local/share/fonts
```

Откатиться на V1:

```bash
cp backup/v1-fonts/CutiveMono-Cyrillic-Regular.ttf ~/.local/share/fonts/CutiveMonoCyrillic/
fc-cache -f ~/.local/share/fonts
```

Проверить, что подхватился нужный файл:

```bash
fc-match "Cutive Mono Cyrillic"
```

## 6. Удаление

```bash
rm -rf ~/.local/share/fonts/CutiveMonoCyrillic
rm -f ~/.config/fontconfig/conf.d/50-cutive-mono-cyrillic.conf
fc-cache -f
```

Если добавляли строку `<include>` в `fonts.conf` — уберите её.

## 7. Если что-то не подхватилось

```bash
fc-list | grep -i cutive          # видит ли система файл
fc-match "Cutive Mono Cyrillic"   # какое семейство реально выбирается
fc-match -s "Cutive Mono Cyrillic" | head -5   # цепочка fallback
fc-cache -fv | grep -i cutive     # что делает кэш
```

Приложения, которые стартовали до `fc-cache`, могут держать старый список
шрифтов: перезапустите их (VS Code, Firefox, Chromium).
