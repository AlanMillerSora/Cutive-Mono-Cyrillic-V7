#!/bin/sh
# Открыть V4 в foot, не устанавливая её в систему.
P="$(cd "$(dirname "$0")" && pwd)"
cat > /tmp/v4-fonts.conf <<CONF
<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "urn:fontconfig:fonts.dtd">
<fontconfig>
  <dir>$P/fonts</dir>
  <cachedir>/tmp/fc-cache-v4</cachedir>
  <include ignore_missing="yes">/etc/fonts/fonts.conf</include>
</fontconfig>
CONF
[ -f /tmp/v3demo.txt ] || printf 'Съешь же ещё этих мягких французских булок.\nThe quick brown fox jumps over the lazy dog.\n' > /tmp/v3demo.txt
FONTCONFIG_FILE=/tmp/v4-fonts.conf exec foot -o font="Cutive Mono Cyrillic:${1:-size=14}" \
  -T "Cutive Mono Cyrillic V4" -e zsh -c 'cat /tmp/v3demo.txt; printf "\n"; exec zsh -i'
