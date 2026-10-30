#!/bin/sh
# Открыть V6 в foot, не устанавливая её в систему.
#   ./demo-v6.sh                 — обычная семья, size=14
#   ./demo-v6.sh size=16         — обычная, другой кегль
#   ./demo-v6.sh size=16 large   — вариант Large (кириллический x-height +6,4 %)
P="$(cd "$(dirname "$0")" && pwd)"
case "${2:-regular}" in
  large) SRC="$P/fonts/CutiveMono-Cyrillic-Large.ttf"; FAM="Cutive Mono Cyrillic Large"; TAG="Large" ;;
  *)     SRC="$P/fonts/CutiveMono-Cyrillic-Regular.ttf"; FAM="Cutive Mono Cyrillic"; TAG="V6" ;;
esac
rm -rf /tmp/v6-fonts && mkdir -p /tmp/v6-fonts
ln -sf "$SRC" /tmp/v6-fonts/
cat > /tmp/v6-fonts.conf <<CONF
<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "urn:fontconfig:fonts.dtd">
<fontconfig>
  <dir>/tmp/v6-fonts</dir>
  <cachedir>/tmp/fc-cache-v6</cachedir>
  <selectfont>
    <rejectfont>
      <glob>$HOME/.local/share/fonts/CutiveMonoCyrillic/*</glob>
    </rejectfont>
  </selectfont>
  <include ignore_missing="yes">/etc/fonts/fonts.conf</include>
</fontconfig>
CONF
[ -f /tmp/v6demo.txt ] || cat > /tmp/v6demo.txt <<'TXT'
Cutive Mono Cyrillic — V6 (6.020), демо без установки
────────────────────────────────────────────────────────
Съешь же ещё этих мягких французских булок.
В чащах юга жил бы цитрус? Да, но фальшивый экземпляр!
Как жизнь? Здание, экземпляр, Дом, Яблоко, ЪЫЬ, бвъыь.
The quick brown fox jumps over the lazy dog. 0123456789
TXT
FONTCONFIG_FILE=/tmp/v6-fonts.conf exec foot -o font="$FAM:${1:-size=14}" \
  -T "Cutive Mono Cyrillic $TAG" -e zsh -c 'cat /tmp/v6demo.txt; printf "\n"; exec zsh -i'
