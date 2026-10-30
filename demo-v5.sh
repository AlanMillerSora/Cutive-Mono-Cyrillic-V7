#!/bin/sh
# Открыть V5 из backup/v5-fonts в foot, не устанавливая её в систему.
# Системная V3 (та же семья) на время демонстрации отключается через rejectfont.
P="$(cd "$(dirname "$0")" && pwd)"
rm -rf /tmp/v5-fonts && mkdir -p /tmp/v5-fonts
ln -sf "$P/backup/v5-fonts/CutiveMono-Cyrillic-Regular.ttf" /tmp/v5-fonts/
cat > /tmp/v5-fonts.conf <<CONF
<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "urn:fontconfig:fonts.dtd">
<fontconfig>
  <dir>/tmp/v5-fonts</dir>
  <cachedir>/tmp/fc-cache-v5</cachedir>
  <selectfont>
    <rejectfont>
      <glob>$HOME/.local/share/fonts/CutiveMonoCyrillic/*</glob>
    </rejectfont>
  </selectfont>
  <include ignore_missing="yes">/etc/fonts/fonts.conf</include>
</fontconfig>
CONF
[ -f /tmp/v5demo.txt ] || cat > /tmp/v5demo.txt <<'TXT'
Cutive Mono Cyrillic — V5 (5.000), не установлена
────────────────────────────────────────────────────────
Съешь же ещё этих мягких французских булок.
В чащах юга жил бы цитрус? Да, но фальшивый экземпляр!
Как жизнь? Здание, экземпляр, Дом, Яблоко, ЪЫЬ, бвъыь.
The quick brown fox jumps over the lazy dog. 0123456789
TXT
FONTCONFIG_FILE=/tmp/v5-fonts.conf exec foot -o font="Cutive Mono Cyrillic:${1:-size=14}" \
  -T "Cutive Mono Cyrillic V5" -e zsh -c 'cat /tmp/v5demo.txt; printf "\n"; exec zsh -i'
