#!/usr/bin/env python3
"""V5 specimens: V3/V4/V5 comparison, alphabets, sizes, mixed text."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "specimens" / "v5"
V5 = ROOT / "fonts" / "CutiveMono-Cyrillic-Regular.ttf"
V4 = ROOT / "backup" / "v4-fonts" / "CutiveMono-Cyrillic-Regular.ttf"
V3 = ROOT / "backup" / "v3-fonts" / "CutiveMono-Cyrillic-Regular.ttf"
BG, INK, ACC = "#fdfcf8", "#171717", "#7a2d4a"

EN1 = "The quick brown fox jumps over the lazy dog."
RU1 = "Съешь же ещё этих мягких французских булок."
RU2 = "В чащах юга жил бы цитрус? Да, но фальшивый экземпляр!"
RU3 = "Дом. Жизнь. Это. Яблоко."
MIX1 = "English + Русский + 1234567890"
MIX2 = "Arch Linux — операционная система на базе Linux."
MIX3 = '$ git commit -m "Добавлена кириллица"'
CAPS = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
LOWS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"


def lf(size=15):
    return ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans.ttf", size)


def line(text, size, font=V5, pad=16):
    f = ImageFont.truetype(str(font), size)
    asc, desc = f.getmetrics()
    im = Image.new("RGB", (int(f.getlength(text)) + pad * 2, asc + desc + pad), BG)
    ImageDraw.Draw(im).text((pad, pad // 2), text, font=f, fill=INK)
    return im


def lab(text, width):
    im = Image.new("RGB", (width, 26), "#ffffff")
    ImageDraw.Draw(im).text((12, 4), text, font=lf(), fill=ACC)
    return im


def stack(imgs, gap=8):
    w = max(i.width for i in imgs)
    h = sum(i.height for i in imgs) + gap * (len(imgs) - 1)
    out = Image.new("RGB", (w, h), "#ffffff")
    y = 0
    for i in imgs:
        out.paste(i, (0, y))
        y += i.height + gap
    return out


def a_three_versions():
    rows = [lab("V3 / V4 / V5 — Д Ж Э Я и слова", 1400)]
    for name, font in (("V3 (installed)", V3), ("V4 (candidate)", V4), ("V5 (new)", V5)):
        rows.append(lab(name, 1400))
        rows.append(line("Дд Жж Ээ Яя — Дом Жизнь Это Яблоко", 54, font))
        rows.append(line(RU3, 34, font))
        rows.append(line(EN1, 34, font))
    return stack(rows)


def b_caps():
    rows = [lab("Заглавные — 76 px", 1800)]
    rows.append(line(CAPS, 76))
    rows.append(line("ABCDEFGHIJKLMNOPQRSTUVWXYZ", 76))
    return stack(rows)


def c_lows():
    rows = [lab("Строчные — 76 px", 1800)]
    rows.append(line(LOWS, 76))
    rows.append(line("abcdefghijklmnopqrstuvwxyz", 76))
    return stack(rows)


def d_hard():
    rows = [lab("Проблемные буквы — 150 px", 2000)]
    rows.append(line("Дд Жж Ээ Яя Лл Шш Щщ Ъъ Ыы Ьь Юю", 150))
    return stack(rows)


def e_sentences():
    rows = [lab("Предложения — 34 px", 1700)]
    for t in (EN1, RU1, RU2, RU3, MIX1, MIX2, MIX3):
        rows.append(line(t, 34))
    return stack(rows)


def f_sizes():
    rows = [lab("Кегли 11–24 px (11–16 ×3, 20/24 ×1)", 1800)]
    for s in (11, 12, 13, 14, 16):
        im = line("Съешь ещё 0123 — The quick brown fox", s, pad=10)
        rows.append(im.resize((im.width * 3, im.height * 3), Image.NEAREST))
    for s in (20, 24):
        rows.append(line("Съешь ещё 0123 — The quick brown fox", s, pad=12))
    return stack(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    a_three_versions().save(OUT / "A-v3-v4-v5.png")
    b_caps().save(OUT / "B-caps.png")
    c_lows().save(OUT / "C-lowercase.png")
    d_hard().save(OUT / "D-problem-glyphs.png")
    e_sentences().save(OUT / "E-sentences.png")
    f_sizes().save(OUT / "F-sizes.png")
    print("ok")


if __name__ == "__main__":
    main()
