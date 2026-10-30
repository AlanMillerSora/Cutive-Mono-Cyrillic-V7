#!/usr/bin/env python3
"""V2 specimen set: A–E. Terminal shots (F) come from real screenshots."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "specimens" / "v2"
FONT = ROOT / "fonts" / "CutiveMono-Cyrillic-Regular.ttf"
ORIG = ROOT / "source" / "original" / "CutiveMono-Regular.ttf"
BG = "#fdfcf8"
INK = "#171717"
ACC = "#7a2d4a"

EN = "The quick brown fox jumps over the lazy dog."
RU1 = "Съешь же ещё этих мягких французских булок."
RU2 = "В чащах юга жил бы цитрус? Да, но фальшивый экземпляр!"
RU3 = "Съешь ещё этих мягких французских булок, да выпей чаю."
MIX1 = "English + Русский + 1234567890"
MIX2 = "Arch Linux — операционная система на базе Linux."
MIX3 = '$ git commit -m "Добавлена кириллица"'

CAPS = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
LOWS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
HARD = "Дд Жж Лл Тт Фф Цц Чч Шш Щщ Ъъ Ыы Ьь Ээ Юю Яя"


def label_font(size=16):
    try:
        return ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default()


def text_img(text: str, size: int, font_path=FONT, pad=20, color=INK, bg=BG):
    f = ImageFont.truetype(str(font_path), size)
    asc, desc = f.getmetrics()
    w = int(f.getlength(text)) + pad * 2
    h = asc + desc + pad
    im = Image.new("RGB", (w, h), bg)
    d = ImageDraw.Draw(im)
    d.text((pad, pad // 2), text, font=f, fill=color)
    return im


def title(text: str, width: int, sub: str = ""):
    lf = label_font(15)
    im = Image.new("RGB", (width, 46 if sub else 30), "#ffffff")
    d = ImageDraw.Draw(im)
    d.text((16, 6), text, font=lf, fill=ACC)
    if sub:
        d.text((16, 24), sub, font=label_font(12), fill="#8a8a8a")
    return im


def vstack(images, gap=10, bg="#ffffff"):
    w = max(i.width for i in images)
    h = sum(i.height for i in images) + gap * (len(images) - 1)
    out = Image.new("RGB", (w, h), bg)
    y = 0
    for i in images:
        out.paste(i, (0, y))
        y += i.height + gap
    return out


def a_latin_vs_cyrillic():
    parts = [title("A. Latin vs Cyrillic — одинаковый кегль 40 px", 1500)]
    for text in (EN, RU1, MIX1):
        parts.append(text_img(text, 40))
    return vstack(parts)


def b_alphabet():
    parts = [title("B. Alphabet comparison — 84 px", 1700)]
    for s in (CAPS, LOWS):
        parts.append(text_img(s, 84))
    parts.append(text_img("Aa Bb Ee Kk Mm Oo Pp Tt Xx", 84))
    return vstack(parts)


def c_problem():
    parts = [title("C. Problem glyphs — 150 px", 1700,
                   "переработаны: донорские чаши o/O, лапки у Д/д, засечки у Г/Б/Т, новая З")]
    im = text_img(HARD, 150)
    parts.append(im)
    return vstack(parts)


def d_small():
    parts = [title("D. Small sizes — 11 / 12 / 13 / 14 / 16 px (×3, nearest)", 1700)]
    for s in (11, 12, 13, 14, 16):
        im = text_img("Съешь ещё 0123 — The quick brown fox", s, pad=10)
        im = im.resize((im.width * 3, im.height * 3), Image.NEAREST)
        parts.append(im)
    return vstack(parts)


def e_mixed():
    parts = [title("E. Mixed text", 1500)]
    for t in (MIX1, MIX2, MIX3, RU2, RU3):
        parts.append(text_img(t, 38))
    return vstack(parts)


def f_side_by_side():
    """Original Latin vs the fork, same words."""
    parts = [title("Original vs fork — 44 px", 1500)]
    parts.append(text_img(EN, 44, ORIG))
    parts.append(text_img(EN, 44, FONT))
    return vstack(parts)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    a_latin_vs_cyrillic().save(OUT / "A-latin-vs-cyrillic.png")
    b_alphabet().save(OUT / "B-alphabet.png")
    c_problem().save(OUT / "C-problem-glyphs.png")
    d_small().save(OUT / "D-small-sizes.png")
    e_mixed().save(OUT / "E-mixed-text.png")
    f_side_by_side().save(OUT / "F-original-vs-fork.png")
    print("written:", *sorted(p.name for p in OUT.glob("*.png")), sep="\n  ")


if __name__ == "__main__":
    main()
